# Linux 설치 가이드

## tkinter 설치 (리눅스)

리눅스에서는 tkinter를 별도로 설치해야 합니다.

### Ubuntu / Debian / Linux Mint
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

### Fedora / RHEL / CentOS
```bash
sudo dnf install python3-tkinter
# 또는 yum
sudo yum install python3-tkinter
```

### Arch Linux / Manjaro
```bash
sudo pacman -S tk
```

### openSUSE
```bash
sudo zypper install python3-tk
```

## 설치 순서

### 1. tkinter 설치
```bash
sudo apt-get install python3-tk
```

### 2. tkinter 확인
```bash
python3 -m tkinter
```
작은 창이 뜨면 성공입니다.

### 3. 프로젝트 의존성 설치
```bash
# 가상환경 생성 (선택사항)
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 4. 프로그램 실행

#### 데스크톱 GUI
```bash
python3 gerber2dxf_gui.py
```

#### CLI 버전 (tkinter 불필요)
```bash
python3 gerber2dxf_merged.py ./Gerber merged.dxf
```

## 문제 해결

### "No module named '_tkinter'" 오류

tkinter가 설치되지 않았거나, Python이 tkinter 지원 없이 빌드되었습니다.

**해결:**
```bash
sudo apt-get install python3-tk
```

### 가상환경에서 tkinter를 찾을 수 없음

가상환경 생성 시 시스템 패키지 접근을 허용:
```bash
python3 -m venv venv --system-site-packages
source venv/bin/activate
```

### X11/Display 오류 (서버 환경)

GUI가 없는 서버 환경에서는 CLI 버전 사용:
```bash
python3 gerber2dxf.py ./Gerber ./output
python3 gerber2dxf_merged.py ./Gerber merged.dxf
```

### WSL (Windows Subsystem for Linux)

WSL2에서 GUI 실행:
1. Windows 11: X서버 자동 지원
2. Windows 10: VcXsrv 또는 X410 설치 필요

```bash
# DISPLAY 환경변수 설정 (필요시)
export DISPLAY=:0
```

## 전체 설치 확인

```bash
python3 -c "import tkinter; import gerbonara; import ezdxf; print('✓ 모든 라이브러리 정상')"
```

## 빠른 시작 (Ubuntu/Debian)

```bash
# 1. tkinter 설치
sudo apt-get update && sudo apt-get install python3-tk

# 2. 의존성 설치
pip install -r requirements.txt

# 3. GUI 실행
python3 gerber2dxf_gui.py
```
