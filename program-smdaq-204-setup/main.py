import sys
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QFormLayout, QLineEdit, QPushButton, QTabWidget, QPlainTextEdit, 
    QSplitter, QLabel, QGroupBox
)
from PyQt6.QtCore import Qt, QDateTime, QTimer, pyqtSignal, QSettings, QCoreApplication, QThread

from communication import send_command
from general import GeneralTab
from config import ConfigTab
from option import OptionTab
from sensor import SensorTab
from peripheral import PeripheralTab
from firmware import FirmwareTab
from my_signal import SignalTab
from data import DataTab
from user_command import UserCommandTab
from utils import *
import protocol as ptcl
from server_pure import SMDAQServerPure
from company import CompanyTab

import threading



class MainWindow(QMainWindow):
    # 스레드 안전한 로깅을 위한 시그널 정의
    log_signal = pyqtSignal(str)
    client_attempt_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # --- 1. 윈도우 기본 설정 ---
        self.setWindowTitle("SMDAQ-204 Setup Program")
        # self.setGeometry(100, 100, 1200, 1300)  # 최대화 모드에서는 주석 처리
        #self.setFixedSize(900, 800)

        # --- 시그널-슬롯 연결 ---
        self.log_signal.connect(self.add_log)
        self.client_attempt_signal.connect(self.on_client_attempt)
        
        # --- 설정 초기화 ---
        self.settings = QSettings("SMDAQ", "SMDAQ-204-Setup")

        # --- 2. 중앙에 들어갈 전체 위젯 및 레이아웃 설정 ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- 3. 상단 연결 정보 그룹 ---

        connection_layout = QHBoxLayout()

        # 저장된 설정 불러오기 (기본값: 기존 값들)
        saved_ip = self.settings.value("client_ip", "192.168.0.62")
        saved_port = self.settings.value("client_port", "5000")
        saved_server_port = self.settings.value("server_port", "9090")
        saved_client_ip = self.settings.value("allowed_client_ip", "192.168.0.1")
        saved_auto_stop_min = self.settings.value("server_auto_stop_min", "10")
        
        self.ip_input = QLineEdit(saved_ip)
        self.port_input = QLineEdit(saved_port)
        
        # 값 변경 시 즉시 저장
        self.ip_input.textChanged.connect(lambda: self.settings.setValue("client_ip", self.ip_input.text()))
        self.port_input.textChanged.connect(lambda: self.settings.setValue("client_port", self.port_input.text()))

        connection_layout.addWidget( QLabel("Client Mode (명령 전송 대상):") )
        connection_layout.addWidget( QLabel("IP") )
        connection_layout.addWidget( self.ip_input )

        connection_layout.addWidget( QLabel("PORT"))
        connection_layout.addWidget( self.port_input )
        connection_layout.addStretch(1)
        main_layout.addLayout(connection_layout)

        # --- 서버 제어 그룹 ---
        server_layout = QHBoxLayout()
        
        # 현재 PC의 IP 주소 가져오기
        local_ip = self.get_local_ip()
        
        self.server_port_input = QLineEdit(saved_server_port)
        self.client_ip_input = QLineEdit(saved_client_ip)  # 접속 허용할 클라이언트 IP 입력
        self.server_auto_stop_input = QLineEdit(saved_auto_stop_min)
        self.server_auto_stop_input.setFixedWidth(60)
        self.server_auto_stop_input.setPlaceholderText("min")
        
        # 서버 설정도 값 변경 시 즉시 저장
        self.server_port_input.textChanged.connect(lambda: self.settings.setValue("server_port", self.server_port_input.text()))
        self.client_ip_input.textChanged.connect(lambda: self.settings.setValue("allowed_client_ip", self.client_ip_input.text()))
        self.server_auto_stop_input.textChanged.connect(lambda: self.settings.setValue("server_auto_stop_min", self.server_auto_stop_input.text()))
        self.server_ip_label = QLabel(f"로컬 PC IP: {local_ip}")
        self.server_status_label = QLabel("서버: 중지됨")
        self.server_start_button = QPushButton("서버 시작")
        self.server_stop_button = QPushButton("서버 중지")
        
        # 서버 관련 변수 초기화
        self.server = None
        self.local_ip = local_ip
        self.pending_response = None
        
        # 버튼 이벤트 연결
        self.server_start_button.clicked.connect(self.start_server)
        self.server_stop_button.clicked.connect(self.stop_server)
        self.client_ip_input.textChanged.connect(self.check_server_button_state)
        
        # 초기 상태 설정
        self.server_stop_button.setEnabled(False)
        # 클라이언트 IP 입력 상태에 따라 서버 시작 버튼 상태 설정
        self.check_server_button_state()

        self.server_idle_timer = QTimer(self)
        self.server_idle_timer.setInterval(10000)
        self.server_idle_timer.timeout.connect(self.check_server_idle)
        self.server_idle_timer.start()
        
        server_layout.addWidget(QLabel("Server Mode"))
        server_layout.addWidget(QLabel("Port"))
        server_layout.addWidget(self.server_port_input)
        server_layout.addWidget(QLabel("Auto Stop (min)"))
        server_layout.addWidget(self.server_auto_stop_input)
        server_layout.addWidget(QLabel("Client IP"))
        server_layout.addWidget(self.client_ip_input)
        server_layout.addWidget(self.server_status_label)
        self.idle_status_message = "상태: 준비됨"
        self.status_hint_label = QLabel(self.idle_status_message)
        self.status_hint_label.setStyleSheet(
            "padding: 0 6px; background: #eef3ff; border: 1px solid #ccd8f2;"
        )
        self.status_hint_label.setFixedHeight(20)
        server_layout.addWidget(self.server_start_button)
        server_layout.addWidget(self.server_stop_button)
        server_layout.addWidget(self.status_hint_label)
        server_layout.addStretch(1)
        main_layout.addLayout(server_layout)



        # --- 4. 중앙 탭 위젯과 하단 로그창을 위한 스플리터 ---
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 4-1. 탭 위젯 생성
        self.tabs = QTabWidget()

        # 각 탭을 self의 속성으로 저장하여 나중에 접근할 수 있도록 함
        self.general_tab    = GeneralTab(self)
        self.config_tab     = ConfigTab(self)
        self.option_tab     = OptionTab(self)
        self.sensor_tab     = SensorTab(self)
        self.peripheral_tab = PeripheralTab(self)
        self.signal_tab     = SignalTab(self)
        self.company_tab    = CompanyTab(self)
        self.firmware_tab   = FirmwareTab(self)
        self.data_tab       = DataTab(self)


        self.user_command_tab = UserCommandTab(self)

        self.tabs.addTab(self.general_tab, "General")


        self.tabs.addTab(self.config_tab,  "Config")

        self.tabs.addTab(self.option_tab,  "Option")


        self.tabs.addTab(self.sensor_tab, "Sensor")

        self.tabs.addTab(self.peripheral_tab, "Peripheral")

        self.tabs.addTab(self.signal_tab, "Signal")

        self.tabs.addTab(self.company_tab, "Company")

        self.tabs.addTab(self.firmware_tab, "Firmware ")
        self.tabs.addTab(self.data_tab, "Data")
        self.tabs.addTab(self.user_command_tab, "UserCommand")

        splitter.addWidget(self.tabs)

        # 4-2. 로그 출력창 생성
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        splitter.addWidget(self.log_output)
        
        splitter.setSizes([850, 350])

        main_layout.addWidget(splitter)

        # --- 5. 하단 버튼들 ---
        bottom_layout = QHBoxLayout()

        # 왼쪽 끝에 Reset 버튼
        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self.send_reset_command)
        bottom_layout.addWidget(reset_button)

        # 로그 클리어 버튼
        clear_log_button = QPushButton("Clear Log")
        clear_log_button.clicked.connect(self.clear_log)
        bottom_layout.addWidget(clear_log_button)

        # 가운데 공간
        bottom_layout.addStretch(1)

        # 오른쪽 끝에 종료 버튼
        exit_button = QPushButton("종료")
        exit_button.clicked.connect(self.close)
        bottom_layout.addWidget(exit_button)
        
        main_layout.addLayout(bottom_layout)

        self.log_signal.emit(self.idle_status_message)
        self.statusBar().showMessage(self.idle_status_message)

    def get_local_ip(self) -> str:
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"

    def check_server_button_state(self):
        """클라이언트 IP 입력 상태에 따라 서버 시작 버튼 활성화 상태 변경"""
        client_ip = self.client_ip_input.text().strip()
        # 서버가 실행 중이 아니고, 클라이언트 IP가 입력된 경우에만 서버 시작 버튼 활성화
        if not (self.server and self.server.is_running):
            self.server_start_button.setEnabled(bool(client_ip))
        
    def validate_ip_address(self, ip: str) -> bool:
        """IP 주소 형식 유효성 검사"""
        import socket
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False

    def set_allowed_client_ip(self, ip: str):
        ip = ip.strip()
        if not ip:
            self.log_signal.emit("오류: 허용할 클라이언트 IP 주소를 선택하세요.")
            return

        if not self.validate_ip_address(ip):
            self.log_signal.emit("오류: 올바른 IP 주소 형식이 아닙니다.")
            return

        self.client_ip_input.setText(ip)
        if self.server and self.server.is_running:
            self.server.set_allowed_client_ip(ip)
            self.log_signal.emit(f"허용 클라이언트 IP 변경: {ip}")

    def add_log(self, message):
        now = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        log_message = f"[{now}] {message}"
        self.log_output.appendPlainText(log_message)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

    def add_log_lines(self, lines):
        if not lines:
            return
        now = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        log_message = "\n".join(f"[{now}] {line}" for line in lines)
        self.log_output.appendPlainText(log_message)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

    def set_app_status(self, message, status_bar_message=None):
        self.status_hint_label.setText(message)
        if status_bar_message is None:
            self.statusBar().showMessage(message)
        else:
            self.statusBar().showMessage(status_bar_message)

    def on_client_attempt(self, ip: str):
        if hasattr(self, "general_tab"):
            self.general_tab.add_incoming_client_ip(ip)

    def get_auto_stop_minutes(self) -> int:
        raw = self.server_auto_stop_input.text().strip()
        if not raw:
            return 0
        try:
            return int(raw)
        except ValueError:
            return 0

    def check_server_idle(self):
        if not (self.server and self.server.is_running):
            return
        auto_stop_min = self.get_auto_stop_minutes()
        if auto_stop_min <= 0:
            return
        last_activity = self.server.get_last_activity()
        if time.time() - last_activity >= auto_stop_min * 60:
            self.log_signal.emit(f"서버 자동 중지: {auto_stop_min}분 이상 비활성")
            self.stop_server()

    def clear_log(self):
        """로그 창을 클리어합니다."""
        self.log_output.clear()
        self.log_signal.emit("로그가 클리어되었습니다.")
    
    def save_settings(self):
        """현재 설정을 저장합니다."""
        self.settings.setValue("client_ip", self.ip_input.text())
        self.settings.setValue("client_port", self.port_input.text())
        self.settings.setValue("server_port", self.server_port_input.text())
        self.settings.setValue("allowed_client_ip", self.client_ip_input.text())
        self.settings.setValue("server_auto_stop_min", self.server_auto_stop_input.text())

    def get_ip_port(self) -> tuple [str, int]:
        ip = self.ip_input.text()
        port = 0
        try:
            port = int(self.port_input.text())
        except ValueError:
            self.log_signal.emit("오류: Port는 숫자만 입력하세요.")
        return ip, port

    def send_reset_command(self):
        #cmd, rep = self.common_command( "W", "H" )
        
        cmd = ptcl.STX + "WH"
        cmd = add_tail(cmd)
        response = self.send_command_unified(cmd)

    def common_command( self, DIR, CMD, data_str=None ):
        if data_str :
            command = ptcl.STX + DIR + CMD + data_str
        else:
            command = ptcl.STX + DIR + CMD

        command = add_tail(command)

        #self.add_log(f"전송 >> {command}")
        response = self.send_command_unified(command)
        #print("command=",command)
        #print("respond=",response)

        return command, response




    def start_server(self):
        # 클라이언트 IP 유효성 검사
        client_ip = self.client_ip_input.text().strip()
        if not client_ip:
            self.log_signal.emit("오류: 허용할 클라이언트 IP 주소를 입력하세요.")
            return
            
        if not self.validate_ip_address(client_ip):
            self.log_signal.emit("오류: 올바른 IP 주소 형식이 아닙니다.")
            return

        try:
            port = int(self.server_port_input.text())
        except ValueError:
            self.log_signal.emit("오류: 서버 포트는 숫자만 입력하세요.")
            return

        if self.server and self.server.is_running:
            self.log_signal.emit("서버가 이미 실행 중입니다.")
            return

        try:
            self.log_signal.emit("서버 시작 중...")
            self.server = SMDAQServerPure(
                host=self.local_ip,  # 로컬 IP 사용
                port=port, 
                log_callback=self.log_signal.emit,
                allowed_client_ip=client_ip,  # 허용된 클라이언트 IP 전달
                client_attempt_callback=self.client_attempt_signal.emit
            )
            
            QTimer.singleShot(100, lambda: self._delayed_server_start(port, client_ip))
            
        except Exception as e:
            self.log_signal.emit(f"서버 시작 중 오류 발생: {e}")
            self.server = None
            
    def _delayed_server_start(self, port, client_ip):
        try:
            if self.server.start_server():
                self.server_status_label.setText(f"서버: 실행 중 (포트 {port})")
                self.server_start_button.setEnabled(False)
                self.server_stop_button.setEnabled(True)
                self.server_port_input.setEnabled(False)
                self.client_ip_input.setEnabled(False)  # 서버 실행 중에는 클라이언트 IP 변경 불가
                self.log_signal.emit(f"서버 시작됨 - {self.local_ip}:{port} (클라이언트: {client_ip})")
            else:
                self.log_signal.emit("서버 시작에 실패했습니다.")
                self.check_server_button_state()  # 버튼 상태 재확인
                
        except Exception as e:
            self.log_signal.emit(f"서버 시작 중 오류 발생: {e}")
            self.server = None
            self.check_server_button_state()  # 버튼 상태 재확인

    def stop_server(self):
        if self.server and self.server.is_running:
            self.server.stop_server()
            self.server_status_label.setText("서버: 중지됨")
            self.server_stop_button.setEnabled(False)
            self.server_port_input.setEnabled(True)
            self.client_ip_input.setEnabled(True)  # 서버 중지 후 클라이언트 IP 변경 가능
            self.check_server_button_state()  # 클라이언트 IP 입력 상태에 따라 시작 버튼 활성화
            self.log_signal.emit("서버가 중지되었습니다.")
        else:
            self.log_signal.emit("실행 중인 서버가 없습니다.")



    def is_server_mode(self) -> bool:
        """서버 모드인지 확인"""
        try:
            return self.server is not None and hasattr(self.server, 'is_running') and self.server.is_running
        except:
            return False

    def send_command_unified(self, command: str, log=False, on_line=None):
        """모드에 따라 명령을 전송하고 응답을 반환합니다."""

        #self.log_signal.emit(f"명령 전송: {command}")

        app = QCoreApplication.instance()
        is_ui_thread = bool(app and QThread.currentThread() == app.thread())
        event_pump = app.processEvents if is_ui_thread else None

        if is_ui_thread:
            self.set_app_status("통신중")

        try:
            if self.server and self.server.is_running:
                # 서버 모드: query 메서드를 사용하여 동기식으로 응답을 받음
                response = self.server.query(command, on_line=on_line, event_pump=event_pump)
                #if log : self.log_signal.emit(f"서버 응답: {response}")
                return response
            else:
                # 클라이언트 모드: 기존 방식대로 전송하고 응답 받기
                ip, port = self.get_ip_port()
                return send_command(command, ip, port, on_line=on_line, event_pump=event_pump)
        finally:
            if is_ui_thread:
                self.set_app_status(self.idle_status_message)



    def closeEvent(self, event):
        # 설정 저장
        self.save_settings()
        
        if self.server and self.server.is_running:
            self.server.stop_server()
            self.log_signal.emit("프로그램 종료 - 서버를 중지합니다.")
        
        self.log_signal.emit("설정이 저장되었습니다.")
        event.accept()





# --- 애플리케이션 실행 코드 ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.showMaximized()  # 최대화 상태로 시작
    sys.exit(app.exec())
