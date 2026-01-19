from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QGroupBox
)
from PyQt6.QtCore import Qt
from communication import *
from utils import *
import protocol as ptcl


class ConfigTab(QWidget):
    def __init__(self, parent):
        """
            'Config' 탭의 UI와 기능을 모두 담고 있는 클래스입니다.
            parent 인자로는 MainWindow의 인스턴스(self)가 전달됩니다.
        """

        super().__init__()

        self.main_window = parent

        main_layout = QVBoxLayout(self)

        # Config Get All
        get_all_layout = QHBoxLayout()
        self.get_all_btn = QPushButton("GET ALL")
        get_all_layout.addWidget(QLabel("Config All"))
        get_all_layout.addWidget(self.get_all_btn)
        get_all_layout.addStretch(1)
        main_layout.addLayout(get_all_layout)

        layout1_config = [
                {'type': 'input_pair', 'label':'V_min:', 'name':'vmin'},
                {'type': 'input_pair', 'label':'V_max:', 'name':'vmax'},
                {'type': 'input_pair', 'label':'Recovery Time:', 'name':'recovery_time'},
                {'type': 'input_pair', 'label':'Retry:', 'name':'retry'},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group1, self.widgets1 = create_dynamic_group('Voltage LIMIT (cmd=T)', layout1_config)




        layout2_config = [
                {'type': 'combo_box', 'label':'Line1:', 'name':'line1','option':['-','Off','On']},
                {'type': 'combo_box', 'label':'Line2:', 'name':'line2','option':['-','Off','On']},
                {'type': 'combo_box', 'label':'Line3:', 'name':'line3','option':['-','Off','On']},
                {'type': 'combo_box', 'label':'Line4:', 'name':'line4','option':['-','Off','On']},
                {'type': 'combo_box', 'label':'ACQ:',   'name':'acq'  ,'option':['-','Off','On']},
                {'type': 'combo_box', 'label':'Alarm:', 'name':'alarm','option':['-','Off','On']},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group2, self.widgets2 = create_dynamic_group_grid_2xN('Line Power (cmd=L)', layout2_config)


        layout3_config = [
                {'type': 'input_pair', 'label':'ACQ Count:', 'name':'acq_count'},
                {'type': 'combo_box',  'label':'Time Unit:', 'name':'time_unit','option':['-','0: sec','1: min']},
                {'type': 'input_pair', 'label':'Interval:',   'name':'interval'},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'}
                ]
        group3, self.widgets3 = create_dynamic_group('Gathering (cmd=G)', layout3_config)




        # --- Communication (cmd=C) 그룹 ---
        comm_group = QGroupBox('Communication (cmd=C)')
        # 그룹 내에서 미니 그룹들을 수직으로 쌓기 위해 QVBoxLayout을 메인 레이아웃으로 사용
        main_comm_layout = QVBoxLayout()

        # --- 미니 그룹 1 (첫 번째 줄) ---
        mini_group_1_layout = QHBoxLayout()

        # 데이터 정의
        self.COMM_OPTIONS_DATA = {
                'LTE BPS' : ['-', '0: 9600', '1: 19200', '2: 38400', '3: 56700', '4: 115200', '5: 230400', '6: 460800', '7: 921600'],
                'MODE' : ['-', '0:LTE', '1:ETH']
                }

        # 'Types' 콤보박스
        types_label = QLabel("Types:")
        self.comm_types_combo = QComboBox()
        self.comm_types_combo.addItems(['-'] + list(self.COMM_OPTIONS_DATA.keys()))

        # 'Value' 콤보박스
        value_label = QLabel("Value:")
        self.comm_value_combo = QComboBox()
        self.comm_value_combo.addItem('-')
        self.comm_value_combo.setFixedWidth(100)

        self.comm_set_btn_widget = QPushButton("SET")

        # 첫 번째 줄 레이아웃에 위젯 추가
        mini_group_1_layout.addWidget(types_label)
        mini_group_1_layout.addWidget(self.comm_types_combo)
        mini_group_1_layout.addWidget(value_label)
        mini_group_1_layout.addWidget(self.comm_value_combo)
        mini_group_1_layout.addStretch()
        mini_group_1_layout.addWidget(self.comm_set_btn_widget)

        # 'SET' 버튼


        # --- 미니 그룹 2 (두 번째 줄) ---
        mini_group_2_layout = QHBoxLayout()

        # 'Custom' 입력 상자
        lte_bps_label = QLabel("Types:")
        self.comm_type_combo_box = QComboBox()
        self.comm_type_combo_box.addItems(['LTE BPS','MODE'])

        mode_label = QLabel("Mode:")
        self.comm_mode_input = QLineEdit()
        #self.comm_mode_input.setReadOnly(True)
        self.comm_mode_input.setFixedWidth(100)


        self.comm_get_btn_widget = QPushButton("GET")


        # 두 번째 줄 레이아웃에 위젯 추가
        mini_group_2_layout.addWidget(lte_bps_label)
        mini_group_2_layout.addWidget(self.comm_type_combo_box)
        mini_group_2_layout.addWidget(mode_label)
        mini_group_2_layout.addWidget(self.comm_mode_input)
        mini_group_2_layout.addStretch()
        mini_group_2_layout.addWidget(self.comm_get_btn_widget)
        #mini_group_2_layout.addStretch() # 버튼을 오른쪽으로 밀기


        # --- 레이아웃 조립 ---
        # 메인 수직 레이아웃에 두 개의 미니 그룹(수평 레이아웃)을 추가
        main_comm_layout.addLayout(mini_group_1_layout)
        main_comm_layout.addLayout(mini_group_2_layout)

        # 최종적으로 그룹 박스의 레이아웃을 설정
        comm_group.setLayout(main_comm_layout)

        # 완성된 그룹을 탭의 메인 레이아웃에 추가
        main_layout.addWidget(comm_group)

        # 시그널 연결
        self.comm_types_combo.currentTextChanged.connect(self.update_comm_value_options)




        layout5_config = [
                {'type': 'combo_box',  'label':'Rain:', 'name':'rain','option':['-','0:Off','1:On']},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
                {'type': 'button', 'text':'Clear Count:', 'name':'clear_count_btn'}
                ]
        group5, self.widgets5 = create_dynamic_group('Rain (cmd=A)', layout5_config )

        main_layout.addWidget(group1)
        main_layout.addWidget(group2)
        main_layout.addWidget(group3)
        main_layout.addWidget(comm_group)
        main_layout.addWidget(group5)









        main_layout.addStretch(1)

        self.widgets1['set_btn'].clicked.connect( self.voltage_limit_set_btn )
        self.widgets1['get_btn'].clicked.connect( self.voltage_limit_get_btn )

        self.widgets2['set_btn'].clicked.connect( self.line_power_set_btn )
        self.widgets2['get_btn'].clicked.connect( self.line_power_get_btn )

        self.widgets3['set_btn'].clicked.connect( self.gathering_set_btn )
        self.widgets3['get_btn'].clicked.connect( self.gathering_get_btn )

        self.comm_set_btn_widget.clicked.connect( self.comm_set_btn )
        self.comm_get_btn_widget.clicked.connect( self.comm_get_btn )



        self.widgets5['get_btn'].clicked.connect( self.rain_get_btn )
        self.widgets5['set_btn'].clicked.connect( self.rain_set_btn )
        self.widgets5['clear_count_btn'].clicked.connect( self.rain_clear_count_btn )
        self.get_all_btn.clicked.connect( self.get_all_settings )



    def get_all_settings( self ):
        tasks = [
            ("Voltage LIMIT", self.voltage_limit_get_btn),
            ("Line Power", self.line_power_get_btn),
            ("Gathering", self.gathering_get_btn),
            ("Communication", self.comm_get_btn),
            ("Rain", self.rain_get_btn),
        ]
        for name, fn in tasks:
            try:
                fn()
            except Exception as e:
                self.main_window.add_log(f"전체 설정 불러오기 오류 ({name}): {e}")

    def gathering_set_btn( self ):

        data_str = self.widgets3['acq_count'].text()
        data_str += str(self.widgets3['time_unit'].currentIndex()-1)
        data_str += self.widgets3['interval'].text()


        command, response = self.common_command( "W", "G", data_str )


    #def parse_gathering_response(self, response):
    #    """Gathering 응답 파싱 함수"""
    #    ans = trim_string( response, 3, 3 )
    #    return_tuple =  parse_by_lengths( ans, "414" )
        
    #    self.widgets3['acq_count'].setText(return_tuple[0])
    #    self.widgets3['time_unit'].setCurrentIndex(int(return_tuple[1]))
    #    self.widgets3['interval'].setText(return_tuple[2])

    def gathering_get_btn( self ):
        command, response = self.common_command( "R", "G" )
        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return

        ans = trim_string( response, 3, 3 )
        return_tuple =  parse_by_lengths( ans, "414" )
        
        print("ru = ", return_tuple )
        self.widgets3['acq_count'].setText(return_tuple[0])
        self.widgets3['time_unit'].setCurrentIndex(int(return_tuple[1])+1)
        self.widgets3['interval'].setText(return_tuple[2])
        #self.handle_response(response, self.parse_gathering_response)



    def comm_set_btn( self ):

        types = self.comm_types_combo.currentText()
        print("types = ", types)
        if types == "LTE BPS" : 
            data_str = "0"
        elif types == "MODE" : 
            data_str = "5"
        else :
            self.main_window.add_log(f"types error : {types}")
            return


        value = self.comm_value_combo.currentText()
        data_str = data_str + value[0]

        if not data_str:
            self.main_window.add_log(f"data_string none: {data_str}")
            
            return

        command, response = self.common_command( "W", "C", data_str )


        #self.widgets2['acq'].setText("0: 9600")






    def parse_comm_response(self, response):
        """Comm 응답 파싱 함수"""
        ans = trim_string( response, 3, 3 )

        print("ans = ", ans)

        if ans=="00": self.comm_mode_input.setText("0: 9600")
        if ans=="01": self.comm_mode_input.setText("1: 19200")
        if ans=="02": self.comm_mode_input.setText("2: 38400")
        if ans=="03": self.comm_mode_input.setText("3: 57600")
        if ans=="04": self.comm_mode_input.setText("4: 115200")
        if ans=="05": self.comm_mode_input.setText("5: 230400")
        if ans=="06": self.comm_mode_input.setText("6: 460800")
        if ans=="07": self.comm_mode_input.setText("7: 921600")

        if ans=="50": self.comm_mode_input.setText("LTE")
        if ans=="51": self.comm_mode_input.setText("ETH")



    def comm_get_btn( self ):
        types = self.comm_type_combo_box.currentText()
        if types == "LTE BPS" :
            data_str = "0"
        if types == "MODE" :
            data_str = "5"

        command, response = self.common_command( "R", "C", data_str )

        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return 


        ans = trim_string( response, 3, 3 )

        if ans=="00": self.comm_mode_input.setText("0: 9600")
        if ans=="01": self.comm_mode_input.setText("1: 19200")
        if ans=="02": self.comm_mode_input.setText("2: 38400")
        if ans=="03": self.comm_mode_input.setText("3: 57600")
        if ans=="04": self.comm_mode_input.setText("4: 115200")
        if ans=="05": self.comm_mode_input.setText("5: 230400")
        if ans=="06": self.comm_mode_input.setText("6: 460800")
        if ans=="07": self.comm_mode_input.setText("7: 921600")

        if ans=="50": self.comm_mode_input.setText("LTE")
        if ans=="51": self.comm_mode_input.setText("ETH")



        #self.handle_response(response, self.parse_comm_response)
        
















    def update_comm_value_options(self, selected_type):
      """'Types' 콤보박스 변경 시 'Value' 콤보박스 옵션을 업데이트하는 메서드"""

        #두 번째 콤보박스의 이전 항목들을 모두 지웁니다.
      self.comm_value_combo.clear()

        #첫 번째 콤보박스에서 선택된 항목(selected_type)이 데이터에 있는지 확인
      if selected_type in self.COMM_OPTIONS_DATA:
        #선택된 항목에 해당하는 옵션 리스트를 가져옵니다.
          options = self.COMM_OPTIONS_DATA[selected_type]
        #가져온 옵션들을 두 번째 콤보박스에 추가합니다.
          self.comm_value_combo.addItems(options)
      else:
        #선택된 항목이 유효하지 않으면 (예: 맨 처음 '-') 기본값만 추가합니다.
          self.comm_value_combo.addItem('-')







    def line_power_set_btn( self ):

        try:
            widget_names = ['line1', 'line2', 'line3', 'line4', 'acq', 'alarm']
            statuses = []
            for name in widget_names:
                #currentIndex()는 'Off'일 때 0, 'On'일 때 1을 반환합니다.
                index = self.widgets2[name].currentIndex()
                statuses.append(str(index-1))

            data_str = "".join(statuses)

        except Exception as e:
            self.main_window.add_log(f"오류: 상태 값을 읽는 중 문제가 발생했습니다: {e}")
            return


        command, response = self.common_command( "W", "L", data_str )




    def handle_response(self, response, success_callback=None):
        """공통 응답 처리 함수"""
        print(f"[DEBUG] handle_response - response: '{response}', callback: {success_callback}")
        
        if response.startswith("오류:") or response == "전송 성공":
            if response.startswith("오류:"):
                self.main_window.add_log(f"❌ {response}")
            print("[DEBUG] 파싱 안함 - 오류 또는 전송 성공")
            return False  # 파싱 안함
        else:
            self.main_window.add_log(f"✅ 응답 << {response}")
            if success_callback:
                print("[DEBUG] 콜백 함수 호출 중...")
                success_callback(response)  # 클라이언트 모드에서만 파싱
                print("[DEBUG] 콜백 함수 완료")
            else:
                print("[DEBUG] 콜백 함수가 None입니다")
            return True  # 성공

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








    def line_power_get_btn( self ):

        command, response = self.common_command( "R", "L" )
        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return

        try:
            ans = trim_string( response,  3, 3)

            return_tuple = parse_by_lengths( ans, "111111" )

            widget_names = ['line1', 'line2', 'line3', 'line4', 'acq', 'alarm']
            
            for status_char, name in zip(return_tuple, widget_names):
                status_int = int(status_char)
                if status_int in [0, 1]:
                    self.widgets2[name].setCurrentIndex(status_int+1)
                else:
                    self.main_window.add_log(f"오류: {name}의 상태값이 0 또는 1이 아닙니다: {status_int}")


        except (ValueError, IndexError):
            self.main_window.add_log(f"오류: 응답 파싱에 실패했습니다. 응답: {response}")





    def rain_clear_count_btn(self):

        command, response = self.common_command( "W", "E" )
        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return

        if  command == response :
            self.main_window.add_log(f"Count가 초기화 되었습니다.")
        else:
            self.main_window.add_log(f"Count가 초기화 되지 않았습니다.")





    def rain_set_btn(self):
        #(인덱스가 0이면 '0:Off', 1이면 '1:On'이므로, 이 값이 전송할 데이터가 됩니다)
        status_to_set = self.widgets5['rain'].currentIndex()

        #전송할 데이터 (상태값 0 또는 1)를 문자열로 변환
        data_str = str(status_to_set-1)

        command, response = self.common_command( "W", "A", data_str )




    def rain_get_btn( self ):
        #ip, port = self.main_window.get_ip_port()

        command, response = self.common_command( "R", "A" )

        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return

        try:
            ans = trim_string( response,  3, 3)

            status = int(ans)+1

            #6. 콤보박스 위젯의 선택 값 변경
            #status 값(0 또는 1)에 따라 콤보박스의 인덱스를 설정
            if status >= 0 and status <= 2:
                self.widgets5['rain'].setCurrentIndex(status)
            else:
                self.main_window.add_log(f"오류: 알 수 없는 상태값입니다. 응답: {status}")

        except (ValueError, IndexError):
            self.main_window.add_log(f"오류: 응답 파싱에 실패했습니다. 응답: {response}")





    def voltage_limit_set_btn( self ):

        try:
            vmin_str      = extract_number_from_text(self.widgets1['vmin'].text())
            vmax_str      = extract_number_from_text(self.widgets1['vmax'].text())
            recovery_time_str = extract_number_from_text(self.widgets1['recovery_time'].text())
            retry_str         = extract_number_from_text(self.widgets1['retry'].text())

            vmin_val = int(  float(vmin_str)*10 )
            vmax_val = int(  float(vmax_str)*10 )
            recovery_time_val = int(  float(recovery_time_str) )
            retry_val = int(  float(retry_str) )
        except ValueError:
            self.main_window.add_log("오류: 숫자 입력 필드에  유호한 숫자를 입력하세요.")
            return

        data_str = (f"{vmin_val:03d}"
                  f"{vmax_val:03d}"
                  f"{recovery_time_val:03d}"
                  f"{retry_val:d}")
            

        command, response = self.common_command( "W", "T", data_str)


    def voltage_limit_get_btn(self):

        # Recovery time 100
        data_str  =  "100"

        #command, response = self.common_command( "R", "T", data_str )
        command, response = self.common_command( "R", "T" )
        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return



        ans = trim_string( response, 3, 3 )

        return_tuple = parse_by_lengths( ans, "3331" )

        vmin = int(return_tuple[0])*0.1
        vmax = int(return_tuple[1])*0.1
        recovery_time = int(return_tuple[2])
        retry = int(return_tuple[3])


        # 칸 오른쪽 정렬
        self.widgets1['vmin'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.widgets1['vmax'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.widgets1['recovery_time'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.widgets1['retry'].setAlignment(Qt.AlignmentFlag.AlignRight)

        self.widgets1['vmin'].setText(str(vmin)+" V");
        self.widgets1['vmax'].setText(str(vmax)+" V");
        self.widgets1['recovery_time'].setText(str(recovery_time)+" s");
        self.widgets1['retry'].setText(str(retry)+" 회");


    
