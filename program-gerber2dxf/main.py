#!/usr/bin/env python3
"""
Gerber to DXF Converter - Desktop GUI
독립 실행 가능한 데스크톱 GUI 프로그램
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QRadioButton, QTextEdit,
    QFileDialog, QMessageBox, QProgressBar, QGroupBox, QButtonGroup,
    QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import os
import math
import zipfile
import tempfile
import shutil
from pathlib import Path
import ezdxf
from gerbonara import GerberFile
from gerbonara.graphic_objects import Line, Arc, Region, Flash


# 레이어별 색상 정의
LAYER_COLORS = {
    'GTL': 1,    # Red - Top Copper
    'GBL': 5,    # Blue - Bottom Copper
    'GTO': 2,    # Yellow - Top Overlay/Silkscreen
    'GBO': 2,    # Yellow - Bottom Overlay
    'GTS': 3,    # Green - Top Solder Mask
    'GBS': 3,    # Green - Bottom Solder Mask
    'GKO': 7,    # White - Keepout/Outline
    'G1': 6,     # Magenta - Inner Layer 1
    'G2': 6,     # Magenta - Inner Layer 2
    'G3': 6,     # Magenta - Inner Layer 3
    'G4': 6,     # Magenta - Inner Layer 4
    'GD1': 8,    # Dark Gray - Drill
    'GG1': 4,    # Cyan - Ground
}


def add_gerber_to_dxf(doc, msp, gerber_path, layer_name):
    """Add Gerber file content to existing DXF document"""
    try:
        gerber = GerberFile.open(gerber_path)

        layer_color = LAYER_COLORS.get(layer_name.upper(), 7)
        doc.layers.add(layer_name, color=layer_color)

        converted_count = 0
        for obj in gerber.objects:
            try:
                if isinstance(obj, Line):
                    msp.add_line(
                        (obj.x1, obj.y1),
                        (obj.x2, obj.y2),
                        dxfattribs={'layer': layer_name}
                    )
                    converted_count += 1

                elif isinstance(obj, Arc):
                    center = obj.center
                    center_x = center.x if hasattr(center, 'x') else (obj.x1 + obj.cx)
                    center_y = center.y if hasattr(center, 'y') else (obj.y1 + obj.cy)
                    radius = math.sqrt(obj.cx**2 + obj.cy**2)

                    start_angle = math.degrees(math.atan2(obj.y1 - center_y, obj.x1 - center_x))
                    end_angle = math.degrees(math.atan2(obj.y2 - center_y, obj.x2 - center_x))

                    if obj.clockwise:
                        start_angle, end_angle = end_angle, start_angle

                    msp.add_arc(
                        center=(center_x, center_y),
                        radius=radius,
                        start_angle=start_angle,
                        end_angle=end_angle,
                        dxfattribs={'layer': layer_name}
                    )
                    converted_count += 1

                elif isinstance(obj, Region):
                    vertices = []
                    for segment in obj.outline:
                        if isinstance(segment, tuple) and len(segment) >= 2:
                            vertices.append((segment[0], segment[1]))
                        elif hasattr(segment, 'x1') and hasattr(segment, 'y1'):
                            vertices.append((segment.x1, segment.y1))
                            if hasattr(segment, 'x2') and hasattr(segment, 'y2'):
                                vertices.append((segment.x2, segment.y2))

                    unique_vertices = []
                    for v in vertices:
                        if not unique_vertices or abs(v[0] - unique_vertices[-1][0]) > 0.001 or abs(v[1] - unique_vertices[-1][1]) > 0.001:
                            unique_vertices.append(v)

                    if len(unique_vertices) >= 3:
                        if abs(unique_vertices[0][0] - unique_vertices[-1][0]) > 0.001 or abs(unique_vertices[0][1] - unique_vertices[-1][1]) > 0.001:
                            unique_vertices.append(unique_vertices[0])

                        msp.add_lwpolyline(
                            unique_vertices,
                            dxfattribs={'layer': layer_name}
                        )
                        converted_count += 1

                elif isinstance(obj, Flash):
                    aperture = obj.aperture
                    aperture_type = type(aperture).__name__

                    if aperture_type == 'CircleAperture':
                        if hasattr(aperture, 'diameter'):
                            radius = aperture.diameter / 2
                            msp.add_circle(
                                center=(obj.x, obj.y),
                                radius=radius,
                                dxfattribs={'layer': layer_name}
                            )
                            converted_count += 1

                    elif aperture_type == 'RectangleAperture':
                        if hasattr(aperture, 'w'):
                            w = aperture.w / 2
                            h = getattr(aperture, 'h', aperture.w) / 2
                            points = [
                                (obj.x - w, obj.y - h),
                                (obj.x + w, obj.y - h),
                                (obj.x + w, obj.y + h),
                                (obj.x - w, obj.y + h),
                                (obj.x - w, obj.y - h)
                            ]
                            msp.add_lwpolyline(
                                points,
                                dxfattribs={'layer': layer_name}
                            )
                            converted_count += 1

                    elif aperture_type == 'ObroundAperture':
                        if hasattr(aperture, 'w'):
                            w = aperture.w / 2
                            h = getattr(aperture, 'h', aperture.w) / 2
                            points = [
                                (obj.x - w, obj.y - h),
                                (obj.x + w, obj.y - h),
                                (obj.x + w, obj.y + h),
                                (obj.x - w, obj.y + h),
                                (obj.x - w, obj.y - h)
                            ]
                            msp.add_lwpolyline(
                                points,
                                dxfattribs={'layer': layer_name}
                            )
                            converted_count += 1

                    elif aperture_type == 'ApertureMacroInstance':
                        primitives = aperture.flash(obj.x, obj.y, obj.unit, obj.polarity_dark)
                        for prim in primitives:
                            prim_type = type(prim).__name__

                            if prim_type == 'Circle':
                                msp.add_circle(
                                    center=(prim.x, prim.y),
                                    radius=prim.r,
                                    dxfattribs={'layer': layer_name}
                                )
                            elif prim_type == 'Rectangle':
                                w = prim.w / 2
                                h = prim.h / 2
                                cx, cy = prim.x, prim.y

                                cos_r = math.cos(math.radians(prim.rotation))
                                sin_r = math.sin(math.radians(prim.rotation))

                                corners = [
                                    (-w, -h), (w, -h), (w, h), (-w, h), (-w, -h)
                                ]

                                points = []
                                for x, y in corners:
                                    rx = cx + x * cos_r - y * sin_r
                                    ry = cy + x * sin_r + y * cos_r
                                    points.append((rx, ry))

                                msp.add_lwpolyline(
                                    points,
                                    dxfattribs={'layer': layer_name}
                                )

                        converted_count += 1

                    else:
                        if hasattr(aperture, 'equivalent_width'):
                            try:
                                width = aperture.equivalent_width()
                                if callable(width):
                                    width = width()
                                radius = width / 2
                                msp.add_circle(
                                    center=(obj.x, obj.y),
                                    radius=radius,
                                    dxfattribs={'layer': layer_name}
                                )
                                converted_count += 1
                            except:
                                pass

            except Exception:
                pass

        return converted_count, len(gerber.objects)

    except Exception as e:
        return 0, 0


class ConversionThread(QThread):
    """변환 작업을 백그라운드에서 수행하는 스레드"""
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    show_message_signal = pyqtSignal(str, str)  # title, message

    def __init__(self, converter):
        super().__init__()
        self.converter = converter

    def run(self):
        try:
            # Extract ZIP if needed
            input_dir = self.converter.prepare_input()

            if self.converter.mode == "merged":
                self.converter.convert_merged(input_dir)
            else:
                self.converter.convert_separate(input_dir)

            self.finished_signal.emit(True, "변환 완료")
        except Exception as e:
            self.log_signal.emit(f"\n❌ 오류 발생: {str(e)}")
            self.finished_signal.emit(False, str(e))
        finally:
            self.converter.cleanup_temp()


class GerberConverterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerber to DXF Converter")
        self.setGeometry(100, 100, 800, 600)

        # Variables
        self.input_path = ""
        self.input_type = "folder"  # "folder" or "zip"
        self.output_file = ""
        self.mode = "merged"  # "merged" or "separate"
        self.temp_dir = None
        self.conversion_thread = None

        self.setup_ui()

    def setup_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title_label = QLabel("Gerber to DXF Converter")
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        subtitle_label = QLabel("PCB Gerber 파일을 DXF 포맷으로 변환")
        subtitle_font = QFont("Arial", 10)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle_label)

        # Input type selection
        input_type_group = QGroupBox("입력 타입")
        input_type_layout = QHBoxLayout()
        self.input_type_button_group = QButtonGroup()

        self.folder_radio = QRadioButton("폴더")
        self.folder_radio.setChecked(True)
        self.folder_radio.toggled.connect(lambda: self.set_input_type("folder"))
        self.input_type_button_group.addButton(self.folder_radio)
        input_type_layout.addWidget(self.folder_radio)

        self.zip_radio = QRadioButton("ZIP 파일")
        self.zip_radio.toggled.connect(lambda: self.set_input_type("zip"))
        self.input_type_button_group.addButton(self.zip_radio)
        input_type_layout.addWidget(self.zip_radio)

        input_type_layout.addStretch()
        input_type_group.setLayout(input_type_layout)
        main_layout.addWidget(input_type_group)

        # Input file/directory
        input_group = QGroupBox("입력 파일/폴더")
        input_layout = QHBoxLayout()
        self.input_path_edit = QLineEdit()
        input_layout.addWidget(self.input_path_edit)
        input_browse_btn = QPushButton("찾아보기...")
        input_browse_btn.clicked.connect(self.browse_input)
        input_layout.addWidget(input_browse_btn)
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        # Mode selection
        mode_group = QGroupBox("변환 모드")
        mode_layout = QVBoxLayout()
        self.mode_button_group = QButtonGroup()

        self.merged_radio = QRadioButton("하나의 DXF로 병합 (여러 레이어)")
        self.merged_radio.setChecked(True)
        self.merged_radio.toggled.connect(lambda: self.set_mode("merged"))
        self.mode_button_group.addButton(self.merged_radio)
        mode_layout.addWidget(self.merged_radio)

        self.separate_radio = QRadioButton("개별 DXF 파일로 분리")
        self.separate_radio.toggled.connect(lambda: self.set_mode("separate"))
        self.mode_button_group.addButton(self.separate_radio)
        mode_layout.addWidget(self.separate_radio)

        mode_group.setLayout(mode_layout)
        main_layout.addWidget(mode_group)

        # Output file
        output_group = QGroupBox("출력 파일/폴더")
        output_layout = QHBoxLayout()
        self.output_file_edit = QLineEdit()
        output_layout.addWidget(self.output_file_edit)
        output_browse_btn = QPushButton("찾아보기...")
        output_browse_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(output_browse_btn)
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        convert_btn = QPushButton("변환 시작")
        convert_btn.setMinimumWidth(120)
        convert_btn.clicked.connect(self.start_conversion)
        button_layout.addWidget(convert_btn)

        quit_btn = QPushButton("종료")
        quit_btn.setMinimumWidth(120)
        quit_btn.clicked.connect(self.close)
        button_layout.addWidget(quit_btn)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        # Progress
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(0)  # Indeterminate mode
        self.progress.setVisible(False)
        main_layout.addWidget(self.progress)

        # Log output
        log_group = QGroupBox("변환 로그")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("준비")

    def set_input_type(self, input_type):
        self.input_type = input_type

    def set_mode(self, mode):
        self.mode = mode

    def browse_input(self):
        if self.input_type == "folder":
            path = QFileDialog.getExistingDirectory(
                self,
                "Gerber 파일이 있는 폴더를 선택하세요"
            )
            if path:
                self.input_path = path
                self.input_path_edit.setText(path)
                self.log(f"입력 폴더 선택: {path}")
        else:  # zip
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Gerber ZIP 파일을 선택하세요",
                "",
                "ZIP files (*.zip);;All files (*.*)"
            )
            if path:
                self.input_path = path
                self.input_path_edit.setText(path)
                self.log(f"입력 ZIP 파일 선택: {path}")

    def browse_output(self):
        if self.mode == "merged":
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "저장할 DXF 파일 이름",
                "",
                "DXF files (*.dxf);;All files (*.*)"
            )
            if filename:
                if not filename.endswith('.dxf'):
                    filename += '.dxf'
                self.output_file = filename
                self.output_file_edit.setText(filename)
                self.log(f"출력 파일: {filename}")
        else:
            directory = QFileDialog.getExistingDirectory(
                self,
                "DXF 파일을 저장할 폴더를 선택하세요"
            )
            if directory:
                self.output_file = directory
                self.output_file_edit.setText(directory)
                self.log(f"출력 폴더: {directory}")

    def log(self, message):
        self.log_text.append(message)
        self.log_text.ensureCursorVisible()
        QApplication.processEvents()

    def start_conversion(self):
        if not self.input_path:
            QMessageBox.critical(self, "오류", "입력 파일/폴더를 선택하세요")
            return

        if not self.output_file:
            QMessageBox.critical(self, "오류", "출력 파일/폴더를 선택하세요")
            return

        if not os.path.exists(self.input_path):
            QMessageBox.critical(self, "오류", "입력 파일/폴더가 존재하지 않습니다")
            return

        # Run conversion in separate thread
        self.progress.setVisible(True)
        self.status_bar.showMessage("변환 중...")
        self.log_text.clear()

        self.conversion_thread = ConversionThread(self)
        self.conversion_thread.log_signal.connect(self.log)
        self.conversion_thread.finished_signal.connect(self.on_conversion_finished)
        self.conversion_thread.show_message_signal.connect(self.show_message)
        self.conversion_thread.start()

    def on_conversion_finished(self, success, message):
        self.progress.setVisible(False)
        if success:
            self.status_bar.showMessage("변환 완료")
        else:
            self.status_bar.showMessage("변환 실패")
            QMessageBox.critical(self, "변환 실패", message)

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def prepare_input(self):
        """Prepare input directory (extract ZIP if needed)"""
        if self.input_type == "zip":
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp()
            zip_path = self.input_path

            self.conversion_thread.log_signal.emit(f"ZIP 파일 압축 해제 중: {zip_path}")

            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.temp_dir)

                self.conversion_thread.log_signal.emit(f"✓ 압축 해제 완료: {self.temp_dir}")
                return self.temp_dir
            except Exception as e:
                raise Exception(f"ZIP 파일 압축 해제 실패: {str(e)}")
        else:
            return self.input_path

    def cleanup_temp(self):
        """Clean up temporary directory"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
            except:
                pass

    def convert_merged(self, input_dir):
        input_path = Path(input_dir)
        output_file = self.output_file

        # Find Gerber files (recursive search for ZIP files)
        gerber_extensions = [
            '.gbr', '.gtl', '.gbl', '.gto', '.gbo', '.gts', '.gbs',
            '.gko', '.g1', '.g2', '.g3', '.g4', '.gd1', '.gg1'
        ]

        gerber_files = []
        for ext in gerber_extensions:
            gerber_files.extend(input_path.rglob(f'*{ext}'))
            gerber_files.extend(input_path.rglob(f'*{ext.upper()}'))

        if not gerber_files:
            raise Exception(f"Gerber 파일을 찾을 수 없습니다: {input_path}")

        self.conversion_thread.log_signal.emit(f"발견된 Gerber 파일: {len(gerber_files)}개")
        self.conversion_thread.log_signal.emit("-" * 60)

        # Create DXF document
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()

        total_converted = 0
        total_objects = 0

        for gerber_file in gerber_files:
            layer_name = gerber_file.suffix[1:].upper()
            self.conversion_thread.log_signal.emit(f"처리 중: {gerber_file.name} → 레이어: {layer_name}")

            converted, total = add_gerber_to_dxf(doc, msp, str(gerber_file), layer_name)
            total_converted += converted
            total_objects += total

            self.conversion_thread.log_signal.emit(f"  ✓ {converted}/{total} 객체 변환")

        # Save DXF
        doc.saveas(output_file)

        self.conversion_thread.log_signal.emit("-" * 60)
        self.conversion_thread.log_signal.emit(f"✅ 변환 완료!")
        self.conversion_thread.log_signal.emit(f"  출력 파일: {output_file}")
        self.conversion_thread.log_signal.emit(f"  총 레이어: {len(gerber_files)}개")
        self.conversion_thread.log_signal.emit(f"  총 객체: {total_converted}/{total_objects}개")

        # Show completion message in main thread
        self.conversion_thread.show_message_signal.emit(
            "변환 완료",
            f"변환이 완료되었습니다!\n\n"
            f"레이어: {len(gerber_files)}개\n"
            f"객체: {total_converted}/{total_objects}개"
        )

    def convert_separate(self, input_dir):
        input_path = Path(input_dir)
        output_path = Path(self.output_file)
        output_path.mkdir(parents=True, exist_ok=True)

        # Find Gerber files (recursive search for ZIP files)
        gerber_extensions = [
            '.gbr', '.gtl', '.gbl', '.gto', '.gbo', '.gts', '.gbs',
            '.gko', '.g1', '.g2', '.g3', '.g4', '.gd1', '.gg1'
        ]

        gerber_files = []
        for ext in gerber_extensions:
            gerber_files.extend(input_path.rglob(f'*{ext}'))
            gerber_files.extend(input_path.rglob(f'*{ext.upper()}'))

        if not gerber_files:
            raise Exception(f"Gerber 파일을 찾을 수 없습니다: {input_path}")

        self.conversion_thread.log_signal.emit(f"발견된 Gerber 파일: {len(gerber_files)}개")
        self.conversion_thread.log_signal.emit("-" * 60)

        success_count = 0
        total_converted = 0
        total_objects = 0

        for gerber_file in gerber_files:
            dxf_file = output_path / f"{gerber_file.name}.dxf"
            layer_name = gerber_file.name

            self.conversion_thread.log_signal.emit(f"변환 중: {gerber_file.name} → {dxf_file.name}")

            try:
                doc = ezdxf.new('R2010')
                msp = doc.modelspace()

                converted, total = add_gerber_to_dxf(doc, msp, str(gerber_file), layer_name)
                doc.saveas(str(dxf_file))

                total_converted += converted
                total_objects += total
                success_count += 1

                self.conversion_thread.log_signal.emit(f"  ✓ {converted}/{total} 객체 변환")
            except Exception as e:
                self.conversion_thread.log_signal.emit(f"  ✗ 실패: {str(e)}")

        self.conversion_thread.log_signal.emit("-" * 60)
        self.conversion_thread.log_signal.emit(f"✅ 변환 완료!")
        self.conversion_thread.log_signal.emit(f"  출력 폴더: {output_path}")
        self.conversion_thread.log_signal.emit(f"  성공: {success_count}/{len(gerber_files)} 파일")
        self.conversion_thread.log_signal.emit(f"  총 객체: {total_converted}/{total_objects}개")

        # Show completion message in main thread
        self.conversion_thread.show_message_signal.emit(
            "변환 완료",
            f"변환이 완료되었습니다!\n\n"
            f"성공: {success_count}/{len(gerber_files)} 파일\n"
            f"객체: {total_converted}/{total_objects}개"
        )


    def closeEvent(self, event):
        """윈도우 종료 이벤트 처리"""
        reply = QMessageBox.question(
            self,
            "종료",
            "프로그램을 종료하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.cleanup_temp()
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    window = GerberConverterGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
