"""
HWP Report Worker — Windows PC에서 실행 (누름틀 템플릿 방식)

실행 방법:  python worker.py
필요 패키지: pip install flask pywin32 pillow
포트: 5100
"""

import base64
import io
import os
import sys
import tempfile
import threading
import ctypes

import pythoncom
import win32clipboard
import win32com.client
from flask import Flask, Response, jsonify, request
from PIL import Image

# exe로 빌드된 경우 번들 내부 경로, 스크립트 실행 시 파일 위치 기준
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS  # PyInstaller 임시 압축 해제 폴더
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template.hwp")

app = Flask(__name__)


# ─── CORS (브라우저에서 직접 호출 허용) ───────────────────────────────────────

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.route("/generate-hwp", methods=["OPTIONS"])
def options_generate():
    return "", 204

@app.route("/health", methods=["OPTIONS"])
def options_health():
    return "", 204


# ─── HWP 빌더 ─────────────────────────────────────────────────────────────────

class HwpTemplateBuilder:
    def __init__(self):
        self.hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
        self.hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

    def _put_text(self, fieldname: str, text: str):
        """텍스트 누름틀 채우기."""
        try:
            self.hwp.PutFieldText(fieldname, str(text))
            print(f"  [INFO] 텍스트 필드 '{fieldname}' = {text}")
        except Exception as e:
            print(f"  [WARN] 텍스트 필드 '{fieldname}': {e}")

    def _put_image(self, fieldname: str, b64_data: str):
        """이미지 누름틀에 클립보드로 이미지 삽입."""
        if not b64_data:
            return
        try:
            # 필드로 이동 (선택 상태)
            moved = self.hwp.MoveToField(fieldname, True, True, True)
            if not moved:
                print(f"  [WARN] 필드 '{fieldname}' 찾을 수 없음")
                return

            # 이미지 → 클립보드 (BMP)
            raw = b64_data.split(",", 1)[1] if "," in b64_data else b64_data
            img = Image.open(io.BytesIO(base64.b64decode(raw))).convert("RGB")
            buf = io.BytesIO()
            img.save(buf, "BMP")
            bmp_data = buf.getvalue()[14:]  # BMP 파일헤더 14바이트 제외

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, bmp_data)
            win32clipboard.CloseClipboard()

            self.hwp.HAction.Run("Paste")
            print(f"  [INFO] 이미지 필드 '{fieldname}' 삽입 완료")
        except Exception as e:
            print(f"  [WARN] 이미지 필드 '{fieldname}': {e}")

    def build(self, data: dict):
        """템플릿 열고 필드 채우기."""
        self.hwp.Open(TEMPLATE_PATH, "HWP", "")

        fields = data.get("fields", {})
        images = data.get("images", [])

        # 텍스트 필드 채우기
        for fname, fvalue in fields.items():
            self._put_text(fname, fvalue)

        # 이미지 필드 채우기 (pic1~pic8)
        for i, img in enumerate(images[:8], 1):
            if img.get("data"):
                self._put_image(f"pic{i}", img["data"])
            self._put_text(f"pic{i}_cap", img.get("caption", ""))

    def save(self, output_path: str):
        self.hwp.SaveAs(output_path, "HWP", "")
        self.hwp.Quit()


# ─── Flask 엔드포인트 ──────────────────────────────────────────────────────────

@app.route("/generate-hwp", methods=["POST"])
def generate_hwp():
    pythoncom.CoInitialize()

    data = request.get_json(silent=True)
    if not data:
        pythoncom.CoUninitialize()
        return jsonify({"error": "요청 데이터 없음"}), 400

    output_path = tempfile.mktemp(suffix=".hwp")
    print(f"[INFO] HWP 생성 시작 (이미지 {len(data.get('images', []))}장)")

    try:
        builder = HwpTemplateBuilder()
        builder.build(data)
        builder.save(output_path)
        print(f"[INFO] HWP 저장 완료: {output_path}")

        with open(output_path, "rb") as f:
            hwp_bytes = f.read()

        print(f"[INFO] 파일 크기: {len(hwp_bytes)} bytes")
        return Response(
            hwp_bytes,
            mimetype="application/octet-stream",
            headers={
                "Content-Disposition": "attachment; filename=report.hwp",
                "Content-Length": str(len(hwp_bytes)),
            },
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        pythoncom.CoUninitialize()
        try:
            os.unlink(output_path)
        except Exception:
            pass


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


# ─── 진입점 ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    def _notify():
        ctypes.windll.user32.MessageBoxTimeoutW(
            0,
            "HWP Worker v1.0 실행 중\n\n포트: 5100\n웹에서 HWP 다운로드 버튼을 사용할 수 있습니다.\n\n종료하려면 작업 관리자에서 hwp_worker_v1.0.exe를 끝내세요.",
            "HWP Worker v1.0",
            0x40,   # MB_ICONINFORMATION
            0,
            4000,   # 4초 후 자동 닫힘
        )
    threading.Thread(target=_notify, daemon=True).start()
    app.run(host="0.0.0.0", port=5100, debug=False)
