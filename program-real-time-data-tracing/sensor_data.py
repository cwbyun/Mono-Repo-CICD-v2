"""
센서 데이터 처리 모듈
"""
from dataclasses import dataclass
from typing import Optional
from config import SensorConfig, load_sensor_config_json
from utils import *

@dataclass
class SensorData:
    """센서 데이터 클래스"""
    length: float
    angle_x: float
    angle_y: float
    temperature: float
    voltage: float
    current: float

def calculate_checksum(data: str) -> int:
    """
    문자열 데이터의 8비트 2의 보수 체크섬을 계산합니다.
    
    Args:
        data: 체크섬을 계산할 입력 문자열
        
    Returns:
        int: 계산된 8비트 체크섬 값
    """
    sum_bytes = sum(ord(c) for c in data) & 0xFF
    checksum = ((~sum_bytes) + 1) & 0xFF
    return checksum

def confirm_checksum( response: str ):

    config = load_sensor_config_json()
    n_chksum = 2+len(config.receive_etx)
    #print("n_chksum = ", n_chksum)
    #print("response =", response)
    i = response.find(config.receive_stx)
    #sss="aaa"
    #print("i = ", i)
    #print("i =", config.receive_stx)
    #print("sss=",sss)
    stemp = response[i:-n_chksum]
    #print("stemp  =", stemp )
    chk = calculate_checksum( stemp )
    chk_hex = f"{chk:02X}"
    #print("r= ",response[-n_chksum:-len(config.receive_etx)])
    if chk_hex == response[-n_chksum:-len(config.receive_etx)]:
        return True
    else :
        #print("chk = ", chk_hex )
        return False


def parse_sensor_string(response: str, config: SensorConfig) -> SensorData:
    """
    센서 응답 문자열을 파싱하여 센서 데이터를 추출합니다.
    
    Args:
        response: 센서로부터 받은 응답 문자열
        config: 센서 설정 객체
        
    Returns:
        SensorData: 파싱된 센서 데이터
        
    Raises:
        ValueError: 응답 형식이 잘못된 경우
    """

    if ( not confirm_checksum( response ) ):
        print("Checksum is WRONG")
        exit(1)


    pre_length = len(config.receive_stx)+len(config.model)+len(config.id)+1  # 마지막 1은 CMD이다.

    length = int(response[pre_length:pre_length+2])
    #print("data length = ", length)
    data_1 = pre_length + 2
    data_2 = data_1 + length

    #print("data string = ", response[data_1:data_2])
    data_str = response[data_1:data_2]

    return_tuple = parse_by_lengths( data_str, "151515151515" )

    Iref = 32767

    data = SensorData(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    data.length      = float(return_tuple[1])*0.01
    data.angle_x     = float(Iref - int(return_tuple[3]))*0.01
    data.angle_y     = float(Iref - int(return_tuple[5]))*0.01
    data.temperature = float(Iref-int(return_tuple[7]))*0.01
    data.voltage     = float(return_tuple[9])*0.01
    data.current     = float(return_tuple[11])*0.1

    return data



