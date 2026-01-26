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


        scroll = QScrollArea()
        scroll.setWidgetResizable( True )
        scroll.setFixedHeight(450)

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
                {'type': 'combo_box', 'label':'Line1:', 'name':'line1', 'option':['-', 'Off', 'On']},
                {'type': 'combo_box', 'label':'Line2:', 'name':'line2', 'option':['-', 'Off', 'On']},
                {'type': 'combo_box', 'label':'Line3:', 'name':'line3', 'option':['-', 'Off', 'On']},
                {'type': 'combo_box', 'label':'Line4:', 'name':'line4', 'option':['-', 'Off', 'On']},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group3, self.widgets3 = create_dynamic_group('Protocil type (cmd=f)', layout3_config )

        scroll.setWidget(content)


        content_layout.addWidget(group1)
        content_layout.addWidget(group2)
        #content_layout.addWidget(group3)

        main_layout.addWidget(scroll)

        main_layout.addStretch(1)

        self.widgets1['get_btn'].clicked.connect( self.angle_calibration_get_btn )
        self.widgets1['set_btn'].clicked.connect( self.angle_calibration_set_btn )

        self.widgets2['get_btn'].clicked.connect( self.retry_sensing_get_btn )
        self.widgets2['set_btn'].clicked.connect( self.retry_sensing_set_btn )


        self.widgets3['get_btn'].clicked.connect( self.protocol_type_get_btn )
        #self.widgets3['set_btn'].clicked.connect( self.protocol_type_set_btn )


    def protocol_type_get_btn( self ):
        try:
            command, response = self.common_command( "R", "f" )
            
            ans = trim_string( response, 3, 3 )
            return_tuple = parse_by_lengths( ans, "1111" )

            self.set_combo_box( "line1", int( return_tuple[0])+1, self.widgets3 )
            self.set_combo_box( "line2", int( return_tuple[1])+1, self.widgets3 )
            self.set_combo_box( "line3", int( return_tuple[2])+1, self.widgets3 )
            self.set_combo_box( "line4", int( return_tuple[3])+1, self.widgets3 )
        except Exception as e:
            print(f"Get Protocol Type Error : {e}")



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


