# Windows 설치 가이드

## tkinter 설치 문제 해결

Windows에서 tkinter가 없다는 오류가 발생하면 다음 방법으로 해결하세요.

### 방법 1: Python 재설치 (권장)

1. [Python 공식 사이트](https://www.python.org/downloads/)에서 최신 버전 다운로드
2. 설치 시 **"tcl/tk and IDLE"** 옵션을 반드시 체크
3. "Customize installation" 선택 후 확인

### 방법 2: 현재 Python 수리

1. Windows 설정 → 앱 → Python 찾기
2. "수정" 또는 "Modify" 클릭
3. "Optional Features"에서 **"tcl/tk and IDLE"** 체크
4. 설치 완료

### 방법 3: tkinter 확인

터미널에서 확인:
```cmd
python -m tkinter
```

작은 창이 뜨면 정상 설치된 것입니다.

## 설치 순서

### 1. Python 확인
```cmd
python --version
```

Python 3.8 이상이어야 합니다.

### 2. 가상환경 생성 (선택사항)
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. 의존성 설치
```cmd
pip install -r requirements.txt
```

### 4. 프로그램 실행

#### 데스크톱 GUI (tkinter 필요)
```cmd
python gerber2dxf_gui.py
```

#### 명령줄 (tkinter 불필요)
```cmd
python gerber2dxf.py ./Gerber ./output
```

또는

```cmd
python gerber2dxf_merged.py ./Gerber merged.dxf
```

## 문제 해결

### "No module named 'tkinter'" 오류
→ 위의 tkinter 설치 방법 참고

### "No module named 'gerbonara'" 오류
```cmd
pip install gerbonara
```

### "No module named 'ezdxf'" 오류
```cmd
pip install ezdxf
```

### Microsoft Store Python 사용 시
Microsoft Store Python은 tkinter가 없을 수 있습니다.
→ python.org에서 Python을 다시 설치하세요.

## 빠른 테스트

설치 확인:
```cmd
python -c "import tkinter; import gerbonara; import ezdxf; print('✓ 모든 라이브러리 정상')"
```
