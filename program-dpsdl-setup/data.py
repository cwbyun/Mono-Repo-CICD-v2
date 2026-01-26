from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QDateEdit,
    QHBoxLayout, QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt, QDate

from communication import *
from utils import *
import protocol as ptcl

from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+
from pathlib import Path
import time
import csv
import sys


class DataTab(QWidget):
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

        content = QWidget(self)
        content_layout = QVBoxLayout(content)

        layout0_config = [
                {'type': 'label', 'text': 'Data Tab의 명령은 Timeout=5초로, 명령 후 최소 5초의 시간이 걸립니다.'},
        ]
        group0, self.widgets0 = create_dynamic_group('NOTICE', layout0_config )

        layout1_config = [
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group1, self.widgets1 = create_dynamic_group('DATA List (cmd=3)', layout1_config )


        layout2_config = [
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group2, self.widgets2 = create_dynamic_group('Latest DATA (cmd=C)', layout2_config )

        layout3_config = [
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group3, self.widgets3 = create_dynamic_group('All DATA (cmd=D)', layout3_config )

        layout4_config = [
                {'type': 'input_pair', 'label':'Data in Folder Number:', 'name':'data_in_folder'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group4, self.widgets4 = create_dynamic_group('Data in Folder (cmd=4)', layout4_config )

        layout5_config = [
                {'type': 'input_pair', 'label':'Folder Number:', 'name':'folder_number'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group5, self.widgets5 = create_dynamic_group('Folder Number (cmd=9)', layout5_config )


        layout6_config = [
                {'type': 'date_range', 'label': '날짜 범위 폴더 정보 조회:', 'name': 'day_range', 'format': 'yyyy-MM-dd', 'width': 150},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group6, self.widgets6 = create_dynamic_group('날짜 범위의 폴더 조회 (cmd=B)', layout6_config )


        #layout6_config = [
                #{'type': 'date_range', 'label': '날짜 범위 폴더 정보 조회:', 'name': 'day_range', 'format': 'yyyy-MM-dd', 'width': 110},
                #{'type': 'button', 'text':'GET', 'name':'get_btn'},
        #]
        #group6, self.widgets6 = create_dynamic_group('날짜 범위의 폴더 조회 (cmd=B)', layout6_config )


        layout7_config = [
                {'type': 'input_pair', 'label':'Folder Number:', 'name':'one_data_list'},
                {'type': 'input_pair', 'label':'Folder Information:', 'name':'folder_information'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group7, self.widgets7 = create_dynamic_group('One Data List (Folder Information) (cmd=A)', layout7_config )
        self.widgets7['folder_information'].setFixedWidth(250)

        layout8_config = [
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group8, self.widgets8 = create_dynamic_group('SD Card File List (cmd=E)', layout8_config )

        layout9_config = [
                {'type': 'date', 'label': 'SD Card File Data(오늘날짜불가):', 'name': 'sd_card_file_data', 'format': 'yyyy-MM-dd', 'width': 150},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group9, self.widgets9 = create_dynamic_group('SD Card File Data (cmd=F)', layout9_config )


        layout10_config = [
                {'type': 'input_pair', 'label': 'Number Data:', 'name': 'number_data'},
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group10, self.widgets10 = create_dynamic_group('Number Data (cmd=G)', layout10_config )

        layout11_config = [
                {'type': 'button', 'text':'GET', 'name':'get_btn'},
        ]
        group11, self.widgets11 = create_dynamic_group('Alarm Data (cmd=H)', layout11_config )

        layout12_config = [
                {'type': 'button', 'text':'STOP', 'name':'get_btn'},
        ]
        group12, self.widgets12 = create_dynamic_group('Stop Reading Logger (cmd=S)', layout12_config )


        layout13_config = [
                {'type': 'date_time', 'label': '설정시간:', 'name': 'datetime', 'default_time': '00:00', 'date_width': 110, 'time_width': 70},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
        ]
        group13, self.widgets13 = create_dynamic_group('Setting Date & Time (cmd=6)', layout13_config )

        layout14_config = [
                {'type': 'input_pair', 'label': 'interval time:', 'name': 'interval_time'},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
        ]
        group14, self.widgets14 = create_dynamic_group('Interval Time (cmd=7)', layout14_config )


        content_layout.addWidget(group0)  # CMD=3
        content_layout.addWidget(group1)  # CMD=3
        content_layout.addWidget(group4)  # 4
        content_layout.addWidget(group5)  # 9
        content_layout.addWidget(group7)  # A
        content_layout.addWidget(group6)  # B
        content_layout.addWidget(group2)  # C
        content_layout.addWidget(group3)  # D
        content_layout.addWidget(group8)  # E
        content_layout.addWidget(group9)  # F
        content_layout.addWidget(group10)  # G
        content_layout.addWidget(group11)  # H
        content_layout.addWidget(group12)  # S
        content_layout.addWidget(group13)  # 6
        content_layout.addWidget(group14)  # 7


        content_layout.addStretch(1)
        scroll.setWidget(content)
        #main_layout.addWidget(scroll)
        #main_layout.addWidget(group2)
        #main_layout.addWidget(group3)
        #main_layout.addWidget(group4)
        #main_layout.addWidget(group5)
        #main_layout.addWidget(group6)
        #main_layout.addWidget(group7)

        main_layout.addWidget(scroll)
        main_layout.addStretch(1)



        self.widgets1['get_btn'].clicked.connect( self.data_list_get_btn )
        #self.widgets1['dl_25_get_btn'].clicked.connect( self.data_list_dl25_get_btn )

        self.widgets2['get_btn'].clicked.connect( self.latest_data_get_btn )
        self.widgets3['get_btn'].clicked.connect( self.all_data_get_btn )


        self.widgets4['get_btn'].clicked.connect( self.data_in_folder_get_btn )


        self.widgets5['get_btn'].clicked.connect( self.folder_number_get_btn )
        self.widgets6['get_btn'].clicked.connect( self.folder_in_range_get_btn )
        self.widgets7['get_btn'].clicked.connect( self.one_data_list_get_btn )
        self.widgets8['get_btn'].clicked.connect( self.sd_card_file_list_get_btn )
        self.widgets9['get_btn'].clicked.connect( self.sd_card_file_data_get_btn )
        self.widgets10['get_btn'].clicked.connect( self.number_data_get_btn )
        self.widgets11['get_btn'].clicked.connect( self.alarm_data_get_btn )
        self.widgets12['get_btn'].clicked.connect( self.stop_reading_get_btn )
        self.widgets13['set_btn'].clicked.connect( self.setting_date_time_set_btn )
        self.widgets14['set_btn'].clicked.connect( self.interval_time_set_btn )




    def interval_time_set_btn( self ):
        data_str = str(int(self.widgets14['interval_time'].text())).zfill(4)
        command, response = self.data_command( "7", data_str )

    def setting_date_time_set_btn( self ):
        data_str = self.widgets13['datetime_date'].date().toString("yyMMdd")
        data_str += (self.widgets13['datetime_time'].text() or '00:00').replace(':','')
        command, response = self.data_command( "6", data_str )





    def stop_reading_get_btn(self):
        command, response = self.data_command("S", log=True )
    
    def alarm_data_get_btn(self):
        command, response = self.data_command("H", log=True )

    def number_data_get_btn(self):
        raw = (self.widgets10['number_data'].text() or "").strip()

        if raw == "":
            n = 1                       # 비었으면 기본값 1
        else:
            try:
                n = int(raw)            # 숫자만 허용
            except ValueError:
                self.main_window.add_log("숫자를 입력하세요.")
                return
            if n < 1:                   # 0 이하 입력 방지(원치 않으면 제거)
                n = 1
            elif n > 9999:
                n = 9999

        data_str = f"{n:04d}"           # -> "0001" ~ "9999"
        command, response = self.data_command("G", data_str, log=True)









    def sd_card_file_data_get_btn( self ):
        data_str = self.widgets9['sd_card_file_data_start'].date().toString("yyyyMMdd")
        command, response = self.data_command( "F", data_str, log=True )


    def sd_card_file_list_get_btn( self ):
        command, response = self.data_command( "E", log=True )




    def one_data_list_get_btn( self ):
        try:
            data_str = self.widgets7['one_data_list'].text().zfill(4)
            #n = extract_number_from_text( self.widgets7['one_data_list'].text() )
            #data_str = f"{n:04d}"
        except:
            self.main_window.add_log(f"폴더 번호를 넣으세요.")
            return

        command, response = self.data_command( "A", data_str, log=True )

        self.widgets7['folder_information'].setText(response)




    def folder_in_range_get_btn( self ):
        self.main_window.add_log("Data를 불러오고 있습니다. 잠시만 기다리세요...")
        start_yymmdd = self.widgets6['day_range_start'].date().toString("yyMMdd")
        end_yymmdd   = self.widgets6['day_range_end'].date().toString("yyMMdd")

        data_str = start_yymmdd+end_yymmdd

        command, response = self.data_command( "B", data_str, log=True )

        filename = self.get_date("folder_in_range")

        self.save_response_as_list( response, filename )




    def folder_number_get_btn( self ):
        command, response = self.data_command( "9", log=True )

        print("res in data.py = ", response )
        
        r = int(response)
        print("int(res) in data.py = ", response )
        self.widgets5['folder_number'].setText(str(r))






    def data_in_folder_get_btn( self ):
        try:
            folder_number = self.widgets4['data_in_folder'].text().zfill(4)
        except:
            self.main_window.add_log(f"폴더 번호를 넣으세요.")
            return

        command, response = self.data_command( "4", folder_number, log=True )

        # Auto-detect format based on first character and parse accordingly
        self.parse_and_save_sensor_data_auto(response, folder_number)

    def parse_and_save_sensor_data_auto(self, response, folder_number):
        """Auto-detect DL24/DL25 format and parse accordingly"""
        try:
            # Convert response to string if needed
            response_str = response.decode("utf-8", "replace") if isinstance(response, (bytes, bytearray)) else response

            # Get first non-empty line to detect format
            lines = [line.strip() for line in response_str.splitlines() if line.strip() and line.strip() != "END"]

            if not lines:
                self.main_window.add_log("응답 데이터가 없습니다.")
                return

            first_line = lines[0]
            if ':' in first_line:
                first_char = first_line.split(':')[0][0] if first_line.split(':')[0] else ''

                if first_char == '0':
                    # DL24 format
                    self.main_window.add_log("DL24 형식으로 감지되었습니다.")
                    self.parse_and_save_sensor_data(response, folder_number)
                elif first_char == '1':
                    # DL25 format
                    self.main_window.add_log("DL25 형식으로 감지되었습니다.")
                    self.parse_and_save_sensor_data_dl25(response, folder_number)
                else:
                    self.main_window.add_log(f"알 수 없는 데이터 형식입니다. 첫 문자: {first_char}")
            else:
                self.main_window.add_log("데이터 형식을 인식할 수 없습니다.")

        except Exception as e:
            self.main_window.add_log(f"데이터 형식 감지 실패: {e}")


    def parse_and_save_sensor_data_dl25(self, response, folder_number):
        """Parse DL25 sensor data response and save as CSV file"""
        try:
            # Convert response to string if needed
            response_str = response.decode("utf-8", "replace") if isinstance(response, (bytes, bytearray)) else response

            # Split by \r and remove empty lines
            lines = [line.strip() for line in response_str.replace('\r\n', '\r').split('\r') if line.strip()]

            if not lines:
                self.main_window.add_log("응답 데이터가 없습니다.")
                return

            # Group data by PK (Primary Key)
            current_time = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
            pk_groups = {}

            for line in lines:
                parts = line.split(':')
                if len(parts) >= 5:
                    sensor_code = parts[0]  # e.g., "1000", "1001", etc.
                    data_value = parts[1]
                    unit_code = parts[2]    # 3,2,2,1,B,C for units
                    manufacturer_model = parts[3]
                    serial_number = parts[4]

                    # Extract PK (second and third digits) and sensor type (fourth digit)
                    if len(sensor_code) >= 4:
                        pk = sensor_code[1:3]  # "00", "01", etc.
                        sensor_type = sensor_code[3]  # "0"=줄길이, "1"=x각도, "2"=y각도, "3"=온도, "4"=전압, "5"=전류

                        # Initialize PK group if not exists
                        if pk not in pk_groups:
                            pk_groups[pk] = {
                                '줄길이': 0,
                                'x각도': 0,
                                'y각도': 0,
                                '온도(도)': 0,
                                '전압(V)': 0,
                                '전류(mA)': 0,
                                '시리얼번호': serial_number
                            }

                        # Map sensor types to data
                        if sensor_type == "0":
                            pk_groups[pk]['줄길이'] = int(data_value) if data_value.isdigit() else 0
                        elif sensor_type == "1":
                            pk_groups[pk]['x각도'] = int(data_value) if data_value.isdigit() else 0
                        elif sensor_type == "2":
                            pk_groups[pk]['y각도'] = int(data_value) if data_value.isdigit() else 0
                        elif sensor_type == "3":
                            pk_groups[pk]['온도(도)'] = int(data_value) if data_value.isdigit() else 0
                        elif sensor_type == "4":
                            pk_groups[pk]['전압(V)'] = int(data_value) if data_value.isdigit() else 0
                        elif sensor_type == "5":
                            pk_groups[pk]['전류(mA)'] = int(data_value) if data_value.isdigit() else 0

            # Create CSV filename with folder number and timestamp
            ts = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d_%H%M%S")

            if getattr(sys, 'frozen', False):
                application_path = Path(sys.executable).parent
            else:
                application_path = Path(__file__).parent

            out_dir = application_path / "logs"
            out_dir.mkdir(parents=True, exist_ok=True)
            csv_filename = out_dir / f"sensor_data_dl25_folder_{folder_number}_{ts}.csv"

            # Write CSV file
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['날짜-시간', '줄길이', 'x각도', 'y각도', '온도(도)', '전압(V)', '전류(mA)', '시리얼번호']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write header
                writer.writeheader()

                # Write data rows for each PK group (sorted by PK)
                for pk in sorted(pk_groups.keys()):
                    sensor_data = pk_groups[pk]
                    csv_row = {
                        '날짜-시간': current_time,
                        '줄길이': sensor_data.get('줄길이', 0),
                        'x각도': sensor_data.get('x각도', 0),
                        'y각도': sensor_data.get('y각도', 0),
                        '온도(도)': sensor_data.get('온도(도)', 0),
                        '전압(V)': sensor_data.get('전압(V)', 0),
                        '전류(mA)': sensor_data.get('전류(mA)', 0),
                        '시리얼번호': sensor_data.get('시리얼번호', '')
                    }
                    writer.writerow(csv_row)

            self.main_window.add_log(f"DL25 센서 데이터 CSV 파일 저장 완료: {csv_filename}")

        except Exception as e:
            self.main_window.add_log(f"DL25 센서 데이터 파싱/저장 실패: {e}")

    def parse_and_save_sensor_data(self, response, folder_number):
        """Parse sensor data response and save as CSV file"""
        try:
            # Convert response to string if needed
            response_str = response.decode("utf-8", "replace") if isinstance(response, (bytes, bytearray)) else response

            # Split into lines and remove empty lines and 'END'
            lines = [line.strip() for line in response_str.splitlines() if line.strip() and line.strip() != "END"]

            if not lines:
                self.main_window.add_log("응답 데이터가 없습니다.")
                return

            # Parse sensor data - group by sensor sets
            current_time = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
            sensor_sets = []
            current_set = {}

            for line in lines:
                parts = line.split(':')
                if len(parts) >= 4:
                    sensor_type = parts[0]
                    data_value = parts[1]
                    manufacturer_model = parts[3]

                    # Extract manufacturer and model
                    manufacturer = manufacturer_model[:2] if len(manufacturer_model) >= 2 else "00"
                    model = manufacturer_model[2:4] if len(manufacturer_model) >= 4 else "00"

                    # Map sensor types and convert to numeric values
                    if sensor_type == "0001":
                        # New sensor set starts with 줄길이
                        if current_set:  # Save previous set if exists
                            sensor_sets.append(current_set)
                        current_set = {
                            '줄길이': int(data_value) if data_value.isdigit() else 0,
                            'x각도': 0,
                            'y각도': 0,
                            '강수량': 0,
                            '제조업체': int(manufacturer) if manufacturer.isdigit() else 0,
                            '모델명': int(model) if model.isdigit() else 0
                        }
                    elif sensor_type == "0052":
                        current_set['x각도'] = int(data_value) if data_value.isdigit() else 0
                    elif sensor_type == "0053":
                        current_set['y각도'] = int(data_value) if data_value.isdigit() else 0
                    elif sensor_type == "0255":
                        current_set['강수량'] = int(data_value) if data_value.isdigit() else 0

            # Add the last set
            if current_set:
                sensor_sets.append(current_set)

            # Create CSV filename with folder number and timestamp
            ts = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d_%H%M%S")

            if getattr(sys, 'frozen', False):
                application_path = Path(sys.executable).parent
            else:
                application_path = Path(__file__).parent

            out_dir = application_path / "logs"
            out_dir.mkdir(parents=True, exist_ok=True)
            csv_filename = out_dir / f"sensor_data_folder_{folder_number}_{ts}.csv"

            # Write CSV file
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['날짜-시간', '줄길이', 'x각도', 'y각도', '강수량', '제조업체', '모델명']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write header
                writer.writeheader()

                # Write data rows for each sensor set
                for sensor_data in sensor_sets:
                    csv_row = {
                        '날짜-시간': current_time,
                        '줄길이': sensor_data.get('줄길이', 0),
                        'x각도': sensor_data.get('x각도', 0),
                        'y각도': sensor_data.get('y각도', 0),
                        '강수량': sensor_data.get('강수량', 0),
                        '제조업체': sensor_data.get('제조업체', 0),
                        '모델명': sensor_data.get('모델명', 0)
                    }
                    writer.writerow(csv_row)

            self.main_window.add_log(f"센서 데이터 CSV 파일 저장 완료: {csv_filename}")

        except Exception as e:
            self.main_window.add_log(f"센서 데이터 파싱/저장 실패: {e}")

    def latest_data_get_btn( self ):
        command, response = self.data_command( "C", log=True )

    def all_data_get_btn( self ):
        self.main_window.add_log("Data를 불러오고 있습니다. 잠시만 기다리세요...")
        command, response = self.data_command( "D", log=False )

        filename = self.get_date( "all_data" )


        self.save_response_as_list( response, filename )


    def get_date( self, name: str ) -> str :
        # 파일명: sensor_data_YYYYMMDD_HHMMSS.txt
        ts = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d_%H%M%S")

        if getattr(sys, 'frozen', False):
            # 실행 파일로 실행될 때 (PyInstaller)
            application_path = Path(sys.executable).parent
        else:
            # 스크립트로 실행될 때
            application_path = Path(__file__).parent

        out_dir = application_path / "logs"

        try:
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{name}_{ts}.txt"
            return out_path
        except OSError as e:
            self.main_window.add_log(f"디렉토리 생성 실패: {e}")
            return None

    def save_response_as_list(self, response, out_path):
        if not out_path:
            self.main_window.add_log("로그 파일을 저장할 수 없습니다. 디렉토리 생성 오류.")
            return

        # response -> 줄 리스트(END 제외, 꼬리표 " <- (...)" 제거)
        s = response.decode("utf-8", "replace") if isinstance(response, (bytes, bytearray)) else response
        lines = [ln.split(" <- ", 1)[0].strip() for ln in s.splitlines() if ln.strip() and ln.strip() != "END"]

        # 저장(그냥 줄 단위 텍스트)
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            self.main_window.add_log(f"저장 완료: {out_path}")
        except OSError as e:
            self.main_window.add_log(f"로그 파일 저장 실패: {e}")



    def data_list_get_btn( self ):

        
        #self.main_window.add_log("Data를 불러오고 있습니다. 잠시만 기다리세요...")
        #time.sleep(1)
        command, response = self.data_command( "3" )

        # 파일명: sensor_data_YYYYMMDD_HHMMSS.txt
        #ts = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d_%H%M%S")
        #out_dir = Path("logs")
        #out_dir.mkdir(parents=True, exist_ok=True)
        #out_path = out_dir / f"data_list_{ts}.txt"
        out_path = self.get_date( "data_list" )

        self.save_response_as_list( response, out_path )

        #ans = trim_string( response, 4, 3 )

        #return_tuple = parse_by_lengths( ans, "11111" )

        #relay_name = ["in1", "in2", "in3", "in4", "in5" ]
        #print("res = ", response)







    def data_command( self, CMD, data_str=None, log=False ):
        #ip, port = self.main_window.get_ip_port()

        if data_str :
            command = ptcl.STX + CMD + data_str
        else:
            command = ptcl.STX + CMD

        command += "Q"

        #self.main_window.add_log(f"전송 >> {command}")
        #response = send_command(command, ip, port)
        response = self.main_window.send_command_unified(command)
        #if log : self.main_window.add_log(f"응답 << {response}")

        return command, response




