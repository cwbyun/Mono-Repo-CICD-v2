from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea,
    QHBoxLayout, QGroupBox
)
from PyQt6.QtCore import Qt
from communication import *
from utils import *
import protocol as ptcl


class OptionTab(QWidget):
    def __init__(self, parent):
        """
            'Option' 탭의 UI와 기능을 모두 담고 있는 클래스입니다.
            parent 인자로는 MainWindow의 인스턴스(self)가 전달됩니다.
        """

        super().__init__()
        self.main_window = parent

        main_layout = QVBoxLayout(self)

        # Option Get All
        get_all_layout = QHBoxLayout()
        self.get_all_btn = QPushButton("GET ALL")
        get_all_layout.addWidget(QLabel("Option All"))
        get_all_layout.addWidget(self.get_all_btn)
        get_all_layout.addStretch(1)
        main_layout.addLayout(get_all_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)


        content = QWidget(self)
        content_layout = QVBoxLayout( content )

        layout1_config = [
                {'type': 'combo_box',  'label':'Warning:', 'name':'warning','option':['-','Off','On']},
                {'type': 'input_pair', 'label':'Timer:',   'name':'timer'},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group1, self.widgets1 = create_dynamic_group('Warning (cmd=O)', layout1_config, input_width=100)



        layout2_config = [
                {'type': 'combo_box',  'label':'Reset:', 'name':'reset','option':['-','Off','On']},
                {'type': 'input_pair', 'label':'시간:',  'name':'hour'},
                {'type': 'input_pair', 'label':'분:',    'name':'min'},
                {'type': 'input_pair', 'label':'초:',    'name':'sec'},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group2, self.widgets2 = create_dynamic_group('ETH Reset (cmd=Y)', layout2_config )

        layout3_config = [
                {'type': 'combo_box',  'label':'Reset:', 'name':'reset','option':['-','Off','On']},
                {'type': 'input_pair', 'label':'시간:',  'name':'hour'},
                {'type': 'input_pair', 'label':'분:',    'name':'min'},
                {'type': 'input_pair', 'label':'초:',    'name':'sec'},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group3, self.widgets3 = create_dynamic_group('Micom Reset (cmd=J)', layout3_config )
        
        layout4_config = [
                {'type': 'combo_box',  'label':'COMM LED:', 'name':'led','option':['-','Off','On']},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group4, self.widgets4 = create_dynamic_group('Comm LED Control (cmd=K)', layout4_config )


        layout5_config = [
                {'type': 'combo_box',  'label':'LED On/Off:', 'name':'led','option':['-','Off','On']},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
        ]
        group5, self.widgets5 = create_dynamic_group('LED On/Off (cmd=X)', layout5_config )

        layout6_config = [
                {'type': 'combo_box',  'label':'Buzzer:', 'name':'buzzer','option':['-','Off','On']},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group6, self.widgets6 = create_dynamic_group('Buzzer (cmd=W)', layout6_config )

        layout7_config = [
                {'type': 'combo_box',  'label':'UPS On/Off:', 'name':'ups','option':['-','Off','On']},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group7, self.widgets7 = create_dynamic_group('UPS On/Off (cmd=i)', layout7_config )


        layout8_config = [
                {'type': 'combo_box',  'label':'LCD Auto Off:',    'name':'lcd','option':['-','Off','On']},
                {'type': 'input_pair', 'label':'Auto Off Timmer:', 'name':'timer'},
                {'type': 'input_pair', 'label':'밝기:',            'name':'percent'},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group8, self.widgets8 = create_dynamic_group('LCD On/Off (cmd=j)', layout8_config )

        scroll.setWidget( content )

        content_layout.addWidget( group1 )
        content_layout.addWidget( group2 )
        content_layout.addWidget( group3 )
        content_layout.addWidget( group4 )
        content_layout.addWidget( group5 )
        content_layout.addWidget( group6 )
        content_layout.addWidget( group7 )
        content_layout.addWidget( group8 )


        #main_layout.addWidget(group1)
        #main_layout.addWidget(group2)
        #main_layout.addWidget(group3)
        #main_layout.addWidget(group4)
        #main_layout.addWidget(group5)
        #main_layout.addWidget(group6)
        #main_layout.addWidget(group7)
        #main_layout.addWidget(group8)
        main_layout.addWidget(scroll)

        self.widgets1['get_btn'].clicked.connect( self.warning_get_btn )
        self.widgets1['set_btn'].clicked.connect( self.warning_set_btn )


        self.widgets2['get_btn'].clicked.connect( self.eth_reset_get_btn )
        self.widgets2['set_btn'].clicked.connect( self.eth_reset_set_btn )

        self.widgets3['get_btn'].clicked.connect( self.micom_reset_get_btn )
        self.widgets3['set_btn'].clicked.connect( self.micom_reset_set_btn )

        self.widgets4['get_btn'].clicked.connect( self.comm_led_get_btn )
        self.widgets4['set_btn'].clicked.connect( self.comm_led_set_btn )

        #self.widgets5['get_btn'].clicked.connect( self.led_control_get_btn )
        self.widgets5['set_btn'].clicked.connect( self.led_control_set_btn )

        self.widgets6['get_btn'].clicked.connect( self.buzzer_get_btn )
        self.widgets6['set_btn'].clicked.connect( self.buzzer_set_btn )

        self.widgets7['get_btn'].clicked.connect( self.ups_get_btn )
        self.widgets7['set_btn'].clicked.connect( self.ups_set_btn )

        self.widgets8['get_btn'].clicked.connect( self.lcd_get_btn )
        self.widgets8['set_btn'].clicked.connect( self.lcd_set_btn )
        self.get_all_btn.clicked.connect( self.get_all_settings )





    def get_all_settings( self ):
        tasks = [
            ("Warning", self.warning_get_btn),
            ("ETH Reset", self.eth_reset_get_btn),
            ("Micom Reset", self.micom_reset_get_btn),
            ("Comm LED", self.comm_led_get_btn),
            ("Buzzer", self.buzzer_get_btn),
            ("UPS", self.ups_get_btn),
            ("LCD", self.lcd_get_btn),
        ]
        for name, fn in tasks:
            try:
                fn()
            except Exception as e:
                self.main_window.add_log(f"전체 설정 불러오기 오류 ({name}): {e}")

    def lcd_set_btn( self ):
        try:
            data_str = str( self.widgets8['lcd'].currentIndex()-1 )
            data_str += str(extract_number_from_text(self.widgets8['timer'].text())).zfill(2)
            data_str += str(extract_number_from_text(self.widgets8['percent'].text())).zfill(3)
            command, response = self.common_command( "W", "j", data_str )
        except Exception as e:
            self.main_window.add_log(f"lcd_set_btn 오류: {e}")
            return



    def lcd_get_btn( self ):
        command, response = self.common_command( "R", "j" )

        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return

        ans = trim_string( response, 3, 3 )

        return_tuple = parse_by_lengths( ans, "123" )

        self.widgets8['lcd'].setCurrentIndex(int(return_tuple[0])+1)

        self.widgets8['timer'].setText(str(int(return_tuple[1]))+" 분")
        self.widgets8['percent'].setText(str(int(return_tuple[2]))+" %")




    def ups_set_btn( self ):
        try:
            data_str = str( self.widgets7['ups'].currentIndex()-1 )
            command, response = self.common_command( "W", "i", data_str )
        except Exception as e:
            self.main_window.add_log(f"ups_set_btn 오류: {e}")
            return

    def ups_get_btn( self ):
        command, response = self.common_command( "R", "i" )

        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return


        ans = trim_string( response, 3, 3 )
        self.widgets7['ups'].setCurrentIndex(int(ans)+1)



    def buzzer_set_btn( self ):
        try:
            data_str = str( self.widgets6['buzzer'].currentIndex()-1 )
            command, response = self.common_command( "W", "W", data_str )
        except Exception as e:
            self.main_window.add_log(f"buzzer_set_btn 오류: {e}")
            return

    def buzzer_get_btn( self ):
        command, response = self.common_command( "R", "W" )

        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return


        ans = trim_string( response, 3, 3 )
        self.widgets6['buzzer'].setCurrentIndex(int(ans)+1)


    def led_control_set_btn( self ):
        try:
            data_str = str( self.widgets5['led'].currentIndex()-1 )
            command, response = self.common_command( "W", "X", data_str )
        except Exception as e:
            self.main_window.add_log(f"led_control_set_btn 오류: {e}")
            return

    def led_control_get_btn( self ):
        command, response = self.common_command( "R", "X" )

        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return

        ans = trim_string( response, 3, 3 )
        print("ans = ", ans)
        self.widgets5['led'].setCurrentIndex(int(ans)+1)


    def comm_led_set_btn( self ):
        try:
            data_str = str( self.widgets4['led'].currentIndex()-1 )
            command, response = self.common_command( "W", "K", data_str )
        except Exception as e:
            self.main_window.add_log(f"comm_led_set_btn 오류: {e}")
            return

    def comm_led_get_btn( self ):
        command, response = self.common_command( "R", "K" )

        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return

        ans = trim_string( response, 3, 3 )
        self.widgets4['led'].setCurrentIndex(int(ans)+1)



    def micom_reset_set_btn( self ):
        try:
            data_str = str( self.widgets3['reset'].currentIndex()-1 )
            data_str += str( int(self.widgets3['hour'].text() )).zfill(2) 
            data_str += str( int(self.widgets3['min'].text() )).zfill(2) 
            data_str += str( int(self.widgets3['sec'].text() )).zfill(2)
            command, response = self.common_command( "W", "J", data_str )
        except Exception as e:
            self.main_window.add_log(f"micom_reset_set_btn 오류: {e}")
            return

    def micom_reset_get_btn( self ):
        command, response = self.common_command( "R", "J" )

        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return

        ans = trim_string( response, 3, 3 )
        return_tuple = parse_by_lengths( ans, "1222" )
        self.widgets3['reset'].setCurrentIndex(int(return_tuple[0])+1)
        self.widgets3['hour'].setText(str(return_tuple[1]))
        self.widgets3['min'].setText(str(return_tuple[2]))
        self.widgets3['sec'].setText(str(return_tuple[3]))



    def eth_reset_set_btn( self ):
        try:
            data_str = str( self.widgets2['reset'].currentIndex()-1 )
            data_str += str( int(self.widgets2['hour'].text() )).zfill(2) 
            data_str += str( int(self.widgets2['min'].text() )).zfill(2) 
            data_str += str( int(self.widgets2['sec'].text() )).zfill(2)

            command, response = self.common_command( "W", "Y", data_str )
        except Exception as e:
            self.main_window.add_log(f"eth_reset_set_btn 오류: {e}")
            return



    def eth_reset_get_btn( self ):

        command, response = self.common_command( "R", "Y" )
        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return

        ans = trim_string( response, 3, 3 )

        return_tuple = parse_by_lengths( ans, "1222" )

        self.widgets2['reset'].setCurrentIndex(int(return_tuple[0])+1)
        self.widgets2['hour'].setText(str(return_tuple[1]))
        self.widgets2['min'].setText(str(return_tuple[2]))
        self.widgets2['sec'].setText(str(return_tuple[3]))





    def warning_set_btn( self ):
        try:
            data_str = str( self.widgets1['warning'].currentIndex()-1 )
            timer_val = int(float(extract_number_from_text(self.widgets1['timer'].text()))*10)
            data_str += str(timer_val).zfill(3)

            if not data_str:
                self.main_window.add_log(f"data string error: {data_str}")
                return

            command, response = self.common_command( "W", "O", data_str )
            
        except Exception as e:
            self.main_window.add_log(f"warning_set_btn 오류: {e}")
            return



    def warning_get_btn( self ):
        command, response = self.common_command( "R", "O" )

        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return

        ans = trim_string( response, 3, 3 )

        return_tuple = parse_by_lengths( ans, "13" )

        self.widgets1['warning'].setCurrentIndex(int(return_tuple[0])+1)
        t = float(return_tuple[1])*0.1
        st = f"{t:.1f}"
        self.widgets1['timer'].setText(st+" sec")



    def common_command( self, DIR, CMD, data_str=None ):
        if data_str :
            command = ptcl.STX + DIR + CMD + data_str
        else:
            command = ptcl.STX + DIR + CMD

        command = add_tail(command)

        self.main_window.add_log(f"전송 >> {command}")
        response = self.main_window.send_command_unified(command)
        print("command=",command)
        print("respond=",response)

        return command, response
