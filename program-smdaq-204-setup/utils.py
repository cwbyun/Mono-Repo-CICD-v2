import sys
from PyQt6.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit, QPushButton,
        QComboBox, QGridLayout, QDateEdit, 
        )
from PyQt6.QtCore import Qt, QDate,  QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
import re



class DateRangeGroup(QGroupBox):
    """QGroupBox 내부에 시작/종료 날짜를 입력하는 위젯 (달력 팝업 지원)"""
    def __init__(self, title="기간 선택", parent: QWidget | None = None,
                 start: QDate | None = None, end: QDate | None = None,
                 min_date: QDate | None = None, max_date: QDate | None = None):
        super().__init__(title, parent)

        self.start = QDateEdit(self)
        self.end   = QDateEdit(self)

        for w in (self.start, self.end):
            w.setCalendarPopup(True)           # ⬅️ 마우스로 달력 선택 가능
            w.setDisplayFormat("yyyy-MM-dd")   # 표시 형식
            # w.setFixedWidth(130)  # 필요하면 폭 고정

        today = QDate.currentDate()
        self.start.setDate(start or today)
        self.end.setDate(end or today.addDays(7))

        if min_date:
            self.start.setMinimumDate(min_date); self.end.setMinimumDate(min_date)
        if max_date:
            self.start.setMaximumDate(max_date); self.end.setMaximumDate(max_date)

        # 시작 ≤ 종료 유지
        self.start.dateChanged.connect(self._sync_start)
        self.end.dateChanged.connect(self._sync_end)

        form = QFormLayout(self)
        form.addRow("시작일", self.start)
        form.addRow("종료일", self.end)

    def _sync_start(self, d: QDate):
        if d > self.end.date():
            self.end.setDate(d)

    def _sync_end(self, d: QDate):
        if d < self.start.date():
            self.start.setDate(d)

    # 값 꺼내기
    def range_qdate(self) -> tuple[QDate, QDate]:
        return self.start.date(), self.end.date()

    def range_str(self) -> tuple[str, str]:
        return (self.start.date().toString("yyyy-MM-dd"),
                self.end.date().toString("yyyy-MM-dd"))



def create_dynamic_group_grid_2xN(title, layout_config, input_width=60, read_only=False):
    """
    데이터 기반으로 2열 그리드 Layout을 생성하는 함수.
    각 행에 두 쌍의 위젯 그룹을 배치합니다.
    'input_pair', 'combo_box', 'combo_input_pair' 타입을 지원합니다.

    Args:
        title(str): 그룹 박스 제목.
        layout_config(list): Layout 구조를 담은 리스트.
        input_width(int): 입력 필드의 고정 너비.

    Returns:
        tuple: (QGroupBox, dict) - 생성된 QGroupBox와 위젯 딕셔너리.
    """
    group_box = QGroupBox(title)
    main_vbox = QVBoxLayout()
    grid_layout = QGridLayout()
    widgets_dict = {}

    row, col = 0, 0

    content_items = [item for item in layout_config if item.get('type') != 'button']
    button_items = [item for item in layout_config if item.get('type') == 'button']

    for item in content_items:
        pair_hbox = QHBoxLayout()
        pair_hbox.setContentsMargins(0, 0, 0, 0)

        item_type = item.get('type')

        if item_type == 'input_pair':
            label = QLabel(item['label'])
            widget = QLineEdit()
            widget.setFixedWidth(input_width)
            widget.setReadOnly(read_only)

            pair_hbox.addWidget(label)
            pair_hbox.addWidget(widget)
            widgets_dict[item['name']] = widget

        elif item_type == 'combo_box':
            label = QLabel(item['label'])
            widget = QComboBox()
            if 'option' in item:
                widget.addItems(item['option'])

            pair_hbox.addWidget(label)
            pair_hbox.addWidget(widget)
            widgets_dict[item['name']] = widget

        elif item_type == 'combo_input_pair':
            # 새로운 타입: ComboBox와 LineEdit 쌍
            combo_box = QComboBox()
            if 'combo_options' in item:
                combo_box.addItems(item['combo_options'])

            line_edit = QLineEdit()
            line_edit.setFixedWidth(input_width)
            line_edit.setReadOnly(read_only)

            pair_hbox.addWidget(combo_box)
            pair_hbox.addWidget(line_edit)

            # 두 위젯을 딕셔너리에 추가
            widgets_dict[item['combo_name']] = combo_box
            widgets_dict[item['input_name']] = line_edit

        # HBox를 그리드 레이아웃에 추가
        grid_layout.addLayout(pair_hbox, row, col)

        col += 1
        if col >= 2:
            row += 1
            col = 0

    grid_layout.setColumnStretch(0, 0)
    grid_layout.setColumnStretch(1, 0)
    grid_layout.setColumnStretch(2, 1)

    main_vbox.addLayout(grid_layout)

    if button_items:
        button_hbox = QHBoxLayout()
        button_hbox.addStretch()
        for btn_item in button_items:
            button = QPushButton(btn_item['text'])
            button_hbox.addWidget(button)
            widgets_dict[btn_item['name']] = button
        main_vbox.addLayout(button_hbox)

    group_box.setLayout(main_vbox)

    return group_box, widgets_dict








def create_dynamic_group_grid_2xN_bak(title, layout_config, input_width=60):
    """
    데이터 기반으로 2열 그리드 Layout을 생성하는 함수.
    각 행에 두 쌍의 레이블과 입력 필드를 배치합니다.

    Args:
        title(str): 그룹 박스 제목.
        layout_config(list): Layout 구조를 담은 리스트.
        input_width(int): 입력 필드의 고정 너비.

    Returns:
        tuple: (QGroupBox, dict) - 생성된 QGroupBox와 위젯 딕셔너리.
    """
    group_box = QGroupBox(title)
    main_vbox = QVBoxLayout()
    grid_layout = QGridLayout()
    widgets_dict = {}

    row, col = 0, 0

    content_items = [item for item in layout_config if item['type'] != 'button']
    button_items = [item for item in layout_config if item['type'] == 'button']

    for item in content_items:
        # 라벨과 위젯을 하나의 HBox로 묶어줍니다.
        pair_hbox = QHBoxLayout()
        pair_hbox.setContentsMargins(0, 0, 0, 0)

        label = QLabel(item['label'])

        widget = None
        if item['type'] == 'input_pair':
            widget = QLineEdit()
            widget.setFixedWidth(input_width)
            widget.setReadOnly(True)
        elif item['type'] == 'combo_box':
            widget = QComboBox()
            if 'option' in item:
                widget.addItems(item['option'])

        if widget:
            pair_hbox.addWidget(label)
            pair_hbox.addWidget(widget)

            # 이 HBox를 그리드 레이아웃에 추가합니다.
            grid_layout.addLayout(pair_hbox, row, col)
            widgets_dict[item['name']] = widget

            col += 1
            if col >= 2:
                row += 1
                col = 0

    # 1열과 2열 사이의 공간이 늘어나도록 stretch를 추가합니다.
    grid_layout.setColumnStretch(0, 0)
    grid_layout.setColumnStretch(1, 0)
    grid_layout.setColumnStretch(2, 1) # 세 번째 보이지 않는 열이 모든 여유 공간을 차지하도록 설정

    main_vbox.addLayout(grid_layout)

    if button_items:
        button_hbox = QHBoxLayout()
        button_hbox.addStretch()
        for item in button_items:
            button = QPushButton(item['text'])
            button_hbox.addWidget(button)
            widgets_dict[item['name']] = button
        main_vbox.addLayout(button_hbox)

    group_box.setLayout(main_vbox)

    return group_box, widgets_dict






def create_dynamic_group_vertical(title, layout_config, input_width=60):
    """
    데이터 기반으로 동적인 세로(Vertical) Layout을 생성하는 함수.

    Args:
        title(str): 그룹 박스 제목.
        layout_config(list): Layout 구조를 담은 리스트.
        input_width(int): 입력 필드의 고정 너비.

    Returns:
        tuple: (QGroupBox, dict) - 생성된 QGroupBox와 위젯 딕셔너리.
    """
    group_box = QGroupBox(title)
    main_vbox = QVBoxLayout()  # 전체 레이아웃을 QVBoxLayout로 변경
    widgets_dict = {}

    # 버튼을 제외한 모든 위젯을 담을 레이아웃
    content_vbox = QVBoxLayout()
    
    # 버튼을 담을 가로 레이아웃
    button_hbox = QHBoxLayout()
    button_hbox.addStretch() # 버튼을 오른쪽으로 정렬하기 위해

    for item in layout_config:
        item_type = item['type']

        if item_type == 'input_pair':
            pair_hbox = QHBoxLayout() # 각 행은 QHBoxLayout로 유지
            label = QLabel(item['label'])
            line_edit = QLineEdit()
            line_edit.setFixedWidth(input_width)
            
            pair_hbox.addWidget(label)
            pair_hbox.addWidget(line_edit)
            pair_hbox.addStretch()  # 레이블과 입력 필드 쌍을 왼쪽으로 정렬
            
            content_vbox.addLayout(pair_hbox)
            widgets_dict[item['name']] = line_edit

        elif item_type == 'combo_box':
            pair_hbox = QHBoxLayout() # 각 행은 QHBoxLayout로 유지
            label = QLabel(item['label'])
            combo_box = QComboBox()
            combo_box.addItems(item['option'])
            
            pair_hbox.addWidget(label)
            pair_hbox.addWidget(combo_box)
            pair_hbox.addStretch()  # 레이블과 콤보박스 쌍을 왼쪽으로 정렬
            
            content_vbox.addLayout(pair_hbox)
            widgets_dict[item['name']] = combo_box
        
        elif item_type == 'button':
            button = QPushButton(item['text'])
            button_hbox.addWidget(button) # 버튼은 별도의 HBox에 추가
            widgets_dict[item['name']] = button

    # 모든 위젯을 담은 세로 레이아웃을 main_vbox에 추가
    main_vbox.addLayout(content_vbox)
    
    # 버튼 레이아웃을 main_vbox에 추가
    main_vbox.addLayout(button_hbox)

    group_box.setLayout(main_vbox)

    return group_box, widgets_dict





def create_dynamic_group(title, layout_config, options_data=None, input_width=60 ):
    """
        데이터 기반으로 동적인 Layout을 생성하는 함수
        Args:
            title(str): 그룹 박스 제목
            layout_config(list): Layout 구조를 담은 리스트
        Returns:
            tuple: (QgroupBox, dict) - 생성된 QGroupBox와 위젯 딕셔너리
    """

    group_box = QGroupBox(title)
    main_hbox = QHBoxLayout()
    widgets_dict = {}

    label_input_hbox = QHBoxLayout()


    for item in layout_config:
        item_type = item['type']

        if item_type == 'input_pair':
            pair_hbox = QHBoxLayout()
            label = QLabel(item['label'])
            line_edit = QLineEdit()
            line_edit.setFixedWidth(input_width)
            pair_hbox.addWidget(label)
            pair_hbox.addWidget(line_edit)

            label_input_hbox.addLayout(pair_hbox)
            label_input_hbox.addStretch()

            widgets_dict[item['name']] = line_edit

        elif item_type == 'label':
            label = QLabel(item['text'])

            label_input_hbox.addWidget( label )
            if 'name' in item:
                widgets_dict[item['name']] = label
            label_input_hbox.addStretch()


        elif item_type == 'combo_box':
            pair_hbox = QHBoxLayout()
            label = QLabel(item['label'])
            combo_box = QComboBox()
            combo_box.addItems(item['option'])
            pair_hbox.addWidget(label)
            pair_hbox.addWidget(combo_box)
            label_input_hbox.addLayout(pair_hbox)
            label_input_hbox.addStretch()
            widgets_dict[item['name']] = combo_box


        elif item_type == 'date_time':  # ✅ 날짜 선택 + 시간 입력
            pair_hbox = QHBoxLayout()
            label = QLabel(item['label'])

            # 날짜(달력 팝업)
            date = QDateEdit()
            date.setCalendarPopup(True)
            date.setDisplayFormat(item.get('date_format', 'yyyy-MM-dd'))
            date.setDate(item.get('default_date', QDate.currentDate()))
            date.setFixedWidth(item.get('date_width', 110))

            # 시간(텍스트 입력 + 검증기, 기본 HH:mm)
            time_edit = QLineEdit()
            time_format = item.get('time_format', 'HH:mm')
            time_edit.setPlaceholderText(item.get('placeholder', time_format))
            time_edit.setFixedWidth(item.get('time_width', 70))
            # 24시간 HH:mm 또는 HH:mm:ss 검증 (PyQt6: QRegularExpression, PyQt5: QRegExp)
            if time_format == 'HH:mm:ss':
                rx = QRegularExpression(r'^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$')
            else:
                rx = QRegularExpression(r'^([01]\d|2[0-3]):([0-5]\d)$')
            time_edit.setValidator(QRegularExpressionValidator(rx, time_edit))
            if 'default_time' in item:
                time_edit.setText(item['default_time'])  # 예: "00:00" 또는 "23:59"

            pair_hbox.addWidget(label)
            pair_hbox.addWidget(date)
            pair_hbox.addWidget(QLabel(" "))
            pair_hbox.addWidget(time_edit)

            label_input_hbox.addLayout(pair_hbox)

            base = item['name']
            widgets_dict[f"{base}_date"] = date
            widgets_dict[f"{base}_time"] = time_edit



        elif item_type == 'date':  # ✅ 추가: 날짜 범위
            pair_hbox = QHBoxLayout()
            label = QLabel(item['label'])

            fmt = item.get('format', 'yyyy-MM-dd')
            start = QDateEdit()
            start.setCalendarPopup(True)          # 마우스로 달력 선택
            start.setDisplayFormat(fmt)
            start.setFixedWidth(item.get('width', 110))  # 폭은 필요시 조정

            # 초기값 (없으면 오늘/일주일 뒤)
            start.setDate(item.get('start', QDate.currentDate().addDays(-1)))

            pair_hbox.addWidget(label)
            pair_hbox.addWidget(start)
            label_input_hbox.addLayout(pair_hbox)

            # 사전에 두 개로 보관: name_start / name_end
            base = item['name']
            widgets_dict[f"{base}_start"] = start


        elif item_type == 'date_range':  # ✅ 추가: 날짜 범위
            pair_hbox = QHBoxLayout()
            label = QLabel(item['label'])

            fmt = item.get('format', 'yyyy-MM-dd')
            start = QDateEdit()
            end   = QDateEdit()
            for w in (start, end):
                w.setCalendarPopup(True)          # 마우스로 달력 선택
                w.setDisplayFormat(fmt)
                w.setFixedWidth(item.get('width', 110))  # 폭은 필요시 조정
                # 제한옵션 (있으면 적용)
                if md := item.get('min_date'): w.setMinimumDate(md)
                if xd := item.get('max_date'): w.setMaximumDate(xd)

            # 초기값 (없으면 오늘/일주일 뒤)
            start.setDate(item.get('start', QDate.currentDate().addDays(-7)))
            end.setDate(item.get('end', QDate.currentDate()))

            # 시작 ≤ 종료 보장(옵션)
            def _sync_start(d): 
                if d > end.date(): end.setDate(d)
            def _sync_end(d):
                if d < start.date(): start.setDate(d)
            start.dateChanged.connect(_sync_start)
            end.dateChanged.connect(_sync_end)

            sep = QLabel(" ~ ")

            pair_hbox.addWidget(label)
            pair_hbox.addWidget(start)
            pair_hbox.addWidget(sep)
            pair_hbox.addWidget(end)
            label_input_hbox.addLayout(pair_hbox)

            # 사전에 두 개로 보관: name_start / name_end
            base = item['name']
            widgets_dict[f"{base}_start"] = start
            widgets_dict[f"{base}_end"]   = end


    #label_input_hbox.setSpacing(10)
    main_hbox.addLayout(label_input_hbox)

    main_hbox.addStretch()

    for item in layout_config:
        if item['type'] == 'button':
            button = QPushButton(item['text'])
            main_hbox.addWidget(button, alignment=Qt.AlignmentFlag.AlignRight)
            widgets_dict[item['name']] = button

    group_box.setLayout(main_hbox)

    return group_box, widgets_dict
        





def parse_by_lengths( data_string: str, length_grammar: str ) -> tuple | None:
    try:
        if '-' in length_grammar:
            lengths = [int(l) for l in length_grammar.split('-')]
        else:
            lengths = [int(l) for l in length_grammar]


    except ValueError:
        return None

    expected_length = sum(lengths)

    if len(data_string) != expected_length:
        return None

    chunks = []

    current_pos = 0

    for length in lengths:
        end_pos = current_pos + length
        chunks.append( data_string [current_pos:end_pos])
        current_pos = end_pos

    return tuple(chunks)



def extract_number_from_text(text):
    #정규식 패턴: 맨 앞에 있는 숫자(부호/소수점 포함)를 찾음
    match = re.match(r'^\s*([+-]?\d+(?:\.\d+)?)', text)
                
    if match:
        return match.group(1) # 찾은 숫자 문자열을 반환
    raise ValueError("유효한 숫자를 찾을 수 없습니다.")




def trim_string(data: str, front_count: int, back_count: int) -> str:
    """
        입력 문자열에서 입력된 글자수를 잘라내고 반환한다.
    """

    # 1. 입력 값의 유효성을 검사합니다. (음수 방지)

    if front_count < 0 or back_count < 0:
        return data
    if front_count + back_count >= len(data):
        return ""

    start_index = front_count
    end_index = len(data) - back_count
    return data[start_index:end_index]




def calculate_checksum(data: str) -> str:
    data_bytes = data.encode('utf-8')

    total_sum = sum( data_bytes )

    lsb_sum = total_sum & 0xFF

    checksum_val = ( ~lsb_sum + 1 )& 0xFF

    return f"{checksum_val:02X}"


def add_tail( command: str ) -> str:
    checksum = calculate_checksum( command )
    command = command + checksum + "Q"
    return command

def check_response(response: str) -> tuple[bool, str]:
    """
    응답 문자열의 유효성을 검증합니다.
    
    Args:
        response (str): 검증할 응답 문자열
    
    Returns:
        tuple[bool, str]: (검증 성공 여부, 오류 메시지)
    """
    import protocol as ptcl
    
    if not response:
        return False, "응답이 비어있습니다."
    
    # ERROR 응답 체크
    if response.startswith("[ERROR]"):
        return False, f"서버 오류: {response}"
    
    # 최소 길이 체크 (STX + 최소 내용 + 체크섬 + ETX = 최소 5자)
    if len(response) < 5:
        return False, f"응답이 너무 짧습니다. 길이: {len(response)}"
    
    # STX로 시작하는지 체크
    if not response.startswith(ptcl.STX):
        return False, f"응답이 올바른 시작 문자('{ptcl.STX}')로 시작하지 않습니다."
    
    # ETX로 끝나는지 체크
    if not response.endswith(ptcl.ETX):
        return False, f"응답이 올바른 종료 문자('{ptcl.ETX}')로 끝나지 않습니다."
    
    # 체크섬 추출 (마지막 3자리: 체크섬 2자리 + ETX)
    if len(response) < 3:
        return False, "체크섬을 추출할 수 없습니다."
    
    try:
        received_checksum = response[-3:-1]  # 마지막에서 3번째부터 1번째까지 (2자리)
        data_part = response[:-3]  # 체크섬과 ETX를 제외한 데이터 부분
        
        # 체크섬이 16진수인지 확인
        int(received_checksum, 16)
        
        # 계산된 체크섬과 비교
        calculated_checksum = calculate_checksum(data_part)
        
        if received_checksum.upper() != calculated_checksum.upper():
            return False, f"체크섬 불일치: 수신({received_checksum}) vs 계산({calculated_checksum})"
        
        return True, "응답이 유효합니다."
        
    except ValueError:
        return False, f"체크섬이 올바른 16진수 형식이 아닙니다: {received_checksum}"
    except Exception as e:
        return False, f"체크섬 검증 중 오류 발생: {str(e)}"




if __name__ == '__main__' :
    test_string1 = "SRV"
    checksum1 = calculate_checksum(test_string1)
    print(f"'{test_string1}'의 checksum: {checksum1}")

    print("\n--- check_response 테스트 ---")
    
    # 테스트 케이스들
    test_cases = [
        ("SRV82Q", "정상 응답"),
        ("", "빈 응답"),
        ("[ERROR] Connection failed", "오류 응답"),
        ("SRVQ", "응답이 너무 짧음"),
        ("SRV82", "Q로 끝나지 않음"),
        ("SRV83Q", "체크섬 불일치"),
        ("SRVXXQ", "잘못된 체크섬 형식"),
        ("SRVA0ABC123DEF88Q", "긴 정상 응답")
    ]
    
    for response, description in test_cases:
        is_valid, message = check_response(response)
        print(f"테스트: {response:<20} ({description})")
        print(f"결과: {'✓' if is_valid else '✗'} {message}\n")

    print("--- parse_by_lengths 테스트 (엄격한 규칙 적용) ---")
    parsed = parse_by_lengths("SRV", "0")
    print(f"'1234567891', '3124' -> {parsed} (예상: None)")








