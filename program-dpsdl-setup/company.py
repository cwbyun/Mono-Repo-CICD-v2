from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea,
    QHBoxLayout, QGroupBox, QTableWidget, QTableWidgetItem, QDialog, QComboBox
)
from PyQt6.QtCore import Qt
from communication import *
from utils import *
import protocol as ptcl
import time

# 통합된 업체 및 모델 데이터 구조
COMPANY_DATA = [
    {"name": "디피에스글로벌", "models": ["TTW"]},
    {"name": "하이드로넷",     "models": ["MK21"]},
    {"name": "신호",     "models": ["SHN530-2"]},
    {"name": "지센",     "models": ["GSD9100"]},
]

class CompanyTab(QWidget):
    def __init__(self, parent):
        """
        'Signal' 탭의 UI와 기능을 모두 담고 있는 클래스입니다.
        parent 인자로는 MainWindow의 인스턴스(self)가 전달됩니다.
        """
        super().__init__()
        self.main_window = parent

        main_layout = QVBoxLayout(self)

        #scroll = QScrollArea()
        #scroll.setWidgetResizable(True)
        #scroll.setFixedHeight(450)

        #content = QWidget(self)
        #content_layout = QVBoxLayout(content)

        # COMPANY_DATA를 사용하여 업체 옵션 생성
        company_options = ['-'] + [f"{i}-{d['name']}" for i,d in enumerate(COMPANY_DATA)]

        layout0_config = [
            {'type': 'combo_box', 'label': 'Sensor Type:', 'name': 'type', 'option': company_options},
            {'type': 'combo_box', 'label': '모델 선택:', 'name': 'model', 'option': ['-']},
            {'type': 'input_pair', 'label': '시작 범위:', 'name': 'start_range'},
            {'type': 'input_pair', 'label': '끝 범위:', 'name': 'end_range'},
            {'type': 'button', 'text': 'ADD', 'name': 'add_btn'},
            {'type': 'button', 'text': 'GET', 'name': 'get_btn'},
        ]
        group0, self.widgets0 = create_dynamic_group('Sensor Maker (cmd=6)', layout0_config, input_width=100)

        self.widgets0['model'].setMinimumWidth(100)













        layout1_config = [
            {'type': 'combo_box', 'label': '업체 선택:', 'name': 'company', 'option': company_options},
            {'type': 'combo_box', 'label': '모델 선택:', 'name': 'model', 'option': ['-']},
            {'type': 'input_pair', 'label': '시작 범위:', 'name': 'start_range'},
            {'type': 'input_pair', 'label': '끝 범위:', 'name': 'end_range'},
            {'type': 'button', 'text': 'ADD', 'name': 'add_btn'},
            {'type': 'button', 'text': 'GET', 'name': 'get_btn'},
        ]
        group1, self.widgets1 = create_dynamic_group('Sensor Maker (cmd=7A)', layout1_config, input_width=100)

        self.widgets1['model'].setMinimumWidth(100)
        self.widgets1['start_range'].setFixedWidth(45)
        self.widgets1['end_range'].setFixedWidth(45)

        # Company Table
        self.table_container = QWidget()
        self.table_layout = QVBoxLayout(self.table_container)


        # COMPANY_DATA를 사용하여 업체 옵션 생성
        #company_options = ['-'] + [f"{i}-{d['name']}" for i,d in enumerate(COMPANY_DATA)]

        layout2_config = [
            {'type': 'combo_box', 'label': 'Line:', 'name': 'line', 'option': ["1","2","3","4"]},
            {'type': 'combo_box', 'label': '업체 선택:', 'name': 'company', 'option': company_options},
            {'type': 'combo_box', 'label': '모델 선택:', 'name': 'model', 'option': ['-']},
            {'type': 'input_pair', 'label': 'PK from:', 'name': 'pk1'},
            {'type': 'input_pair', 'label': 'PK to:', 'name': 'pk2'},
            {'type': 'input_pair', 'label': 'ID from:', 'name': 'id1'},
            {'type': 'input_pair', 'label': 'ID to:', 'name': 'id2'},
            {'type': 'button', 'text': 'SET', 'name': 'set_btn'},
            {'type': 'button', 'text': 'GET', 'name': 'get_btn'},
        ]
        group2, self.widgets2 = create_dynamic_group('Sensor ID (cmd=7D)', layout2_config, input_width=100)

        self.widgets2['model'].setMinimumWidth(100)
        self.widgets2['pk1'].setMinimumWidth(30)
        self.widgets2['pk2'].setMinimumWidth(30)
        self.widgets2['id1'].setMinimumWidth(30)
        self.widgets2['id2'].setMinimumWidth(30)

        # Sensor ID Table
        self.id_table_container = QWidget()
        self.id_table_layout = QVBoxLayout(self.id_table_container)





        main_layout.addWidget(group1)
        main_layout.addWidget(self.table_container) # Maker Table


        main_layout.addWidget(group2)
        main_layout.addWidget(self.id_table_container) # Maker Table
        main_layout.addStretch(1)



        self.widgets1['add_btn'].clicked.connect(self.sensor_maker_add_btn)
        self.widgets1['get_btn'].clicked.connect(self.sensor_maker_get_btn)
        self.widgets1['company'].currentTextChanged.connect(self.on_company_changed)


        self.widgets2['set_btn'].clicked.connect(self.sensor_id_set_btn)
        self.widgets2['get_btn'].clicked.connect(self.sensor_id_get_btn)
        self.widgets2['company'].currentTextChanged.connect(self.on_company_changed2)





    def sensor_id_set_btn( self ):

        try:
            # Line
            data_str = str( int(self.widgets2['line'].currentIndex()) )

            # Company
            cc = self.widgets2['company'].currentText() 
            print( "cc = ", cc )
            ee = self.get_company_index( cc[2:] )

            gg = self.widgets2['model'].currentText() 
            ff = self.get_model_index( ee, gg ) + 1
            print("ff = ", ff )


            dd = self.get_company_index( cc[2:] ) + 1
            print( dd )
            data_str += str(dd).zfill(2) + str(ff).zfill(2)



            data0 = data_str
            print("data0 = ", data0)

            pk1 = int(self.widgets2['pk1'].text())

            tmp = self.widgets2['pk2'].text()
            pk2 = int(tmp) if tmp.strip() else 0

            id1 = int(self.widgets2['id1'].text())

            tmp = self.widgets2['id2'].text()
            id2 = int(tmp) if tmp.strip() else 0


            print("pk1 = ", pk1 )
            print("pk2 = ", pk2 )
            print("pk1 = ", id1 )
            print("pk2 = ", id2 )


            if pk2==0 and id2==0 :
                spk = str(pk1).zfill(2)
                sid = str(id1)
                data_str = data0 + spk + gg.replace("-","")  + sid + ","
                print("data_str = ", data_str )
                command, response = self.common_command( "W", "7D", data_str )

            elif pk2!=0 and id2!=0 :

                if pk2-pk1 == id2-id1 :
                    n = id2-id1
                    print("n = ", n )
                    for i in range(0,n+1):
                        spk = str(pk1+i).zfill(2)
                        sid = str(id1+i)

                        data_str = data0 + spk + gg.replace("-","")  + sid + ","
                        print("data_str = ", data_str )

                        command, response = self.common_command( "W", "7D", data_str )

            elif pk2==0 and id2!=0 :
                    n = id2-id1
                    print("n = ", n )
                    spk = str(pk1).zfill(2)
                    for i in range(0,n+1):
                        sid = str(id1+i)

                        data_str = data0 + spk + gg.replace("-","")  + sid + ","
                        print("data_str = ", data_str )
                        command, response = self.common_command( "W", "7D", data_str )

        
            self.sensor_id_get_btn()
        except:
            return


    def sensor_id_get_btn( self ):
        try:
            # 각 라인별 센서 ID를 가져와서 테이블로 만든다.
            data_str = str( int(self.widgets2['line'].currentText())-1 )

            self.main_window.add_log(f"라인 {int(data_str)+1}의 ID를 가져옵니다.")
            command, response = self.common_command( "R", "7D", data_str )
            is_valid, error_message = check_response(response)
            if not is_valid:
                self.main_window.add_log(f"응답 검증 실패: {error_message}")
                return



            ans = trim_string( response, 4, 3 )
            parts = ans.split(",")

            print("parts = ", parts)
            line = parts[0][0]
            print("line = ", line)
            n = int(parts[0][1:3])
            print("n = ", n)


            # 기존 테이블 삭제 (있다면)
            for i in reversed(range(self.id_table_layout.count())):
                widget_to_remove = self.id_table_layout.itemAt(i).widget()
                if widget_to_remove:
                    widget_to_remove.setParent(None)

            if n==0 : 
                return

            parts[0] = parts[0][3:]

            # 테이블 생성
            table = QTableWidget()
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels([ "Line", "Company", "Model", "PK", "ID", "수정", "삭제"])
            table.setRowCount(n)

            # 컬럼 너비 설정 (픽셀 단위)
            table.setColumnWidth(0, 50)  # Line 컬럼
            table.setColumnWidth(1, 250)  # Company 컬럼
            table.setColumnWidth(2, 200)  # Model 컬럼
            table.setColumnWidth(3, 100)  # PK
            table.setColumnWidth(4, 200)  # ID
            table.setColumnWidth(5, 50)  # Modify Button
            table.setColumnWidth(6, 50)  # Delete Button

            for i in range(n):
                print(parts[i])

                company_num = int(parts[i][0:2])
                model_num   = int(parts[i][2:4])
                pk          = int(parts[i][4:6])
                sensor_id   = parts[i][6:]
                #0123 456789 012345
                #0202 000000 000255

                print("company = ", self.get_company_name( company_num ))
                print("modelny = ", self.get_model_name( company_num, model_num ))

                company = self.get_company_name( company_num )
                model = self.get_model_name( company_num, model_num )



                #table.setItem(i, 0, QTableWidgetItem(str(i+1)))
                table.setItem(i, 0, QTableWidgetItem(str(int(line)+1)))
                table.setItem(i, 1, QTableWidgetItem(company))
                table.setItem(i, 2, QTableWidgetItem(model))
                table.setItem(i, 3, QTableWidgetItem(str(pk)))
                table.setItem(i, 4, QTableWidgetItem(sensor_id))
                #table.setItem(i, 5, QTableWidgetItem("수정"))

                self.add_id_modify_button(table,i)
                self.add_id_delete_button(table,i)


            self.id_table_layout.addWidget(table)

    
        except:
            return



    def modify_and_delete_id_row(self, table, button, row, action ):
        # Sensor ID를 수정하거나 삭제한다.
        try :
            line      = str(int(table.item(row,0).text())-1)
            company   = table.item(row,1).text()
            model     = table.item(row,2).text()
            pk        = table.item(row,3).text()
            sensor_id = table.item(row,4).text()

            print("line = ", line)
            print("com = ", company)
            print("mod = ", model)
            print("pk = ", pk)
            print("s_id = ", sensor_id)


            company_num = self.get_company_index(company)
            model_num = self.get_model_index(company_num, model)

            print("com = ", company_num)
            print("mod = ", model_num)

            data_str  = line
            data_str += str(company_num+1).zfill(2)
            data_str += str(model_num+1).zfill(2)

            if action=="modify" : data_str += pk

            data_str += sensor_id  + ","


            if action=="modify" :
                command, response = self.common_command( "W", "7D", data_str )

            if action=="delete" :
                command, response = self.common_command( "W", "7E", data_str )
                
            is_valid, error_message = check_response(response)
            if not is_valid:
                self.main_window.add_log(f"응답 검증 실패: {error_message}")
                return

            self.sensor_id_get_btn()
        except:
            return

    def delete_id_row(self, table, button, row):
        # Sensor ID를 삭제한다.

        try :
            line      = str(int(table.item(row,0).text())-1)
            company   = table.item(row,1).text()
            model     = table.item(row,2).text()
            pk        = table.item(row,3).text()
            sensor_id = table.item(row,4).text()

            print("line = ", line)
            print("com = ", company)
            print("mod = ", model)
            print("pk = ", pk)
            print("s_id = ", sensor_id)


            company_num = self.get_company_index(company)
            model_num = self.get_model_index(company_num, model)

            print("com = ", company_num)
            print("mod = ", model_num)

            data_str  = line
            data_str += str(company_num+1).zfill(2)
            data_str += str(model_num+1).zfill(2)
            data_str += sensor_id  + ","


            command, response = self.common_command( "W", "7E", data_str )
                
            is_valid, error_message = check_response(response)
            if not is_valid:
                self.main_window.add_log(f"응답 검증 실패: {error_message}")
                return

            self.sensor_id_get_btn()
        except:
            return


    def add_id_modify_button( self, table, row):
        btn = QPushButton("수정")

        btn.clicked.connect(lambda del_action, b=btn: self.modify_and_delete_id_row(table,b, row, "modify"))
        # 버튼을 셀에 넣기 위해 QWidget + QHBoxLayout 사용
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addWidget(btn)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        # 5는 6번째 컬럼에 넣는 것이다.
        table.setCellWidget(row, 5, widget)  # 마지막 컬럼에 버튼 삽입
        return


    def add_id_delete_button( self, table, row):
        btn = QPushButton("삭제")

        btn.clicked.connect(lambda del_action, b=btn: self.delete_id_row(table,b, row))
        

        # 버튼을 셀에 넣기 위해 QWidget + QHBoxLayout 사용
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addWidget(btn)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        # 5는 6번째 컬럼에 넣는 것이다.
        table.setCellWidget(row, 6, widget)  # 마지막 컬럼에 버튼 삽입












    def sensor_maker_add_btn( self ):

        try :
            company = self.widgets1["company"].currentText()
            model = self.widgets1["model"].currentText()

            print("com = ", company)
            print("mod = ", model)

            # 회사 이름 앞에 숫자 제거를 위해 2부터 시작한다.
            company_num = self.get_company_index(company[2:])
            model_num   = self.get_model_index(company_num, model)

            start_range = self.widgets1["start_range"].text().zfill(6)
            end_range = self.widgets1["end_range"].text().zfill(6)

    
            data_str = str( company_num+1).zfill(2)
            data_str += str(model_num+1).zfill(2)
            data_str += start_range + end_range

            print("data_str = ", data_str )

            command, response = self.common_command( "W", "7A", data_str )

            self.sensor_maker_get_btn()
        
        except:
            return




    def get_company_index(self, name):
        for i, company in enumerate(COMPANY_DATA):
            print("name.. = ", name)
            print("com... = ", company)
            if company["name"] == name:
                return i
        return -1  # 없으면 -1 반환


    def get_model_index(self, company_idx, model_name):
        """
        company_idx : COMPANY_DATA 리스트에서 회사 인덱스 (0부터 시작)
        model_name : 찾고자 하는 모델명
        """
        models = COMPANY_DATA[company_idx]["models"]
        try:
            return models.index(model_name)  # 리스트에서 인덱스 반환
        except ValueError:
            return -1  # 없으면 -1 반환






    def delete_row(self, table, button, row):

        try :

            company = table.item(row,0).text()
            model = table.item(row,1).text()
            start_range = table.item(row,2).text()
            end_range   = table.item(row,3).text()

            print("com = ", company)
            print("mod = ", model)
            print("start_range = ", start_range)
            print("end_ragne = ", end_range)


            company_num = self.get_company_index(company)
            model_num = self.get_model_index(company_num, model)

            print("com = ", company_num)
            print("mod = ", model_num)

            data_str  = str(company_num+1).zfill(2)
            data_str += str(model_num+1).zfill(2)
            data_str += str(start_range).zfill(6)
            data_str += str(end_range).zfill(6)


            command, response = self.common_command( "W", "7B", data_str )
                
            is_valid, error_message = check_response(response)
            if not is_valid:
                self.main_window.add_log(f"응답 검증 실패: {error_message}")
                return


            # 클릭된 버튼이 들어있는 행을 찾음
            #for i in range(table.rowCount()):
            #    if table.cellWidget(i, 5) == button.parent():  # 버튼이 마지막 컬럼에 있다고 가정
            #        print(f"{i+1}번째 행 삭제!")  # 여기서 원하는 작업 수행 가능
            #        table.removeRow(i)
            #        break

            self.sensor_maker_get_btn()
        except:
            return



    def add_delete_button( self, table, row):
        btn = QPushButton("삭제")

        btn.clicked.connect(lambda del_action, b=btn: self.delete_row(table,b, row))
        

        # 버튼을 셀에 넣기 위해 QWidget + QHBoxLayout 사용
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addWidget(btn)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        # 5는 6번째 컬럼에 넣는 것이다.
        table.setCellWidget(row, 5, widget)  # 마지막 컬럼에 버튼 삽입



    def sensor_maker_get_btn( self ):

        try :
            command, response = self.common_command( "R", "7A" )
                
            is_valid, error_message = check_response(response)
            if not is_valid:
                self.main_window.add_log(f"응답 검증 실패: {error_message}")
                return


            # 기존 테이블 삭제 (있다면)
            for i in reversed(range(self.table_layout.count())):
                widget_to_remove = self.table_layout.itemAt(i).widget()
                if widget_to_remove:
                    widget_to_remove.setParent(None)



            ans = trim_string( response, 4, 3 )
            parts = ans.split(",")

            n = int(parts[0][0:2])
            print("n = ", n)

            parts[0] = parts[0][2:]

            # 테이블 생성
            table = QTableWidget()
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels([ "Company", "Model", "Start Scan Range", "End Scan Range", "수정", "삭제"])
            table.setRowCount(n)

            # 컬럼 너비 설정 (픽셀 단위)
            table.setColumnWidth(0, 250)  # Company 컬럼
            table.setColumnWidth(1, 200)  # Model 컬럼
            table.setColumnWidth(2, 170)  # Start Scan range 컬럼
            table.setColumnWidth(3, 170)  # End Scan range
            table.setColumnWidth(4, 50)  # Modify Button
            table.setColumnWidth(5, 50)  # Delete Button

            for i in range(n):
                print(parts[i])

                company_num = int(parts[i][0:2])
                model_num   = int(parts[i][2:4])
                start_scan  = int(parts[i][4:10])
                end_scan    = int(parts[i][10:16])
                #0123 456789 012345
                #0202 000000 000255
    
                print("company = ", self.get_company_name( company_num ))
                print("modelny = ", self.get_model_name( company_num, model_num ))
                company = self.get_company_name( company_num )
                model = self.get_model_name( company_num, model_num )



                #table.setItem(i, 0, QTableWidgetItem(str(i+1)))
                table.setItem(i, 0, QTableWidgetItem(company))
                table.setItem(i, 1, QTableWidgetItem(model))
                table.setItem(i, 2, QTableWidgetItem(str(start_scan)))
                table.setItem(i, 3, QTableWidgetItem(str(end_scan)))
                table.setItem(i, 4, QTableWidgetItem("수정"))

                self.add_delete_button(table,i)

            self.table_layout.addWidget(table)

        except:
            return




    def get_company_name( self, company_num ):
        return COMPANY_DATA[company_num-1]["name"]

    def get_model_name( self, company_num, model_num ):
        return COMPANY_DATA[company_num-1]["models"][model_num-1]



    def _update_model_combo(self, company_text, model_combo):
        model_combo.clear()
        model_combo.addItem('-')
        if company_text != '-' and company_text.split('-')[0].isdigit():
            company_idx = int(company_text.split('-')[0])
            if 0 <= company_idx < len(COMPANY_DATA):
                models = COMPANY_DATA[company_idx]['models']
                for i, model in enumerate(models):
                    model_combo.addItem(f"{model}")


    def on_company_changed(self, company_text):
        self._update_model_combo(company_text, self.widgets1['model'])


    def on_company_changed2(self, company_text):
        self._update_model_combo(company_text, self.widgets2['model'])



    def common_command(self, DIR, CMD, data_str=None):
        command = ptcl.STX + DIR + CMD + (data_str or "")
        command = add_tail(command)
        self.main_window.add_log(f"전송 >> {command}")
        response = self.main_window.send_command_unified(command)
        return command, response



