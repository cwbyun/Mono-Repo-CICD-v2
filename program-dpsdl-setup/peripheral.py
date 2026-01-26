
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QGroupBox
)
from PyQt6.QtCore import Qt
from communication import *
from utils import *
import protocol as ptcl


class PeripheralTab(QWidget):
    def __init__(self, parent):
        """
            'Peripheral' 탭의 UI와 기능을 모두 담고 있는 클래스입니다.
            parent 인자로는 MainWindow의 인스턴스(self)가 전달됩니다.
        """

        super().__init__()
        self.main_window = parent

        main_layout = QVBoxLayout(self)


        layout0_config = [
                {'type': 'combo_box',  'label':'Timeout:', 'name':'timeout','option':['-','Off','On']},
                {'type': 'input_pair', 'label':'Period Time:',      'name':'period'},
                {'type': 'button', 'text':'SET',    'name':'set_btn'},
                {'type': 'button', 'text':'GET',    'name':'get_btn'},
        ]
        group0, self.widgets0 = create_dynamic_group('Lan Inactivity Timeout (cmd=8)', layout0_config, input_width=100)



        layout1_config = [
                {'type': 'combo_box',  'label':'SD Card:', 'name':'sd_card','option':['-','Off','On']},
                {'type': 'button', 'text':'SET',    'name':'set_btn'},
                {'type': 'button', 'text':'GET',    'name':'get_btn'},
                {'type': 'button', 'text':'DELETE', 'name':'del_btn'},
        ]
        group1, self.widgets1 = create_dynamic_group('SD Card on/off (cmd=9)', layout1_config, input_width=100)



        layout2_config = [
                {'type': 'input_pair', 'label':'Status:',      'name':'status'},
                {'type': 'input_pair', 'label':'On/Off:',      'name':'onoff'},
                {'type': 'input_pair', 'label':'Total Count:', 'name':'total_count'},
                {'type': 'input_pair', 'label':'Good Count:',  'name':'good_count'},
                {'type': 'input_pair', 'label':'Error Count:', 'name':'error_count'},
                {'type': 'input_pair', 'label':'Error Code:',  'name':'error_code'},
                {'type': 'button', 'text':'GET',   'name':'get_btn'},
                {'type': 'button', 'text':'CLEAR', 'name':'clear_btn'},
        ]
        group2, self.widgets2 = create_dynamic_group_grid_2xN('SD Card Status (cmd=b)', layout2_config )


        layout3_config = [
                {'type': 'input_pair', 'label':'Result:', 'name':'result'},
                {'type': 'input_pair', 'label':'Error:',  'name':'error'},
                {'type': 'button', 'text':'TEST', 'name':'test_btn'},
        ]
        group3, self.widgets3 = create_dynamic_group('Test Write/Read SD Card (cmd=c)', layout3_config, input_width=150 )
        
        layout4_config = [
                {'type': 'label', 'text':'Clear SD Card:'},
                {'type': 'button', 'text':'Clear', 'name':'clr_btn'},
        ]
        group4, self.widgets4 = create_dynamic_group('Clear SD Status (cmd=b)', layout4_config, input_width=150 )


        main_layout.addWidget(group0)
        main_layout.addWidget(group1)
        main_layout.addWidget(group2)
        main_layout.addWidget(group3)
        main_layout.addWidget(group4)

        main_layout.addStretch(1)


        self.widgets0['get_btn'].clicked.connect( self.lan_inactivity_get_btn )
        self.widgets0['set_btn'].clicked.connect( self.lan_inactivity_set_btn )


        self.widgets1['get_btn'].clicked.connect( self.sd_card_get_btn )
        self.widgets1['set_btn'].clicked.connect( self.sd_card_set_btn )
        self.widgets1['del_btn'].clicked.connect( self.sd_card_del_btn )

        self.widgets2['get_btn'].clicked.connect( self.sd_card_status_get_btn )
        self.widgets2['clear_btn'].clicked.connect( self.sd_card_status_clear_btn )


        self.widgets3['test_btn'].clicked.connect( self.test_sd_card_test_btn )
        self.widgets4['clr_btn'].clicked.connect( self.clear_sd_card_clr_btn )


    def clear_sd_card_clr_btn( self ):
        try:
            command, response = self.common_command( "W", "b" )
            print("Cleared SD Card Status")
            
        except Exception as e :
            print(f"Clear SD Card Error : {e}")




    def lan_inactivity_set_btn( self ):
        try:
            data_str = str(self.get_combo_box( 'timeout', self.widgets0 )-1)
            data_str += str(extract_number_from_text( self.get_input_box( 'period', self.widgets0 ) )).zfill(4)

            command, response = self.common_command( "W", "8", data_str )


        except Exception as e:
            print(f"Set Lan Inactivity Error : {e}")


    def lan_inactivity_get_btn( self ):
        try:
            command, response = self.common_command( "R", "8" )

            ans = trim_string( response, 3, 3 )
            return_tuple = parse_by_lengths( ans, "14" )

            self.set_combo_box( 'timeout', int(return_tuple[0])+1, self.widgets0 )
            self.set_input_box( 'period', str(int(return_tuple[1]))+" 분", self.widgets0 )

        except Exception as e:
            print(f"Get Lan Inactivity Error : {e}")


    def test_sd_card_test_btn( self ):
        try:
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
        except Exception as e:
            self.main_window.add_log(f"test_sd_card_test_btn 오류: {e}")
            return


    def sd_card_status_clear_btn( self ):
        command, response = self.common_command( "W", "b" )

        if command==response :
            self.main_window.add_log("SD Card Status를 모두 삭제했습니다.")


    def sd_card_status_get_btn( self ):
        try:
            command, response = self.common_command( "R", "b" )

            ans = trim_string( response, 3, 3 )
            return_tuple = parse_by_lengths( ans, "117772" )

            print(return_tuple)

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
        except Exception as e:
            self.main_window.add_log(f"sd_card_status_get_btn 오류: {e}")
            return



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
        try:
            command, response = self.common_command( "R", "3" )

            ans = trim_string( response, 3, 3 )
            return_tuple = parse_by_lengths( ans, "133" )

            self.set_combo_box( 'reconnection', int(return_tuple[0])+1, self.widgets5 )
            self.set_input_box( 'box1', str(int(return_tuple[1]))+' 초', self.widgets5 )
            self.set_input_box( 'box2', str(int(return_tuple[2]))+' 초', self.widgets5 )
        except Exception as e:
            self.main_window.add_log(f"reconnection_get_btn 오류: {e}")
            return
        
        

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
        try:
            command, response = self.common_command( "R", "0" )
            ans = trim_string( response, 3, 3 )
            #self.widgets1['auto_id'].setCurrentIndex( int(ans)+1 )
            ans = float(ans)/10.
            
            self.set_input_box( 'temperature', str(ans).zfill(1)+" 도", self.widgets3 )
        except Exception as e:
            self.main_window.add_log(f"temperature_get_btn 오류: {e}")
            return


    def clear_alarm_set_btn( self ):
        try:
            command, response = self.common_command( "W", "Z" )

            if command == response :
                self.set_combo_box( 'alarm', 1, self.widgets2 )
        except Exception as e:
            self.main_window.add_log(f"clear_alarm_set_btn 오류: {e}")
            return 






    def sd_card_set_btn( self ):
        try:
            data_str = str(self.widgets1['sd_card'].currentIndex()-1)
            command, response = self.common_command( "W", "9", data_str )
        except Exception as e:
            self.main_window.add_log(f"sd_card_set_btn 오류: {e}")
            return


    def sd_card_del_btn( self ):
        command, response = self.common_command( "W", "a" )

        if command == response :
            self.main_window.add_log("SD Card의 모든 내용을 지웠습니다.")



    def sd_card_get_btn( self ):
        try:
            command, response = self.common_command( "R", "9" )
            ans = trim_string( response, 3, 3 )
            #self.widgets1['auto_id'].setCurrentIndex( int(ans)+1 )
            self.set_combo_box( 'sd_card', int(ans)+1, self.widgets1 )
        except Exception as e:
            self.main_window.add_log(f"sd_card_get_btn 오류: {e}")
            return






    def set_input_box( self, box_name, value, widget_id ):
        widget_id[box_name].setText( value )
    def get_input_box( self, box_name, widget_id ):
        return widget_id[box_name].text()

    def set_combo_box( self, box_name, value, widget_id ):
        widget_id[box_name].setCurrentIndex( value )

    def get_combo_box( self, box_name, widget_id ):
        return widget_id[box_name].currentIndex()


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


