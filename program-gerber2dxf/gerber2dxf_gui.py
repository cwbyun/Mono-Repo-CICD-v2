#!/usr/bin/env python3
"""
Gerber to DXF Converter - Desktop GUI
독립 실행 가능한 데스크톱 GUI 프로그램
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
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


class GerberConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerber to DXF Converter")
        self.root.geometry("800x600")

        # Variables
        self.input_path = tk.StringVar()
        self.input_type = tk.StringVar(value="folder")  # "folder" or "zip"
        self.output_file = tk.StringVar()
        self.mode = tk.StringVar(value="merged")  # "merged" or "separate"
        self.temp_dir = None

        # Window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        self.setup_ui()

    def setup_ui(self):
        # Title
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        ttk.Label(title_frame, text="Gerber to DXF Converter",
                 font=('Arial', 16, 'bold')).pack()
        ttk.Label(title_frame, text="PCB Gerber 파일을 DXF 포맷으로 변환",
                 font=('Arial', 10)).pack()

        # Input type selection
        input_type_frame = ttk.LabelFrame(self.root, text="입력 타입", padding="10")
        input_type_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Radiobutton(input_type_frame, text="폴더",
                       variable=self.input_type, value="folder").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(input_type_frame, text="ZIP 파일",
                       variable=self.input_type, value="zip").pack(side=tk.LEFT, padx=5)

        # Input file/directory
        input_frame = ttk.LabelFrame(self.root, text="입력 파일/폴더", padding="10")
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Entry(input_frame, textvariable=self.input_path, width=60).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(input_frame, text="찾아보기...", command=self.browse_input).pack(side=tk.LEFT)

        # Mode selection
        mode_frame = ttk.LabelFrame(self.root, text="변환 모드", padding="10")
        mode_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Radiobutton(mode_frame, text="하나의 DXF로 병합 (여러 레이어)",
                       variable=self.mode, value="merged").pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="개별 DXF 파일로 분리",
                       variable=self.mode, value="separate").pack(anchor=tk.W)

        # Output file
        output_frame = ttk.LabelFrame(self.root, text="출력 파일/폴더", padding="10")
        output_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Entry(output_frame, textvariable=self.output_file, width=60).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(output_frame, text="찾아보기...", command=self.browse_output).pack(side=tk.LEFT)

        # Buttons
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)

        button_inner_frame = ttk.Frame(button_frame)
        button_inner_frame.pack()

        ttk.Button(button_inner_frame, text="변환 시작", command=self.start_conversion,
                  width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_inner_frame, text="종료", command=self.quit_app,
                  width=15).pack(side=tk.LEFT, padx=5)

        # Progress
        progress_frame = ttk.Frame(self.root, padding="10")
        progress_frame.pack(fill=tk.X)
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X)

        # Log output
        log_frame = ttk.LabelFrame(self.root, text="변환 로그", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_bar = ttk.Label(self.root, text="준비", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def browse_input(self):
        if self.input_type.get() == "folder":
            path = filedialog.askdirectory(title="Gerber 파일이 있는 폴더를 선택하세요")
            if path:
                self.input_path.set(path)
                self.log(f"입력 폴더 선택: {path}")
        else:  # zip
            path = filedialog.askopenfilename(
                title="Gerber ZIP 파일을 선택하세요",
                filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
            )
            if path:
                self.input_path.set(path)
                self.log(f"입력 ZIP 파일 선택: {path}")

    def browse_output(self):
        if self.mode.get() == "merged":
            filename = filedialog.asksaveasfilename(
                title="저장할 DXF 파일 이름",
                defaultextension=".dxf",
                filetypes=[("DXF files", "*.dxf"), ("All files", "*.*")]
            )
            if filename:
                self.output_file.set(filename)
                self.log(f"출력 파일: {filename}")
        else:
            directory = filedialog.askdirectory(title="DXF 파일을 저장할 폴더를 선택하세요")
            if directory:
                self.output_file.set(directory)
                self.log(f"출력 폴더: {directory}")

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def quit_app(self):
        """종료 확인 후 프로그램 종료"""
        if messagebox.askyesno("종료", "프로그램을 종료하시겠습니까?"):
            self.cleanup_temp()
            self.root.quit()
            self.root.destroy()

    def start_conversion(self):
        if not self.input_path.get():
            messagebox.showerror("오류", "입력 파일/폴더를 선택하세요")
            return

        if not self.output_file.get():
            messagebox.showerror("오류", "출력 파일/폴더를 선택하세요")
            return

        if not os.path.exists(self.input_path.get()):
            messagebox.showerror("오류", "입력 파일/폴더가 존재하지 않습니다")
            return

        # Run conversion in separate thread
        thread = threading.Thread(target=self.convert)
        thread.daemon = True
        thread.start()

    def convert(self):
        self.progress.start()
        self.status_bar.config(text="변환 중...")
        self.log_text.delete(1.0, tk.END)

        try:
            # Extract ZIP if needed
            input_dir = self.prepare_input()

            if self.mode.get() == "merged":
                self.convert_merged(input_dir)
            else:
                self.convert_separate(input_dir)
        except Exception as e:
            self.log(f"\n❌ 오류 발생: {str(e)}")
            self.status_bar.config(text="변환 실패")
            messagebox.showerror("변환 실패", str(e))
        finally:
            self.cleanup_temp()
            self.progress.stop()

    def prepare_input(self):
        """Prepare input directory (extract ZIP if needed)"""
        if self.input_type.get() == "zip":
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp()
            zip_path = self.input_path.get()

            self.log(f"ZIP 파일 압축 해제 중: {zip_path}")

            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.temp_dir)

                self.log(f"✓ 압축 해제 완료: {self.temp_dir}")
                return self.temp_dir
            except Exception as e:
                raise Exception(f"ZIP 파일 압축 해제 실패: {str(e)}")
        else:
            return self.input_path.get()

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
        output_file = self.output_file.get()

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

        self.log(f"발견된 Gerber 파일: {len(gerber_files)}개")
        self.log("-" * 60)

        # Create DXF document
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()

        total_converted = 0
        total_objects = 0

        for gerber_file in gerber_files:
            layer_name = gerber_file.suffix[1:].upper()
            self.log(f"처리 중: {gerber_file.name} → 레이어: {layer_name}")

            converted, total = add_gerber_to_dxf(doc, msp, str(gerber_file), layer_name)
            total_converted += converted
            total_objects += total

            self.log(f"  ✓ {converted}/{total} 객체 변환")

        # Save DXF
        doc.saveas(output_file)

        self.log("-" * 60)
        self.log(f"✅ 변환 완료!")
        self.log(f"  출력 파일: {output_file}")
        self.log(f"  총 레이어: {len(gerber_files)}개")
        self.log(f"  총 객체: {total_converted}/{total_objects}개")

        self.status_bar.config(text=f"변환 완료: {total_converted}/{total_objects} 객체")
        messagebox.showinfo("변환 완료",
                           f"변환이 완료되었습니다!\n\n"
                           f"레이어: {len(gerber_files)}개\n"
                           f"객체: {total_converted}/{total_objects}개")

    def convert_separate(self, input_dir):
        input_path = Path(input_dir)
        output_path = Path(self.output_file.get())
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

        self.log(f"발견된 Gerber 파일: {len(gerber_files)}개")
        self.log("-" * 60)

        success_count = 0
        total_converted = 0
        total_objects = 0

        for gerber_file in gerber_files:
            dxf_file = output_path / f"{gerber_file.name}.dxf"
            layer_name = gerber_file.name

            self.log(f"변환 중: {gerber_file.name} → {dxf_file.name}")

            try:
                doc = ezdxf.new('R2010')
                msp = doc.modelspace()

                converted, total = add_gerber_to_dxf(doc, msp, str(gerber_file), layer_name)
                doc.saveas(str(dxf_file))

                total_converted += converted
                total_objects += total
                success_count += 1

                self.log(f"  ✓ {converted}/{total} 객체 변환")
            except Exception as e:
                self.log(f"  ✗ 실패: {str(e)}")

        self.log("-" * 60)
        self.log(f"✅ 변환 완료!")
        self.log(f"  출력 폴더: {output_path}")
        self.log(f"  성공: {success_count}/{len(gerber_files)} 파일")
        self.log(f"  총 객체: {total_converted}/{total_objects}개")

        self.status_bar.config(text=f"변환 완료: {success_count}/{len(gerber_files)} 파일")
        messagebox.showinfo("변환 완료",
                           f"변환이 완료되었습니다!\n\n"
                           f"성공: {success_count}/{len(gerber_files)} 파일\n"
                           f"객체: {total_converted}/{total_objects}개")


def main():
    root = tk.Tk()
    app = GerberConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
