from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea,
    QHBoxLayout, QGroupBox
)
from PyQt6.QtCore import Qt
from communication import *
from utils import *
import protocol as ptcl


class SignalTab(QWidget):
    def __init__(self, parent):
        """
            'Signal' 탭의 UI와 기능을 모두 담고 있는 클래스입니다.
            parent 인자로는 MainWindow의 인스턴스(self)가 전달됩니다.
        """

        super().__init__()
        self.main_window = parent

        main_layout = QVBoxLayout(self)

        # Signal Get All
        get_all_layout = QHBoxLayout()
        self.get_all_btn = QPushButton("GET ALL")
        get_all_layout.addWidget(QLabel("Signal All"))
        get_all_layout.addWidget(self.get_all_btn)
        get_all_layout.addStretch(1)
        main_layout.addLayout(get_all_layout)


        scroll = QScrollArea()
        scroll.setWidgetResizable( True )

        content= QWidget(self)
        content_layout = QVBoxLayout(content)

        layout1_config = [
                {'type': 'input_pair', 'label':'Angle Calibration:', 'name':'angle'},
                {'type': 'input_pair', 'label':'Percentage:',        'name':'percent'},
                {'type': 'button', 'text':'SET',    'name':'set_btn'},
                {'type': 'button', 'text':'GET',    'name':'get_btn'},
        ]
        group1, self.widgets1 = create_dynamic_group('Angle Calibration (cmd=d)', layout1_config, input_width=100)

        layout2_config = [
                {'type': 'input_pair', 'label':'Distance:', 'name':'distance'},
                {'type': 'input_pair', 'label':'Angle:',    'name':'angle'},
                {'type': 'button', 'text':'SET',    'name':'set_btn'},
                {'type': 'button', 'text':'GET',    'name':'get_btn'},
        ]
        group2, self.widgets2 = create_dynamic_group('Retry Sensing (cmd=e)', layout2_config, input_width=100)


        layout3_config = [
                {'type': 'combo_box',  'label':'Relay1:', 'name':'relay1', 'option':['-','Off','On']},
                {'type': 'input_pair', 'label':'Timer1:', 'name':'timer1'},
                {'type': 'combo_box',  'label':'Relay2:', 'name':'relay2', 'option':['-','Off','On']},
                {'type': 'input_pair', 'label':'Timer2:', 'name':'timer2'},
                {'type': 'combo_box',  'label':'Relay3:', 'name':'relay3', 'option':['-','Off','On']},
                {'type': 'input_pair', 'label':'Timer3:', 'name':'timer3'},
                {'type': 'combo_box',  'label':'Relay4:', 'name':'relay4', 'option':['-','Off','On']},
                {'type': 'input_pair', 'label':'Timer4:', 'name':'timer4'},
                {'type': 'combo_box',  'label':'Relay5:', 'name':'relay5', 'option':['-','Off','On']},
                {'type': 'input_pair', 'label':'Timer5:', 'name':'timer5'},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group3, self.widgets3 = create_dynamic_group_grid_2xN('Signal Relay On/Off (cmd=hA)', layout3_config )

        layout4_config = [
                {'type': 'combo_box',  'label':'IN1:', 'name':'in1', 'option':['-','Off','On']},
                {'type': 'combo_box',  'label':'IN2:', 'name':'in2', 'option':['-','Off','On']},
                {'type': 'combo_box',  'label':'IN3:', 'name':'in3', 'option':['-','Off','On']},
                {'type': 'combo_box',  'label':'IN4:', 'name':'in4', 'option':['-','Off','On']},
                {'type': 'combo_box',  'label':'IN5:', 'name':'in5', 'option':['-','Off','On']},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group4, self.widgets4 = create_dynamic_group('Signal Input (cmd=hB)', layout4_config )

        layout5_config = [
                {'type': 'combo_box',  'label':'Remote Relay1:', 'name':'relay1', 'option':['-','Off','On']},
                {'type': 'input_pair', 'label':'Remote Timer1:', 'name':'timer1'},
                {'type': 'combo_box',  'label':'Remote Relay2:', 'name':'relay2', 'option':['-','Off','On']},
                {'type': 'input_pair', 'label':'Remote Timer2:', 'name':'timer2'},
                {'type': 'combo_box',  'label':'Remote Relay3:', 'name':'relay3', 'option':['-','Off','On']},
                {'type': 'input_pair', 'label':'Remote Timer3:', 'name':'timer3'},
                {'type': 'combo_box',  'label':'Remote Relay4:', 'name':'relay4', 'option':['-','Off','On']},
                {'type': 'input_pair', 'label':'Remote Timer4:', 'name':'timer4'},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group5, self.widgets5 = create_dynamic_group_grid_2xN('Remote Relay On/Off (cmd=hC)', layout5_config )

        layout6_config = [
                {'type': 'combo_box',  'label':'Voltage1:', 'name':'onoff1', 'option':['-','Off','On']},
                {'type': 'input_pair', 'label':'Value:',    'name':'voltage1'},
                {'type': 'combo_box',  'label':'Voltage2:', 'name':'onoff2', 'option':['-','Off','On']},
                {'type': 'input_pair', 'label':'Value:',    'name':'voltage2'},
                {'type': 'input_pair', 'label':'Meas1:', 'name':'meas1'},
                {'type': 'input_pair', 'label':'Meas2:', 'name':'meas2'},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group6, self.widgets6 = create_dynamic_group_grid_2xN('Power Supply (cmd=hD)', layout6_config )



        layout7_config = [
                {'type': 'input_pair', 'label':'LTE Delay Time:', 'name':'lte_delay_time'},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group7, self.widgets7 = create_dynamic_group('ETH Comm Other (cmd=f)', layout7_config )

        scroll.setWidget(content)


        content_layout.addWidget(group1)
        content_layout.addWidget(group2)
        content_layout.addWidget(group3)
        content_layout.addWidget(group4)
        content_layout.addWidget(group5)
        content_layout.addWidget(group6)
        content_layout.addWidget(group7)

        main_layout.addWidget(scroll)

        self.widgets1['get_btn'].clicked.connect( self.angle_calibration_get_btn )
        self.widgets1['set_btn'].clicked.connect( self.angle_calibration_set_btn )

        self.widgets2['get_btn'].clicked.connect( self.retry_sensing_get_btn )
        self.widgets2['set_btn'].clicked.connect( self.retry_sensing_set_btn )

        self.widgets3['get_btn'].clicked.connect( self.signal_relay_get_btn )
        self.widgets3['set_btn'].clicked.connect( self.signal_relay_set_btn )

        self.widgets4['get_btn'].clicked.connect( self.signal_input_get_btn )

        self.widgets5['get_btn'].clicked.connect( self.remote_relay_get_btn )
        self.widgets5['set_btn'].clicked.connect( self.remote_relay_set_btn )


        self.widgets6['get_btn'].clicked.connect( self.power_supply_get_btn )
        self.widgets6['set_btn'].clicked.connect( self.power_supply_set_btn )


        self.widgets7['get_btn'].clicked.connect( self.eth_comm_get_btn )
        self.widgets7['set_btn'].clicked.connect( self.eth_comm_set_btn )
        self.get_all_btn.clicked.connect( self.get_all_settings )

    def get_all_settings( self ):
        tasks = [
            ("Angle Calibration", self.angle_calibration_get_btn),
            ("Retry Sensing", self.retry_sensing_get_btn),
            ("Signal Relay", self.signal_relay_get_btn),
            ("Signal Input", self.signal_input_get_btn),
            ("Remote Relay", self.remote_relay_get_btn),
            ("Power Supply", self.power_supply_get_btn),
            ("ETH Comm", self.eth_comm_get_btn),
        ]
        for name, fn in tasks:
            try:
                fn()
            except Exception as e:
                self.main_window.add_log(f"전체 설정 불러오기 오류 ({name}): {e}")

    def eth_comm_set_btn( self ):
        try:
            data_str = str(extract_number_from_text(self.widgets7['lte_delay_time'].text())).zfill(3)
            #print("data= ", data_str)
            command, response = self.common_command( "W", "f", data_str )
            ans = trim_string( response, 3, 3 )
            self.set_input_box( "lte_delay_time", str(int(ans)) + " ms", self.widgets7 )
        except Exception as e:
            self.main_window.add_log(f"eth_comm_set_btn 오류: {e}")
            return


    def eth_comm_get_btn( self ):
        try:
            command, response = self.common_command( "R", "f" )
            ans = trim_string( response, 3, 3 )
            self.set_input_box( "lte_delay_time", str(int(ans)) + " ms", self.widgets7 )
        except Exception as e:
            self.main_window.add_log(f"eth_comm_get_btn 오류: {e}")
            return


    def power_supply_set_btn( self ):
        try:
            data_str  = str(self.widgets6['onoff1'].currentIndex() -1 )
            data_str += str(int(float(extract_number_from_text(self.widgets6['voltage1'].text()) )*10)).zfill(3)
            data_str += str(self.widgets6['onoff2'].currentIndex() -1 )
            data_str += str(int(float(extract_number_from_text(self.widgets6['voltage2'].text()) )*10)).zfill(3)
            #data_str += str(int(float(extract_number_from_text(self.widgets6['meas1'].text()) )*10)).zfill(3)
            #data_str += str(int(float(extract_number_from_text(self.widgets6['meas2'].text()) )*10)).zfill(3)

            #print("data = ", data_str)
            command, response = self.common_command( "W", "hD", data_str )

            if command == response :
                self.main_window.add_log("Signal Relay가 설정되었습니다.")
        except Exception as e:
            self.main_window.add_log(f"power_supply_set_btn 오류: {e}")
            return

    def power_supply_get_btn( self ):
        try:
            command, response = self.common_command( "R", "hD" )

            ans = trim_string( response, 4, 3 )

            #print("ans = ", ans)
            return_tuple = parse_by_lengths( ans, "131333" )
            #print("retun_tuple = ", return_tuple)

            #relay_name = ["onoff1", "voltage1","onoff2", "voltage2", "meas1", "meas2"]

            self.set_combo_box( "onoff1", int(return_tuple[0])+1, self.widgets6 )

            temp = float(return_tuple[1])*0.1
            self.set_input_box( "voltage1", str(f"{temp:.1f}") + " V", self.widgets6 )

            self.set_combo_box( "onoff2", int(return_tuple[2])+1, self.widgets6 )

            temp = float(return_tuple[3])*0.1
            self.set_input_box( "voltage2", str(f"{temp:.1f}") + " V", self.widgets6 )

            temp = float(return_tuple[4])*0.1
            self.set_input_box( "meas1", str(f"{temp:.1f}") + " V", self.widgets6 )

            temp = float(return_tuple[4])*0.1
            self.set_input_box( "meas2", str(f"{temp:.1f}") + " V", self.widgets6 )
        except Exception as e:
            self.main_window.add_log(f"power_supply_get_btn 오류: {e}")
            return




    def remote_relay_set_btn( self ):
        try:
            data_str  = str(self.widgets5['relay1'].currentIndex() -1 )
            data_str += str(int(float(extract_number_from_text(self.widgets5['timer1'].text()) )*10)).zfill(4)
            data_str += str(self.widgets5['relay2'].currentIndex() -1 )
            data_str += str(int(float(extract_number_from_text(self.widgets5['timer2'].text()) )*10)).zfill(4)
            data_str += str(self.widgets5['relay3'].currentIndex() -1 )
            data_str += str(int(float(extract_number_from_text(self.widgets5['timer3'].text()) )*10)).zfill(4)
            data_str += str(self.widgets5['relay4'].currentIndex() -1 )
            data_str += str(int(float(extract_number_from_text(self.widgets5['timer4'].text()) )*10)).zfill(4)

            command, response = self.common_command( "W", "hC", data_str )

            if command == response :
                self.main_window.add_log("Signal Relay가 설정되었습니다.")
        except Exception as e:
            self.main_window.add_log(f"remote_relay_set_btn 오류: {e}")
            return


    def remote_relay_get_btn( self ):
        try:
            command, response = self.common_command( "R", "hC" )

            ans = trim_string( response, 4, 3 )

            #print("ans = ", ans)
            return_tuple = parse_by_lengths( ans, "14141414" )
            if return_tuple is None:
                self.main_window.add_log("데이터 파싱 실패: 응답 형식이 올바르지 않습니다.")
                return
            #print("retun_tuple = ", return_tuple)

            relay_name = ["relay1", "timer1","relay2", "timer2", "relay3", "timer3","relay4","timer4"]
            for i in range(8):
                if  i % 2 ==0 :
                    #print("retun_tuple[i] = ", return_tuple[i])
                    self.set_combo_box( relay_name[i], int(return_tuple[i])+1, self.widgets5 )
                else:
                    temp = float(return_tuple[i])*0.1
                    self.set_input_box( relay_name[i], str(f"{temp:.1f}") + " 초", self.widgets5 )
        except Exception as e:
            self.main_window.add_log(f"remote_relay_get_btn 오류: {e}")
            return





    def signal_input_get_btn( self ):
        try:
            command, response = self.common_command( "R", "hB" )

            ans = trim_string( response, 4, 3 )

            return_tuple = parse_by_lengths( ans, "11111" )
            if return_tuple is None:
                self.main_window.add_log("데이터 파싱 실패: 응답 형식이 올바르지 않습니다.")
                return

            relay_name = ["in1", "in2", "in3", "in4", "in5" ]
            i= 0
            for val in return_tuple :
                self.set_combo_box( relay_name[i], int(val)+1, self.widgets4 )
                i = i+1
        except Exception as e:
            self.main_window.add_log(f"signal_input_get_btn 오류: {e}")
            return



    def signal_relay_set_btn( self ):
        try:
            data_str  = str(self.widgets3['relay1'].currentIndex() -1 )
            data_str += str(int(float(extract_number_from_text(self.widgets3['timer1'].text() ))*10)).zfill(4)
            #print("1 =", data_str)
            data_str += str(self.widgets3['relay2'].currentIndex() -1 )
            data_str += str(int(float(extract_number_from_text(self.widgets3['timer2'].text() ))*10)).zfill(4)
            #print("2 =", data_str)
            data_str += str(self.widgets3['relay3'].currentIndex() -1 )
            data_str += str(int(float(extract_number_from_text(self.widgets3['timer3'].text() ))*10)).zfill(4)
            #print("3 =", data_str)
            data_str += str(self.widgets3['relay4'].currentIndex() -1 )
            data_str += str(int(float(extract_number_from_text(self.widgets3['timer4'].text() ))*10)).zfill(4)
            #print("4 =", data_str)
            data_str += str(self.widgets3['relay5'].currentIndex() -1 )
            data_str += str(int(float(extract_number_from_text(self.widgets3['timer5'].text() ))*10)).zfill(4)
            #print("5 =", data_str)

            command, response = self.common_command( "W", "hA", data_str )

            if command == response :
                self.main_window.add_log("Signal Relay가 설정되었습니다.")
        except Exception as e:
            self.main_window.add_log(f"signal_relay_set_btn 오류: {e}")
            return





    #widgets3
    def signal_relay_get_btn( self ):
        command, response = self.common_command( "R", "hA" )

        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return

        ans = trim_string( response, 4, 3 )

        #print("ans = ", ans)
        return_tuple = parse_by_lengths( ans, "1414141414" )
        if return_tuple is None:
            self.main_window.add_log("데이터 파싱 실패: 응답 형식이 올바르지 않습니다.")
            return

        relay_name = ["relay1", "timer1","relay2", "timer2", "relay3", "timer3","relay4","timer4","relay5","timer5"]
        for i in range(10):
            if  i % 2 ==0 :
                self.set_combo_box( relay_name[i], int(return_tuple[i])+1, self.widgets3 )
            else:
                #print("i = ",return_tuple[i])
                temp = int(return_tuple[i])*0.1
                self.set_input_box( relay_name[i], str(f"{temp:.1f}")+" 초", self.widgets3 )




    def retry_sensing_set_btn( self ):
        try:
            data_str  = str(int(float(extract_number_from_text(self.widgets2['distance'].text()   ))*100 )).zfill(4)
            data_str += str(int(float(extract_number_from_text(self.widgets2['angle'].text() ))*1000)).zfill(4)

            command, response = self.common_command( "W", "e", data_str )

            if command == response :
                self.main_window.add_log("Retry Sensing이 설정되었습니다.")
        except Exception as e:
            self.main_window.add_log(f"retry_sensing_set_btn 오류: {e}")
            return


    def retry_sensing_get_btn( self ):
        try:
            command, response = self.common_command( "R", "e" )

            ans = trim_string( response, 3, 3 )

            return_tuple = parse_by_lengths( ans, "44" )
            if return_tuple is None:
                self.main_window.add_log("데이터 파싱 실패: 응답 형식이 올바르지 않습니다.")
                return

            temp1 = float(return_tuple[0])*0.01
            temp2 = float(return_tuple[1])*0.001
            width_value1 = f"{temp1:.2f}"
            width_value2 = f"{temp2:.3f}"

            self.set_input_box( "distance", str( width_value1 )+" mm", self.widgets2 )
            self.set_input_box( "angle",    str( width_value2 )+" 도", self.widgets2 )
        except Exception as e:
            self.main_window.add_log(f"retry_sensing_get_btn 오류: {e}")
            return






    def angle_calibration_get_btn( self ):
        try:
            command, response = self.common_command( "R", "d" )

            ans = trim_string( response, 3, 3 )

            return_tuple = parse_by_lengths( ans, "43" )
            if return_tuple is None:
                self.main_window.add_log("데이터 파싱 실패: 응답 형식이 올바르지 않습니다.")
                return

            temp = float(return_tuple[0])*0.001
            width_value = f"{temp:.3f}"
            percent_value = int( return_tuple[1] )

            self.set_input_box( "angle", str( width_value )+" 도", self.widgets1 )
            self.set_input_box( "percent", str( percent_value )+" %", self.widgets1 )
        except Exception as e:
            self.main_window.add_log(f"angle_calibration_get_btn 오류: {e}")
            return


    def angle_calibration_set_btn( self ):
        try:
            #data_str  = self.widgets1['anlge'].text().zfill(4)
            #data_str += self.widgets1['percent'].text().zfill(3)

            data_str = int(float(extract_number_from_text(self.widgets1['angle'].text() ))*1000)
            data_str = str(data_str).zfill(4)
            data_str += str(extract_number_from_text(self.widgets1['percent'].text() )).zfill(3)
            #print("data+sta = ", data_str)
            #data_str  = str(extract_number_from_text(self.widgets1['angle'].text()   )*1000).zfill(4)
            #data_str += str(extract_number_from_text(self.widgets1['percent'].text() )).zfill(3)

            #print("data+sta = ", data_str)
            command, response = self.common_command( "W", "d", data_str )

            if command == response :
                self.main_window.add_log("Angle Calibration이 설정되었습니다.")
        except Exception as e:
            self.main_window.add_log(f"angle_calibration_set_btn 오류: {e}")
            return



    def test_sd_card_test_btn( self ):
        command, response = self.common_command( "W", "c" )

        ans = trim_string( response, 3, 3 )
        return_tuple = parse_by_lengths( ans, "12" )

        if return_tuple[0] == '0' : self.set_input_box( "result", "OK(성공)", self.widgets3 )
        if return_tuple[0] == '1' : self.set_input_box( "result", "NG(실패)", self.widgets3 )
        if return_tuple[0] == '2' : self.set_input_box( "result", "Empty(SD card 없음)", self.widgets3 )

        if return_tuple[1] == "00" : self.set_input_box( "error", "FR_OK", self.widgets3 )
        if return_tuple[1] == "01" : self.set_input_box( "error", "FR_DISK_ERR", self.widgets3 )
        if return_tuple[1] == "02" : self.set_input_box( "error", "FR_INT_ERR", self.widgets3 )
        if return_tuple[1] == "03" : self.set_input_box( "error", "FR_NOT_READY", self.widgets3 )
        if return_tuple[1] == "04" : self.set_input_box( "error", "FR_NO_FILE", self.widgets3 )
        if return_tuple[1] == "05" : self.set_input_box( "error", "FR_NO_PATH", self.widgets3 )
        if return_tuple[1] == "06" : self.set_input_box( "error", "FR_INVAID_NAME", self.widgets3 )
        if return_tuple[1] == "07" : self.set_input_box( "error", "FR_DENIED", self.widgets3 )
        if return_tuple[1] == "08" : self.set_input_box( "error", "FR_EXIST", self.widgets3 )
        if return_tuple[1] == "09" : self.set_input_box( "error", "FR_INVALID_OBJECT", self.widgets3 )
        if return_tuple[1] == "10" : self.set_input_box( "error", "FR_WRITE_PROTECT", self.widgets3 )
        if return_tuple[1] == "11" : self.set_input_box( "error", "FR_INVALID_DRIVE", self.widgets3 )
        if return_tuple[1] == "12" : self.set_input_box( "error", "FR_NOT_ENABLED", self.widgets3 )
        if return_tuple[1] == "13" : self.set_input_box( "error", "FR_NO_FILESYSTEM", self.widgets3 )
        if return_tuple[1] == "14" : self.set_input_box( "error", "FR_MKFS_ABORTED", self.widgets3 )
        if return_tuple[1] == "15" : self.set_input_box( "error", "FR_TIMEOUT", self.widgets3 )
        if return_tuple[1] == "16" : self.set_input_box( "error", "FR_LOCKED", self.widgets3 )
        if return_tuple[1] == "17" : self.set_input_box( "error", "FR_NOT_ENOUGH_CORE", self.widgets3 )
        if return_tuple[1] == "18" : self.set_input_box( "error", "FR_TOO_MANY_OPEN_FILES", self.widgets3 )
        if return_tuple[1] == "19" : self.set_input_box( "error", "FR_INVALID_PARAMETER", self.widgets3 )


    def sd_card_status_clear_btn( self ):
        command, response = self.common_command( "W", "b" )

        if command==response :
            self.main_window.add_log("SD Card Status를 모두 삭제했습니다.")


    def sd_card_status_get_btn( self ):
        command, response = self.common_command( "R", "b" )

        ans = trim_string( response, 3, 3 )
        return_tuple = parse_by_lengths( ans, "117772" )

        #print(return_tuple)

        if return_tuple[0]=='0' : 
            self.set_input_box( "status", "Ready", self.widgets2 )
        elif return_tuple[0]=='1' : 
            self.set_input_box( "status", "Busy", self.widgets2 )
        elif return_tuple[0]=='2' : 
            self.set_input_box( "status", "Empty", self.widgets2 )

        if return_tuple[1]=='0' : 
            self.set_input_box( "onoff", "OFF", self.widgets2 )
        else :
            self.set_input_box( "onoff", "ON", self.widgets2 )

        self.set_input_box( "total_count", str(int(return_tuple[2])), self.widgets2 )
        self.set_input_box( "good_count", str(int(return_tuple[3])), self.widgets2 )
        self.set_input_box( "error_count", str(int(return_tuple[4])), self.widgets2 )


        if return_tuple[5] == "00" : self.set_input_box( "error_code", "FR_OK", self.widgets2 )
        if return_tuple[5] == "01" : self.set_input_box( "error_code", "FR_DISK_ERR", self.widgets2 )
        if return_tuple[5] == "02" : self.set_input_box( "error_code", "FR_INT_ERR", self.widgets2 )
        if return_tuple[5] == "03" : self.set_input_box( "error_code", "FR_NOT_READY", self.widgets2 )
        if return_tuple[5] == "04" : self.set_input_box( "error_code", "FR_NO_FILE", self.widgets2 )
        if return_tuple[5] == "05" : self.set_input_box( "error_code", "FR_NO_PATH", self.widgets2 )
        if return_tuple[5] == "06" : self.set_input_box( "error_code", "FR_INVAID_NAME", self.widgets2 )
        if return_tuple[5] == "07" : self.set_input_box( "error_code", "FR_DENIED", self.widgets2 )
        if return_tuple[5] == "08" : self.set_input_box( "error_code", "FR_EXIST", self.widgets2 )
        if return_tuple[5] == "09" : self.set_input_box( "error_code", "FR_INVALID_OBJECT", self.widgets2 )
        if return_tuple[5] == "10" : self.set_input_box( "error_code", "FR_WRITE_PROTECT", self.widgets2 )
        if return_tuple[5] == "11" : self.set_input_box( "error_code", "FR_INVALID_DRIVE", self.widgets2 )
        if return_tuple[5] == "12" : self.set_input_box( "error_code", "FR_NOT_ENABLED", self.widgets2 )
        if return_tuple[5] == "13" : self.set_input_box( "error_code", "FR_NO_FILESYSTEM", self.widgets2 )
        if return_tuple[5] == "14" : self.set_input_box( "error_code", "FR_MKFS_ABORTED", self.widgets2 )
        if return_tuple[5] == "15" : self.set_input_box( "error_code", "FR_TIMEOUT", self.widgets2 )
        if return_tuple[5] == "16" : self.set_input_box( "error_code", "FR_LOCKED", self.widgets2 )
        if return_tuple[5] == "17" : self.set_input_box( "error_code", "FR_NOT_ENOUGH_CORE", self.widgets2 )
        if return_tuple[5] == "18" : self.set_input_box( "error_code", "FR_TOO_MANY_OPEN_FILES", self.widgets2 )
        if return_tuple[5] == "19" : self.set_input_box( "error_code", "FR_INVALID_PARAMETER", self.widgets2 )



    def reconnection_set_btn( self ):
        data_str = str(self.widgets5['reconnection'].currentIndex()-1)
        data_str += str(extract_number_from_text(self.widgets5['box1'].text())).zfill(3)
        data_str += str(extract_number_from_text(self.widgets5['box2'].text())).zfill(3)

        #print(data_str)

        command, response = self.common_command( "W", "3", data_str )




    def reconnection_get_btn( self ):
        command, response = self.common_command( "R", "3" )

        ans = trim_string( response, 3, 3 )
        return_tuple = parse_by_lengths( ans, "133" )

        self.set_combo_box( 'reconnection', int(return_tuple[0])+1, self.widgets5 )
        self.set_input_box( 'box1', str(int(return_tuple[1]))+' 초', self.widgets5 )
        self.set_input_box( 'box2', str(int(return_tuple[2]))+' 초', self.widgets5 )
        
        

    def voltage_of_lines( self ):
        command, response = self.common_command( "R", "1" )

        ans = trim_string( response, 3, 3 )

        return_tuple = parse_by_lengths( ans, "4444444444" )

        box_names = ['vin_ac','vin_dc','line1_in','line1_out','line2_in','line2_out','line3_in','line3_out', 'line4_in', 'line4_out']

        for i in range (10):
            #print(return_tuple[i])
            ss = "{:.2f}".format(float(return_tuple[i])*0.01)
            self.widgets4[box_names[i]].setText( ss+" V" )


    def temperature_get_btn( self ):
        command, response = self.common_command( "R", "0" )
        ans = trim_string( response, 3, 3 )
        #self.widgets1['auto_id'].setCurrentIndex( int(ans)+1 )
        ans = float(ans)/10.
        
        self.set_input_box( 'temperature', str(ans).zfill(1)+" 도", self.widgets3 )


    def clear_alarm_set_btn( self ):
        command, response = self.common_command( "W", "Z" )

        if command == response :
            self.set_combo_box( 'alarm', 1, self.widgets2 ) 






    def sd_card_set_btn( self ):
        data_str = str(self.widgets1['sd_card'].currentIndex()-1)
        command, response = self.common_command( "W", "9", data_str )


    def sd_card_del_btn( self ):
        command, response = self.common_command( "W", "a" )

        if command == response :
            self.main_window.add_log("SD Card의 모든 내용을 지웠습니다.")



    def sd_card_get_btn( self ):
        command, response = self.common_command( "R", "9" )
        ans = trim_string( response, 3, 3 )
        #self.widgets1['auto_id'].setCurrentIndex( int(ans)+1 )
        self.set_combo_box( 'sd_card', int(ans)+1, self.widgets1 )






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
