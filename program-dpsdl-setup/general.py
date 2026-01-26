from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame,
    QComboBox, QFileDialog, QMessageBox, QApplication
)

from utils import *
import protocol as ptcl
import time


class GeneralTab(QWidget):


    def __init__(self, parent):
        """
            '기본 설정' 탭의 UI와 기능을 모두 담고 있는 클래스입니다.
            parent 인자로는 MainWindow의 인스턴스(self)가 전달됩니다.
        """

        super().__init__()

        self.main_window = parent

        main_layout = QVBoxLayout(self)


        # Version..........
        version_layout = QHBoxLayout()
        version_button = QPushButton("Version")
        self.version_label = QLabel("---")
        self.version_label.setMinimumWidth(150)

        version_layout.addWidget( version_button )
        version_layout.addWidget( self.version_label )
        version_layout.addStretch( 1 )

        main_layout.addLayout( version_layout )


        # line .................
        line = QFrame()
        line.setFrameShape( QFrame.Shape.HLine )
        line.setFrameShadow( QFrame.Shadow.Sunken )
        main_layout.addWidget( line )

        # CSV Export/Import..........
        csv_layout = QHBoxLayout()
        
        export_csv_button = QPushButton("Export to CSV")
        export_csv_button.setMinimumHeight(30)
        
        import_csv_button = QPushButton("Import from CSV")
        import_csv_button.setMinimumHeight(30)

        csv_layout.addWidget( export_csv_button )
        csv_layout.addWidget( import_csv_button )
        csv_layout.addStretch( 1 )

        main_layout.addLayout( csv_layout )

        # line .................
        line2 = QFrame()
        line2.setFrameShape( QFrame.Shape.HLine )
        line2.setFrameShadow( QFrame.Shadow.Sunken )
        main_layout.addWidget( line2 )




        # Factory Initialization

        factory_reset_layout = QHBoxLayout()

        self.factory_reset_combo =  QComboBox()
        self.factory_reset_combo.addItems( [
            "0: Config Format",
            "1: ID Format",
            "2: Sensing Value Format",
            "3: All Format"
            ])
        factory_reset_button = QPushButton("SET")


        factory_reset_layout.addWidget( QLabel("Factory Reset") )
        factory_reset_layout.addWidget( self.factory_reset_combo )
        factory_reset_layout.addWidget( factory_reset_button )
        factory_reset_layout.addStretch( 1 )


        main_layout.addLayout( factory_reset_layout )



        # Set Date & Time
        date_time_layout = QHBoxLayout()
        layout13_config = [
                {'type': 'date_time', 'label': '시간 설정:', 'name': 'datetime', 'default_time': '00:00', 'date_width': 110, 'time_width': 70},
                {'type': 'button', 'text':'SET', 'name':'set_btn'},
        ]
        group, self.dateTime = create_dynamic_group('Setting Date & Time (cmd=6)', layout13_config )

        date_time_layout.addWidget( group )
        date_time_layout.addStretch( 1 )
        

        main_layout.addLayout( date_time_layout )




        main_layout.addStretch(1)

        version_button.clicked.connect(self.send_version_command)
        #export_csv_button.clicked.connect(self.export_to_csv)
        #import_csv_button.clicked.connect(self.import_from_csv)
        factory_reset_button.clicked.connect( self.execute_selected_option )
        self.dateTime['set_btn'].clicked.connect( self.date_time_set_btn )

    def date_time_set_btn( self ):

        #print("clicked")
        data_str = self.dateTime['datetime_date'].date().toString("yyMMdd")
        data_str += (self.dateTime['datetime_time'].text() or '00:00').replace(':','')

        #command, response = self.data_command( "6", data_str )

        command = ptcl.STX + "6" + data_str + "Q"
        response = self.main_window.send_command_unified(command)
        self.main_window.add_log("날짜 시간 Setting은 응답없음.")




    def execute_selected_option( self ):

        data_str = str(self.factory_reset_combo.currentIndex())

        print("data = ", data_str )
        command, response = self.server_common_command( "W", "R", data_str )


    def send_version_command(self):

        command, response = self.server_common_command( "R", "V" )

        is_valid, error_message = check_response(response)
        if not is_valid:
            self.main_window.add_log(f"응답 검증 실패: {error_message}")
            return
        
        """'Version' 버튼 클릭 시 호출됩니다."""
        # MainWindow의 통신 메서드를 직접 호출
        
        ans = trim_string( response, 3, 3 )
        print('ans =', ans)

        self.version_label.setText(ans)

        print("com = ", command)
        print("res = ", response)


    def server_common_command( self, DIR, CMD, data_str=None):

        command = ptcl.STX + DIR + CMD

        if  data_str:
            command += data_str

        command = add_tail( command )

        response = self.main_window.send_command_unified( command )
        return command, response
