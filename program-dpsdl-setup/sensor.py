from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
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
        

        # 전용 테이블 레이아웃으로 더 깔끔하게 구성
        lines_def = [
            ('Line1', 'line1_in', 'line1_out'),
            ('Line2', 'line2_in', 'line2_out'),
            ('Line3', 'line3_in', 'line3_out'),
            ('Line4', 'line4_in', 'line4_out'),
        ]
        group4, self.widgets4 = create_voltage_lines_group(
            'Voltage of Lines (cmd=1)',
            'Vin DC:', 'vin_dc',
            lines_def,
            input_width=60,
            read_only=True,
            button_text='GET'
        )

        # Get Hydronet Offset ID
        layout6_config = [
                {'type': 'input_pair', 'label':'Offset ID:',    'name':'offsetid'},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group6, self.widgets6 = create_dynamic_group('Hydronet Offset ID (cmd=2)', layout6_config, input_width=100)

        layout5_config = [
                {'type': 'combo_box',  'label':'Reconnection:', 'name':'reconnection','option':['-','Off','On']},
                {'type': 'input_pair', 'label':'첫 번째:', 'name':'box1'},
                {'type': 'input_pair', 'label':'첫 번째:', 'name':'box2'},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group5, self.widgets5 = create_dynamic_group('Reconnection (cmd=3)', layout5_config )



        layout7_config = [
                {'type': 'combo_box',  'label':'Line:',   'name':'line',  'option':['-','1','2','3','4']},
                {'type': 'combo_box',  'label':'Sensor:', 'name':'sensor','option':['0:DPS','1:Hydronet','2:Shinho','3:GSEN']},
                {'type': 'combo_box',  'label':'BPS:',    'name':'bps',   'option':['0:9600','1:19200','2:38400','3:57600','4:115200','5:230400','6:460800']},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group7, self.widgets7 = create_dynamic_group('Line Sensor & COMM Config (cmd=4)', layout7_config )

        layout8_config = [
                {'type': 'combo_box',  'label':'Sensor:',   'name':'sensor',  'option':['-','0:Hydronet','1:Shiho','2:GSEN']},
                {'type': 'input_pair', 'label':'ID', 'name':'id'},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group8, self.widgets8 = create_dynamic_group('Sensor Offset ID (cmd=5)', layout8_config )

        layout9_config = [
                {'type': 'combo_box',  'label':'DPS Sensor:',   'name':'type',  'option':['-','0:Strain','1:온도','2:각도', '3:길이','4:강우량','5:압력']},
                {'type': 'button', 'text':'Add', 'name':'add_btn'},
                {'type': 'button', 'text':'Delete', 'name':'del_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group9, self.widgets9 = create_dynamic_group('DPS Sensor Type (cmd=6)', layout9_config )





        main_layout.addWidget(group1)
        main_layout.addWidget(group2)
        main_layout.addWidget(group3)
        main_layout.addWidget(group4)
        main_layout.addWidget(group6)
        main_layout.addWidget(group5)
        main_layout.addWidget(group7)
        main_layout.addWidget(group8)
        main_layout.addWidget(group9)

        # DPS Sensor Type 테이블 (초기에는 숨김)
        self.dps_table = QTableWidget(0, 2, self)
        self.dps_table.setHorizontalHeaderLabels(["Type ID", "Type"])
        self.dps_table.horizontalHeader().setStretchLastSection(True)
        self.dps_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.dps_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.dps_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.dps_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.dps_table.setVisible(False)
        main_layout.addWidget(self.dps_table)

        main_layout.addStretch(1)

        self.widgets1['get_btn'].clicked.connect( self.auto_id_get_btn )
        self.widgets2['set_btn'].clicked.connect( self.clear_alarm_set_btn )
        self.widgets3['get_btn'].clicked.connect( self.temperature_get_btn )
        self.widgets4['get_btn'].clicked.connect( self.voltage_of_lines )
        self.widgets5['set_btn'].clicked.connect( self.reconnection_set_btn )
        self.widgets5['get_btn'].clicked.connect( self.reconnection_get_btn )
        self.widgets6['set_btn'].clicked.connect( self.offset_id_set_btn )
        self.widgets6['get_btn'].clicked.connect( self.offset_id_get_btn )

        self.widgets7['set_btn'].clicked.connect( self.line_sensor_set_btn )
        self.widgets7['get_btn'].clicked.connect( self.line_sensor_get_btn )

        self.widgets8['get_btn'].clicked.connect( self.sensor_offset_id_get_btn )
        self.widgets8['set_btn'].clicked.connect( self.sensor_offset_id_set_btn )

        self.widgets9['add_btn'].clicked.connect( self.dpssensor_type_add_btn )
        self.widgets9['del_btn'].clicked.connect( self.dpssensor_type_del_btn )
        self.widgets9['get_btn'].clicked.connect( self.dpssensor_type_get_btn )


    def _dps_type_name(self, type_id: int) -> str:
        mapping = {
            0: 'Strain',
            1: '온도',
            2: '각도',
            3: '길이',
            4: '강우량',
            5: '압력',
        }
        return mapping.get(type_id, f"Unknown({type_id})")

    def _dps_type_exists(self, type_id: int) -> bool:
        for r in range(self.dps_table.rowCount()):
            item = self.dps_table.item(r, 0)
            if not item:
                continue
            try:
                existing = int(item.text())
            except ValueError:
                continue
            if existing == type_id:
                return True
        return False



    def _add_dps_type_row(self, type_id: int):
        name = self._dps_type_name(type_id)
        row = self.dps_table.rowCount()
        self.dps_table.insertRow(row)
        id_item = QTableWidgetItem(str(type_id))
        name_item = QTableWidgetItem(name)
        self.dps_table.setItem(row, 0, id_item)
        self.dps_table.setItem(row, 1, name_item)
        if not self.dps_table.isVisible():
            self.dps_table.setVisible(True)

    def _selected_dps_type(self) -> int | None:
        row = self.dps_table.currentRow()
        if row < 0:
            return None
        item = self.dps_table.item(row, 0)
        if not item:
            return None
        try:
            return int(item.text())
        except ValueError:
            return None

    def dpssensor_type_add_btn( self ):
        try:
            sel = int(self.get_combo_box('type', self.widgets9)) - 1
        except Exception:
            sel = -1

        if sel < 0:
            self.main_window.add_log('추가할 Sensor Type을 선택하세요.')
            return

        if self._dps_type_exists(sel):
            self.main_window.add_log('이미 추가된 Sensor Type 입니다.')
            return

        # 장치에 Add 명령 전송 (CMD=6A)
        try:
            command, response = self.common_command("W", "6A", str(sel))
            is_valid, error_message = check_response(response)
            if not is_valid:
                self.main_window.add_log(f"응답 검증 실패: {error_message}")
                return
        except Exception as e:
            self.main_window.add_log(f"DPS Sensor Type Add 오류: {e}")
            return

        # UI 테이블에 반영
        self._add_dps_type_row(sel)

    # 호환용 별칭 (요청 명칭 대응)
    def dpssensor_add_btn(self):
        self.dpssensor_type_add_btn()

    def dpssensor_type_del_btn( self ):
        sel_type = self._selected_dps_type()
        if sel_type is None:
            self.main_window.add_log('삭제할 Sensor Type 행을 선택하세요.')
            return

        # 장치에 Delete 명령 전송 (CMD=6D)
        try:
            command, response = self.common_command("W", "6D", str(sel_type))
            is_valid, error_message = check_response(response)
            if not is_valid:
                self.main_window.add_log(f"응답 검증 실패: {error_message}")
                return
        except Exception as e:
            self.main_window.add_log(f"DPS Sensor Type Delete 오류: {e}")
            return

        # UI 테이블에서 제거
        row = self.dps_table.currentRow()
        if row >= 0:
            self.dps_table.removeRow(row)
        if self.dps_table.rowCount() == 0:
            self.dps_table.setVisible(False)

    def dpssensor_type_get_btn( self ):
        # 장치로부터 현재 DPS Sensor Type 목록을 조회 (CMD=6)
        command, response = self.common_command("R", "6")

        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return

        try:
            ans = trim_string(response, 3, 3)
            ids: list[int] = []

            # 우선 숫자 토큰들 추출 (공백/쉼표 등 구분자 대응)
            import re
            tokens = re.findall(r"\d+", ans)
            for t in tokens:
                v = int(t)
                if 0 <= v <= 5:
                    ids.append(v)

            # 토큰이 없고 0/1만으로 구성된 문자열이면 비트마스크로 해석 (예: '101001')
            if not ids and ans and all(ch in '01' for ch in ans) and len(ans) <= 8:
                for i, ch in enumerate(ans):
                    if ch == '1' and 0 <= i <= 5:
                        ids.append(i)

            # 중복 제거 및 정렬
            ids = sorted(set(ids))

            # 테이블 갱신
            self.dps_table.setRowCount(0)
            for type_id in ids:
                self._add_dps_type_row(type_id)
            self.dps_table.setVisible(bool(ids))

        except Exception as e:
            self.main_window.add_log(f"DPS Sensor Type GET 처리 오류: {e}")

    # 호환용 별칭 (요청 명칭 대응)
    def dpssensor_del_btn(self):
        self.dpssensor_type_del_btn()

    def sensor_offset_id_set_btn( self ):
        try:
            #data_str  = str(self.widgets8['sensor'].currentIndex()-1)
            #data_str  += self.widgets8['id'].text()

            data_str = str( self.get_combo_box( 'sensor', self.widgets8 )-1 )
            data_str += self.get_input_box( 'id', self.widgets8 ).zfill(3)
            print("line = ", data_str)
            command, response = self.common_command( "W", "5", data_str )
        except Exception as e:
            self.main_window.add_log(f"Set Sensor Offset ID (cmd=5) Error: {e}")


    def sensor_offset_id_get_btn( self ):
        command, response = self.common_command( "R", "5" )

        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return


        try :
            ans = trim_string( response, 3, 3 )
            return_tuple = parse_by_lengths( ans, "13") 
            #print("ans = ", ans)
            self.set_combo_box( 'sensor', int(return_tuple[0])+1, self.widgets8 )
            self.set_input_box( 'id', return_tuple[1], self.widgets8 )
        except Exception as e :
            print(f"Get Sensor Offset ID cmd=5 Error: {e}")




    def line_sensor_set_btn( self ):
        try:
            #print("line = ", self.widgets7['line'].currentIndex())
            data_str  = str(int(self.widgets7['line'].currentIndex())-1)
            #print("line = ", data_str)
            data_str += str(self.widgets7['sensor'].currentIndex())
            #print("sensor = ",data_str)
            data_str += str(self.widgets7['bps'].currentIndex())
            #print("bps = ", data_str)

            #print(data_str)

            command, response = self.common_command( "W", "4", data_str )
        except Exception as e:
            self.main_window.add_log(f"Line Sensor(cmd=4) Error: {e}")
            return



    def line_sensor_get_btn( self ):
        command, response = self.common_command( "R", "4" )

        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return

        try :
            ans = trim_string( response, 3, 3 )
            print("ans = ", ans)

            self.set_combo_box( 'line', int(ans[0])+1, self.widgets7 )
            self.set_combo_box( 'sensor', int(ans[1]), self.widgets7 )
            self.set_combo_box( 'bps', int(ans[2]), self.widgets7 )
        except Exception as e:
            print(f"Error : {e} ")





    def offset_id_set_btn( self ):
        try:
            data_str = self.widgets6['offsetid'].text()

            print(data_str)

            command, response = self.common_command( "W", "2", data_str )
        except Exception as e:
            self.main_window.add_log(f"reconnection_set_btn 오류: {e}")
            return




    def offset_id_get_btn( self ):
        command, response = self.common_command( "R", "2" )

        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return

        ans = trim_string( response, 3, 3 )
        print("ans = ", ans)
        self.set_input_box( 'offsetid', ans, self.widgets6 )
        



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

        return_tuple = parse_by_lengths( ans, "333333333" )

        box_names = ['vin_dc','line1_in','line1_out','line2_in','line2_out','line3_in','line3_out', 'line4_in', 'line4_out']
        #box_names = ['vin_ac','vin_dc','line1_in','line1_out','line2_in','line2_out','line3_in','line3_out', 'line4_in', 'line4_out']

        for i in range (9):
            #print(return_tuple[i])
            ss = "{:.2f}".format(float(return_tuple[i])*0.1)
            self.widgets4[box_names[i]].setText( ss+" V" )


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
