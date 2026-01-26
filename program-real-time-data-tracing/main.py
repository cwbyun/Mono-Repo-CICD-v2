"""
센서 데이터 실시간 그래프 GUI
PyQt6와 matplotlib 조합
"""
import sys
import threading
import time
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure



# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False



# 시스템에 설치된 한글 폰트 찾기 및 설정
font_list = fm.findSystemFonts(fontpaths=None, fontext='ttf')
korean_fonts = []
for font in font_list:
    try:
        font_prop = fm.FontProperties(fname=font)
        font_name = font_prop.get_name()
        if any(korean in font_name.lower() for korean in ['nanum', 'malgun', 'gulim', 'dotum', 'batang']):
            korean_fonts.append(font_name)
    except:
        continue

if korean_fonts:
    plt.rcParams['font.family'] = korean_fonts[0]
else:
    # 한글 폰트가 없으면 영문으로 레이블 변경
    plt.rcParams['font.family'] = 'DejaVu Sans'
from PyQt5.QtCore import QTimer, pyqtSignal, QObject, QThread, Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, QGroupBox,
    QGridLayout, QMessageBox, QCheckBox
)

from serial_comm import SerialCommunicator
from sensor_data import SensorData


class SensorDataCollector(QObject):
    """센서 데이터 수집을 담당하는 워커 클래스"""
    data_received = pyqtSignal(SensorData)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, port: str, baudrate: int, interval: float):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.interval = interval
        self.running = False
        self.serial_comm = None
    
    def start_collection(self):
        """데이터 수집 시작"""
        self.running = True
        try:
            self.serial_comm = SerialCommunicator(self.port, self.baudrate)
            
            while self.running:
                try:
                    data = self.serial_comm.collect_sensor_data_once()
                    self.data_received.emit(data)
                except Exception as e:
                    self.error_occurred.emit(f"데이터 수집 오류: {str(e)}")
                
                time.sleep(self.interval)
                
        except Exception as e:
            self.error_occurred.emit(f"시리얼 연결 오류: {str(e)}")
    
    def stop_collection(self):
        """데이터 수집 중지"""
        self.running = False


class RealTimePlotWidget(QWidget):
    """matplotlib을 사용한 실시간 플롯 위젯"""
    
    def __init__(self, title: str, unit: str, max_points: int = 100, y_min: float = None, y_max: float = None):
        super().__init__()
        self.title = title
        self.unit = unit
        self.max_points = max_points
        self.y_min = y_min
        self.y_max = y_max
        self.start_time = None  # 시작 시간 기록
        
        # 데이터 저장용 deque
        self.times = deque(maxlen=max_points)
        self.values = deque(maxlen=max_points)
        
        # matplotlib 설정 (그래프 크기 증가)
        self.figure = Figure(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        # 여백 조정으로 X축 tick이 잘리지 않도록
        self.figure.subplots_adjust(bottom=0.15, top=0.9, left=0.1, right=0.95)
        
        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.setContentsMargins(2, 2, 2, 2)  # 마진 최소화
        self.setLayout(layout)
        
        # 플롯 초기화 (점과 선 함께)
        self.line, = self.ax.plot([], [], 'bo-', linewidth=2, markersize=4)
        self.ax.set_title(title)
        self.ax.set_ylabel(f'{title} ({unit})')
        self.ax.grid(True, alpha=0.3)
        
        # Y축 범위 고정 (지정된 경우)
        if y_min is not None and y_max is not None:
            self.ax.set_ylim(y_min, y_max)
        
        # 자동 스케일링을 위한 설정
        self.ax.relim()
        self.ax.autoscale_view()
    
    def update_data(self, value: float):
        """새로운 데이터 포인트 추가"""
        current_time = datetime.now()
        
        # 첫 번째 데이터 포인트일 때 시작 시간 설정
        if self.start_time is None:
            self.start_time = current_time
            
        self.times.append(current_time)
        self.values.append(value)
        
        # 플롯 업데이트
        if len(self.times) >= 1:
            self.line.set_data(list(self.times), list(self.values))
            
            # X축 시간 포맷 설정 (HH:MM:SS) - 자동 눈금 조정
            import matplotlib.dates as mdates
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            
            # X축 범위를 시작 시간부터 현재까지로 설정 (계속 확장)
            end_time = current_time
            start_display = self.start_time
            
            self.ax.set_xlim(start_display, end_time)
            
            # Y축 범위 처리
            if self.y_min is not None and self.y_max is not None:
                # 고정 범위 유지
                self.ax.set_ylim(self.y_min, self.y_max)
            else:
                # 자동 스케일링
                if len(self.values) > 0:
                    min_val = min(self.values)
                    max_val = max(self.values)
                    margin = (max_val - min_val) * 0.1 if max_val != min_val else 1
                    self.ax.set_ylim(min_val - margin, max_val + margin)
            
            # X축 라벨 회전
            plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45)
            self.canvas.draw()
    
    def reset_start_time(self):
        """시작 시간 리셋"""
        self.start_time = None


class SensorGraphGUI(QMainWindow):
    """센서 데이터 실시간 그래프 메인 GUI"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("실시간 센서 데이터 모니터")
        self.setGeometry(100, 100, 1400, 900)
        
        # 데이터 수집 관련 변수
        self.collector_thread = None
        self.data_collector = None
        self.is_collecting = False
        
        # 그래프 위젯들 초기화
        self.plot_widgets: Dict[str, RealTimePlotWidget] = {}
        
        # UI 초기화
        self.init_ui()
    
    def init_ui(self):
        """UI 초기화"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 헤더 제거 - 공간 절약
        
        # 설정 패널
        self.create_config_panel(main_layout)
        
        # 그래프 영역
        self.create_graph_area(main_layout)
        
        # 제어 버튼
        self.create_control_buttons(main_layout)
    
    def create_header(self, parent_layout):
        """상단 헤더 (회사명 + 제목) 생성 - 고정 높이"""
        header_widget = QWidget()
        header_widget.setFixedHeight(20)  # 고정 높이로 설정
        header_layout = QVBoxLayout(header_widget)
        header_layout.setSpacing(1)
        header_layout.setContentsMargins(5, 5, 5, 5)
        
        # 헤더는 간소화 - 제목이나 회사명 제거
        header_layout.addStretch()
        
        # 구분선
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #E0E0E0;")
        header_layout.addWidget(line)
        
        parent_layout.addWidget(header_widget)
    
    def get_available_ports(self):
        """사용 가능한 시리얼 포트 목록 반환"""
        import serial.tools.list_ports
        ports = [port.device for port in serial.tools.list_ports.comports()]
        return ports if ports else ["/dev/ttyUSB0", "COM1", "COM2"]
    
    def load_sensor_config_values(self):
        """JSON 파일에서 센서 설정값 로드"""
        try:
            from config import load_sensor_config_json
            config = load_sensor_config_json()
            return {
                'model': config.model,
                'id': config.id,
                'send_stx': config.send_stx,
                'send_etx': config.send_etx,
                'receive_stx': config.receive_stx,
                'receive_etx': config.receive_etx
            }
        except Exception as e:
            return {
                'model': 'JW17',
                'id': '000000', 
                'send_stx': '@#T',
                'send_etx': 'Q',
                'receive_stx': '@#J',
                'receive_etx': 'Q'
            }
    
    def create_config_panel(self, parent_layout):
        """설정 패널 생성 - 두 줄 구조 (라벨/입력창)"""
        # 상단 레이아웃 (설정 + 설정저장 + 회사명 + 종료버튼)
        top_layout = QHBoxLayout()
        
        # 설정 그룹 (두 줄 구조) - 제목 없이
        config_group = QGroupBox()
        config_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 5px;
                padding-top: 5px;
            }
        """)
        config_layout = QGridLayout()
        
        # JSON 설정값 로드
        sensor_config = self.load_sensor_config_values()
        
        # 라벨 스타일 설정
        label_style = """
            QLabel {
                font-size: 12px;
                font-weight: bold;
                padding: 2px;
            }
        """
        
        # 첫 번째 줄: 라벨들
        port_label = QLabel("포트")
        port_label.setStyleSheet(label_style)
        config_layout.addWidget(port_label, 0, 0)
        
        baudrate_label = QLabel("보드레이트")
        baudrate_label.setStyleSheet(label_style)
        config_layout.addWidget(baudrate_label, 0, 1)
        
        interval_label = QLabel("간격(초)")
        interval_label.setStyleSheet(label_style)
        config_layout.addWidget(interval_label, 0, 2)
        
        model_label = QLabel("MODEL")
        model_label.setStyleSheet(label_style)
        config_layout.addWidget(model_label, 0, 3)
        
        id_label = QLabel("ID")
        id_label.setStyleSheet(label_style)
        config_layout.addWidget(id_label, 0, 4)
        
        rx_stx_label = QLabel("RX_STX")
        rx_stx_label.setStyleSheet(label_style)
        config_layout.addWidget(rx_stx_label, 0, 5)
        
        # 입력 필드 스타일 설정
        input_style = """
            QComboBox, QLineEdit, QSpinBox {
                font-size: 11px;
                padding: 4px;
                border: 1px solid #ccc;
                border-radius: 3px;
                min-height: 20px;
            }
            QComboBox:focus, QLineEdit:focus, QSpinBox:focus {
                border-color: #007acc;
            }
        """
        
        # 두 번째 줄: 입력 필드들
        self.port_combo = QComboBox()
        available_ports = self.get_available_ports()
        self.port_combo.addItems(available_ports)
        self.port_combo.setFixedWidth(100)
        self.port_combo.setStyleSheet(input_style)
        config_layout.addWidget(self.port_combo, 1, 0)
        
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baudrate_combo.setCurrentText("19200")
        self.baudrate_combo.setFixedWidth(80)
        self.baudrate_combo.setStyleSheet(input_style)
        config_layout.addWidget(self.baudrate_combo, 1, 1)
        
        self.interval_input = QSpinBox()
        self.interval_input.setRange(1, 60)
        self.interval_input.setValue(2)
        self.interval_input.setFixedWidth(70)
        self.interval_input.setStyleSheet(input_style)
        config_layout.addWidget(self.interval_input, 1, 2)
        
        self.model_input = QLineEdit(sensor_config['model'])
        self.model_input.setFixedWidth(70)
        self.model_input.setStyleSheet(input_style)
        config_layout.addWidget(self.model_input, 1, 3)
        
        self.id_input = QLineEdit(sensor_config['id'])
        self.id_input.setFixedWidth(80)
        self.id_input.setStyleSheet(input_style)
        config_layout.addWidget(self.id_input, 1, 4)
        
        self.receive_stx_input = QLineEdit(sensor_config['receive_stx'])
        self.receive_stx_input.setFixedWidth(60)
        self.receive_stx_input.setStyleSheet(input_style)
        config_layout.addWidget(self.receive_stx_input, 1, 5)
        
        # 숨겨진 나머지 설정값들 (업데이트용)
        self.send_stx_input = QLineEdit(sensor_config['send_stx'])
        self.send_etx_input = QLineEdit(sensor_config['send_etx'])
        self.receive_etx_input = QLineEdit(sensor_config['receive_etx'])
        self.max_points_input = QSpinBox()
        self.max_points_input.setRange(50, 1000)
        self.max_points_input.setValue(100)
        
        config_group.setLayout(config_layout)
        config_group.setMaximumHeight(100)
        config_group.setContentsMargins(2, 2, 2, 2)
        
        # 설정 저장 버튼
        save_settings_btn = QPushButton("설정 저장")
        save_settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                min-width: 80px;
                max-height: 40px;
            }
            QPushButton:hover { background-color: #e68900; }
        """)
        save_settings_btn.clicked.connect(self.update_sensor_config)
        
        # 회사명 (오른쪽 끝에 위치)
        company_label = QLabel("DPS-GLOBAL Co. Ltd.")
        company_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        company_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #666666;
                margin: 5px;
                padding: 5px;
            }
        """)
        
        # 상단 레이아웃 구성 (종료 버튼은 하단으로 이동)
        top_layout.addWidget(config_group)
        top_layout.addWidget(save_settings_btn)
        #top_layout.addWidget(company_label)
        top_layout.addStretch()
        
        parent_layout.addLayout(top_layout)
    
    def update_sensor_config(self):
        """센서 설정을 JSON 파일에 업데이트"""
        try:
            import json
            config_data = {
                "MODEL": self.model_input.text().strip(),
                "ID": self.id_input.text().strip(),
                "SEND_STX": self.send_stx_input.text().strip(),
                "SEND_ETX": self.send_etx_input.text().strip(),
                "RECEIVE_STX": self.receive_stx_input.text().strip(),
                "RECEIVE_ETX": self.receive_etx_input.text().strip()
            }
            
            with open("sensor_info.json", "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            
            QMessageBox.information(self, "성공", "센서 설정이 업데이트되었습니다.")
            
        except Exception as e:
            QMessageBox.critical(self, "오류", f"설정 업데이트 실패: {str(e)}")
    
    def create_graph_area(self, parent_layout):
        """그래프 영역 생성"""
        graph_group = QGroupBox("센서 데이터 그래프")
        graph_layout = QGridLayout()
        
        # 6개 센서 데이터 그래프 생성 (윗줄: Wire, Angle(x), Angle(y) / 아랫줄: Temperature, Voltage, Current)
        # 한글 폰트 사용 가능 여부에 따라 레이블 선택
        use_korean = korean_fonts and plt.rcParams['font.family'] in korean_fonts
        
        if use_korean:
            sensors = [
                ("length", "와이어 길이", "mm", 0, 0, None, None),
                ("angle_x", "각도 (X)", "°", 0, 1, None, None),
                ("angle_y", "각도 (Y)", "°", 0, 2, None, None),
                ("temperature", "온도", "°C", 1, 0, -10, 45),
                ("voltage", "전압", "V", 1, 1, 0, 30),
                ("current", "전류", "mA", 1, 2, 0, 100)
            ]
        else:
            sensors = [
                ("length", "Wire Length", "mm", 0, 0, None, None),
                ("angle_x", "Angle (X)", "°", 0, 1, None, None),
                ("angle_y", "Angle (Y)", "°", 0, 2, None, None),
                ("temperature", "Temperature", "°C", 1, 0, -10, 45),
                ("voltage", "Voltage", "V", 1, 1, 0, 30),
                ("current", "Current", "mA", 1, 2, 0, 100)
            ]
        
        max_points = self.max_points_input.value()
        
        for sensor_key, title, unit, row, col, y_min, y_max in sensors:
            plot_widget = RealTimePlotWidget(title, unit, max_points, y_min, y_max)
            self.plot_widgets[sensor_key] = plot_widget
            graph_layout.addWidget(plot_widget, row, col)
        
        graph_group.setLayout(graph_layout)
        parent_layout.addWidget(graph_group)
    
    def create_control_buttons(self, parent_layout):
        """제어 버튼 생성 - 컴팩트"""
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("시작")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        self.start_button.clicked.connect(self.start_monitoring)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("중지")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover { background-color: #da190b; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        self.clear_button = QPushButton("초기화")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover { background-color: #0b7dda; }
        """)
        self.clear_button.clicked.connect(self.clear_graphs)
        button_layout.addWidget(self.clear_button)
        
        # 데이터 저장 버튼
        save_data_button = QPushButton("데이터 저장")
        save_data_button.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover { background-color: #7B1FA2; }
        """)
        save_data_button.clicked.connect(self.save_data_to_file)
        button_layout.addWidget(save_data_button)
        
        # 그래프 저장 버튼
        save_graph_button = QPushButton("그래프 저장")
        save_graph_button.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover { background-color: #455A64; }
        """)
        save_graph_button.clicked.connect(self.save_graphs_to_file)
        button_layout.addWidget(save_graph_button)
        
        button_layout.addStretch()  # 공간 확보
        
        # 종료 버튼 (오른쪽 끝)
        exit_button = QPushButton("종료")
        exit_button.setStyleSheet("""
            QPushButton {
                background-color: #FF4444;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #FF6666;
            }
            QPushButton:pressed {
                background-color: #CC0000;
            }
        """)
        exit_button.clicked.connect(self.close)
        button_layout.addWidget(exit_button)
        
        parent_layout.addLayout(button_layout)
        
        # 상태바
        self.statusBar().showMessage("준비됨")
    
    def start_monitoring(self):
        """모니터링 시작"""
        if self.is_collecting:
            return
        
        try:
            port = self.port_combo.currentText().strip()
            baudrate = int(self.baudrate_combo.currentText())
            interval = self.interval_input.value()
            
            if not port:
                QMessageBox.warning(self, "오류", "시리얼 포트를 선택하세요.")
                return
            
            # 데이터 수집기 생성
            self.data_collector = SensorDataCollector(port, baudrate, interval)
            self.data_collector.data_received.connect(self.on_data_received)
            self.data_collector.error_occurred.connect(self.on_error)
            
            # 별도 스레드에서 데이터 수집 시작
            self.collector_thread = QThread()
            self.data_collector.moveToThread(self.collector_thread)
            self.collector_thread.started.connect(self.data_collector.start_collection)
            self.collector_thread.start()
            
            self.is_collecting = True
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.statusBar().showMessage(f"모니터링 중... ({port}, {baudrate} bps)")
            
        except Exception as e:
            QMessageBox.critical(self, "오류", f"모니터링 시작 실패: {str(e)}")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        if not self.is_collecting:
            return
        
        if self.data_collector:
            self.data_collector.stop_collection()
        
        if self.collector_thread and self.collector_thread.isRunning():
            self.collector_thread.quit()
            self.collector_thread.wait()
        
        self.is_collecting = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.statusBar().showMessage("중지됨")
    
    def on_data_received(self, data: SensorData):
        """새로운 센서 데이터 수신 처리"""
        # 각 그래프에 데이터 추가
        self.plot_widgets["length"].update_data(float(data.length))
        self.plot_widgets["angle_x"].update_data(float(data.angle_x))
        self.plot_widgets["angle_y"].update_data(float(data.angle_y))
        self.plot_widgets["temperature"].update_data(float(data.temperature))
        self.plot_widgets["voltage"].update_data(float(data.voltage))
        self.plot_widgets["current"].update_data(float(data.current))
        
        # 상태바 업데이트
        # 한글 폰트 지원 여부에 따라 상태바 메시지 설정
        use_korean = korean_fonts and plt.rcParams['font.family'] in korean_fonts
        if use_korean:
            status_msg = (
                f"최근 데이터 - 길이: {data.length}mm, 온도: {data.temperature}°C, "
                f"전압: {data.voltage}V - {datetime.now().strftime('%H:%M:%S')}"
            )
        else:
            status_msg = (
                f"Latest - Length: {data.length}mm, Temp: {data.temperature}°C, "
                f"Voltage: {data.voltage}V - {datetime.now().strftime('%H:%M:%S')}"
            )
        self.statusBar().showMessage(status_msg)
    
    def on_error(self, error_msg: str):
        """오류 발생 처리"""
        QMessageBox.warning(self, "오류", error_msg)
        self.stop_monitoring()
    
    def clear_graphs(self):
        """모든 그래프 초기화"""
        for plot_widget in self.plot_widgets.values():
            plot_widget.times.clear()
            plot_widget.values.clear()
            plot_widget.reset_start_time()  # 시작 시간 리셋
            plot_widget.line.set_data([], [])
            plot_widget.ax.relim()
            plot_widget.ax.autoscale_view()
            plot_widget.canvas.draw()
        
        self.statusBar().showMessage("그래프 초기화됨")
    
    def save_data_to_file(self):
        """현재 그래프 데이터를 CSV 파일로 저장"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            import csv
            from datetime import datetime
            
            # 파일 경로 선택
            file_path, _ = QFileDialog.getSaveFileName(
                self, "데이터 저장", 
                f"sensor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV files (*.csv)"
            )
            
            if not file_path:
                return
            
            # CSV 파일 작성
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # 헤더 작성
                headers = ['timestamp']
                for sensor_name in ['length', 'angle_x', 'angle_y', 'temperature', 'voltage', 'current']:
                    headers.append(sensor_name)
                writer.writerow(headers)
                
                # 데이터 개수 확인 (가장 긴 데이터 기준)
                max_length = max(len(widget.times) for widget in self.plot_widgets.values()) if self.plot_widgets else 0
                
                # 데이터 행 작성
                for i in range(max_length):
                    row = []
                    
                    # 시간 추가 (첫 번째 위젯의 시간 사용)
                    first_widget = list(self.plot_widgets.values())[0] if self.plot_widgets else None
                    if first_widget and i < len(first_widget.times):
                        row.append(first_widget.times[i].strftime('%Y-%m-%d %H:%M:%S'))
                    else:
                        row.append('')
                    
                    # 각 센서 데이터 추가
                    for sensor_name in ['length', 'angle_x', 'angle_y', 'temperature', 'voltage', 'current']:
                        if sensor_name in self.plot_widgets and i < len(self.plot_widgets[sensor_name].values):
                            row.append(self.plot_widgets[sensor_name].values[i])
                        else:
                            row.append('')
                    
                    writer.writerow(row)
            
            QMessageBox.information(self, "성공", f"데이터가 저장되었습니다:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "오류", f"데이터 저장 실패: {str(e)}")
    
    def save_graphs_to_file(self):
        """현재 그래프들을 이미지 파일로 저장"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            import matplotlib.pyplot as plt
            from datetime import datetime
            
            # 파일 경로 선택
            file_path, _ = QFileDialog.getSaveFileName(
                self, "그래프 저장", 
                f"sensor_graphs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                "PNG files (*.png);;PDF files (*.pdf);;SVG files (*.svg)"
            )
            
            if not file_path:
                return
            
            # 전체 그래프를 하나의 figure에 결합
            fig, axes = plt.subplots(2, 3, figsize=(18, 12))
            
            # 한글 폰트 사용 가능 여부에 따라 제목과 레이블 선택
            use_korean = korean_fonts and plt.rcParams['font.family'] in korean_fonts
            
            if use_korean:
                fig.suptitle('센서 데이터 그래프', fontsize=16, fontweight='bold')
                sensors = [
                    ('length', '와이어 길이', 'mm', 0, 0),
                    ('angle_x', '각도 (X)', '°', 0, 1),
                    ('angle_y', '각도 (Y)', '°', 0, 2),
                    ('temperature', '온도', '°C', 1, 0),
                    ('voltage', '전압', 'V', 1, 1),
                    ('current', '전류', 'mA', 1, 2)
                ]
            else:
                fig.suptitle('Sensor Data Graphs', fontsize=16, fontweight='bold')
                sensors = [
                    ('length', 'Wire Length', 'mm', 0, 0),
                    ('angle_x', 'Angle (X)', '°', 0, 1),
                    ('angle_y', 'Angle (Y)', '°', 0, 2),
                    ('temperature', 'Temperature', '°C', 1, 0),
                    ('voltage', 'Voltage', 'V', 1, 1),
                    ('current', 'Current', 'mA', 1, 2)
                ]
            
            for sensor_key, title, unit, row, col in sensors:
                ax = axes[row, col]
                if sensor_key in self.plot_widgets:
                    widget = self.plot_widgets[sensor_key]
                    if len(widget.times) > 0 and len(widget.values) > 0:
                        ax.plot(widget.times, widget.values, 'bo-', linewidth=2, markersize=4)
                        ax.set_title(title)
                        ax.set_ylabel(f'{title} ({unit})')
                        ax.grid(True, alpha=0.3)
                        
                        # X축 시간 포맷
                        import matplotlib.dates as mdates
                        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
                        
                        # Y축 범위 설정
                        if widget.y_min is not None and widget.y_max is not None:
                            ax.set_ylim(widget.y_min, widget.y_max)
                        
                        # X축 라벨 회전
                        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
                    else:
                        ax.text(0.5, 0.5, 'No Data', ha='center', va='center', transform=ax.transAxes)
                        ax.set_title(title)
                        ax.set_ylabel(f'{title} ({unit})')
            
            plt.tight_layout()
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            QMessageBox.information(self, "성공", f"그래프가 저장되었습니다:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "오류", f"그래프 저장 실패: {str(e)}")
    
    def closeEvent(self, event):
        """창 닫기 이벤트 처리"""
        self.stop_monitoring()
        event.accept()


def main():
    """메인 함수"""
    app = QApplication(sys.argv)
    window = SensorGraphGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
