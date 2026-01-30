from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QGroupBox
)
from PyQt6.QtCore import Qt
from communication import *
from utils import *
import protocol as ptcl


class UserCommandTab(QWidget):
    def __init__(self, parent):
        """
            'UserCommand' 탭의 UI와 기능을 모두 담고 있는 클래스입니다.
            parent 인자로는 MainWindow의 인스턴스(self)가 전달됩니다.
        """

        super().__init__()
        self.main_window = parent

        main_layout = QVBoxLayout(self)

        # 안내 문장 추가
        info_label = QLabel("[ 안내 ] Enter 키: Send (체크섬 없이 전송) | Checksum+Send 버튼: 체크섬 추가하여 전송")
        info_label.setStyleSheet("color: #555; font-size: 11px; padding: 5px;")
        main_layout.addWidget(info_label)

        layout1_config = [
                {'type': 'input_pair', 'label':'Command:', 'name':'command'},
                {'type': 'button', 'text':'Checksum+Send', 'name':'checksum'},
                {'type': 'button', 'text':'Send', 'name':'send'},
        ]
        group1, self.widgets1 = create_dynamic_group('Test Write/Read SD Card (cmd=c)', layout1_config, input_width=150 )


        main_layout.addWidget(group1)
        main_layout.addStretch()

        self.widgets1['checksum'].clicked.connect( self.user_command_checksum_btn )
        self.widgets1['send'].clicked.connect( self.user_command_send_btn )
        self.widgets1['command'].returnPressed.connect( self.user_command_send_btn )


    def user_command_send_btn( self ):
        #ip, port = self.main_window.get_ip_port()
        command = self.widgets1['command'].text()
        #print("command = ", command)

        #self.main_window.add_log(f"전송 >> {command}")
        #response = send_command(command, ip, port)

        response = self.main_window.send_command_unified( command )
        #self.main_window.add_log(f"응답 << {response}")









    def user_command_checksum_btn( self ):
        command = self.widgets1['command'].text()

        #print("command = ", command)
        #ip, port = self.main_window.get_ip_port()

        command = add_tail(command)

        self.main_window.add_log(f"전송 >> {command}")
        #response = send_command(command, ip, port)
        response = self.main_window.send_command_unified( command )
        self.main_window.add_log(f"응답 << {response}")



    def set_input_box( self, box_name, value, widget_id ):
        widget_id[box_name].setText( value )


