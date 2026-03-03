import subprocess
import sys

print("=" * 40)
print(" HWP Worker 빌드 시작")
print("=" * 40)

# 패키지 설치
subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "pywin32", "flask", "pillow"])

# PyInstaller 빌드
subprocess.run([
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--noconsole",
    "--add-data", "template.hwp;.",
    "--hidden-import", "win32com",
    "--hidden-import", "win32com.client",
    "--hidden-import", "win32clipboard",
    "--hidden-import", "win32api",
    "--hidden-import", "pythoncom",
    "--hidden-import", "pywintypes",
    "--name", "hwp_worker_v1.0",
    "main.py",
])

print()
print("=" * 40)
print(" 빌드 완료: dist\\hwp_worker_v1.0.exe")
print(" 이 파일 하나만 배포하면 됩니다.")
print("=" * 40)
input("엔터를 누르면 창이 닫힙니다...")
