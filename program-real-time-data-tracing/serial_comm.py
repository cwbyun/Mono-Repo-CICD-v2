"""
시리얼 통신 모듈
"""
import serial
import time
import json
from typing import Optional
from config import SensorConfig, load_sensor_config_json
from sensor_data import SensorData, calculate_checksum, parse_sensor_string

class SerialCommunicator:
    """시리얼 통신 클래스"""
    
    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 19200, timeout: int = 2):
        """
        시리얼 통신 객체를 초기화합니다.
        
        Args:
            port: 시리얼 포트 경로
            baudrate: 통신 속도
            timeout: 타임아웃 (초)
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        
    def collect_sensor_data_once(self) -> SensorData:
        """
        센서에서 데이터를 한 번 수집합니다.
        
        Returns:
            SensorData: 수집된 센서 데이터
            
        Raises:
            serial.SerialException: 시리얼 통신 오류
            ValueError: 데이터 파싱 오류
        """
        # 설정 파일 로드
        config = load_sensor_config_json()
        
        # 시리얼 포트 연결
        with serial.Serial(self.port, self.baudrate, timeout=self.timeout) as ser:
            # 쿼리 생성
            # CMD=A이고 이 후 문자열이 없으므로 길이가 00 이다.
            cmd = "A00"
            query = config.send_stx + config.model + config.id + cmd
            
            # 체크섬 계산 및 추가
            checksum = calculate_checksum(query)
            query += f"{checksum:02X}" + config.send_etx
            
            #print(f"query = {query}")
            
            # 데이터 전송
            ser.write(query.encode('ascii'))
            
            # 응답 수신 (완전한 응답을 받을 때까지 반복)
            read_data = ""
            response_complete = False
            max_attempts = 50  # 최대 시도 횟수 제한
            attempts = 0
            
            while not response_complete and attempts < max_attempts:
                attempts += 1
                
                # 대기 중인 바이트 수 확인 후 읽기
                bytes_to_read = ser.in_waiting
                if bytes_to_read > 0:
                    temp_data = ser.read(bytes_to_read).decode('ascii', errors='ignore')
                else:
                    # 대기 중인 데이터가 없으면 1바이트만 읽되 짧은 타임아웃 설정
                    temp_data = ser.read(1).decode('ascii', errors='ignore')
                
                if temp_data:
                    read_data += temp_data
                    
                    # ETX 문자가 포함되어 있는지 확인하여 응답 완료 여부 판단
                    if config.receive_etx in read_data:
                        response_complete = True
                        
                # 데이터가 없고 읽은 데이터도 없으면 종료
                elif len(read_data) == 0:
                    break
                    
                # 짧은 대기 (CPU 사용률 감소)
                time.sleep(0.001)
            




            bytes_read = len(read_data)
            if bytes_read <= 0:
                raise ValueError("응답 데이터를 받지 못했습니다")
            
            # 데이터 파싱 및 반환
            return parse_sensor_string(read_data, config)
