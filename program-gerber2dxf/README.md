# Gerber to DXF Converter - Desktop Version

PCB Gerber 파일을 DXF 포맷으로 변환하는 데스크톱 프로그램

## 설치

### Windows

자세한 설치 방법은 [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md) 참조

1. Python 3.8 이상 설치 (python.org에서 다운로드)
2. 의존성 설치:
```cmd
pip install -r requirements.txt
```

### Linux

자세한 설치 방법은 [INSTALL_LINUX.md](INSTALL_LINUX.md) 참조

1. tkinter 설치:
```bash
sudo apt-get install python3-tk
```

2. 의존성 설치:
```bash
pip install -r requirements.txt
```

## 사용법

### 방법 1: 데스크톱 GUI (추천)

독립 실행 가능한 GUI 프로그램:

**Windows:**
```cmd
python gerber2dxf_gui.py
```

**Linux:**
```bash
python3 gerber2dxf_gui.py
```

#### GUI 사용법:

1. **입력 타입 선택**
   - 폴더: Gerber 파일이 있는 폴더
   - ZIP 파일: 압축된 Gerber 파일

2. **입력 파일/폴더 선택**
   - "찾아보기" 버튼 클릭하여 선택

3. **변환 모드 선택**
   - **병합 모드**: 여러 Gerber를 하나의 DXF로 (레이어별 색상)
   - **분리 모드**: 각 Gerber를 개별 DXF로

4. **출력 파일/폴더 선택**
   - 병합 모드: DXF 파일 이름 지정
   - 분리 모드: 출력 폴더 선택

5. **변환 시작** 버튼 클릭

6. 변환 완료 후 **종료** 버튼으로 프로그램 종료

### 방법 2: 명령줄 (CLI)

#### 개별 DXF 파일로 변환:

**Windows:**
```cmd
python gerber2dxf.py ./Gerber ./output
```

**Linux:**
```bash
python3 gerber2dxf.py ./Gerber ./output
```

#### 하나의 DXF로 병합 (레이어별 색상):

**Windows:**
```cmd
python gerber2dxf_merged.py ./Gerber merged_pcb.dxf
```

**Linux:**
```bash
python3 gerber2dxf_merged.py ./Gerber merged_pcb.dxf
```

## 파일 설명

- **gerber2dxf_gui.py** - 데스크톱 GUI 프로그램 (메인)
- **gerber2dxf.py** - CLI 버전 (각 Gerber를 개별 DXF로)
- **gerber2dxf_merged.py** - CLI 버전 (여러 Gerber를 하나의 DXF로)
- **requirements.txt** - 필요한 라이브러리 목록
- **INSTALL_WINDOWS.md** - Windows 설치 가이드
- **INSTALL_LINUX.md** - Linux 설치 가이드

## 지원하는 Gerber 파일

- .GTL (Top Layer) - 빨강
- .GBL (Bottom Layer) - 파랑
- .GTO (Top Overlay) - 노랑
- .GBO (Bottom Overlay) - 노랑
- .GTS (Top Solder Mask) - 초록
- .GBS (Bottom Solder Mask) - 초록
- .GKO (Keep Out / Board Outline) - 흰색
- .G1, .G2, .G3, .G4 (Inner Layers) - 마젠타
- .GD1 (Drill) - 회색
- .GG1 (Ground) - 청록

## 레이어 색상 (병합 모드)

병합 모드에서 각 레이어는 DXF에서 다음 색상으로 표시됩니다:

| 레이어 | 색상 | 설명 |
|--------|------|------|
| GTL | Red | Top Copper |
| GBL | Blue | Bottom Copper |
| GTO/GBO | Yellow | Overlay/Silkscreen |
| GTS/GBS | Green | Solder Mask |
| GKO | White | Board Outline |
| G1-G4 | Magenta | Inner Layers |
| GD1 | Dark Gray | Drill |
| GG1 | Cyan | Ground |

## DXF 파일 사용

생성된 DXF 파일은 다음 프로그램에서 열 수 있습니다:
- AutoCAD
- LibreCAD (무료)
- QCAD (무료)
- FreeCAD (무료)
- DraftSight

## 문제 해결

### Windows에서 tkinter 없음
- [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md) 참조

### Linux에서 tkinter 없음
```bash
sudo apt-get install python3-tk
```

### "No module named 'gerbonara'" 오류
```bash
pip install -r requirements.txt
```

## 기술 스택

- **gerbonara** - Gerber 파일 파싱
- **ezdxf** - DXF 파일 생성
- **tkinter** - 데스크톱 GUI (Python 표준 라이브러리)

## 라이선스

MIT License
