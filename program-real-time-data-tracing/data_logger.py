"""
데이터 로거 모듈
"""
import csv
import os
import time
from datetime import datetime
from typing import Optional
from serial_comm import SerialCommunicator
from sensor_data import SensorData

class DataLogger:
    """센서 데이터 로거 클래스"""
    
    def __init__(self, filename: str = "sensor_data.csv", interval: int = 5, 
                 port: str = "/dev/ttyUSB0", baudrate: int = 19200):
        """
        데이터 로거를 초기화합니다.
        
        Args:
            filename: CSV 파일명
            interval: 데이터 수집 간격 (초)
            port: 시리얼 포트 경로
            baudrate: 통신 속도
        """
        self.filename = filename
        self.interval = interval
        self.serial_comm = SerialCommunicator(port, baudrate)
        
    def get_timestamp(self) -> str:
        """
        현재 시간을 문자열로 반환합니다.
        
        Returns:
            str: 현재 시간 (YYYY-MM-DD HH:MM:SS 형식)
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def write_header_if_needed(self) -> None:
        """
        CSV 파일이 존재하지 않으면 헤더를 작성합니다.
        """
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'timestamp', 'length', 'angle_x', 'angle_y', 
                    'temperature', 'voltage', 'current'
                ])
    
    def log_data(self, data: SensorData) -> None:
        """
        센서 데이터를 CSV 파일에 기록합니다.
        
        Args:
            data: 센서 데이터
        """
        timestamp = self.get_timestamp()
        
        # 헤더가 필요한 경우 작성
        self.write_header_if_needed()
        
        # 데이터 추가
        with open(self.filename, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                timestamp, data.length, data.angle_x, data.angle_y,
                data.temperature, data.voltage, data.current
            ])
        
        print(f"데이터 저장됨: {self.filename}")
    
    def start_logging(self) -> None:
        """
        데이터 로깅을 시작합니다. Ctrl+C로 종료할 수 있습니다.
        """
        #print(f"데이터 로깅 시작 ({self.interval}초 간격)")
        #print("종료하려면 Ctrl+C를 누르세요")
        
        try:
            while True:
                try:
                    # 센서 데이터 수집
                    data = self.serial_comm.collect_sensor_data_once()
                    
                    # CSV 파일에 기록
                    self.log_data(data)
                    
                    print(f"길이: {data.length:.2f}mm, "
                          f"각도: X={data.angle_x:.2f}°, Y={data.angle_y:.2f}°, "
                          f"온도: {data.temperature:.2f}°C, "
                          f"전압: {data.voltage:.2f}V, "
                          f"전류: {data.current:.1f}mA")
                    
                except Exception as e:
                    print(f"오류 발생: {e}")
                
                # 지정된 간격만큼 대기
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n데이터 로깅을 종료합니다.")
