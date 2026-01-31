import socket
import time
from utils import calculate_checksum
import protocol as ptcl

def _normalize_command(command: str) -> str:
    clean_cmd = command.strip().replace("\n", "").replace("\r", "")
    if clean_cmd.startswith("\x02"):
        clean_cmd = clean_cmd[1:]
    if clean_cmd.endswith("\x03"):
        clean_cmd = clean_cmd[:-1]
    if clean_cmd.startswith(ptcl.STX):
        clean_cmd = clean_cmd[len(ptcl.STX):]
    if clean_cmd.endswith(ptcl.ETX):
        clean_cmd = clean_cmd[:-len(ptcl.ETX)]
    return clean_cmd

def _get_end_mode(clean_cmd: str) -> str:
    if clean_cmd.startswith('E') or clean_cmd.startswith('F'):
        return "END_STATUS"
    if (clean_cmd.startswith('3') or clean_cmd.startswith('4') or
        clean_cmd.startswith('C') or clean_cmd.startswith('D') or
        clean_cmd.startswith('G') or clean_cmd.startswith('H') or
        clean_cmd.startswith('B')):
        return "END"
    return ""

def _line_ending_index(buffer: bytes) -> int:
    if buffer.endswith(b"\r\n"):
        return len(buffer) - 2
    if buffer.endswith(b"\n") or buffer.endswith(b"\r"):
        return len(buffer) - 1
    return -1

def _buffer_has_end_line(buffer: bytes) -> bool:
    end_idx = _line_ending_index(buffer)
    if end_idx < 3:
        return False
    start_idx = end_idx - 3
    if buffer[start_idx:end_idx] != b"END":
        return False
    if start_idx == 0:
        return True
    return buffer[start_idx - 1] in (10, 13)

def _buffer_has_end_status(buffer: bytes) -> bool:
    end_idx = _line_ending_index(buffer)
    if end_idx < 5:
        return False
    start_idx = end_idx - 5
    suffix = buffer[start_idx:end_idx]
    if suffix[:3] != b"END":
        return False
    if suffix[3] in (10, 13) or suffix[4] in (10, 13):
        return False
    if start_idx == 0:
        return True
    return buffer[start_idx - 1] in (10, 13)

def _buffer_has_end_marker(buffer: bytes, end_mode: str) -> bool:
    if not buffer:
        return False
    if end_mode == "END":
        return _buffer_has_end_line(buffer)
    if end_mode == "END_STATUS":
        return _buffer_has_end_status(buffer)
    return False

def _drain_line_buffer(line_buffer: bytearray, on_line) -> bytearray:
    parts = line_buffer.splitlines(keepends=True)
    if not parts:
        return line_buffer
    if not (parts[-1].endswith(b"\n") or parts[-1].endswith(b"\r")):
        partial = parts.pop()
    else:
        partial = b""
    for part in parts:
        text = part.rstrip(b"\r\n").decode("utf-8", errors="replace")
        if text:
            on_line(text)
    return bytearray(partial)

def _should_wait_for_etx(command: str) -> bool:
    """
    명령에 따라 ETX('Q')를 기다려야 하는지 판단
    """
    # ETX가 없는 짧은 명령들
    short_commands = ['9', 'A']

    clean_cmd = _normalize_command(command)

    for short_cmd in short_commands:
        if clean_cmd.startswith(short_cmd):
            return False

    return True

def _get_command_timeout(command: str) -> tuple:
    """
    명령에 따른 적절한 타임아웃 시간과 대기 전략 반환
    Returns: (socket_timeout, max_wait_time, wait_for_etx)
    """
    clean_cmd = _normalize_command(command)

    # 데이터 조회 명령들 (긴 응답) - Data Tab의 대부분 명령
    if (clean_cmd.startswith('3') or clean_cmd.startswith('4') or
        clean_cmd.startswith('C') or clean_cmd.startswith('D') or
        clean_cmd.startswith('E') or clean_cmd.startswith('F') or
        clean_cmd.startswith('G') or clean_cmd.startswith('H') or
        clean_cmd.startswith('B')):
        return (10.0, 120.0, True)   # socket timeout, max wait, wait for ETX
    # 짧은 명령들 (ETX 없음)
    elif clean_cmd.startswith('9') or clean_cmd.startswith('A'):
        return (3.0, 4.0, False)   # 짧은 타임아웃, ETX 대기 안함
    # 일반 명령들
    else:
        return (5.0, 8.0, True)    # 일반적인 설정

def send_command(command: str, ip: str, port: int, on_line=None) -> str:
    """
        지정된 IP와 포트로 TCP 소켓 통신을 통해 명령을 보내고 응답을 받습니다.

        Args:
            command (str): 장비에 보낼 문자열 명령.
            ip (str): 장비의 IP 주소.
            port (int): 장비의 포트 번호.

        Returns:
            str: 장비로부터 받은 응답 문자열. 오류 발생 시 오류 메시지를 반환합니다.
    """

    # 명령에 따른 타임아웃 및 전략 결정
    socket_timeout, max_wait_time, wait_for_etx = _get_command_timeout(command)
    end_mode = _get_end_mode(_normalize_command(command))

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(socket_timeout)

            # SO_REUSEADDR 설정으로 이전 연결 재사용 허용
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            sock.connect( (ip, port ) )

            sock.sendall( (command + "\n").encode("utf-8"))

            response_bytes = b""
            line_buffer = bytearray()
            start_time = time.time()
            needs_complete_response = bool(end_mode) or wait_for_etx

            while True:
                # 최대 대기 시간 초과 검사
                if time.time() - start_time > max_wait_time:
                    break

                try:
                    chunk = sock.recv(8192)
                    if not chunk:
                        break
                    response_bytes += chunk
                    if on_line:
                        line_buffer.extend(chunk)
                        line_buffer = _drain_line_buffer(line_buffer, on_line)

                    if end_mode and _buffer_has_end_marker(response_bytes, end_mode):
                        break
                    # ETX를 기다려야 하는 명령의 경우
                    if wait_for_etx and response_bytes.endswith(b'Q'):
                        break
                    # ETX를 기다리지 않는 명령의 경우, 데이터가 있으면 잠깐 더 기다림
                    elif not wait_for_etx and len(response_bytes) > 0:
                        # 추가 데이터가 올 수 있으니 짧게 대기
                        sock.settimeout(0.5)
                        continue

                except socket.timeout:
                    # ETX를 기다리지 않는 명령이거나, 이미 데이터가 있으면 종료
                    if not needs_complete_response:
                        if len(response_bytes) > 0:
                            break
                    continue

            # 소켓 명시적으로 종료
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except:
                pass  # 이미 연결이 끊어진 경우 무시

            # 응답 처리 및 유효성 검사
            if on_line and line_buffer:
                tail = line_buffer.decode("utf-8", errors="replace").strip()
                if tail:
                    on_line(tail)
            response_str = response_bytes.decode('utf-8', errors='ignore').strip()

            # 디버그 정보 (필요시 주석 해제)
            # print(f"CMD: {command.strip()[:20]}..., Wait ETX: {wait_for_etx}, Response len: {len(response_str)}")

            return response_str

    except socket.timeout:
        error_msg = f"[ERROR] 응답 시간 초과 (타임아웃: {socket_timeout}초)"
        return error_msg
    except ConnectionRefusedError:
        error_msg = "[ERROR] 연결 거부됨 - 서버가 응답하지 않거나 이미 다른 클라이언트가 연결되어 있습니다"
        return error_msg
    except Exception as e:
        error_msg = f"[ERROR] 통신 오류: {e}"
        return error_msg


def send_command_to_server(command: str, ip: str, port: int, on_line=None) -> str:
    """
    서버 테스트용 클라이언트 함수 - 기존 send_command와 동일하지만 명시적 구분
    """
    return send_command(command, ip, port, on_line=on_line)


def format_server_response(data: str) -> str:
    """
    서버 응답을 표준 프로토콜 형식으로 포맷팅
    
    Args:
        data (str): 응답 데이터
    
    Returns:
        str: STX + data + ETX 형식의 응답
    """
    return f"{ptcl.STX}{data}{ptcl.ETX}"


def parse_client_command(raw_command: str) -> str:
    """
    클라이언트로부터 받은 원시 명령을 파싱
    
    Args:
        raw_command (str): STX, ETX, 개행문자가 포함된 원시 명령
    
    Returns:
        str: 정리된 명령 문자열
    """
    # STX, ETX, 개행문자 제거
    clean_command = raw_command.strip()
    clean_command = clean_command.replace(ptcl.STX, "")
    clean_command = clean_command.replace(ptcl.ETX, "")
    clean_command = clean_command.replace("\n", "")
    clean_command = clean_command.replace("\r", "")
    
    return clean_command.strip()


def create_error_response(error_message: str) -> str:
    """
    에러 응답 생성
    
    Args:
        error_message (str): 에러 메시지
    
    Returns:
        str: 포맷팅된 에러 응답
    """
    return format_server_response(f"ERROR:{error_message}")







    
