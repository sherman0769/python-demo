# api/rpg.py
import os, json
from http.server import BaseHTTPRequestHandler
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

SYSTEM_PROMPT = (
    "你是一位幽默、友善但有適度挑戰性的文字冒險 GM，"
    "世界觀設定在融合奇幻與科幻的『銀河龍與地城』。"
    "每次回應："
    "1) 先描寫劇情（不超過 120 字）\n"
    "2) 再提出 2~3 個可選動作 (A/B/C)\n"
    "僅使用繁體中文，不要暴雷未來劇情。"
)

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

            # 把歷史轉成 Gemini Messages 格式
            messages = [{"role": "user", "parts": SYSTEM_PROMPT}]
            for entry in history:
                messages.append({"role": "user", "parts": entry["user"]})
                messages.append({"role": "model", "parts": entry["gm"]})

            # 取得玩家最新輸入
            user_input = payload.get("user", "")
            if user_input:
                messages.append({"role": "user", "parts": user_input})

            response = model.generate_content(messages)
            gm_reply = response.text.strip()

            # 更新歷史
            history.append({"user": user_input, "gm": gm_reply})

            self._json(200, {"reply": gm_reply, "history": history})

        except Exception as e:
            self._json(500, {"error": str(e)})
