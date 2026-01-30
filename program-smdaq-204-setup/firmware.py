from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QGroupBox, QFileDialog, QProgressBar, QApplication
)
from PyQt6.QtCore import ( Qt, QTimer )
from communication import *
from utils import *
import time
import protocol as ptcl


class FirmwareTab(QWidget):
    def __init__(self, parent):
        """
            'Fireware' 탭의 UI와 기능을 모두 담고 있는 클래스입니다.
            parent 인자로는 MainWindow의 인스턴스(self)가 전달됩니다.
        """

        super().__init__()
        self.main_window = parent

        main_layout = QVBoxLayout(self)

        # 서버 모드 경고 UI 추가
        #self.server_mode_warning = QGroupBox("⚠️ 서버 모드 경고")
        #self.server_mode_warning.setStyleSheet("""
        #    QGroupBox {
        #        font-weight: bold;
        #        border: 2px solid red;
        #        border-radius: 5px;
        #        margin-top: 10px;
        #        background-color: #ffeeee;
        #    }
        #    QGroupBox::title {
        #        subcontrol-origin: margin;
        #        left: 10px;
        #        padding: 0 5px 0 5px;
        #        color: red;
        #    }
        #""")
        
        #warning_layout = QVBoxLayout()
        #warning_label = QLabel("서버 모드에서는 펌웨어 업그레이드를 수행할 수 없습니다.\n"
        #                      "펌웨어 업그레이드를 위해서는 서버를 중지하고 클라이언트 모드를 사용하세요.")
        #warning_label.setWordWrap(True)

        #warning_label.setStyleSheet("color: red; font-weight: bold;")
        #warning_layout.addWidget(warning_label)
        #self.server_mode_warning.setLayout(warning_layout)
        #self.server_mode_warning.setVisible(False)  # 초기에는 숨김
        
        #main_layout.addWidget(self.server_mode_warning)


        # 펌웨어 파일 선택을 위한 그룹박스 생성
        file_selection_group = QGroupBox("Firmware File Selection")

        # 그룹박스 내부에서 사용할 레이아웃 (수평 방향)
        file_layout = QHBoxLayout()

        # 1. 파일 경로를 표시할 라벨과 읽기 전용 텍스트 상자
        file_path_label = QLabel("HEX File Path:")
        self.file_path_display = QLineEdit()
        self.file_path_display.setReadOnly(True) # 사용자가 직접 수정할 수 없도록 설정

        # 2. 파일 선택 대화상자를 열 버튼
        self.select_file_button = QPushButton("Select File...")

        # 수평 레이아웃에 위젯들 추가
        file_layout.addWidget(file_path_label)
        file_layout.addWidget(self.file_path_display, 1) # 텍스트 상자가 남은 공간을 모두 차지하도록 설정
        file_layout.addWidget(self.select_file_button)

        # 그룹박스에 수평 레이아웃 설정
        file_selection_group.setLayout(file_layout)

        # 메인 레이아웃에 그룹박스 추가
        main_layout.addWidget(file_selection_group)

        # 펌웨어 업그레이드 시작 버튼 (일단 비활성화)
        self.process_button = QPushButton("Start Firmware Upgrade")
        self.process_button.setEnabled( True )

        # --- 아래 3줄의 프로그레스 바 생성 코드를 추가하세요 ---
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setValue(0)



        main_layout.addWidget(self.process_button)
        main_layout.addWidget(self.progress_bar)




        # 위젯들을 위로 밀어 올리기 위한 스트레치 추가
        main_layout.addStretch(1)

        self.select_file_button.clicked.connect(self.open_file_dialog)

        self.flash_timeout_timer = QTimer(self)
        self.flash_timeout_timer.setSingleShot(True)
        self.flash_timeout_timer.setInterval(10000)
        self.flash_timeout_timer.timeout.connect(self.cancel_flash)

        self.process_button.clicked.connect(self.start_upgrade)
        
        # 서버 모드 상태 업데이트를 위한 타이머
        self.ui_update_timer = QTimer(self)
        #self.ui_update_timer.timeout.connect(self.update_ui_based_on_server_mode)
        self.ui_update_timer.start(1000)  # 1초마다 확인

    #def update_ui_based_on_server_mode(self):
    #    """서버 모드 상태에 따라 UI를 업데이트"""
    #    is_server_mode = self.main_window.is_server_mode()
        
    #    # 서버 모드 경고 표시/숨김
    #    self.server_mode_warning.setVisible(is_server_mode)
        
    #    # 서버 모드에서는 펌웨어 관련 UI 비활성화
    #    if is_server_mode:
    #        self.select_file_button.setEnabled(False)
    #        self.process_button.setEnabled(False)
    #    else:
    #        # 클라이언트 모드일 때는 파일 선택 여부에 따라 활성화
    #        self.select_file_button.setEnabled(True)
    #        is_file_selected = bool(self.file_path_display.text())
    #        self.process_button.setEnabled(is_file_selected)

    def start_upgrade( self ):
        """
        "Start Firmware Upgrade" 버튼 클릭 시 실행될 메인 메서드.
        """
        # 서버 모드 확인 - 이중 체크
        #if self.main_window.is_server_mode():
        #    self.main_window.add_log("❌ 오류: 서버 모드에서는 펌웨어 업그레이드를 수행할 수 없습니다.")
        #    self.main_window.add_log("펌웨어 업그레이드를 위해서는 먼저 서버를 중지하세요.")
        #    return

        # 1. 선택된 파일 경로 가져오기
        file_path = self.file_path_display.text()
        if not file_path:
            self.main_window.add_log("오류: 펌웨어 파일이 선택되지 않았습니다.")
            return

        # 2. 업그레이드 중 UI 비활성화
        self.main_window.add_log(f"'{file_path}' 파일로 펌웨어 업그레이드를 시작합니다.")
        self.select_file_button.setEnabled(False)
        self.process_button.setEnabled(False)

        try:

            #self.main_window.add_log("HEX 파일을 읽는 중...")
            #with open(file_path, 'r') as f:
            #    hex_lines = f.readlines()
            #self.main_window.add_log(f"총 {len(hex_lines)} 라인을 읽었습니다.")
    
            # 4. (구현 예정) BOOT 모드 진입 명령 전송
            self.main_window.add_log("장비를 BOOT 모드로 전환합니다...")

            try:
                # ... (파일 읽기 코드) ...

                # 4. BOOT 모드 진입 명령 전송
                self.main_window.add_log("장비를 BOOT 모드로 전환합니다...")

                # 'SWNB' 명령을 3회 전송
                for i in range(3):
                    self.main_window.add_log(f"BOOT 모드 진입 시도 ({i+1}/3)...")
                    QApplication.processEvents()  # UI 응답성 유지
                    cmd, response = self.common_command("W", "N", "B", log=True )

                    #print("res = ", response )
                    is_valid, error_message = check_response(response)
                    if not is_valid:
                        self.main_window.add_log(f"응답 검증 실패: {error_message}")
                        return

                    ans = trim_string( response, 3, 3 )
                    
                    if i==2 and ans=="0" : 
                        self.main_window.add_log("BOOT 모드 진입 성공. 10초 안에 확인 버튼을 누르세요.")

                        # 버튼의 역할과 연결을 변경
                        self.process_button.setText("Confirm Flash")
                        self.process_button.setEnabled(True)
                        self.process_button.clicked.disconnect()
                        self.process_button.clicked.connect(self.confirm_and_flash)

                        # 10초 타이머 시작
                        self.flash_timeout_timer.start()

            except Exception as e:
                self.main_window.add_log(f"❌ 오류 발생: {e}")
                self.reset_ui_to_initial_state()


        except Exception as e:
            # 8. 오류 처리
            self.main_window.add_log(f"❌ 오류 발생: {e}")
            self.main_window.add_log("펌웨어 업그레이드 실패.")

        finally:
            # 9. 종료 처리 (성공/실패에 관계없이 항상 실행)
            #self.main_window.add_log("업그레이드 절차를 종료합니다.")
            self.select_file_button.setEnabled(True)
            self.process_button.setEnabled(True)



    def confirm_and_flash(self):
        """ 2단계: 사용자가 확인 버튼을 누르면 실제 플래싱을 시작합니다. """
        self.flash_timeout_timer.stop() # 타이머 중지
        self.main_window.add_log("사용자 확인. 실제 펌웨어 전송을 시작합니다.")
        self.process_button.setEnabled(False)

        try:
            # --- 이전에 만들었던 파일 크기 및 데이터 전송 로직이 여기에 들어갑니다 ---
            file_path = self.file_path_display.text()
            with open(file_path, 'r') as f:
                hex_lines = [line.strip() for line in f if line.strip()]


            # --- HEX 파일 크기 전송 ---
            data_line_count = sum(1 for line in hex_lines if line[7:9] == '00')
            count_str = str(data_line_count).zfill(5)
            cmd, response = self.common_command("W", "N", "T" + count_str, log=True)


            #print("res = ", response )
            is_valid, error_message = check_response(response)
            if not is_valid:
                self.main_window.add_log(f"응답 검증 실패: {error_message}")
                return



            print("cmd      = ", cmd )
            print("response = ", response )

            ans = trim_string( response, 3, 3 )

            if ans=='0' : 
                self.main_window.add_log("펌웨어 크기 정보 전송 성공.")
            else :
                raise Exception("펌웨어 크기 정보 전송 실패")


            # --- HEX 데이터 라인별 전송 ---
            self.main_window.add_log(f"데이터 전송을 시작합니다... (총 {data_line_count}개)")
            self.progress_bar.setMaximum(100) # 프로그레스 바 최대값을 100으로 설정

            current_address = None
            processed_count = 0
            log_interval = 500  # 500개마다 한 번씩 로그

            for i, line in enumerate(hex_lines):
                if not line.startswith(':'):
                    continue

                # UI 응답성 유지 (주기적으로 호출)
                if i % 10 == 0:  # 10줄마다 한 번씩
                    QApplication.processEvents()

                record_type = line[7:9]

                # 유형 00: 데이터 레코드
                if record_type == '00':
                    data = line[9:-2]
                    data_len_str = str(len(data)).zfill(2)  # HEX 문자열 길이 (10진수 2자리)
                    if self.send_command_with_retry("W", "N", "D" + data_len_str + data ) == False:
                        raise Exception(f"{i+1}번째 라인 데이터 전송 실패")
                    processed_count += 1

                    # 진행 상황 로그 (50개마다)
                    if processed_count % log_interval == 0:
                        progress = int((processed_count / data_line_count) * 100)
                        self.main_window.add_log(f"진행: {processed_count}/{data_line_count} ({progress}%)")

                # 유형 04: 확장 주소 레코드
                elif record_type == '04':
                    address_data = line[9:-2]
                    if current_address != address_data:
                        # 확장 주소 로그는 중요하므로 유지
                        self.main_window.add_log(f"확장 주소 설정: 0x{address_data}")
                        if self.send_command_with_retry("W", "N", "A" + address_data ) == False:
                            raise Exception(f"{i+1}번째 라인 주소 전송 실패")
                        current_address = address_data

                # 유형 05: 프로그램 시작 주소 (무시) - 로그 제거
                elif record_type == '05':
                    continue

                # 유형 01: 파일 끝 레코드
                elif record_type == '01':
                    self.main_window.add_log("파일의 끝(EOF)에 도달했습니다.")
                    break # 루프 종료

                # 프로그레스 바 업데이트 (처리된 데이터 라인 기준)
                if record_type == '00' and data_line_count > 0:
                    progress = int((processed_count / data_line_count) * 100)
                    self.progress_bar.setValue(progress)
                    # UI 응답성 유지
                    QApplication.processEvents()

                time.sleep(0.005)

            # --- 다운로드 완료 명령 전송 ---
            self.main_window.add_log("데이터 전송 완료. 종료 명령을 보냅니다.")
            cmd, response = self.common_command("W", "N", "E", log=True)
            ans = trim_string( response, 3, 3 )
            if ans == '1' : raise Exception("완료 명령 전송 실패")

            if ans == '0' :
                self.main_window.add_log("✅ 펌웨어 업그레이드 성공!")
                self.progress_bar.setValue(100) # 100% 채우기
                # 펌웨어 완료 후 서버 중지
                if self.main_window.server and self.main_window.server.is_running:
                    self.main_window.add_log("펌웨어 완료: 서버를 중지합니다.")
                    self.main_window.stop_server()

        except Exception as e:
            self.main_window.add_log(f"❌ 펌웨어 전송 중 오류 발생: {e}")
        finally:
            self.reset_ui_to_initial_state()
      








    def send_command_with_retry(self, DIR, CMD, data_str=None, retries=3, delay=0.2):
        """
        명령 전송에 실패하면 정해진 횟수만큼 재시도합니다.

        :param retries: 최대 재시도 횟수
        :param delay: 재시도 사이의 대기 시간 (초)
        :return: 성공 시 True, 최종 실패 시 False
        """
        for attempt in range(retries):
            cmd, response = self.common_command(DIR, CMD, data_str, log=False)
            ans = trim_string( response, 3, 3 )
            if ans=='0' : return True  # 성공 시 즉시 True 반환

            # 재시도 로그 제거 - 너무 많은 로그 방지
            QApplication.processEvents()  # UI 응답성 유지
            time.sleep(delay) # 잠시 대기

        # 최종 실패 시에만 로그
        self.main_window.add_log(f"명령 전송 실패: {DIR}{CMD} (재시도 {retries}회)")
        return False # 모든 재시도가 실패하면 False 반환


    def cancel_flash(self):
        """ 10초 타임아웃 시 호출되어 플래싱을 취소합니다. """
        self.main_window.add_log("타임아웃: 10초 동안 확인 버튼을 누르지 않아 업그레이드를 취소합니다.")
        self.reset_ui_to_initial_state()

    def reset_ui_to_initial_state(self):
        """ 모든 UI 상태를 초기(파일 선택 전/후) 상태로 되돌립니다. """
        self.flash_timeout_timer.stop()

        # 버튼 텍스트와 연결 상태를 원래대로 복구
        self.process_button.setText("Start Firmware Upgrade")
        try:
            self.process_button.clicked.disconnect()
        except TypeError:
            pass # 이미 연결이 끊겨있으면 무시
        self.process_button.clicked.connect(self.start_upgrade)

        # 파일 선택 여부에 따라 버튼 활성화 상태 조절
        is_file_selected = bool(self.file_path_display.text())
        self.select_file_button.setEnabled(True)
        self.process_button.setEnabled(is_file_selected)
        self.main_window.add_log("UI 상태가 초기화되었습니다.")








    def open_file_dialog(self):
        """
        파일 선택 대화상자를 열고 사용자가 선택한 파일의 경로를 처리합니다.
        """
        # 서버 모드에서는 파일 선택 불가
        #if self.main_window.is_server_mode():
        #    self.main_window.add_log("❌ 서버 모드에서는 펌웨어 파일을 선택할 수 없습니다.")
        #    return

        # QFileDialog.getOpenFileName()을 호출하여 파일 선택 대화상자를 엽니다.
        # 이 함수는 (파일 경로, 선택된 필터) 튜플을 반환합니다.
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Firmware File",  # 대화상자 제목
            "",                      # 시작 디렉토리 (비워두면 현재 디렉토리)
            "Hex Files (*.hex)"  # 파일 필터
        )

        # 사용자가 파일을 선택했는지 확인 (취소 버튼을 누르면 file_name은 비어있음)
        if file_name:
            # 선택된 파일 경로를 QLineEdit에 표시
            self.file_path_display.setText(file_name)
            # "Start Firmware Upgrade" 버튼 활성화 (서버 모드가 아닐 때만)
            #if not self.main_window.is_server_mode():
            #    self.process_button.setEnabled(True)
            # 메인 윈도우 로그에 선택된 파일 기록
            self.main_window.add_log(f"Firmware file selected: {file_name}")
        else:
            # 파일 선택이 취소된 경우
            self.file_path_display.clear()
            self.process_button.setEnabled(False)
            self.main_window.add_log("File selection cancelled.")






    def common_command( self, DIR, CMD, data_str=None, log=None ):
        #ip, port = self.main_window.get_ip_port()

        if data_str :
            command = ptcl.STX + DIR + CMD + data_str
        else:
            command = ptcl.STX + DIR + CMD

        command = add_tail(command)

        if log : self.main_window.add_log(f"전송 >> {command}")
        response = self.main_window.send_command_unified( command )
        if log : self.main_window.add_log(f"응답 << {response}")

        return command, response


