"""
HWP Report Worker — Windows PC에서 실행 (누름틀 템플릿 방식)

실행 방법:  python worker.py
필요 패키지: pip install flask pywin32 pillow
포트: 5100
"""

import base64
import io
import os
import socket
import sys
import tempfile
import threading
import traceback
import ctypes
import time
from datetime import datetime

# 에러 로그 경로 (exe 실행 파일 옆에 생성)
_exe_dir = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__))
_log_path = os.path.join(_exe_dir, "hwp_worker_error.log")
_image_cache_dir = os.path.join(_exe_dir, "_hwp_img_cache")
WORKER_VERSION = "2026-03-04-imgfix6-clean"

try:
    import pythoncom
    import win32clipboard
    import win32com.client
    from flask import Flask, Response, jsonify, request
    from PIL import Image
except Exception as _e:
    with open(_log_path, "w", encoding="utf-8") as _f:
        traceback.print_exc(file=_f)
    ctypes.windll.user32.MessageBoxW(
        0,
        f"초기화 실패: {_e}\n\n{_log_path} 파일을 확인하세요.",
        "HWP Worker 오류",
        0x10,
    )
    sys.exit(1)

# template.hwp는 exe(또는 스크립트) 옆에 두어야 합니다 — 직원이 직접 교체 가능
TEMPLATE_PATH = os.path.join(_exe_dir, "template.hwp")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB
os.makedirs(_image_cache_dir, exist_ok=True)


def _log(msg: str):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    try:
        with open(_log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


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
        except Exception as e:
            _log(f"  [WARN] 텍스트 필드 '{fieldname}': {e}")

    def _move_to_field_for_image(self, fieldname: str) -> bool:
        """이미지 누름틀 위치로 이동(실제 성공한 시그니처만 사용)."""
        try:
            if hasattr(self.hwp, "FieldExist") and not self.hwp.FieldExist(fieldname):
                _log(f"  [WARN] 필드 '{fieldname}' 찾을 수 없음(FieldExist=False)")
                return False
        except Exception:
            # 일부 버전/환경에서는 FieldExist 호출이 불안정할 수 있어 무시하고 진행
            pass

        try:
            moved = self.hwp.MoveToField(fieldname, True, True, True)
            if moved in (False, 0):
                _log(f"  [WARN] 필드 '{fieldname}' 이동 실패: MoveToField returned {moved}")
                return False
            return True
        except Exception as e:
            _log(f"  [WARN] 필드 '{fieldname}' 이동 실패: {e}")
            return False

    def _put_image_by_insertpicture(self, image_path: str) -> bool:
        """Clipboard 실패 시 폴백용 InsertPicture."""
        last_err = None

        try:
            ret = self.hwp.InsertPicture(
                image_path,
                True,
                1,
                False,
                False,
                0,
            )
            if ret not in (False, 0):
                return True
        except Exception as e:
            last_err = e

        # 일부 환경에서는 액션 기반 호출이 더 안정적입니다.
        try:
            self.hwp.HAction.GetDefault("InsertPicture", self.hwp.HParameterSet.HInsertPicture.HSet)
            pset = self.hwp.HParameterSet.HInsertPicture
            pset.FileName = image_path
            try:
                pset.Embedded = True
            except Exception:
                pass
            try:
                pset.Embeded = True
            except Exception:
                pass
            try:
                pset.SizeOption = 1
            except Exception:
                pass
            ret = self.hwp.HAction.Execute("InsertPicture", pset.HSet)
            if ret not in (False, 0):
                return True
        except Exception as e:
            last_err = e

        if last_err:
            _log(f"  [WARN] InsertPicture 실패: {last_err}")
        return False

    def _put_image_by_clipboard(self, bmp_data: bytes) -> bool:
        """클립보드 + Paste 폴백 방식."""
        # 클립보드 설정 (잠금 해제 재시도)
        for attempt in range(5):
            opened = False
            try:
                win32clipboard.OpenClipboard()
                opened = True
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, bmp_data)
                break
            except Exception as clip_err:
                if attempt == 4:
                    raise
                _log(f"  [WARN] 클립보드 재시도 {attempt+1}/5: {clip_err}")
                time.sleep(0.2)
            finally:
                if opened:
                    try:
                        win32clipboard.CloseClipboard()
                    except Exception:
                        pass

        # HWP가 클립보드를 인식할 시간 확보
        time.sleep(0.15)
        try:
            ret = self.hwp.Run("Paste")
            if ret in (False, 0):
                return False
        except Exception:
            ret = self.hwp.HAction.Run("Paste")
            if ret in (False, 0):
                return False
        # 붙여넣기 완료 대기
        time.sleep(0.1)
        return True

    def _put_image(self, fieldname: str, b64_data: str):
        """이미지 누름틀에 클립보드로 이미지 삽입."""
        if not b64_data:
            return False
        try:
            if not self._move_to_field_for_image(fieldname):
                return False

            raw = b64_data.split(",", 1)[1] if "," in b64_data else b64_data
            binary = base64.b64decode(raw)

            # 확장자/포맷 불일치 이슈를 피하기 위해 실제 PNG로 재인코딩해서 저장
            img = Image.open(io.BytesIO(binary)).convert("RGB")
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".png",
                prefix="hwp_img_",
                dir=_image_cache_dir,
            ) as tf:
                img.save(tf, format="PNG")
                tmp_path = tf.name

            # 현재 운영 환경에서 안정적으로 동작한 경로
            buf = io.BytesIO()
            img.save(buf, "BMP")
            bmp_data = buf.getvalue()[14:]  # BMP 파일헤더 14바이트 제외
            if self._put_image_by_clipboard(bmp_data):
                _log(f"  [INFO] 이미지 필드 '{fieldname}' 삽입 완료(Clipboard)")
                return True

            # Clipboard 실패 시 InsertPicture 폴백
            if self._put_image_by_insertpicture(tmp_path):
                _log(f"  [INFO] 이미지 필드 '{fieldname}' 삽입 완료(InsertPicture)")
                return True

            _log(f"  [WARN] 이미지 필드 '{fieldname}': Clipboard/InsertPicture 모두 실패")
            return False
        except Exception as e:
            _log(f"  [WARN] 이미지 필드 '{fieldname}': {e}")
            return False

    def build(self, data: dict):
        """템플릿 열고 필드 채우기."""
        if not os.path.exists(TEMPLATE_PATH):
            raise FileNotFoundError(
                f"template.hwp 파일이 없습니다.\n"
                f"아래 경로에 template.hwp를 복사하세요:\n{TEMPLATE_PATH}"
            )
        self.hwp.Open(TEMPLATE_PATH, "HWP", "")

        fields = data.get("fields", {})
        images = data.get("images", [])

        # 텍스트 필드 채우기
        for fname, fvalue in fields.items():
            self._put_text(fname, fvalue)

        # 이미지 필드 채우기
        # field 키가 있으면 해당 필드명 사용(도면 등), 없으면 pic1~pic8 자동 부여
        pic_counter = 1
        image_failures = []
        for img in images:
            field_name = img.get("field")
            if field_name:
                if img.get("data"):
                    ok = self._put_image(field_name, img["data"])
                    if not ok:
                        image_failures.append(field_name)
            else:
                if pic_counter > 8:
                    break
                if img.get("data"):
                    auto_field = f"pic{pic_counter}"
                    ok = self._put_image(auto_field, img["data"])
                    if not ok:
                        image_failures.append(auto_field)
                self._put_text(f"pic{pic_counter}_cap", img.get("caption", ""))
                pic_counter += 1

        if image_failures:
            fail_fields = ", ".join(image_failures)
            raise RuntimeError(f"이미지 삽입 실패 필드: {fail_fields}")

    def save(self, output_path: str):
        try:
            self.hwp.SaveAs(output_path, "HWP", "")
        finally:
            try:
                self.hwp.Quit()
            except Exception:
                pass


# ─── Flask 엔드포인트 ──────────────────────────────────────────────────────────

@app.route("/generate-hwp", methods=["POST"])
def generate_hwp():
    pythoncom.CoInitialize()

    data = request.get_json(silent=True)
    if not data:
        pythoncom.CoUninitialize()
        return jsonify({"error": "요청 데이터 없음"}), 400

    output_path = tempfile.mktemp(suffix=".hwp")
    _log(f"[INFO] HWP 생성 시작 (이미지 {len(data.get('images', []))}장, version={WORKER_VERSION})")

    try:
        builder = HwpTemplateBuilder()
        builder.build(data)
        builder.save(output_path)
        _log(f"[INFO] HWP 저장 완료: {output_path}")

        with open(output_path, "rb") as f:
            hwp_bytes = f.read()

        _log(f"[INFO] 파일 크기: {len(hwp_bytes)} bytes")
        return Response(
            hwp_bytes,
            mimetype="application/octet-stream",
            headers={
                "Content-Disposition": "attachment; filename=report.hwp",
                "Content-Length": str(len(hwp_bytes)),
            },
        )
    except Exception as e:
        traceback.print_exc()
        try:
            with open(_log_path, "a", encoding="utf-8") as f:
                traceback.print_exc(file=f)
        except Exception:
            pass
        return jsonify({"error": str(e)}), 500
    finally:
        pythoncom.CoUninitialize()
        try:
            os.unlink(output_path)
        except Exception:
            pass


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "version": WORKER_VERSION})


# ─── 진입점 ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    PORT = 5100

    def _msgbox(title, msg, icon=0x40, timeout=4000):
        ctypes.windll.user32.MessageBoxTimeoutW(0, msg, title, icon, 0, timeout)

    def _is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0

    if _is_port_in_use(PORT):
        # 이미 실행 중 → 알림 후 종료
        _msgbox(
            "HWP Worker v1.0",
            f"이미 실행 중입니다. (포트 {PORT})\n\n웹에서 HWP 다운로드 버튼을 바로 사용할 수 있습니다.",
            0x40,
            5000,
        )
    else:
        # 정상 시작
        threading.Thread(
            target=_msgbox,
            args=(
                "HWP Worker v1.0",
                f"실행 중  (포트: {PORT})\n\n웹에서 HWP 다운로드 버튼을 사용할 수 있습니다.\n\n종료: 작업 관리자 → hwp_worker_v1.0.exe → 작업 끝내기",
                0x40,
                4000,
            ),
            daemon=True,
        ).start()
        app.run(host="0.0.0.0", port=PORT, debug=False)
