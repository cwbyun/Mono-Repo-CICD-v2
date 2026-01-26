from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QGroupBox, QFileDialog, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from communication import *
from utils import *
import time
import os
import glob
import protocol as ptcl


class FirmwareTab(QWidget):
    def __init__(self, parent):
        """
            'Firmware' 탭: 구형 장비용 펌웨어 플래싱 절차 구현
            - command.png 사양의 W N 계열 명령 사용 (T/A/D/E/C)
            - HEX 파일은 기본적으로 'Firmware' 폴더 내 파일을 사용
        """

        super().__init__()
        self.main_window = parent

        main_layout = QVBoxLayout(self)

        # 펌웨어 파일 선택 영역
        file_selection_group = QGroupBox("Firmware File Selection")
        file_layout = QHBoxLayout()
        file_path_label = QLabel("HEX File Path:")
        self.file_path_display = QLineEdit()
        self.file_path_display.setReadOnly(True)
        self.select_file_button = QPushButton("Select File...")
        file_layout.addWidget(file_path_label)
        file_layout.addWidget(self.file_path_display, 1)
        file_layout.addWidget(self.select_file_button)
        file_selection_group.setLayout(file_layout)
        main_layout.addWidget(file_selection_group)

        # 진행 버튼 및 진행률
        self.process_button = QPushButton("Start Firmware Upgrade")
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.process_button)
        main_layout.addWidget(self.progress_bar)

        main_layout.addStretch(1)

        # 기본 HEX 자동 선택 (Firmware 폴더)
        self._auto_select_default_hex()

        # 시그널 연결
        self.select_file_button.clicked.connect(self.open_file_dialog)
        self.process_button.clicked.connect(self.start_upgrade)

        # 확인 대기 타이머 (BOOT 진입 후 10초 제한)
        self.flash_timeout_timer = QTimer(self)
        self.flash_timeout_timer.setSingleShot(True)
        self.flash_timeout_timer.setInterval(10000)
        self.flash_timeout_timer.timeout.connect(self.cancel_flash)

        # --- Flash behavior knobs (for legacy variance) ---
        # DOWNLOAD NUMBER mode: use total count of type-00 lines (per howto)
        self.download_number_mode = 'lines'
        # Data encoding for D packet: only 'ascii_hex' is implemented; 'raw' placeholder for validation
        self.data_encoding = 'ascii_hex'
        # Inter-record delay (seconds)
        self.inter_record_delay = 0.10  # conservative (>20ms)
        # Additional delay right after address set (A) before first D
        self.delay_after_address = 0.10
        # Log the very first A/D exchange verbosely for capture
        self.log_early_exchange = True
        self._logged_first_A = False
        self._logged_first_D = False
        # LENGTH(dd) calculation mode for D: 'bytes' (LL) or 'hexchars' (len(DATA))
        # howto/program-smdaq-204-setup 기준: hexchars 사용
        self.dd_mode = 'hexchars'
        # Post-BPS settle delay
        self.post_bps_settle = 1.0
        # Current BPS dd and fallback candidates
        self.current_bps_dd = '24'  # ETH:115200 default
        self.bps_fallbacks = ['23', '22', '25']  # 57600, 38400, 230400

    # --- UI 동작 ---
    def _log(self, message: str):
        try:
            # 메인 윈도우 초기화 이전에도 안전하게 동작하도록 보호
            if hasattr(self.main_window, 'add_log'):
                self.main_window.add_log(message)
            else:
                print(message)
        except Exception:
            print(message)

    def _auto_select_default_hex(self):
        try:
            base = os.path.join(os.path.dirname(__file__), 'Firmware')
            candidates = sorted(glob.glob(os.path.join(base, '*.hex')))
            if candidates:
                self.file_path_display.setText(candidates[0])
                self.process_button.setEnabled(True)
                self._log(f"Auto-selected HEX: {candidates[0]}")
            else:
                self.process_button.setEnabled(False)
                self._log("Firmware 폴더에 HEX 파일이 없습니다.")
        except Exception as e:
            self.process_button.setEnabled(False)
            self._log(f"HEX 자동 선택 중 오류: {e}")

    def open_file_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Firmware File",
            "",
            "Hex Files (*.hex)"
        )
        if file_name:
            self.file_path_display.setText(file_name)
            self.process_button.setEnabled(True)
            self._log(f"Firmware file selected: {file_name}")
        else:
            if not self.file_path_display.text():
                self.process_button.setEnabled(False)
            self._log("File selection cancelled.")

    # --- 플래싱 절차 ---
    def start_upgrade(self):
        file_path = self.file_path_display.text()
        if not file_path:
            self._log("오류: 펌웨어 파일이 선택되지 않았습니다.")
            return

        self._log(f"'{file_path}' 파일로 펌웨어 업그레이드를 시작합니다.")
        self.select_file_button.setEnabled(False)
        self.process_button.setEnabled(False)

        try:
            # BOOT 모드 진입 (SWNB) 3회 시도
            self._log("장비를 BOOT 모드로 전환합니다...")
            for i in range(3):
                self._log(f"BOOT 모드 진입 시도 ({i+1}/3)...")
                cmd, response = self.common_command("W", "N", "B", log=True)
                is_valid, error_message = check_response(response)
                if not is_valid:
                    self._log(f"응답 검증 실패: {error_message}")
                    return
                ans = trim_string(response, 3, 3)
                if i == 2 and ans == '0':
                    self._log("BOOT 모드 진입 성공. 10초 안에 확인 버튼을 누르세요.")
                    self.process_button.setText("Confirm Flash")
                    self.process_button.setEnabled(True)
                    self.process_button.clicked.disconnect()
                    self.process_button.clicked.connect(self.confirm_and_flash)
                    self.flash_timeout_timer.start()
        except Exception as e:
            self._log(f"❌ 오류 발생: {e}")
            self.reset_ui_to_initial_state()
        finally:
            # 사용자의 확인을 기다리는 상태로 두므로 버튼은 위에서 재연결
            pass

    def confirm_and_flash(self):
        self.flash_timeout_timer.stop()
        self._log("사용자 확인. 실제 펌웨어 전송을 시작합니다.")
        self.process_button.setEnabled(False)

        try:
            file_path = self.file_path_display.text()
            with open(file_path, 'r') as f:
                hex_lines = [line.strip() for line in f if line.strip()]

            # 데이터 레코드 통계 계산
            data_line_count = 0
            total_data_bytes = 0
            for line in hex_lines:
                if not (line.startswith(':') and len(line) >= 11):
                    continue
                if line[7:9] == '00':
                    data_line_count += 1
                    try:
                        total_data_bytes += int(line[1:3], 16)
                    except Exception:
                        pass

            # 50-1 START DOWNLOAD: 총 데이터 라인 수 전송 (T + ddddd)
            count_str = str(data_line_count).zfill(5)
            cmd, response = self.common_command("W", "N", "T" + count_str, log=True)
            is_valid, error_message = check_response(response)
            if not is_valid:
                self._log(f"응답 검증 실패: {error_message}")
                return
            ans = trim_string(response, 3, 3)
            if ans != '0':
                raise Exception(f"펌웨어 크기 정보 전송 실패(lines), 코드: {ans}")
            self._log(f"펌웨어 크기 정보 전송 성공 (라인 수: {data_line_count}).")

            # 50-5: 다운로드 프로그램의 통신속도 설정 (ETH:115200 -> dd=24)
            try:
                # howto: SWCdd, dd = 인터페이스(2:ETH) + 속도 index(4:115200)
                bps_dd = self.current_bps_dd
                self._log("다운로드 BPS를 ETH:115200으로 설정합니다 (SWC24)...")
                cmd, response = self.common_command("W", "C", bps_dd, log=True)
                is_valid, error_message = check_response(response)
                if not is_valid:
                    self._log(f"BPS 설정 응답 검증 실패: {error_message}")
                else:
                    # 응답은 전송과 동일한 에코(SWCdd) 형식임
                    content = response[:-3] if len(response) >= 3 else ""
                    if content.startswith(f"SWC{bps_dd}"):
                        self._log("BPS 설정 응답 확인(SWC 에코).")
                    else:
                        self._log(f"예상과 다른 BPS 응답: {response}")
                # 속도 전환 직후 소폭 대기 (일부 장비 안정화용)
                time.sleep(self.post_bps_settle)
            except Exception as e:
                self._log(f"BPS 설정 중 예외: {e}")

            # 데이터 전송 루프 (A: 확장 주소, D: 데이터, E: 종료)
            self._log("데이터 전송을 시작합니다...")
            self.progress_bar.setMaximum(100)
            current_address = None  # 상위 16비트 주소 (type-04)
            saw_extended_addr = False
            processed_count = 0

            for i, line in enumerate(hex_lines):
                if not line.startswith(':'):
                    continue

                record_type = line[7:9]

                if record_type == '00':  # Data record
                    # Intel HEX parsing + checksum verify
                    try:
                        ll = int(line[1:3], 16)
                        addr = int(line[3:7], 16)
                        rtype = int(line[7:9], 16)
                        data = line[9:9 + ll * 2]
                        chk_hex = line[9 + ll * 2: 9 + ll * 2 + 2]
                        chk_val = int(chk_hex, 16)

                        # compute Intel HEX checksum (two's complement of byte sum)
                        total = ll + ((addr >> 8) & 0xFF) + (addr & 0xFF) + rtype
                        for j in range(0, len(data), 2):
                            total += int(data[j:j+2], 16)
                        total &= 0xFF
                        calc_chk = ((~total + 1) & 0xFF)
                        if calc_chk != chk_val:
                            raise ValueError(f"HEX 체크섬 불일치: 수신({chk_hex}) vs 계산({calc_chk:02X})")
                    except Exception as e:
                        raise Exception(f"{i+1}번째 라인 파싱/체크섬 오류: {e}")

                    # 필요한 경우 첫 데이터 전송 전 기본 주소(0000) 설정
                    if not saw_extended_addr and current_address is None:
                        # 일부 장비는 첫 D 이전에 A0000을 요구할 수 있음
                        if self.send_command_with_retry("W", "N", "A0000",
                                                        log=(self.log_early_exchange and not self._logged_first_A)):
                            self._logged_first_A = True
                            time.sleep(self.delay_after_address)
                        current_address = "0000"  # 플래그 용도

                    # Adaptive SWND send: try dd as hexchars then bytes (or vice versa)
                    attempts = []
                    if self.dd_mode == 'hexchars':
                        attempts = [len(data), ll]
                    else:
                        attempts = [ll, len(data)]

                    sent_ok = False
                    for dd_v in attempts:
                        dd_bytes = f"{dd_v:02d}"
                        _, resp = self.common_command("W", "N", "D" + dd_bytes + data,
                                                      log=(self.log_early_exchange and not self._logged_first_D))
                        ans_try = trim_string(resp, 3, 3)
                        if ans_try == '0':
                            sent_ok = True
                            break
                        else:
                            self._log(f"D NG(dd={dd_v}), 코드={ans_try}")
                            time.sleep(0.05)

                    # 마지막 대안: 주소+타입을 앞에 붙여 전송
                    if not sent_ok:
                        addr_rtype = f"{addr:04X}{rtype:02X}"
                        payload2 = addr_rtype + data
                        for dd_v in ([len(payload2), ll + 3] if self.dd_mode == 'hexchars' else [ll + 3, len(payload2)]):
                            dd_bytes = f"{dd_v:02d}"
                            _, resp = self.common_command("W", "N", "D" + dd_bytes + payload2,
                                                          log=(self.log_early_exchange and not self._logged_first_D))
                            ans_try = trim_string(resp, 3, 3)
                            if ans_try == '0':
                                sent_ok = True
                                break
                            else:
                                self._log(f"D NG(with addr/type, dd={dd_v}), 코드={ans_try}")
                                time.sleep(0.05)

                    # BPS fallback on first data if still NG
                    if not sent_ok and processed_count == 0:
                        for fb in self.bps_fallbacks:
                            self._log(f"D NG 지속 → BPS 변경 시도(SWC{fb})")
                            _, resp_c = self.common_command("W", "C", fb, log=True)
                            ok_c, err_c = check_response(resp_c)
                            if not ok_c:
                                self._log(f"BPS 변경 응답 검증 실패: {err_c}")
                                continue
                            time.sleep(self.post_bps_settle)
                            # 주소 재설정
                            if current_address:
                                self._log(f"BPS 변경 후 주소 재설정: 0x{current_address}")
                                if not self.send_command_with_retry("W", "N", "A" + current_address, retries=2, delay=0.2):
                                    self._log("주소 재설정 실패")
                            # 다시 dd 시도
                            for dd_v in attempts:
                                dd_bytes = f"{dd_v:02d}"
                                _, resp = self.common_command("W", "N", "D" + dd_bytes + data,
                                                              log=(self.log_early_exchange and not self._logged_first_D))
                                ans_try = trim_string(resp, 3, 3)
                                if ans_try == '0':
                                    sent_ok = True
                                    self.current_bps_dd = fb
                                    self._log(f"BPS {fb}에서 D 성공.")
                                    break
                                else:
                                    self._log(f"D NG(dd={dd_v})@BPS {fb}, 코드={ans_try}")
                                    time.sleep(0.05)
                            if sent_ok:
                                break

                    if not sent_ok:
                        raise Exception(f"{i+1}번째 라인 데이터 전송 실패")
                    if not self._logged_first_D and self.log_early_exchange:
                        self._logged_first_D = True
                    processed_count += 1

                elif record_type == '04':  # Extended linear address
                    address_data = line[9:-2]
                    if current_address != address_data:
                        self._log(f"확장 주소 설정: 0x{address_data}")
                        if not self.send_command_with_retry(
                            "W", "N", "A" + address_data,
                            log=(self.log_early_exchange and not self._logged_first_A)
                        ):
                            raise Exception(f"{i+1}번째 라인 주소 전송 실패")
                        current_address = address_data
                        saw_extended_addr = True
                        self._logged_first_A = True
                        time.sleep(self.delay_after_address)

                elif record_type == '05':
                    # 시작 주소 레코드는 무시
                    continue

                elif record_type == '01':  # EOF
                    break

                # 프로그레스 업데이트
                if record_type == '00' and data_line_count > 0:
                    progress = int((processed_count / data_line_count) * 100)
                    self.progress_bar.setValue(progress)

                time.sleep(self.inter_record_delay)

            # 50-4 DOWNLOAD END (E)
            self._log("데이터 전송 완료. 종료 명령을 보냅니다.")
            cmd, response = self.common_command("W", "N", "E", log=True)
            ans = trim_string(response, 3, 3)
            if ans == '1':
                raise Exception("완료 명령 전송 실패")
            self._log("✅ 펌웨어 업그레이드 성공!")
            self.progress_bar.setValue(100)

        except Exception as e:
            self._log(f"❌ 펌웨어 전송 중 오류 발생: {e}")
        finally:
            self.reset_ui_to_initial_state()

    def send_command_with_retry(self, DIR, CMD, data_str=None, retries=3, delay=0.2, log=False):
        for attempt in range(retries):
            cmd, response = self.common_command(DIR, CMD, data_str, log=log)
            ans = trim_string(response, 3, 3)
            if ans == '0':
                return True
            self._log(f"응답 오류. {delay}초 후 재시도... ({attempt + 1}/{retries})")
            time.sleep(delay)
        return False

    def cancel_flash(self):
        self._log("타임아웃: 10초 동안 확인 버튼을 누르지 않아 업그레이드를 취소합니다.")
        self.reset_ui_to_initial_state()

    def reset_ui_to_initial_state(self):
        self.flash_timeout_timer.stop()
        self.process_button.setText("Start Firmware Upgrade")
        try:
            self.process_button.clicked.disconnect()
        except TypeError:
            pass
        self.process_button.clicked.connect(self.start_upgrade)

        is_file_selected = bool(self.file_path_display.text())
        self.select_file_button.setEnabled(True)
        self.process_button.setEnabled(is_file_selected)
        self._log("UI 상태가 초기화되었습니다.")

    # --- 공통 명령 ---
    def common_command(self, DIR, CMD, data_str=None, log=None):
        if data_str:
            command = ptcl.STX + DIR + CMD + data_str
        else:
            command = ptcl.STX + DIR + CMD
        command = add_tail(command)
        if log:
            self._log(f"전송 >> {command}")
        response = self.main_window.send_command_unified(command)
        if log:
            self._log(f"응답 << {response}")
        return command, response
