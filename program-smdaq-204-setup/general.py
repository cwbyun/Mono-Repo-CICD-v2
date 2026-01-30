from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame,
    QComboBox, QFileDialog, QMessageBox, QApplication
)
from PyQt6.QtCore import QDate

from utils import *
import protocol as ptcl
import time
import socket
import struct
from datetime import datetime

DEFAULT_NTC_SERVERS = [
    "kr.pool.ntp.org",
    "time.kriss.re.kr",
    "pool.ntp.org",
    "time.google.com",
]


class GeneralTab(QWidget):


    def __init__(self, parent):
        """
            '기본 설정' 탭의 UI와 기능을 모두 담고 있는 클래스입니다.
            parent 인자로는 MainWindow의 인스턴스(self)가 전달됩니다.
        """

        super().__init__()

        self.main_window = parent

        main_layout = QVBoxLayout(self)


        # Version..........
        version_layout = QHBoxLayout()
        version_button = QPushButton("Version")
        self.version_label = QLabel("---")
        self.version_label.setMinimumWidth(150)

        version_layout.addWidget( version_button )
        version_layout.addWidget( self.version_label )
        version_layout.addStretch( 1 )

        main_layout.addLayout( version_layout )


        # line .................
        line = QFrame()
        line.setFrameShape( QFrame.Shape.HLine )
        line.setFrameShadow( QFrame.Shadow.Sunken )
        main_layout.addWidget( line )

        # CSV Export/Import..........
        csv_layout = QHBoxLayout()
        
        export_csv_button = QPushButton("Export to CSV")
        export_csv_button.setMinimumHeight(30)
        
        import_csv_button = QPushButton("Import from CSV")
        import_csv_button.setMinimumHeight(30)

        csv_layout.addWidget( export_csv_button )
        csv_layout.addWidget( import_csv_button )
        csv_layout.addStretch( 1 )

        main_layout.addLayout( csv_layout )

        # line .................
        line2 = QFrame()
        line2.setFrameShape( QFrame.Shape.HLine )
        line2.setFrameShadow( QFrame.Shadow.Sunken )
        main_layout.addWidget( line2 )




        # Factory Initialization

        factory_reset_layout = QHBoxLayout()

        self.factory_reset_combo =  QComboBox()
        self.factory_reset_combo.addItems( [
            "0: Config Format",
            "1: ID Format",
            "2: Sensing Value Format",
            "3: All Format"
            ])
        factory_reset_button = QPushButton("SET")


        factory_reset_layout.addWidget( QLabel("Factory Reset") )
        factory_reset_layout.addWidget( self.factory_reset_combo )
        factory_reset_layout.addWidget( factory_reset_button )
        factory_reset_layout.addStretch( 1 )


        main_layout.addLayout( factory_reset_layout )



        # Set Date & Time
        date_time_layout = QHBoxLayout()
        layout13_config = [
                {'type': 'date_time', 'label': '시간 설정:', 'name': 'datetime', 'default_time': '00:00:00', 'date_width': 110, 'time_width': 85, 'time_format': 'HH:mm:ss'},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
        ]
        group, self.dateTime = create_dynamic_group('Setting Date & Time (cmd=6)', layout13_config )

        date_time_layout.addWidget( group )
        date_time_layout.addStretch( 1 )
        

        main_layout.addLayout( date_time_layout )

        # NTC Time Read
        ntc_layout = QHBoxLayout()
        saved_ntc_server = self.main_window.settings.value("ntc_server", "")
        saved_ntc_port = self.main_window.settings.value("ntc_port", "123")
        self.ntc_server_input = QLineEdit(saved_ntc_server)
        self.ntc_server_input.setPlaceholderText("ntc server (blank = auto)")
        self.ntc_server_input.setMinimumWidth(180)
        self.ntc_port_input = QLineEdit(saved_ntc_port)
        self.ntc_port_input.setFixedWidth(60)
        self.ntc_read_button = QPushButton("Read NTC")
        ntc_layout.addWidget( QLabel("NTC Server") )
        ntc_layout.addWidget( self.ntc_server_input )
        ntc_layout.addWidget( QLabel("Port") )
        ntc_layout.addWidget( self.ntc_port_input )
        ntc_layout.addWidget( self.ntc_read_button )
        ntc_layout.addStretch( 1 )
        main_layout.addLayout( ntc_layout )

        self.ntc_server_input.textChanged.connect(
            lambda: self.main_window.settings.setValue("ntc_server", self.ntc_server_input.text())
        )
        self.ntc_port_input.textChanged.connect(
            lambda: self.main_window.settings.setValue("ntc_port", self.ntc_port_input.text())
        )

        # line .................
        line3 = QFrame()
        line3.setFrameShape( QFrame.Shape.HLine )
        line3.setFrameShadow( QFrame.Shadow.Sunken )
        main_layout.addWidget( line3 )

        # Incoming Client IP selection
        incoming_layout = QHBoxLayout()
        self.incoming_ip_combo = QComboBox()
        self.incoming_ip_combo.setMinimumWidth(160)
        self.use_incoming_ip_button = QPushButton("Use Selected IP")
        self.clear_incoming_ip_button = QPushButton("Clear")
        incoming_layout.addWidget( QLabel("Incoming Client IP") )
        incoming_layout.addWidget( self.incoming_ip_combo )
        incoming_layout.addWidget( self.use_incoming_ip_button )
        incoming_layout.addWidget( self.clear_incoming_ip_button )
        incoming_layout.addStretch( 1 )
        main_layout.addLayout( incoming_layout )

        self.incoming_ip_set = set()




        main_layout.addStretch(1)

        version_button.clicked.connect(self.send_version_command)
        #export_csv_button.clicked.connect(self.export_to_csv)
        #import_csv_button.clicked.connect(self.import_from_csv)
        factory_reset_button.clicked.connect( self.execute_selected_option )
        self.dateTime['set_btn'].clicked.connect( self.date_time_set_btn )
        self.ntc_read_button.clicked.connect( self.read_ntc_time_btn )
        self.use_incoming_ip_button.clicked.connect( self.apply_incoming_ip )
        self.clear_incoming_ip_button.clicked.connect( self.clear_incoming_ip_list )

    def date_time_set_btn( self ):

        data_str = self.dateTime['datetime_date'].date().toString("yyMMdd")
        time_text = (self.dateTime['datetime_time'].text() or '00:00:00').strip()

        # 시간에서 시:분:초 추출
        time_parts = time_text.split(':')
        if len(time_parts) >= 3:
            hh = time_parts[0].zfill(2)
            mm = time_parts[1].zfill(2)
            ss = time_parts[2].zfill(2)
        elif len(time_parts) == 2:
            hh = time_parts[0].zfill(2)
            mm = time_parts[1].zfill(2)
            ss = "00"
        else:
            hh = "00"
            mm = "00"
            ss = "00"

        # 옵션 1: 초 포함 (S6yyMMddHHmmssQ)
        # data_str += hh + mm + ss
        # command = ptcl.STX + "6" + data_str + "Q"

        # 옵션 2: 초 제외 (S6yyMMddHHmmQ) - 이 옵션으로 테스트
        data_str += hh + mm
        command = ptcl.STX + "6" + data_str + "Q"

        self.main_window.add_log(f"전송 >> {command}")
        response = self.main_window.send_command_unified(command)
        if response:
            self.main_window.add_log(f"응답 << {response}")
        else:
            self.main_window.add_log("응답 없음 (시간 설정 명령은 응답이 없을 수 있음)")

    def read_ntc_time_btn( self ):
        server = self.ntc_server_input.text().strip()
        if server:
            servers = [s.strip() for s in server.replace(";", ",").split(",") if s.strip()]
        else:
            servers = list(DEFAULT_NTC_SERVERS)
            self.main_window.add_log("NTC 서버 자동 선택 모드로 동작합니다.")

        port_text = self.ntc_port_input.text().strip()
        try:
            port = int(port_text) if port_text else 123
        except ValueError:
            self.main_window.add_log("오류: NTC 포트는 숫자만 입력하세요.")
            return

        if port < 1 or port > 65535:
            self.main_window.add_log("오류: NTC 포트 범위는 1~65535 입니다.")
            return

        try:
            ntc_time, used_server = self.fetch_ntc_time_from_servers(servers, port)
        except Exception as e:
            self.main_window.add_log(f"오류: NTC 서버 시간 읽기 실패: {e}")
            return

        self.dateTime['datetime_date'].setDate(QDate(ntc_time.year, ntc_time.month, ntc_time.day))
        self.dateTime['datetime_time'].setText(ntc_time.strftime("%H:%M:%S"))
        self.main_window.add_log(
            f"NTC 시간 수신: {ntc_time.strftime('%Y-%m-%d %H:%M:%S')} (서버: {used_server})"
        )
        self.main_window.add_log("SET 버튼으로 적용하세요.")

    def fetch_ntc_time_from_servers( self, servers: list[str], port: int ) -> tuple[datetime, str]:
        last_error = None
        for server in servers:
            try:
                return self.fetch_ntc_time(server, port), server
            except Exception as e:
                last_error = e
                if len(servers) > 1:
                    self.main_window.add_log(f"NTC 서버 실패: {server} ({e})")
                continue
        if last_error:
            raise last_error
        raise ValueError("사용 가능한 NTC 서버가 없습니다.")

    def fetch_ntc_time( self, server: str, port: int ) -> datetime:
        request = b'\x1b' + 47 * b'\0'
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(2.5)
            sock.sendto(request, (server, port))
            data, _ = sock.recvfrom(1024)

        if len(data) < 48:
            raise ValueError("응답 길이가 짧습니다.")

        seconds, fraction = struct.unpack("!II", data[40:48])
        ntp_time = seconds + (fraction / 2**32)
        unix_time = ntp_time - 2208988800
        return datetime.fromtimestamp(unix_time)



    def execute_selected_option( self ):

        data_str = str(self.factory_reset_combo.currentIndex())

        print("data = ", data_str )
        command, response = self.server_common_command( "W", "R", data_str )


    def send_version_command(self):

        command, response = self.server_common_command( "R", "V" )

        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return
        
        """'Version' 버튼 클릭 시 호출됩니다."""
        # MainWindow의 통신 메서드를 직접 호출
        
        ans = trim_string( response, 3, 3 )
        print('ans =', ans)

        self.version_label.setText(ans)

        print("com = ", command)
        print("res = ", response)

    def add_incoming_client_ip(self, ip: str):
        ip = ip.strip()
        if not ip or ip in self.incoming_ip_set:
            return
        self.incoming_ip_set.add(ip)
        self.incoming_ip_combo.addItem(ip)
        self.incoming_ip_combo.setCurrentText(ip)

    def apply_incoming_ip(self):
        ip = self.incoming_ip_combo.currentText().strip()
        if not ip:
            self.main_window.add_log("오류: 선택된 Incoming Client IP가 없습니다.")
            return
        self.main_window.set_allowed_client_ip(ip)

    def clear_incoming_ip_list(self):
        self.incoming_ip_set.clear()
        self.incoming_ip_combo.clear()

    def server_common_command( self, DIR, CMD, data_str=None):

        command = ptcl.STX + DIR + CMD

        if  data_str:
            command += data_str

        command = add_tail( command )

        response = self.main_window.send_command_unified( command )
        return command, response
