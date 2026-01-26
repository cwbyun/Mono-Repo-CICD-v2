import serial
import time
import logging
from typing import Optional, Union, Dict

class RS485Communication:
    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 115200, 
                 timeout: float = 1.0, stx: str = "@", etx: str = "*",
                 recv_stx: str = None, recv_etx: str = None):
        """
        RS485 통신 클래스
        
        Args:
            port: 시리얼 포트 경로 (기본값: /dev/ttyUSB0)
            baudrate: 통신 속도 (기본값: 115200)
            timeout: 응답 대기 시간 (기본값: 1.0초)
            stx: Send STX 문자열 (기본값: "@")
            etx: Send ETX 문자열 (기본값: "*")
            recv_stx: Receive STX 문자열 (기본값: None, stx와 동일)
            recv_etx: Receive ETX 문자열 (기본값: None, etx와 동일)
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection: Optional[serial.Serial] = None
        self.STX = stx  # Send STX (문자열)
        self.ETX = etx  # Send ETX (문자열)
        self.RECV_STX = recv_stx or stx  # Receive STX (문자열)
        self.RECV_ETX = recv_etx or etx  # Receive ETX (문자열)
        
        # 로깅 설정 (터미널 출력 제거)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.ERROR)  # ERROR 레벨만 터미널에 출력

    def connect(self) -> bool:
        """시리얼 포트에 연결"""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            self.logger.info(f"Connected to {self.port} at {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            self.logger.error(f"Failed to connect to {self.port}: {e}")
            return False

    def disconnect(self):
        """시리얼 포트 연결 해제"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.logger.info(f"Disconnected from {self.port}")

    def is_connected(self) -> bool:
        """연결 상태 확인"""
        return (self.serial_connection is not None and 
                self.serial_connection.is_open)

    def calculate_checksum(self, data: Union[str, bytes]) -> str:
        """
        체크섬 계산 (SUM + 0xFF XOR + 1, ASCII 2자리)
        
        Args:
            data: 체크섬을 계산할 데이터 (STX + query-string)
            
        Returns:
            계산된 체크섬 값 (ASCII 2자리 문자열)
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # 모든 바이트의 합계 계산
        total_sum = sum(data)
        
        # 0xFF와 XOR 후 +1
        checksum = (total_sum ^ 0xFF) + 1
        
        # 8비트로 제한 (0x00~0xFF)
        checksum = checksum & 0xFF
        
        # ASCII 2자리 16진수 문자열로 변환
        return f"{checksum:02X}"

    def build_simple_command(self, query_string: str, prestring: str = "", poststring: str = "") -> bytes:
        """
        STX + PRESTRING + query-string + POSTSTRING + ETX 형태의 명령 패킷 생성 (체크섬 없음)
        
        Args:
            query_string: 전송할 쿼리 문자열 (메인 명령)
            prestring: STX 다음에 올 공통 접두사 (선택적)
            poststring: 쿼리 다음에 올 공통 접미사 (선택적)
            
        Returns:
            완성된 명령 패킷 (bytes)
        """
        # STX + PRESTRING + query-string + POSTSTRING + ETX
        full_command = self.STX + prestring + query_string + poststring + self.ETX
        
        return full_command.encode('utf-8')

    def build_command(self, query_string: str, prestring: str = "", poststring: str = "") -> bytes:
        """
        STX + PRESTRING + query-string + POSTSTRING + CHECKSUM + ETX 형태의 명령 패킷 생성
        
        Args:
            query_string: 전송할 쿼리 문자열 (메인 명령)
            prestring: STX 다음에 올 공통 접두사 (선택적)
            poststring: 쿼리 다음에 올 공통 접미사 (선택적)
            
        Returns:
            완성된 명령 패킷 (bytes)
        """
        # STX + PRESTRING + query-string + POSTSTRING 결합
        stx_and_data = self.STX + prestring + query_string + poststring
        
        # 체크섬 계산 (STX + PRESTRING + query-string + POSTSTRING에 대해)
        checksum_str = self.calculate_checksum(stx_and_data)
        
        # 최종 패킷: STX + PRESTRING + query-string + POSTSTRING + CHECKSUM + ETX
        full_command = stx_and_data + checksum_str + self.ETX
        
        return full_command.encode('utf-8')
    
    def preview_simple_command(self, query_string: str, prestring: str = "", poststring: str = "") -> Dict[str, str]:
        """
        연결 없이 간단한 명령 패킷 미리보기 (체크섬 없음)
        
        Args:
            query_string: 전송할 쿼리 문자열
            prestring: STX 다음에 올 공통 접두사 (선택적)
            poststring: 쿼리 다음에 올 공통 접미사 (선택적)
            
        Returns:
            명령 정보를 담은 딕셔너리
        """
        # STX + PRESTRING + query-string + POSTSTRING + ETX
        full_command = self.STX + prestring + query_string + poststring + self.ETX
        command_bytes = full_command.encode('utf-8')
        
        return {
            'stx': self.STX,
            'prestring': prestring,
            'query_string': query_string,
            'poststring': poststring,
            'etx': self.ETX,
            'checksum': 'N/A',
            'full_command': full_command,
            'full_command_hex': command_bytes.hex().upper(),
            'command_length': str(len(command_bytes))
        }
    
    def preview_command(self, query_string: str, prestring: str = "", poststring: str = "") -> Dict[str, str]:
        """
        연결 없이 명령 패킷 미리보기
        
        Args:
            query_string: 전송할 쿼리 문자열
            prestring: STX 다음에 올 공통 접두사 (선택적)
            poststring: 쿼리 다음에 올 공통 접미사 (선택적)
            
        Returns:
            명령 정보를 담은 딕셔너리
        """
        # STX + PRESTRING + query-string + POSTSTRING 결합
        stx_and_data = self.STX + prestring + query_string + poststring
        
        # 체크섬 계산
        checksum_str = self.calculate_checksum(stx_and_data)
        
        # 최종 패킷
        full_command = stx_and_data + checksum_str + self.ETX
        command_bytes = full_command.encode('utf-8')
        
        return {
            'stx': self.STX,
            'prestring': prestring,
            'query_string': query_string,
            'poststring': poststring,
            'etx': self.ETX,
            'stx_and_data': stx_and_data,
            'checksum': checksum_str,
            'full_command': full_command,
            'full_command_hex': command_bytes.hex().upper(),
            'command_length': str(len(command_bytes))
        }

    def send_simple_query(self, query_string: str) -> Optional[str]:
        """
        간단한 데이터를 전송하고 응답 받기 (체크섬 없음)
        
        Args:
            query_string: 전송할 쿼리 문자열
            
        Returns:
            수신된 응답 문자열 또는 None (실패시)
        """
        if not self.is_connected():
            self.logger.error("Not connected to serial port")
            return None

        try:
            # 간단한 명령 패킷 생성 (체크섬 없음)
            command = self.build_simple_command(query_string)
            
            # 송신 버퍼 클리어
            self.serial_connection.reset_output_buffer()
            self.serial_connection.reset_input_buffer()
            
            # 데이터 전송
            self.serial_connection.write(command)
            self.logger.info(f"Sent (simple): {command.hex()}")
            
            # 응답 대기 개선
            response = b""
            start_time = time.time()
            etx_bytes = self.ETX.encode('utf-8')
            
            # 수신용 ETX로 응답 대기
            recv_etx_bytes = self.RECV_ETX.encode('utf-8')
            
            while time.time() - start_time < self.timeout:
                try:
                    # 1바이트씩 읽어서 수신 ETX까지 수집
                    byte_data = self.serial_connection.read(1)
                    if byte_data:
                        response += byte_data
                        # 수신 ETX를 찾으면 종료
                        if response.endswith(recv_etx_bytes):
                            break
                    else:
                        time.sleep(0.01)
                except serial.SerialTimeoutException:
                    continue
            
            if response:
                self.logger.info(f"Received: {response.hex()}")
                return self.parse_response(response)
            else:
                self.logger.warning("No response received")
                return None
                
        except serial.SerialException as e:
            self.logger.error(f"Serial communication error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return None

    def send_query(self, query_string: str) -> Optional[str]:
        """
        데이터를 전송하고 응답 받기
        
        Args:
            query_string: 전송할 쿼리 문자열
            
        Returns:
            수신된 응답 문자열 또는 None (실패시)
        """
        if not self.is_connected():
            self.logger.error("Not connected to serial port")
            return None

        try:
            # 명령 패킷 생성
            command = self.build_command(query_string)
            
            # 송신 버퍼 클리어
            self.serial_connection.reset_output_buffer()
            self.serial_connection.reset_input_buffer()
            
            # 데이터 전송
            self.serial_connection.write(command)
            self.logger.info(f"Sent: {command.hex()}")
            
            # 응답 대기 개선
            response = b""
            start_time = time.time()
            etx_bytes = self.ETX.encode('utf-8')
            
            # 수신용 ETX로 응답 대기
            recv_etx_bytes = self.RECV_ETX.encode('utf-8')
            
            while time.time() - start_time < self.timeout:
                try:
                    # 1바이트씩 읽어서 수신 ETX까지 수집
                    byte_data = self.serial_connection.read(1)
                    if byte_data:
                        response += byte_data
                        # 수신 ETX를 찾으면 종료
                        if response.endswith(recv_etx_bytes):
                            break
                    else:
                        time.sleep(0.01)
                except serial.SerialTimeoutException:
                    continue
            
            if response:
                self.logger.info(f"Received: {response.hex()}")
                return self.parse_response(response)
            else:
                self.logger.warning("No response received")
                return None
                
        except serial.SerialException as e:
            self.logger.error(f"Serial communication error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return None

    def parse_response(self, response: bytes) -> Optional[str]:
        """
        응답 패킷 파싱 - 수신된 데이터를 있는 그대로 처리
        
        Args:
            response: 수신된 응답 패킷
            
        Returns:
            파싱된 데이터 문자열 (전체 응답)
        """
        try:
            # 바이트를 문자열로 디코딩
            response_str = response.decode('utf-8', errors='replace')
            
            # 수신된 데이터를 있는 그대로 반환
            self.logger.info(f"Parsed response: {response_str}")
            return response_str
            
        except Exception as e:
            self.logger.error(f"Error parsing response: {e}")
            return None
    
    def parse_structured_response(self, response_str: str) -> Optional[dict]:
        """
        구조화된 응답 파싱: STX + PRE + CMD + LENGTH + data_string + CHKSUM + ETX
        
        Args:
            response_str: 수신된 응답 문자열
            
        Returns:
            파싱된 데이터 딕셔너리 또는 None
        """
        try:
            # 기본 구조 파싱
            if not response_str.startswith(self.RECV_STX):
                self.logger.error(f"Invalid receive STX: {response_str[:10]}")
                return None
            
            if not response_str.endswith(self.RECV_ETX):
                self.logger.error(f"Invalid receive ETX: {response_str[-10:]}")
                return None
            
            # STX, ETX 제거
            content = response_str[len(self.RECV_STX):-len(self.RECV_ETX)]
            
            # 최소 길이 확인 (PRE + CMD + LENGTH + CHKSUM = 최소 6자)
            if len(content) < 6:
                self.logger.error("Response content too short")
                return None
            
            # CHKSUM (마지막 2자리) 분리
            data_part = content[:-2]
            checksum = content[-2:]
            
            # PRE는 고정 길이 (예: JW17000000 = 10자)
            # 실제 구조: PRE(10) + CMD(1) + LENGTH(1 or 2) + data_string
            pre = data_part[:10]  # JW17000000
            cmd = data_part[10]   # A, C, E, F, G, H, I
            
            # LENGTH 파싱 (F 명령은 1자리, 다른 명령은 2자리)
            if cmd == 'F':
                # F 명령만 1자리 LENGTH (버그)
                length_str = data_part[11]
                data_start = 12
            else:
                # 다른 모든 명령은 2자리 LENGTH
                length_str = data_part[11:13]
                data_start = 13
                
            try:
                data_length = int(length_str)
                data_string = data_part[data_start:data_start+data_length]
                
                if len(data_string) != data_length:
                    self.logger.error(f"Data length mismatch: expected {data_length}, got {len(data_string)}")
                    return None
                
            except ValueError:
                self.logger.error(f"Invalid length value: {length_str}")
                return None
            
            result = {
                'pre': pre,
                'cmd': cmd,
                'length': data_length,
                'data_string': data_string,
                'checksum': checksum,
                'raw_response': response_str
            }
            
            # CMD별 데이터 파싱
            if cmd == 'A':
                parsed_data = self.parse_cmd_a_data(data_string)
                result['parsed_data'] = parsed_data
            elif cmd == 'C':
                parsed_data = self.parse_cmd_c_data(data_string)
                result['parsed_data'] = parsed_data
            elif cmd == 'E':
                parsed_data = self.parse_cmd_e_data(data_string)
                result['parsed_data'] = parsed_data
            elif cmd == 'F':
                parsed_data = self.parse_cmd_f_data(data_string)
                result['parsed_data'] = parsed_data
            elif cmd == 'G':
                parsed_data = self.parse_cmd_g_data(data_string)
                result['parsed_data'] = parsed_data
            elif cmd == 'H':
                parsed_data = self.parse_cmd_h_data(data_string)
                result['parsed_data'] = parsed_data
            elif cmd == 'I':
                parsed_data = self.parse_cmd_i_data(data_string)
                result['parsed_data'] = parsed_data
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error parsing structured response: {e}")
            return None
    
    def parse_cmd_a_data(self, data_string: str) -> dict:
        """
        CMD=A 데이터 파싱
        형식: 3 05822 2 32748 2 32910 1 30001 B 01133 C 00309
        
        Args:
            data_string: 파싱할 데이터 문자열
            
        Returns:
            파싱된 센서 데이터
        """
        result = {}
        pos = 0
        
        try:
            # 변위계 길이 (3 05822 -> 58.22)
            if pos < len(data_string) and data_string[pos] == '3':
                displacement_raw = data_string[pos+1:pos+6]  # 05822
                displacement = float(displacement_raw) / 100.0  # 58.22
                result['displacement'] = displacement
                pos += 6
            
            # X 각도 LSB (2 32748)
            if pos < len(data_string) and data_string[pos] == '2':
                x_angle_raw = data_string[pos+1:pos+6]  # 32748
                result['x_angle_lsb'] = int(x_angle_raw)
                pos += 6
            
            # Y 각도 LSB (2 32910)  
            if pos < len(data_string) and data_string[pos] == '2':
                y_angle_raw = data_string[pos+1:pos+6]  # 32910
                result['y_angle_lsb'] = int(y_angle_raw)
                pos += 6
            
            # 온도 (1 30001 -> (32767 - 30001) / 100)
            if pos < len(data_string) and data_string[pos] == '1':
                temp_raw = data_string[pos+1:pos+6]  # 30001
                temp_value = (32767 - int(temp_raw)) / 100.0  # 32767에서 빼고 100으로 나누기
                result['temperature'] = temp_value
                pos += 6
            
            # 전압 (B 01133 -> 11.33V)
            if pos < len(data_string) and data_string[pos] == 'B':
                voltage_raw = data_string[pos+1:pos+6]  # 01133
                voltage = float(voltage_raw) / 100.0  # 11.33
                result['voltage'] = voltage
                pos += 6
            
            # 전류 (C 00309 -> 30.9mA)
            if pos < len(data_string) and data_string[pos] == 'C':
                current_raw = data_string[pos+1:pos+6]  # 00309
                current = float(current_raw) / 10.0  # 30.9
                result['current_ma'] = current
                pos += 6
            
        except Exception as e:
            self.logger.error(f"Error parsing CMD A data: {e}")
        
        return result
    
    def parse_cmd_c_data(self, data_string: str) -> dict:
        """
        CMD=C 데이터 파싱
        형식: d.dd d d d d d.ddd d d d (총 16자)
        
        Args:
            data_string: 파싱할 데이터 문자열 (LENGTH=16)
            
        Returns:
            파싱된 설정 데이터
        """
        result = {}
        
        try:
            if len(data_string) != 16:
                self.logger.error(f"CMD C data length should be 16, got {len(data_string)}")
                return result
            
            # 1. 버전 (d.dd) - 처음 4자리
            version_raw = data_string[0:4]  # 예: "1.23"
            result['version'] = float(version_raw)
            
            # 2. 쪽보드 센스 종류 (d) - 5번째 문자
            sensor_type_code = int(data_string[4])
            sensor_types = {0: "MPU6050", 1: "ISM330DHCX", 2: "SCL3300-D01", 9: "없음"}
            result['sensor_type'] = sensor_types.get(sensor_type_code, f"알 수 없음({sensor_type_code})")
            result['sensor_type_code'] = sensor_type_code
            
            # 3. 종단저항릴레이 (d) - 6번째 문자  
            relay_code = int(data_string[5])
            result['termination_relay'] = "연결" if relay_code == 1 else "끊김"
            result['termination_relay_code'] = relay_code
            
            # 4. 온도보상 (d) - 7번째 문자
            temp_comp_code = int(data_string[6])
            result['temperature_compensation'] = "on" if temp_comp_code == 1 else "off"
            result['temperature_compensation_code'] = temp_comp_code
            
            # 5. 변위계기준상태 (d) - 8번째 문자
            disp_status_code = int(data_string[7])
            result['displacement_status'] = "정상" if disp_status_code == 1 else "불량"
            result['displacement_status_code'] = disp_status_code
            
            # 6. 변위계 기준전압 (d.ddd) - 9~13번째 문자
            voltage_raw = data_string[8:13]  # 예: "3.300"
            result['reference_voltage'] = float(voltage_raw)
            
            # 7. 각도계상태 (d) - 14번째 문자
            angle_status_code = int(data_string[13])
            result['angle_status'] = "정상" if angle_status_code == 1 else "불량"
            result['angle_status_code'] = angle_status_code
            
            # 8. 변위계 설정 (d) - 15번째 문자
            disp_setting_code = int(data_string[14])
            result['displacement_setting'] = "on" if disp_setting_code == 1 else "off"
            result['displacement_setting_code'] = disp_setting_code
            
            # 9. 각도계 설정 (d) - 16번째 문자
            angle_setting_code = int(data_string[15])
            result['angle_setting'] = "on" if angle_setting_code == 1 else "off"
            result['angle_setting_code'] = angle_setting_code
            
        except Exception as e:
            self.logger.error(f"Error parsing CMD C data: {e}")
        
        return result
    
    def parse_cmd_e_data(self, data_string: str) -> dict:
        """
        CMD=E 데이터 파싱 (응답용)
        형식: d (총 1자) - 연결 상태 현재 설정
        
        Args:
            data_string: 파싱할 데이터 문자열 (LENGTH=02, 실제 데이터는 1자)
            
        Returns:
            파싱된 연결 상태 데이터
        """
        result = {}
        
        try:
            if len(data_string) < 1:
                self.logger.error(f"CMD E data length should be at least 1, got {len(data_string)}")
                return result
            
            # 연결 상태 현재 설정 (d) - 첫 번째 문자
            status_code = int(data_string[0])
            result['connection_status'] = "연결" if status_code == 1 else "끊김"
            result['connection_status_code'] = status_code
            result['status_message'] = f"연결상태가 {result['connection_status']}으로 설정되어 있습니다"
            
        except Exception as e:
            self.logger.error(f"Error parsing CMD E data: {e}")
        
        return result
    
    def parse_cmd_f_data(self, data_string: str) -> dict:
        """
        CMD=F 데이터 파싱
        형식: 릴레이 off 시간(초) 문자열
        
        Args:
            data_string: 파싱할 데이터 문자열 (릴레이 off 시간)
            
        Returns:
            파싱된 릴레이 off 시간 데이터
        """
        result = {}
        
        try:
            # 릴레이 off 시간 그대로 파싱
            try:
                relay_off_time = int(data_string)
                result['relay_off_time'] = relay_off_time
            except ValueError:
                self.logger.error(f"Invalid relay off time: {data_string}")
                result['relay_off_time'] = 0
                result['relay_off_time_str'] = data_string
            
        except Exception as e:
            self.logger.error(f"Error parsing CMD F data: {e}")
        
        return result
    
    def parse_cmd_g_data(self, data_string: str) -> dict:
        """
        CMD=G 데이터 파싱 (응답용)
        형식: d (총 1자) - 온도보상 현재 상태
        
        Args:
            data_string: 파싱할 데이터 문자열 (LENGTH=01, 실제 데이터는 1자)
            
        Returns:
            파싱된 온도보상 상태 데이터
        """
        result = {}
        
        try:
            if len(data_string) < 1:
                self.logger.error(f"CMD G data length should be at least 1, got {len(data_string)}")
                return result
            
            # 온도보상 현재 상태 (d) - 첫 번째 문자
            temp_comp_code = int(data_string[0])
            result['temperature_compensation'] = "ON" if temp_comp_code == 1 else "OFF"
            result['temperature_compensation_code'] = temp_comp_code
            result['status_message'] = f"온도보상 설정이 {result['temperature_compensation']}으로 되어있습니다"
            
        except Exception as e:
            self.logger.error(f"Error parsing CMD G data: {e}")
        
        return result
    
    def parse_cmd_h_data(self, data_string: str) -> dict:
        """
        CMD=H 데이터 파싱
        형식: 데이터 없음 - RESET 명령
        
        Args:
            data_string: 파싱할 데이터 문자열 (보통 빈 문자열)
            
        Returns:
            파싱된 RESET 명령 데이터
        """
        result = {}
        
        try:
            # RESET 명령은 데이터가 없으므로 단순히 상태만 표시
            result['reset_status'] = "Reset되었습니다"
            result['command_type'] = "RESET"
            
        except Exception as e:
            self.logger.error(f"Error parsing CMD H data: {e}")
        
        return result
    
    def parse_cmd_i_data(self, data_string: str) -> dict:
        """
        CMD=I 데이터 파싱
        형식: 10자리 ID 문자열
        
        Args:
            data_string: 파싱할 데이터 문자열 (10자리 ID)
            
        Returns:
            파싱된 ID 데이터
        """
        result = {}
        
        try:
            # 10자리 ID 그대로 출력
            result['device_id'] = data_string
            result['id_length'] = len(data_string)
            
        except Exception as e:
            self.logger.error(f"Error parsing CMD I data: {e}")
        
        return result

    def set_stx_etx(self, stx: str, etx: str, recv_stx: str = None, recv_etx: str = None):
        """STX와 ETX 값 변경"""
        self.STX = stx
        self.ETX = etx
        if recv_stx is not None:
            self.RECV_STX = recv_stx
        if recv_etx is not None:
            self.RECV_ETX = recv_etx
        self.logger.info(f"STX/ETX updated: Send STX='{stx}', ETX='{etx}', Recv STX='{self.RECV_STX}', ETX='{self.RECV_ETX}'")

    def __enter__(self):
        """with 문 지원"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """with 문 지원"""
        self.disconnect()