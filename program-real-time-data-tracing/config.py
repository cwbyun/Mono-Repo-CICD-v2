"""
센서 설정 관리 모듈
"""

import json
from dataclasses import dataclass

@dataclass
class SensorConfig:
    model: str
    id: str
    send_stx: str
    send_etx: str
    receive_stx: str
    receive_etx: str

def load_sensor_config_json(path="sensor_info.json") -> SensorConfig:
    # utf-8-sig: 파일에 BOM이 있어도 안전
    with open(path, "r", encoding="utf-8-sig") as f:
        cfg = json.load(f)
    return SensorConfig(
        model=cfg["MODEL"].strip(),
        id=cfg["ID"].strip(),
        send_stx=cfg["SEND_STX"].strip(),
        send_etx=cfg["SEND_ETX"].strip(),
        receive_stx=cfg["RECEIVE_STX"].strip(),
        receive_etx=cfg["RECEIVE_ETX"].strip(),
    )

