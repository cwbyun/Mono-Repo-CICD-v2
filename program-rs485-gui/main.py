#!/usr/bin/env python3

import sys
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTextEdit, QLineEdit, QPushButton,
                             QLabel, QComboBox, QSpinBox, QGroupBox, QSplitter,
                             QMessageBox, QStatusBar)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QFont, QTextCursor
from rs485_communication import RS485Communication
import serial.tools.list_ports

class CommunicationWorker(QThread):
    """별도 스레드에서 통신 처리"""
    response_received = pyqtSignal(str, str)  # command, response
    error_occurred = pyqtSignal(str)
    
    def __init__(self, comm_obj, command, use_checksum=True):
        super().__init__()
        self.comm_obj = comm_obj
        self.command = command
        self.use_checksum = use_checksum
    
    def run(self):
        try:
            if self.use_checksum:
                response = self.comm_obj.send_query(self.command)
            else:
                response = self.comm_obj.send_simple_query(self.command)
            
            if response:
                self.response_received.emit(self.command, response)
            else:
                self.error_occurred.emit(f"No response for command: {self.command}")
        except Exception as e:
            self.error_occurred.emit(f"Communication error: {str(e)}")

class RS485GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.comm = None
        self.worker = None
        self.init_ui()
        self.refresh_ports()
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("RS485 Communication Tool")
        self.setGeometry(100, 100, 900, 700)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 연결 설정 그룹
        connection_group = self.create_connection_group()
        main_layout.addWidget(connection_group)
        
        # 프로토콜 설정 그룹
        protocol_group = self.create_protocol_group()
        main_layout.addWidget(protocol_group)
        
        # 스플리터로 상하 분할
        splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(splitter)
        
        # 명령 입력 그룹
        command_group = self.create_command_group()
        splitter.addWidget(command_group)
        
        # 로그 표시 그룹
        log_group = self.create_log_group()
        splitter.addWidget(log_group)
        
        # 스플리터 비율 설정
        splitter.setSizes([250, 450])
        
        # 상태바
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def create_connection_group(self):
        """연결 설정 그룹 생성"""
        group = QGroupBox("Connection Settings")
        layout = QHBoxLayout()
        
        # 포트 선택
        layout.addWidget(QLabel("Port:"))
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(150)
        layout.addWidget(self.port_combo)
        
        # 포트 새로고침 버튼
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        layout.addWidget(self.refresh_btn)
        
        # 보드레이트 설정
        layout.addWidget(QLabel("Baudrate:"))
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baudrate_combo.setCurrentText("19200")
        layout.addWidget(self.baudrate_combo)
        
        # 타임아웃 설정
        layout.addWidget(QLabel("Timeout(s):"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 30)
        self.timeout_spin.setValue(2)
        layout.addWidget(self.timeout_spin)
        
        # 연결/해제 버튼
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        self.connect_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        layout.addWidget(self.connect_btn)
        
        layout.addStretch()  # 남은 공간 채우기
        
        group.setLayout(layout)
        return group
    
    def create_protocol_group(self):
        """프로토콜 설정 그룹 생성"""
        group = QGroupBox("Protocol Settings")
        layout = QVBoxLayout()
        
        # 송신 설정
        send_layout = QHBoxLayout()
        send_layout.addWidget(QLabel("Send -"))
        
        # 송신 STX 설정
        send_layout.addWidget(QLabel("STX:"))
        self.send_stx_combo = QComboBox()
        self.send_stx_combo.addItems(["@", "S", "@#T"])
        self.send_stx_combo.setCurrentText("@#T")
        self.send_stx_combo.setFixedWidth(80)
        self.send_stx_combo.currentTextChanged.connect(self.update_preview)
        send_layout.addWidget(self.send_stx_combo)
        
        # 송신 ETX 설정
        send_layout.addWidget(QLabel("ETX:"))
        self.send_etx_combo = QComboBox()
        self.send_etx_combo.addItems(["*", "Q", "@"])
        self.send_etx_combo.setCurrentText("Q")
        self.send_etx_combo.setFixedWidth(80)
        self.send_etx_combo.currentTextChanged.connect(self.update_preview)
        send_layout.addWidget(self.send_etx_combo)
        
        send_layout.addStretch()
        layout.addLayout(send_layout)
        
        # 수신 설정
        recv_layout = QHBoxLayout()
        recv_layout.addWidget(QLabel("Receive -"))
        
        # 수신 STX 설정
        recv_layout.addWidget(QLabel("STX:"))
        self.recv_stx_combo = QComboBox()
        self.recv_stx_combo.addItems(["@#J", "S", "D"])
        self.recv_stx_combo.setCurrentText("@#J")
        self.recv_stx_combo.setFixedWidth(80)
        recv_layout.addWidget(self.recv_stx_combo)
        
        # 수신 ETX 설정
        recv_layout.addWidget(QLabel("ETX:"))
        self.recv_etx_combo = QComboBox()
        self.recv_etx_combo.addItems(["Q", "*", "&"])
        self.recv_etx_combo.setCurrentText("Q")
        self.recv_etx_combo.setFixedWidth(80)
        recv_layout.addWidget(self.recv_etx_combo)
        
        recv_layout.addStretch()
        layout.addLayout(recv_layout)
        
        group.setLayout(layout)
        return group
    
    def create_command_group(self):
        """명령 입력 그룹 생성"""
        group = QGroupBox("Command Input & Preview")
        layout = QVBoxLayout()
        
        # 전체 명령 입력 라인
        full_input_layout = QHBoxLayout()
        full_input_layout.addWidget(QLabel("Full Command:"))
        
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter full command here or use separate fields below...")
        self.command_input.returnPressed.connect(self.send_checksum_command)
        self.command_input.textChanged.connect(self.update_preview)
        full_input_layout.addWidget(self.command_input)
        
        # Send 버튼 (STX + content + ETX만)
        self.send_simple_btn = QPushButton("Send")
        self.send_simple_btn.clicked.connect(self.send_simple_command)
        full_input_layout.addWidget(self.send_simple_btn)
        
        # CHKSUM+Send 버튼 (STX + content + CHKSUM + ETX)
        self.send_checksum_btn = QPushButton("CHKSUM+Send")
        self.send_checksum_btn.clicked.connect(self.send_checksum_command)
        full_input_layout.addWidget(self.send_checksum_btn)
        
        # 미리보기 버튼
        self.preview_btn = QPushButton("Preview")
        self.preview_btn.clicked.connect(self.show_preview)
        full_input_layout.addWidget(self.preview_btn)
        
        layout.addLayout(full_input_layout)
        
        # 구분선
        from PyQt6.QtWidgets import QFrame
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # 분할 명령 입력 영역
        parts_layout = QVBoxLayout()
        parts_layout.addWidget(QLabel("Or use separate command parts:"))
        
        # PRE, ID, CMD, POSTSTRING 입력
        parts_input_layout = QHBoxLayout()
        
        # PRESTRING
        parts_input_layout.addWidget(QLabel("PRE(4자리):"))
        self.prestring_input = QLineEdit()
        self.prestring_input.setText("JW17")
        self.prestring_input.setFixedWidth(120)
        self.prestring_input.textChanged.connect(self.update_combined_command)
        parts_input_layout.addWidget(self.prestring_input)
        
        # ID (6자리 정수, 0 패딩)
        parts_input_layout.addWidget(QLabel("ID:"))
        self.id_input = QLineEdit()
        self.id_input.setText("0")
        self.id_input.setFixedWidth(120)
        self.id_input.textChanged.connect(self.update_combined_command)
        parts_input_layout.addWidget(self.id_input)
        
        # CMD
        parts_input_layout.addWidget(QLabel("CMD:"))
        self.cmd_combo = QComboBox()
        self.cmd_combo.addItems(["", "A", "C", "E", "F", "G", "H", "I"])
        self.cmd_combo.currentTextChanged.connect(self.on_cmd_changed)
        self.cmd_combo.setFixedWidth(120)
        parts_input_layout.addWidget(self.cmd_combo)
        
        # POSTSTRING
        self.poststring_input = QLineEdit()
        parts_input_layout.addWidget(QLabel("POST(자동):"))
        self.poststring_input.setText("00")
        self.poststring_input.setFixedWidth(120)
        self.poststring_input.textChanged.connect(self.update_combined_command)
        parts_input_layout.addWidget(self.poststring_input)

        # E, G 명령용 ON/OFF 콤보박스
        self.onoff_label = QLabel("ON/OFF:")
        self.onoff_combo = QComboBox()
        self.onoff_combo.addItems(["ON", "OFF"])
        self.onoff_combo.setFixedWidth(80)
        self.onoff_combo.currentTextChanged.connect(self.on_onoff_changed)
        parts_input_layout.addWidget(self.onoff_label)
        parts_input_layout.addWidget(self.onoff_combo)

        # 초기에는 숨김
        self.onoff_label.setVisible(False)
        self.onoff_combo.setVisible(False)

        # F 명령용 시간(초) 입력박스
        self.time_label = QLabel("시간(초):")
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("예: 20")
        self.time_input.setFixedWidth(80)
        self.time_input.textChanged.connect(self.on_f_params_changed)
        parts_input_layout.addWidget(self.time_label)
        parts_input_layout.addWidget(self.time_input)

        # F 명령용 제외 ID 입력박스
        self.exclude_id_label = QLabel("제외ID(10자리):")
        self.exclude_id_input = QLineEdit()
        self.exclude_id_input.setPlaceholderText("10자리")
        self.exclude_id_input.setFixedWidth(120)
        self.exclude_id_input.textChanged.connect(self.on_f_params_changed)
        parts_input_layout.addWidget(self.exclude_id_label)
        parts_input_layout.addWidget(self.exclude_id_input)

        # 초기에는 숨김
        self.time_label.setVisible(False)
        self.time_input.setVisible(False)
        self.exclude_id_label.setVisible(False)
        self.exclude_id_input.setVisible(False)

        # 분할 명령 전송 버튼
        self.send_parts_btn = QPushButton("Send Parts")
        self.send_parts_btn.clicked.connect(self.send_combined_command)
        parts_input_layout.addWidget(self.send_parts_btn)
        
        parts_layout.addLayout(parts_input_layout)
        layout.addLayout(parts_layout)
        
        # 빠른 명령 버튼들
        #quick_layout = QHBoxLayout()
        #quick_layout.addWidget(QLabel("Quick Commands:"))
        
        #quick_commands = ["STATUS", "VERSION", "HELLO", "RESET"]
        #self.quick_buttons = []
        #for cmd in quick_commands:
        #    btn = QPushButton(cmd)
        #    btn.clicked.connect(lambda checked, command=cmd: self.send_quick_command(command))
        #    quick_layout.addWidget(btn)
        #    self.quick_buttons.append(btn)
        
        #quick_layout.addStretch()
        #layout.addLayout(quick_layout)
        
        # 미리보기 표시 영역
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(QLabel("Command Preview:"))
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(80)
        self.preview_text.setFont(QFont("Consolas", 9))
        preview_layout.addWidget(self.preview_text)
        
        layout.addLayout(preview_layout)
        
        group.setLayout(layout)
        return group
    
    def create_log_group(self):
        """로그 표시 그룹 생성"""
        group = QGroupBox("Communication Log")
        layout = QVBoxLayout()
        
        # 로그 표시 영역
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.log_text)
        
        # 제어 버튼들
        button_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("Clear Log")
        self.clear_btn.clicked.connect(self.clear_log)
        button_layout.addWidget(self.clear_btn)
        
        self.save_btn = QPushButton("Save Log")
        self.save_btn.clicked.connect(self.save_log)
        button_layout.addWidget(self.save_btn)
        
        button_layout.addStretch()
        
        # 종료 버튼
        self.exit_btn = QPushButton("Exit")
        self.exit_btn.clicked.connect(self.close_application)
        self.exit_btn.setStyleSheet("QPushButton { background-color: #ff5722; color: white; font-weight: bold; }")
        button_layout.addWidget(self.exit_btn)
        
        layout.addLayout(button_layout)
        
        group.setLayout(layout)
        return group
    
    def update_preview(self):
        """미리보기 업데이트"""
        query = self.command_input.text()
        stx = self.send_stx_combo.currentText() or "@"
        etx = self.send_etx_combo.currentText() or "*"
        
        if query:
            # 임시 통신 객체로 미리보기 생성
            temp_comm = RS485Communication(stx=stx, etx=etx)
            preview_info = temp_comm.preview_command(query)
            
            preview_text = f"Full Command: {preview_info['full_command']}\n"
            preview_text += f"Hex: {preview_info['full_command_hex']}\n"
            preview_text += f"Checksum: {preview_info['checksum']}"
            
            self.preview_text.setText(preview_text)
        else:
            self.preview_text.clear()
    
    def show_preview(self):
        """상세 미리보기 다이얼로그 표시"""
        query = self.command_input.text().strip()
        if not query:
            QMessageBox.information(self, "Info", "Please enter a command to preview.")
            return
        
        stx = self.send_stx_combo.currentText() or "@"
        etx = self.send_etx_combo.currentText() or "*"
        
        # 임시 통신 객체로 미리보기 생성
        temp_comm = RS485Communication(stx=stx, etx=etx)
        
        # 체크섬 있는 버전과 없는 버전 모두 생성
        preview_with_checksum = temp_comm.preview_command(query)
        preview_simple = temp_comm.preview_simple_command(query)
        
        # 상세 정보 표시
        details = f"""
Command Preview Details:

Input Command: '{query}'
STX: '{stx}' | ETX: '{etx}'

=== SEND (Simple) ===
Full Command: {preview_simple['full_command']}
Hex: {preview_simple['full_command_hex']}
Length: {preview_simple['command_length']} bytes

=== CHKSUM+SEND ===
Full Command: {preview_with_checksum['full_command']}
Hex: {preview_with_checksum['full_command_hex']}
Checksum: {preview_with_checksum['checksum']}
Length: {preview_with_checksum['command_length']} bytes
"""
        
        QMessageBox.information(self, "Command Preview", details)
    
    def refresh_ports(self):
        """시리얼 포트 목록 새로고침"""
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            self.port_combo.addItem(f"{port.device} - {port.description}")
        
        if not ports:
            self.port_combo.addItem("No ports found")
        
        self.log_message("INFO", f"Found {len(ports)} serial ports")
    
    def toggle_connection(self):
        """연결/해제 토글"""
        if self.comm and self.comm.is_connected():
            self.disconnect_device()
        else:
            self.connect_device()
    
    def connect_device(self):
        """장치 연결"""
        if self.port_combo.count() == 0 or self.port_combo.currentText() == "No ports found":
            QMessageBox.warning(self, "Warning", "No serial ports available")
            return
        
        # 포트 이름 추출
        port_text = self.port_combo.currentText()
        port_name = port_text.split(" - ")[0]
        
        baudrate = int(self.baudrate_combo.currentText())
        timeout = self.timeout_spin.value()
        stx = self.send_stx_combo.currentText() or "@"
        etx = self.send_etx_combo.currentText() or "*"
        
        recv_stx = self.recv_stx_combo.currentText() or "@#J"
        recv_etx = self.recv_etx_combo.currentText() or "Q"
        
        try:
            self.comm = RS485Communication(port=port_name, baudrate=baudrate, timeout=timeout, 
                                         stx=stx, etx=etx, recv_stx=recv_stx, recv_etx=recv_etx)
            
            if self.comm.connect():
                self.connect_btn.setText("Disconnect")
                self.connect_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")
                self.send_simple_btn.setEnabled(True)
                self.send_checksum_btn.setEnabled(True)
                
                # 빠른 명령 버튼들 활성화
                #for btn in self.quick_buttons:
                #    btn.setEnabled(True)
                
                self.status_bar.showMessage(f"Connected to {port_name}")
                self.log_message("INFO", f"Connected to {port_name} at {baudrate} baud with STX='{stx}', ETX='{etx}'")
            else:
                QMessageBox.critical(self, "Error", f"Failed to connect to {port_name}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")
    
    def disconnect_device(self):
        """장치 연결 해제"""
        if self.comm:
            self.comm.disconnect()
            self.comm = None
        
        self.connect_btn.setText("Connect")
        self.connect_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.send_simple_btn.setEnabled(False)
        self.send_checksum_btn.setEnabled(False)
        
        # 빠른 명령 버튼들 비활성화
        #for btn in self.quick_buttons:
        #    btn.setEnabled(False)
        
        self.status_bar.showMessage("Disconnected")
        self.log_message("INFO", "Disconnected")
    
    def send_command(self):
        """명령 전송 (기본 체크섬 포함)"""
        command = self.command_input.text().strip()
        if not command:
            return
        
        self.send_query(command, use_checksum=True)
        # 마지막 질의를 유지하기 위해 clear() 제거
        # self.command_input.clear()
        self.update_preview()  # 미리보기 업데이트
    
    def send_simple_command(self):
        """간단한 명령 전송 (체크섬 없음)"""
        command = self.command_input.text().strip()
        if not command:
            return
        
        self.send_query(command, use_checksum=False)
        self.update_preview()  # 미리보기 업데이트
    
    def send_checksum_command(self):
        """체크섬 포함 명령 전송"""
        command = self.command_input.text().strip()
        if not command:
            return
        
        self.send_query(command, use_checksum=True)
        self.update_preview()  # 미리보기 업데이트
    
    def send_quick_command(self, command):
        """빠른 명령 전송"""
        self.send_query(command, use_checksum=True)
    
    def on_cmd_changed(self, cmd_text):
        """CMD 선택 변경 시 처리"""
        cmd_descriptions = {
            "A": "센서의 모든 데이터를 가져옵니다.",
            "C": "Status를 읽습니다.",
            "E": "종단 저항릴레이를 설정합니다.",
            "F": "통신 릴레이를 차단합니다.",
            "G": "온도 보상을 설정합니다.",
            "H": "Reset 합니다.",
            "I": "ID를 요청합니다."
        }

        # 선택된 CMD에 대한 설명을 로그에 출력
        if cmd_text and cmd_text in cmd_descriptions:
            self.log_message("INFO", f"CMD {cmd_text} 선택: {cmd_descriptions[cmd_text]}")

        # E, G 명령일 때만 ON/OFF 콤보박스 표시
        if cmd_text in ["E", "G"]:
            self.onoff_label.setVisible(True)
            self.onoff_combo.setVisible(True)
        else:
            self.onoff_label.setVisible(False)
            self.onoff_combo.setVisible(False)

        # F 명령일 때만 시간/제외ID 입력박스 표시
        if cmd_text == "F":
            self.time_label.setVisible(True)
            self.time_input.setVisible(True)
            self.exclude_id_label.setVisible(True)
            self.exclude_id_input.setVisible(True)
        else:
            self.time_label.setVisible(False)
            self.time_input.setVisible(False)
            self.exclude_id_label.setVisible(False)
            self.exclude_id_input.setVisible(False)

        # 명령 업데이트
        self.update_combined_command()

    def on_f_params_changed(self):
        """F 명령 파라미터 변경 시 처리"""
        # 명령 업데이트
        self.update_combined_command()

    def on_onoff_changed(self, onoff_text):
        """ON/OFF 선택 변경 시 처리"""
        # 현재 선택된 CMD가 E 또는 G일 때만 처리
        cmd_text = self.cmd_combo.currentText()
        if cmd_text in ["E", "G"]:
            if onoff_text == "ON":
                post_value = "11"
            else:  # OFF
                post_value = "10"

            self.poststring_input.setText(post_value)
            self.log_message("INFO", f"CMD {cmd_text} - {onoff_text} 선택: POST={post_value}")

        # 명령 업데이트
        self.update_combined_command()

    def update_combined_command(self):
        """분할 입력 필드들을 결합하여 전체 명령 업데이트"""
        prestring = self.prestring_input.text()
        id_text = self.id_input.text()
        cmd = self.cmd_combo.currentText()
        poststring = self.poststring_input.text()
        
        # ID를 6자리로 0패딩
        if id_text and id_text.isdigit():
            padded_id = id_text.zfill(6)
        else:
            padded_id = id_text
        

        # CMD에 따른 POST 자동 설정
        cmd_upper = cmd.upper()

        # E, G 명령의 경우 ON/OFF 콤보박스 값에 따라 POST 설정
        if cmd_upper in ["E", "G"] and self.onoff_combo.isVisible():
            onoff_value = self.onoff_combo.currentText()
            if onoff_value == "ON":
                post_value = "011"
            else:  # OFF
                post_value = "010"
            self.poststring_input.setText(post_value)
            poststring = post_value  # 변수도 업데이트
        else:
            # 일반 명령들의 기본 POST 값
            cmd_post_mapping = {
                "A": "00",  # 센서 데이터 조회
                "C": "00",  # 상태 조회
                "E": "11",  # 종단 저항릴레이 설정 (기본값 ON)
                "F": "14",  # 통신 릴레이 차단 시간 (20초)
                "G": "11",  # 온도 보상 설정 (기본값 ON)
                "H": "00",  # Reset
                "I": "00"   # ID 요청
            }

            if cmd_upper in cmd_post_mapping:
                post_value = cmd_post_mapping[cmd_upper]
                self.poststring_input.setText(post_value)
                poststring = post_value  # 변수도 업데이트

        # CMD=I인 경우 특별 처리: PRE 공백, ID=0000000000
        if cmd_upper == "I":
            self.prestring_input.setText("")
            self.id_input.setText("0000000000")
            # 변수들도 업데이트
            prestring = ""
            id_text = "0000000000"
            padded_id = "0000000000"

        # 분할 입력이 있으면 결합하여 전체 명령 필드 업데이트
        if prestring or padded_id or cmd or poststring:
            combined = prestring + padded_id + cmd + poststring

            # F 명령의 경우 POST 다음에 시간(4자리)과 제외ID(10자리) 추가
            if cmd_upper == "F" and self.time_input.isVisible():
                time_text = self.time_input.text().strip()
                exclude_id_text = self.exclude_id_input.text().strip()

                # 시간을 4자리 0패딩
                if time_text and time_text.isdigit():
                    time_padded = time_text.zfill(4)
                else:
                    time_padded = "0000"

                # 제외 ID를 10자리로 맞춤 (부족하면 0패딩, 초과하면 자름)
                if exclude_id_text:
                    exclude_id_padded = exclude_id_text.ljust(10, '0')[:10]
                else:
                    exclude_id_padded = "0000000000"

                combined = combined + time_padded + exclude_id_padded

            # 전체 명령 필드 업데이트 시 무한루프 방지를 위해 시그널 차단
            self.command_input.blockSignals(True)
            self.command_input.setText(combined)
            self.command_input.blockSignals(False)
        
        self.update_preview()
    
    def send_combined_command(self):
        """분할 명령 전송"""
        prestring = self.prestring_input.text()
        id_text = self.id_input.text()
        cmd = self.cmd_combo.currentText().upper()
        poststring = self.poststring_input.text()
        
        # CMD=G, E인 경우 Send Parts 버튼 사용 금지
        if cmd == 'G':
            self.log_message("INFO", "CMD=G는 Full Command로만 전송 가능합니다.")
            self.log_message("INFO", "예시: G011 (온도보상 ON), G010 (온도보상 OFF)")
            QMessageBox.information(self, "CMD=G 사용법", 
                                  "CMD=G는 온도보상 설정 명령으로 Full Command 필드에서만 사용 가능합니다.\n\n"
                                  "사용 예시:\n"
                                  "- 온도보상 ON: G011\n"
                                  "- 온도보상 OFF: G010")
            return
        elif cmd == 'E':
            self.log_message("INFO", "CMD=E는 Full Command로만 전송 가능합니다.")
            self.log_message("INFO", "예시: JW17000000E011 (연결), JW17000000E010 (끊김)")
            QMessageBox.information(self, "CMD=E 사용법", 
                                  "CMD=E는 연결상태 설정 명령으로 Full Command 필드에서만 사용 가능합니다.\n\n"
                                  "사용 예시:\n"
                                  "- 연결: E011\n"
                                  "- 끊김: E010")
            return
        
        # ID를 6자리로 0패딩
        if id_text and id_text.isdigit():
            padded_id = id_text.zfill(6)
        else:
            padded_id = id_text
        
        combined = prestring + padded_id + cmd + poststring
        if combined.strip():
            self.send_query(combined, use_checksum=True)
    
    def send_query(self, command, use_checksum=True):
        """실제 질의 전송"""
        
        if not self.comm or not self.comm.is_connected():
            # 연결이 없어도 미리보기는 표시
            self.log_message("PREVIEW", f"Command: {command}")
            temp_comm = RS485Communication(stx=self.send_stx_combo.currentText() or "@", etx=self.send_etx_combo.currentText() or "*")
            if use_checksum:
                preview_info = self.comm.preview_command(command) if self.comm else temp_comm.preview_command(command)
            else:
                preview_info = self.comm.preview_simple_command(command) if self.comm else temp_comm.preview_simple_command(command)
            self.log_message("PREVIEW", f"Full packet: {preview_info['full_command']}")
            self.log_message("PREVIEW", f"Hex: {preview_info['full_command_hex']}")
            checksum_note = f" (Checksum: {preview_info['checksum']})" if use_checksum else " (No checksum)"
            QMessageBox.information(self, "Not Connected", 
                                  f"Not connected to device.\n\nPreview:\nCommand: {preview_info['full_command']}\nHex: {preview_info['full_command_hex']}{checksum_note}")
            return
        
        # STX/ETX 업데이트
        stx = self.send_stx_combo.currentText() or "@"
        etx = self.send_etx_combo.currentText() or "*"
        recv_stx = self.recv_stx_combo.currentText() or "@#J"
        recv_etx = self.recv_etx_combo.currentText() or "Q"
        self.comm.set_stx_etx(stx, etx, recv_stx, recv_etx)
        
        checksum_type = "CHKSUM+SEND" if use_checksum else "SEND"
        self.log_message("SEND", f"[{checksum_type}] {command}")
        
        # 미리보기도 함께 표시
        if use_checksum:
            preview_info = self.comm.preview_command(command)
        else:
            preview_info = self.comm.preview_simple_command(command)
            
        checksum_info = f" (Checksum: {preview_info['checksum']})" if use_checksum else " (No checksum)"
        self.log_message("PREVIEW", f"Sending: {preview_info['full_command']} (Hex: {preview_info['full_command_hex']}){checksum_info}")
        
        self.status_bar.showMessage("Sending command...")
        
        # 별도 스레드에서 통신 처리
        self.worker = CommunicationWorker(self.comm, command, use_checksum)
        self.worker.response_received.connect(self.on_response_received)
        self.worker.error_occurred.connect(self.on_error_occurred)
        self.worker.start()
    
    def on_response_received(self, command, response):
        """응답 수신 처리"""
        self.log_message("RECV", response)
        
        # 구조화된 응답 파싱 시도
        if self.comm:
            parsed = self.comm.parse_structured_response(response)
            if parsed and 'parsed_data' in parsed:
                self.display_parsed_data(parsed['parsed_data'], parsed['cmd'])
        
        self.status_bar.showMessage("Ready")
    
    def on_error_occurred(self, error_msg):
        """에러 처리"""
        self.log_message("ERROR", error_msg)
        self.status_bar.showMessage("Error occurred")
    
    def display_parsed_data(self, parsed_data, cmd):
        """파싱된 데이터를 로그에 표시"""
        if cmd == 'A':
            # CMD A 센서 데이터 표시
            data_lines = []
            if 'displacement' in parsed_data:
                data_lines.append(f"변위계: {parsed_data['displacement']:.2f}")
            if 'x_angle_lsb' in parsed_data:
                data_lines.append(f"X각도: {parsed_data['x_angle_lsb']} LSB")
            if 'y_angle_lsb' in parsed_data:
                data_lines.append(f"Y각도: {parsed_data['y_angle_lsb']} LSB")
            if 'temperature' in parsed_data:
                data_lines.append(f"온도: {parsed_data['temperature']:.2f}°C")
            if 'voltage' in parsed_data:
                data_lines.append(f"전압: {parsed_data['voltage']:.2f}V")
            if 'current_ma' in parsed_data:
                data_lines.append(f"전류: {parsed_data['current_ma']:.1f}mA")
            
            if data_lines:
                formatted_data = " | ".join(data_lines)
                self.log_message("PARSED", formatted_data)
                
        elif cmd == 'C':
            # CMD C 설정 데이터 표시
            data_lines = []
            if 'version' in parsed_data:
                data_lines.append(f"버전: {parsed_data['version']:.2f}")
            if 'sensor_type' in parsed_data:
                data_lines.append(f"센서: {parsed_data['sensor_type']}")
            if 'termination_relay' in parsed_data:
                data_lines.append(f"종단저항: {parsed_data['termination_relay']}")
            if 'temperature_compensation' in parsed_data:
                data_lines.append(f"온도보상: {parsed_data['temperature_compensation']}")
            if 'displacement_status' in parsed_data:
                data_lines.append(f"변위계상태: {parsed_data['displacement_status']}")
            if 'reference_voltage' in parsed_data:
                data_lines.append(f"기준전압: {parsed_data['reference_voltage']:.3f}V")
            if 'angle_status' in parsed_data:
                data_lines.append(f"각도계상태: {parsed_data['angle_status']}")
            if 'displacement_setting' in parsed_data:
                data_lines.append(f"변위계설정: {parsed_data['displacement_setting']}")
            if 'angle_setting' in parsed_data:
                data_lines.append(f"각도계설정: {parsed_data['angle_setting']}")
            
            if data_lines:
                formatted_data = " | ".join(data_lines)
                self.log_message("PARSED", formatted_data)
                
        elif cmd == 'E':
            # CMD E 연결 상태 설정 확인 표시
            if 'status_message' in parsed_data:
                self.log_message("PARSED", parsed_data['status_message'])
                
        elif cmd == 'F':
            # CMD F 릴레이 off 시간 표시
            if 'relay_off_time' in parsed_data:
                self.log_message("PARSED", f"릴레이오프시간: {parsed_data['relay_off_time']}초")
                
                
        elif cmd == 'G':
            # CMD G 온도보상 현재 상태 표시
            if 'status_message' in parsed_data:
                self.log_message("PARSED", parsed_data['status_message'])
                
        elif cmd == 'H':
            # CMD H RESET 명령 표시
            if 'reset_status' in parsed_data:
                self.log_message("PARSED", parsed_data['reset_status'])
                
        elif cmd == 'I':
            # CMD I ID 데이터 표시
            if 'device_id' in parsed_data:
                self.log_message("PARSED", f"Device ID: {parsed_data['device_id']}")
    
    def log_message(self, msg_type, message):
        """로그 메시지 추가"""
        timestamp = time.strftime("%H:%M:%S")
        
        # 메시지 타입별 색상
        if msg_type == "SEND":
            color = "blue"
        elif msg_type == "RECV":
            color = "green"
        elif msg_type == "ERROR":
            color = "red"
        elif msg_type == "PREVIEW":
            color = "purple"
        elif msg_type == "PARSED":
            color = "darkgreen"
        else:  # INFO
            color = "black"
        
        formatted_msg = f'<span style="color: {color};"><b>[{timestamp}] {msg_type}:</b> {message}</span>'
        
        self.log_text.append(formatted_msg)
        
        # 자동으로 마지막 줄로 스크롤
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def clear_log(self):
        """로그 클리어"""
        self.log_text.clear()
        self.log_message("INFO", "Log cleared")
    
    def save_log(self):
        """로그 저장"""
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Log", "rs485_log.txt", "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    # HTML 태그 제거하고 저장
                    plain_text = self.log_text.toPlainText()
                    f.write(plain_text)
                
                self.log_message("INFO", f"Log saved to {filename}")
                QMessageBox.information(self, "Success", f"Log saved to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save log: {str(e)}")
    
    def close_application(self):
        """애플리케이션 종료"""
        if self.comm and self.comm.is_connected():
            self.disconnect_device()
        self.close()
    
    def closeEvent(self, event):
        """프로그램 종료시 연결 해제"""
        if self.comm and self.comm.is_connected():
            self.disconnect_device()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = RS485GUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
