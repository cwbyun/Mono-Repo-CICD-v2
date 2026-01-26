import socket
import threading
import time
from typing import Optional, Callable

class SMDAQServerPure:
    """
    순수 Python 스레딩만 사용하는 1:1 동기 통신 서버.
    - 지정된 IP의 클라이언트 하나만 연결을 허용합니다.
    - 연결된 상태에서 다른 연결 시도는 거부됩니다.
    - query() 메서드를 통해 동기식 요청/응답을 처리합니다.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 5001, 
                 log_callback: Optional[Callable] = None,
                 allowed_client_ip: Optional[str] = None):
        self.host = host
        self.port = port
        self.log_callback = log_callback
        self.allowed_client_ip = allowed_client_ip
        self.server_socket: Optional[socket.socket] = None
        self.server_thread: Optional[threading.Thread] = None
        self.is_running = False
        
        self.client_socket: Optional[socket.socket] = None
        self.client_address: Optional[tuple] = None
        
        self._stop_event = threading.Event()
        # Use re-entrant lock to avoid deadlocks when nested calls (_disconnect_client inside locked contexts)
        self._client_lock = threading.RLock()
        # When a client is already connected, suppress noisy reject logs
        self.suppress_reject_log_when_connected = True
        # If a new connection arrives from the allowed IP while occupied,
        # drop the old client and accept the new one (helps when device reconnects)
        self.replace_existing_on_reconnect = True

    def log(self, message: str):
        log_msg = f"[SERVER] {message}"
        if self.log_callback:
            try:
                self.log_callback(log_msg)
            except Exception:
                print(log_msg)
        else:
            print(log_msg)
    
    def start_server(self) -> bool:
        if self.is_running:
            self.log("서버가 이미 실행 중입니다.")
            return False
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            
            self.is_running = True
            self._stop_event.clear()
            
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()
            
            self.log(f"서버가 {self.host}:{self.port}에서 시작되었습니다.")
            return True
        except Exception as e:
            self.log(f"서버 시작 실패: {e}")
            return False
    
    def stop_server(self):
        if not self.is_running:
            return
        self.is_running = False
        self._stop_event.set()
        
        self._disconnect_client()

        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
        
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=5.0)
            
        self.log("서버가 중지되었습니다.")
    
    def _server_loop(self):
        """서버 메인 루프 - 단일 클라이언트 접속 처리"""
        self.server_socket.settimeout(1.0)
        while not self._stop_event.is_set():
            try:
                new_socket, new_address = self.server_socket.accept()
            except socket.timeout:
                continue  # 타임아웃은 정상적인 상황이므로 루프 계속
            except OSError:
                # 소켓이 닫혔을 때 OSError가 발생합니다.
                # 서버 종료 신호(_stop_event)가 설정되었다면, 이는 정상적인 종료 과정입니다.
                if self._stop_event.is_set():
                    break  # 루프를 정상적으로 빠져나감
                else:
                    # 예기치 않은 오류일 경우 로그를 남기고 종료
                    self.log("소켓 accept 중 예기치 않은 OSError 발생.")
                    break

            if self._stop_event.is_set():
                new_socket.close()
                break

            with self._client_lock:
                client_ip = new_address[0]
                if self.allowed_client_ip and client_ip != self.allowed_client_ip:
                    self.log(f"접속 거부 (허용되지 않은 IP): {new_address}")
                    new_socket.close()
                    continue

                if self.client_socket is not None:
                    # If the same allowed client tries to reconnect, replace existing
                    if (self.replace_existing_on_reconnect and
                        (self.allowed_client_ip is None or client_ip == self.allowed_client_ip)):
                        self.log(f"기존 클라이언트를 새 연결로 교체: {new_address}")
                        self._disconnect_client()
                        self.client_socket = new_socket
                        self.client_address = new_address
                        self._handle_initial_client_message(new_socket)
                        continue
                    # Otherwise reject silently to avoid spam
                    if not self.suppress_reject_log_when_connected:
                        self.log(f"접속 거부 (이미 클라이언트 연결됨): {new_address}")
                    try:
                        new_socket.close()
                    except Exception:
                        pass
                    continue
                
                self.log(f"클라이언트 연결됨: {new_address}")
                self.client_socket = new_socket
                self.client_address = new_address

                # 클라이언트 초기 메시지만 한 번 처리
                self._handle_initial_client_message(new_socket)

    def _handle_initial_client_message(self, client_socket):
        """클라이언트 접속 시 초기 메시지만 한 번 처리합니다."""
        try:
            client_socket.settimeout(2.0)  # 2초 타임아웃
            data = client_socket.recv(1024)

            if data:
                message = data.decode('utf-8', errors='ignore').strip()
                if message and len(message) < 50:  # 작은 메시지만 클라이언트 ID로 간주
                    self.log(f"클라이언트 메시지: '{message}'")
                    self.log(f"{message}가 접속했습니다.")

        except socket.timeout:
            self.log("클라이언트로부터 초기 메시지를 받지 못했습니다.")
        except Exception as e:
            self.log(f"초기 메시지 처리 중 오류: {e}")
        finally:
            # 타임아웃을 None으로 되돌림 (블로킹 모드)
            try:
                client_socket.settimeout(None)
            except:
                pass

    def _disconnect_client(self):
        """현재 연결된 클라이언트를 안전하게 종료합니다."""
        with self._client_lock:
            if self.client_socket:
                self.log(f"클라이언트 연결 종료: {self.client_address}")
                try:
                    self.client_socket.shutdown(socket.SHUT_RDWR)
                except (socket.error, OSError):
                    pass # 이미 닫혔을 수 있음
                try:
                    self.client_socket.close()
                except (socket.error, OSError):
                    pass
                self.client_socket = None
                self.client_address = None

    def query(self, command: str, timeout: float = 5.0) -> Optional[str]:
        """
        클라이언트에게 동기식으로 명령을 보내고 응답을 기다립니다.
        :param command: 전송할 명령 문자열
        :param timeout: 응답을 기다릴 최대 시간 (초)
        :return: 클라이언트의 응답 문자열, 에러 또는 타임아웃 시 특정 에러 메시지
        """
        with self._client_lock:
            if not self.client_socket:
                self.log("명령 전송 실패: 클라이언트가 연결되지 않았습니다.")
                return "[ERROR] Client not connected"

            try:
                # 1. 소켓 타임아웃 설정
                self.client_socket.settimeout(timeout)

                # 2. 명령 전송
                full_command = command + '''\n'''
                self.client_socket.sendall(full_command.encode('utf-8'))
                self.log(f"명령 전송: '{command}' -> {self.client_address}")

                # 3. 응답 수신
                buffer = bytearray()
                while True:
                    try:
                        data = self.client_socket.recv(1024)
                        if not data:
                            break
                        buffer.extend(data)
                    except socket.timeout:
                        break

                    # 응답이 'Q'로 끝나는지 확인
                    if buffer.endswith(b'Q'):
                        break

                response = buffer.decode('utf-8', errors='ignore').strip()
                self.log(f"응답 수신: '{response}' <- {self.client_address}")
                return response

            except socket.timeout:
                self.log(f"응답 시간 초과 (Timeout: {timeout}s)")
                return "[ERROR] Timeout"
            except (socket.error, ConnectionResetError) as e:
                self.log(f"소켓 오류: {e}. 클라이언트 연결을 종료합니다.")
                self._disconnect_client()
                return f"[ERROR] Socket error: {e}"
            finally:
                # 다음을 위해 소켓 타임아웃을 블로킹 모드로 되돌림
                if self.client_socket:
                    self.client_socket.settimeout(None)

    def get_status(self) -> dict:
        """서버 상태 반환"""
        with self._client_lock:
            is_client_connected = self.client_socket is not None
        return {
            'running': self.is_running,
            'host': self.host,
            'port': self.port,
            'client_connected': is_client_connected,
            'client_address': self.client_address if is_client_connected else None
        }
