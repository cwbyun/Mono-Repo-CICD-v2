from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea,
    QHBoxLayout, QGroupBox, QTableWidget, QTableWidgetItem, QDialog, QComboBox,
    QSizePolicy
)
from PyQt6.QtCore import Qt
from communication import *
from utils import *
import protocol as ptcl
import time
import re

# 통합된 업체 및 모델 데이터 구조
COMPANY_DATA = [
    {"name": "디피에스글로벌", "models": ["DTA-01", "DP-17"]},
    {"name": "주원엔지니어링", "models": ["JTA-01", "JW-17"]},
    {"name": "STR", "models": ["STM-01", "STW-01"]},
    {"name": "G-SEN", "models": ["GSD-9100", "GSD-7000", "GSD-6100"]},
    {"name": "APM-Tech", "models": ["AT-10", "WT-1000", "INT-7300"]},
    {"name": "성진지오텍", "models": ["SJ-2001", "SJ-4200", "SJ-4700"]},
    {"name": "하이드로넷", "models": ["MK-21"]},
    {"name": "신호시스템", "models": ["SHN530-2"]},
    {"name": "리온테크", "models": ["SCA126V-10", "HCA526V-10", "ACA626V-10"]},
    {"name": "다음테크", "models": ["INT-7800D", "INT-8100"]},
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

        group1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        group1.setMaximumHeight(group1.sizeHint().height())

        # Company Table
        self.table_container = QWidget()
        self.table_layout = QVBoxLayout(self.table_container)
        self.table_layout.setContentsMargins(0, 0, 0, 0)
        self.table_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


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
            {'type': 'button', 'text': '전체 선택/해제', 'name': 'toggle_all_btn'},
            {'type': 'button', 'text': '선택 삭제', 'name': 'delete_selected_btn'},
        ]
        group2, self.widgets2 = create_dynamic_group('Sensor ID (cmd=7D)', layout2_config, input_width=100)

        self.widgets2['model'].setMinimumWidth(100)
        self.widgets2['pk1'].setMinimumWidth(30)
        self.widgets2['pk2'].setMinimumWidth(30)
        self.widgets2['id1'].setMinimumWidth(30)
        self.widgets2['id2'].setMinimumWidth(30)

        group2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        group2.setMaximumHeight(group2.sizeHint().height())

        # Sensor ID Table
        self.id_table_container = QWidget()
        self.id_table_layout = QVBoxLayout(self.id_table_container)
        self.id_table_layout.setContentsMargins(0, 0, 0, 0)
        self.id_table_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)





        main_layout.addWidget(group1)
        main_layout.addWidget(self.table_container) # Maker Table


        main_layout.addWidget(group2)
        main_layout.addWidget(self.id_table_container) # Maker Table
        main_layout.setStretchFactor(self.table_container, 1)
        main_layout.setStretchFactor(self.id_table_container, 2)



        self.widgets1['add_btn'].clicked.connect(self.sensor_maker_add_btn)
        self.widgets1['get_btn'].clicked.connect(self.sensor_maker_get_btn)
        self.widgets1['company'].currentTextChanged.connect(self.on_company_changed)


        self.widgets2['set_btn'].clicked.connect(self.sensor_id_set_btn)
        self.widgets2['get_btn'].clicked.connect(self.sensor_id_get_btn)
        self.widgets2['toggle_all_btn'].clicked.connect(self.toggle_all_ids)
        self.widgets2['delete_selected_btn'].clicked.connect(self.delete_selected_ids)
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

            pk1_text = self.widgets2['pk1'].text().strip()
            pk2_text = self.widgets2['pk2'].text().strip()
            id1_text = self.widgets2['id1'].text().strip()
            id2_text = self.widgets2['id2'].text().strip()

            if pk2_text == "0":
                pk2_text = ""
            if id2_text == "0":
                id2_text = ""

            if not pk1_text or not id1_text:
                self.main_window.add_log("PK/ID 입력이 필요합니다.")
                return
            if not pk1_text.isdigit():
                self.main_window.add_log("PK는 숫자만 입력 가능합니다.")
                return
            if pk2_text and not pk2_text.isdigit():
                self.main_window.add_log("PK 범위 입력은 숫자만 가능합니다.")
                return
            if pk2_text and not id2_text:
                self.main_window.add_log("PK to 입력 시 ID to도 필요합니다.")
                return

            pk1 = int(pk1_text)
            pk2 = int(pk2_text) if pk2_text else None
            id1_parsed = self.parse_sensor_id(gg, id1_text)
            if not id1_parsed:
                self.main_window.add_log("ID 형식이 올바르지 않습니다. (예: 1001, STM-1001)")
                return


            print("pk1 = ", pk1 )
            print("pk2 = ", pk2 )


            if id2_text:
                id2_parsed = self.parse_sensor_id(gg, id2_text)
                if not id2_parsed:
                    self.main_window.add_log("ID to 형식이 올바르지 않습니다. (예: 1003, STM-1003)")
                    return

                id1_prefix, id1_num, id1_width = id1_parsed
                id2_prefix, id2_num, id2_width = id2_parsed
                if id1_prefix.upper() != id2_prefix.upper():
                    self.main_window.add_log("ID 접두어가 일치하지 않습니다.")
                    return
                if id1_width and id2_width and id1_width != id2_width:
                    self.main_window.add_log("ID 자리수가 일치하지 않습니다. (예: 001 ~ 010)")
                    return
                if id2_num < id1_num:
                    self.main_window.add_log("ID 범위가 올바르지 않습니다.")
                    return

                id_width = id1_width if id1_width else id2_width
                count = id2_num - id1_num
                if pk2 is not None:
                    if pk2 < pk1:
                        self.main_window.add_log("PK 범위가 올바르지 않습니다.")
                        return
                    if pk2 - pk1 != count:
                        self.main_window.add_log("PK 범위와 ID 범위 개수가 일치하지 않습니다.")
                        return

                spk_fixed = str(pk1).zfill(2)
                for i in range(0, count + 1):
                    spk = str(pk1 + i).zfill(2) if pk2 is not None else spk_fixed
                    sid = self.format_sensor_id(id1_prefix, id1_num + i, id_width)
                    data_str = data0 + spk + sid + ","
                    command, response = self.common_command( "W", "7D", data_str )
            else:
                spk = str(pk1).zfill(2)
                sid = self.build_sensor_id(gg, id1_text)
                if not sid:
                    self.main_window.add_log("ID 입력이 올바르지 않습니다.")
                    return
                data_str = data0 + spk + sid + ","
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
            table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            table.setColumnCount(8)
            table.setHorizontalHeaderLabels([ "Line", "Company", "Model", "PK", "ID", "수정", "삭제", "선택"])
            table.setRowCount(n)

            # 컬럼 너비 설정 (픽셀 단위)
            table.setColumnWidth(0, 50)  # Line 컬럼
            table.setColumnWidth(1, 250)  # Company 컬럼
            table.setColumnWidth(2, 200)  # Model 컬럼
            table.setColumnWidth(3, 100)  # PK
            table.setColumnWidth(4, 200)  # ID
            table.setColumnWidth(5, 50)  # Modify Button
            table.setColumnWidth(6, 50)  # Delete Button
            table.setColumnWidth(7, 50)  # Select

            for i in range(n):
                print(parts[i])

                company_num = int(parts[i][0:2])
                model_num   = int(parts[i][2:4])
                pk_text     = parts[i][4:6]
                pk          = int(pk_text)
                sensor_id   = parts[i][6:]
                #0123 456789 012345
                #0202 000000 000255

                print("company = ", self.get_company_name( company_num ))
                print("modelny = ", self.get_model_name( company_num, model_num ))

                company = self.get_company_name( company_num )
                model = self.get_model_name( company_num, model_num )



                #table.setItem(i, 0, QTableWidgetItem(str(i+1)))
                line_item = QTableWidgetItem(str(int(line)+1))
                company_item = QTableWidgetItem(company)
                model_item = QTableWidgetItem(model)
                pk_item = QTableWidgetItem(str(pk))
                id_item = QTableWidgetItem(sensor_id)
                id_item.setData(Qt.ItemDataRole.UserRole, {
                    "line": int(line),
                    "company": company,
                    "model": model,
                    "pk": pk_text,
                    "sensor_id": sensor_id,
                })

                table.setItem(i, 0, line_item)
                table.setItem(i, 1, company_item)
                table.setItem(i, 2, model_item)
                table.setItem(i, 3, pk_item)
                table.setItem(i, 4, id_item)
                #table.setItem(i, 5, QTableWidgetItem("수정"))

                self.add_id_modify_button(table,i)
                self.add_id_delete_button(table,i)
                select_item = QTableWidgetItem()
                select_item.setFlags(select_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                select_item.setCheckState(Qt.CheckState.Unchecked)
                table.setItem(i, 7, select_item)


            table.resizeRowsToContents()
            self.adjust_table_height(table, table.rowCount(), set_max=False)
            self.id_table_layout.addWidget(table)
            self.id_table = table

    
        except:
            return



    def modify_and_delete_id_row(self, table, button, row, action ):
        # Sensor ID를 수정하거나 삭제한다.
        try :
            line_text = table.item(row,0).text()
            company   = table.item(row,1).text()
            model     = table.item(row,2).text()
            pk_text   = table.item(row,3).text()
            sensor_id = table.item(row,4).text()

            original = None
            id_item = table.item(row,4)
            if id_item:
                original = id_item.data(Qt.ItemDataRole.UserRole)
            if isinstance(original, dict):
                old_line = original.get("line", int(line_text) - 1)
                old_company = original.get("company", company)
                old_model = original.get("model", model)
                old_sensor_id = original.get("sensor_id", sensor_id)
            else:
                old_line = int(line_text) - 1
                old_company = company
                old_model = model
                old_sensor_id = sensor_id

            line = str(int(line_text) - 1)
            pk = str(int(pk_text)).zfill(2)

            print("line = ", line)
            print("com = ", company)
            print("mod = ", model)
            print("pk = ", pk)
            print("s_id = ", sensor_id)


            company_num = self.get_company_index(company)
            model_num = self.get_model_index(company_num, model)
            if company_num < 0 or model_num < 0:
                self.main_window.add_log("오류: 업체 또는 모델 정보가 올바르지 않습니다.")
                return

            print("com = ", company_num)
            print("mod = ", model_num)

            if action == "modify":
                old_company_num = self.get_company_index(old_company)
                old_model_num = self.get_model_index(old_company_num, old_model)
                if old_company_num < 0 or old_model_num < 0:
                    self.main_window.add_log("오류: 기존 업체 또는 모델 정보가 올바르지 않습니다.")
                    return

                delete_str = str(old_line)
                delete_str += str(old_company_num+1).zfill(2)
                delete_str += str(old_model_num+1).zfill(2)
                delete_str += old_sensor_id + ","

                command, response = self.common_command( "W", "7E", delete_str )
                is_valid, error_message = check_response(response)
                if not is_valid:
                    self.main_window.add_log(f"응답 검증 실패: {error_message}")
                    return

                data_str  = line
                data_str += str(company_num+1).zfill(2)
                data_str += str(model_num+1).zfill(2)
                data_str += pk
                data_str += sensor_id + ","

                command, response = self.common_command( "W", "7D", data_str )
                is_valid, error_message = check_response(response)
                if not is_valid:
                    self.main_window.add_log(f"응답 검증 실패: {error_message}")
                    return

            if action == "delete":
                data_str  = line
                data_str += str(company_num+1).zfill(2)
                data_str += str(model_num+1).zfill(2)
                data_str += sensor_id + ","

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
            if self.delete_id_row_by_table(table, row):
                self.sensor_id_get_btn()
        except:
            return

    def delete_id_row_by_table(self, table, row) -> bool:
        try:
            line_text = table.item(row,0).text()
            company   = table.item(row,1).text()
            model     = table.item(row,2).text()
            sensor_id = table.item(row,4).text()

            original = None
            id_item = table.item(row,4)
            if id_item:
                original = id_item.data(Qt.ItemDataRole.UserRole)
            if isinstance(original, dict):
                line = str(original.get("line", int(line_text) - 1))
                company = original.get("company", company)
                model = original.get("model", model)
                sensor_id = original.get("sensor_id", sensor_id)
            else:
                line = str(int(line_text) - 1)

            company_num = self.get_company_index(company)
            model_num = self.get_model_index(company_num, model)
            if company_num < 0 or model_num < 0:
                self.main_window.add_log("오류: 업체 또는 모델 정보가 올바르지 않습니다.")
                return False

            data_str  = line
            data_str += str(company_num+1).zfill(2)
            data_str += str(model_num+1).zfill(2)
            data_str += sensor_id  + ","

            command, response = self.common_command( "W", "7E", data_str )
            is_valid, error_message = check_response(response)
            if not is_valid:
                self.main_window.add_log(f"응답 검증 실패: {error_message}")
                return False

            return True
        except Exception as e:
            self.main_window.add_log(f"삭제 실패: {e}")
            return False


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

    def delete_selected_ids(self):
        table = getattr(self, "id_table", None)
        if not table:
            self.main_window.add_log("Sensor ID 테이블이 없습니다.")
            return

        selected_rows = []
        for row in range(table.rowCount()):
            item = table.item(row, 7)
            if item and item.checkState() == Qt.CheckState.Checked:
                selected_rows.append(row)

        if not selected_rows:
            self.main_window.add_log("삭제할 항목을 선택하세요.")
            return

        for row in selected_rows:
            self.delete_id_row_by_table(table, row)

        self.sensor_id_get_btn()

    def toggle_all_ids(self):
        table = getattr(self, "id_table", None)
        if not table:
            self.main_window.add_log("Sensor ID 테이블이 없습니다.")
            return

        any_unchecked = False
        for row in range(table.rowCount()):
            item = table.item(row, 7)
            if item and item.checkState() != Qt.CheckState.Checked:
                any_unchecked = True
                break

        new_state = Qt.CheckState.Checked if any_unchecked else Qt.CheckState.Unchecked
        for row in range(table.rowCount()):
            item = table.item(row, 7)
            if item:
                item.setCheckState(new_state)

    def adjust_table_height(self, table, row_count, apply=True, fixed_height=None, set_max=True):
        header = table.horizontalHeader().height()
        frame = table.frameWidth() * 2
        height = header + frame
        for row in range(row_count):
            height += table.rowHeight(row)
        if fixed_height is not None:
            height = fixed_height
        if apply:
            table.setMinimumHeight(height)
            if set_max:
                table.setMaximumHeight(height)
        return height











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
            if self.delete_maker_row_by_table(table, row):
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

    def add_modify_button( self, table, row):
        btn = QPushButton("수정")
        btn.clicked.connect(lambda del_action, b=btn: self.modify_maker_row(table, b, row))

        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addWidget(btn)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        table.setCellWidget(row, 4, widget)

    def modify_maker_row(self, table, button, row):
        try:
            if not self.delete_maker_row_by_table(table, row):
                return

            company = table.item(row, 0).text()
            model = table.item(row, 1).text()
            start_range = table.item(row, 2).text()
            end_range = table.item(row, 3).text()

            company_num = self.get_company_index(company)
            model_num = self.get_model_index(company_num, model)
            if company_num < 0 or model_num < 0:
                self.main_window.add_log("오류: 업체 또는 모델 정보가 올바르지 않습니다.")
                return

            data_str = str(company_num+1).zfill(2)
            data_str += str(model_num+1).zfill(2)
            data_str += str(extract_number_from_text(start_range)).zfill(6)
            data_str += str(extract_number_from_text(end_range)).zfill(6)

            command, response = self.common_command( "W", "7A", data_str )
            is_valid, error_message = check_response(response)
            if not is_valid:
                self.main_window.add_log(f"응답 검증 실패: {error_message}")
                return

            self.sensor_maker_get_btn()
        except Exception as e:
            self.main_window.add_log(f"수정 실패: {e}")

    def delete_maker_row_by_table(self, table, row) -> bool:
        try:
            company = table.item(row, 0).text()
            model = table.item(row, 1).text()
            start_range = table.item(row, 2).text()
            end_range = table.item(row, 3).text()

            original = None
            company_item = table.item(row, 0)
            if company_item:
                original = company_item.data(Qt.ItemDataRole.UserRole)
            if isinstance(original, dict):
                company = original.get("company", company)
                model = original.get("model", model)
                start_range = original.get("start_range", start_range)
                end_range = original.get("end_range", end_range)

            company_num = self.get_company_index(company)
            model_num = self.get_model_index(company_num, model)
            if company_num < 0 or model_num < 0:
                self.main_window.add_log("오류: 업체 또는 모델 정보가 올바르지 않습니다.")
                return False

            data_str  = str(company_num+1).zfill(2)
            data_str += str(model_num+1).zfill(2)
            data_str += str(extract_number_from_text(start_range)).zfill(6)
            data_str += str(extract_number_from_text(end_range)).zfill(6)

            command, response = self.common_command( "W", "7B", data_str )
            is_valid, error_message = check_response(response)
            if not is_valid:
                self.main_window.add_log(f"응답 검증 실패: {error_message}")
                return False

            return True
        except Exception as e:
            self.main_window.add_log(f"삭제 실패: {e}")
            return False



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
            self.maker_table_height = None



            ans = trim_string( response, 4, 3 )
            parts = ans.split(",")

            n = int(parts[0][0:2])
            print("n = ", n)

            parts[0] = parts[0][2:]

            # 테이블 생성
            table = QTableWidget()
            table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
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
                company_item = QTableWidgetItem(company)
                company_item.setData(Qt.ItemDataRole.UserRole, {
                    "company": company,
                    "model": model,
                    "start_range": str(start_scan).zfill(6),
                    "end_range": str(end_scan).zfill(6),
                })
                table.setItem(i, 0, company_item)
                table.setItem(i, 1, QTableWidgetItem(model))
                table.setItem(i, 2, QTableWidgetItem(str(start_scan)))
                table.setItem(i, 3, QTableWidgetItem(str(end_scan)))

                self.add_modify_button(table,i)
                self.add_delete_button(table,i)

            table.resizeRowsToContents()
            self.maker_table_height = self.adjust_table_height(table, table.rowCount(), set_max=False)
            self.table_layout.addWidget(table)

        except:
            return




    def get_company_name( self, company_num ):
        return COMPANY_DATA[company_num-1]["name"]

    def get_model_name( self, company_num, model_num ):
        return COMPANY_DATA[company_num-1]["models"][model_num-1]

    def build_sensor_id(self, model_text: str, raw_id: str) -> str:
        parsed = self.parse_sensor_id(model_text, raw_id)
        if not parsed:
            return ""
        prefix, number, width = parsed
        return self.format_sensor_id(prefix, number, width)

    def format_sensor_id(self, prefix: str, number: int, width: int) -> str:
        num_str = str(number)
        if width:
            num_str = num_str.zfill(width)
        return f"{prefix}{num_str}"

    def parse_sensor_id(self, model_text: str, raw_id: str):
        raw = raw_id.strip()
        if not raw:
            return None

        model_prefix = model_text.replace("-", "")

        if raw.isdigit():
            return (model_prefix, int(raw), 0)

        raw_no_sep = raw.replace("-", "").replace(" ", "")
        if raw_no_sep.upper().startswith(model_prefix.upper()) and len(raw_no_sep) > len(model_prefix):
            suffix = raw_no_sep[len(model_prefix):]
            if suffix.isdigit():
                width = len(suffix) if len(suffix) > 1 and suffix.startswith("0") else 0
                return (model_prefix, int(suffix), width)

        match = re.match(r'^(.*?)(\d+)$', raw)
        if not match:
            return None

        prefix_raw = match.group(1)
        num_str = match.group(2)
        if not num_str:
            return None

        prefix_norm = prefix_raw.replace("-", "").replace(" ", "")
        if not prefix_norm:
            send_prefix = model_prefix
        else:
            send_prefix = prefix_norm

        number = int(num_str)
        width = len(num_str) if len(num_str) > 1 and num_str.startswith("0") else 0
        return (send_prefix, number, width)



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
