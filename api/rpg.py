# api/rpg.py
import os, json
from http.server import BaseHTTPRequestHandler
import google.generativeai as genai

# ---------- Gemini 設定 ----------
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
# 使用免費額度可用的模型，速度較快
model = genai.GenerativeModel("gemini-2.0-flash")

SYSTEM_PROMPT = (
    "你是一位幽默且有挑戰性的文字冒險 GM，"
    "世界觀融合奇幻與科幻，名為『銀河龍與地城』。"
    "每次回答：先 120 字內劇情描述，再列 2~3 個可選動作 (A/B/C)。"
    "請使用繁體中文，且不要暴雷未來劇情。"
)


# ---------- HTTP Handler ----------
class handler(BaseHTTPRequestHandler):
    def _json(self, code: int, data: dict):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length) or "{}")

            history: list[dict] = payload.get("history", [])
            user_input: str = payload.get("user", "")

            # 組 Gemini 對話
            messages = [{"role": "user", "parts": SYSTEM_PROMPT}]
            for h in history:
                messages.append({"role": "user",  "parts": h["user"]})
                messages.append({"role": "model", "parts": h["gm"]})
            if user_input:
                messages.append({"role": "user", "parts": user_input})

            # 產生劇情
            resp = model.generate_content(messages)
            gm_reply = resp.text.strip()

            # 更新歷史
            history.append({"user": user_input, "gm": gm_reply})

            self._json(200, {
                "reply": gm_reply,
                "history": history
            })

        except Exception as e:
            self._json(500, {"error": str(e)})
