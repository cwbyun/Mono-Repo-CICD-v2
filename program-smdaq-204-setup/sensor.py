from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QGroupBox
)
from PyQt6.QtCore import Qt
from communication import *
from utils import *
import protocol as ptcl


class SensorTab(QWidget):
    def __init__(self, parent):
        """
            'Sensor' 탭의 UI와 기능을 모두 담고 있는 클래스입니다.
            parent 인자로는 MainWindow의 인스턴스(self)가 전달됩니다.
        """

        super().__init__()
        self.main_window = parent

        main_layout = QVBoxLayout(self)

        # Sensor Get All
        get_all_layout = QHBoxLayout()
        self.get_all_btn = QPushButton("GET ALL")
        get_all_layout.addWidget(QLabel("Sensor All"))
        get_all_layout.addWidget(self.get_all_btn)
        get_all_layout.addStretch(1)
        main_layout.addLayout(get_all_layout)

        layout1_config = [
                {'type': 'combo_box',  'label':'Auto ID Status:', 'name':'auto_id','option':['-','Ready','Run','Complete']},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group1, self.widgets1 = create_dynamic_group('Auto ID Progress (cmd=U)', layout1_config, input_width=100)



        layout2_config = [
                {'type': 'combo_box',  'label':'Clear Alarm:', 'name':'alarm','option':['-','Cleared']},
                {'type': 'button', 'text':'Clear Alarm', 'name':'set_btn'},
        ]
        group2, self.widgets2 = create_dynamic_group('Clear Alarm (cmd=Z)', layout2_config )

        layout3_config = [
                {'type': 'input_pair', 'label':'Temperature:',    'name':'temperature'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group3, self.widgets3 = create_dynamic_group('Temperature (cmd=0)', layout3_config )
        

        layout4_config = [
                {'type': 'input_pair', 'label':'Vin AC:', 'name':'vin_ac'},
                {'type': 'input_pair', 'label':'Vin DC:', 'name':'vin_dc'},
                {'type': 'input_pair', 'label':'Line1 IN:',  'name':'line1_in'},
                {'type': 'input_pair', 'label':'Line1 OUT:', 'name':'line1_out'},
                {'type': 'input_pair', 'label':'Line2 IN:',  'name':'line2_in'},
                {'type': 'input_pair', 'label':'Line2 OUT:', 'name':'line2_out'},
                {'type': 'input_pair', 'label':'Line3 IN:',  'name':'line3_in'},
                {'type': 'input_pair', 'label':'Line3 OUT:', 'name':'line3_out'},
                {'type': 'input_pair', 'label':'Line4 IN:',  'name':'line4_in'},
                {'type': 'input_pair', 'label':'Line4 OUT:', 'name':'line4_out'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group4, self.widgets4 = create_dynamic_group_grid_2xN('Voltage of Lines (cmd=1)', layout4_config, read_only=True )





        layout5_config = [
                {'type': 'combo_box',  'label':'Reconnection:', 'name':'reconnection','option':['-','Off','On']},
                {'type': 'input_pair', 'label':'첫 번째:', 'name':'box1'},
                {'type': 'input_pair', 'label':'첫 번째:', 'name':'box2'},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group5, self.widgets5 = create_dynamic_group('Reconnection (cmd=3)', layout5_config )



        main_layout.addWidget(group1)
        main_layout.addWidget(group2)
        main_layout.addWidget(group3)
        main_layout.addWidget(group4)
        main_layout.addWidget(group5)

        main_layout.addStretch(1)

        self.widgets1['get_btn'].clicked.connect( self.auto_id_get_btn )
        self.widgets2['set_btn'].clicked.connect( self.clear_alarm_set_btn )
        self.widgets3['get_btn'].clicked.connect( self.temperature_get_btn )
        self.widgets4['get_btn'].clicked.connect( self.voltage_of_lines )
        self.widgets5['set_btn'].clicked.connect( self.reconnection_set_btn )
        self.widgets5['get_btn'].clicked.connect( self.reconnection_get_btn )
        self.get_all_btn.clicked.connect( self.get_all_settings )






    def get_all_settings( self ):
        tasks = [
            ("Auto ID", self.auto_id_get_btn),
            ("Temperature", self.temperature_get_btn),
            ("Voltage of Lines", self.voltage_of_lines),
            ("Reconnection", self.reconnection_get_btn),
        ]
        for name, fn in tasks:
            try:
                fn()
            except Exception as e:
                self.main_window.add_log(f"전체 설정 불러오기 오류 ({name}): {e}")

    def reconnection_set_btn( self ):
        try:
            data_str = str(self.widgets5['reconnection'].currentIndex()-1)
            data_str += str(extract_number_from_text(self.widgets5['box1'].text())).zfill(3)
            data_str += str(extract_number_from_text(self.widgets5['box2'].text())).zfill(3)

            print(data_str)

            command, response = self.common_command( "W", "3", data_str )
        except Exception as e:
            self.main_window.add_log(f"reconnection_set_btn 오류: {e}")
            return




    def reconnection_get_btn( self ):
        command, response = self.common_command( "R", "3" )

        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return

        ans = trim_string( response, 3, 3 )
        return_tuple = parse_by_lengths( ans, "133" )

        self.set_combo_box( 'reconnection', int(return_tuple[0])+1, self.widgets5 )
        self.set_input_box( 'box1', str(int(return_tuple[1]))+' 초', self.widgets5 )
        self.set_input_box( 'box2', str(int(return_tuple[2]))+' 초', self.widgets5 )
        
        

    def voltage_of_lines( self ):
        command, response = self.common_command( "R", "1" )

        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return


        ans = trim_string( response, 3, 3 )

        return_tuple = parse_by_lengths( ans, "4444444444" )
        if not return_tuple:
            self.main_window.add_log("Voltage of Lines 응답 파싱 실패: 형식 오류")
            return

        box_names = ['vin_ac','vin_dc','line1_in','line1_out','line2_in','line2_out','line3_in','line3_out', 'line4_in', 'line4_out']

        try:
            for i in range (10):
                #print(return_tuple[i])
                ss = "{:.2f}".format(float(return_tuple[i])*0.01)
                self.widgets4[box_names[i]].setText( ss+" V" )
        except Exception as e:
            self.main_window.add_log(f"Voltage of Lines 응답 처리 오류: {e}")
            return


    def temperature_get_btn( self ):
        command, response = self.common_command( "R", "0" )
        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return
        ans = trim_string( response, 3, 3 )
        pm = ans[0]
        #self.widgets1['auto_id'].setCurrentIndex( int(ans)+1 )
        print("pm in sensor = ", pm)

        if pm=='-':
            fans = -float(ans)
        else:
            fans = float(ans)

        if abs(fans)>100:
            ans = fans/10.
        else:
            ans = fans
        
        self.set_input_box( 'temperature', str(ans).zfill(1)+" 도", self.widgets3 )


    def clear_alarm_set_btn( self ):
        command, response = self.common_command( "W", "Z" )
        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return

        if command == response :
            self.set_combo_box( 'alarm', 1, self.widgets2 ) 

    def auto_id_get_btn( self ):
        command, response = self.common_command( "R", "U" )

        #print("res = ", response )
        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return

        ans = trim_string( response, 3, 3 )

        print("ans = ", ans )
        #self.widgets1['auto_id'].setCurrentIndex( int(ans)+1 )
        self.set_combo_box( 'auto_id', int(ans)+1, self.widgets1 )


    def set_input_box( self, box_name, value, widget_id ):
        widget_id[box_name].setText( value )

    def set_combo_box( self, box_name, value, widget_id ):
        widget_id[box_name].setCurrentIndex( value )


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
