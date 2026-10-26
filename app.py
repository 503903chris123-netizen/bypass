import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import PyBypass as bypasser

app = Flask(__name__)
CORS(app)  # 允许前端跨域访问

# ！！！把这里换成你自己的 Turnstile 密钥 ！！！
TURNSTILE_SECRET_KEY = "0x4AAAAAAFmM_7gn1bpkxm5keVdLP5LUyJM"
TURNSTILE_SITE_KEY = "0x4AAAAAAFmM_2ZFDB9Bor0J" 

@app.route('/api/config', methods=['GET'])
def get_config():
    # 前端用这个接口来获取 Site Key
    return jsonify({"siteKey": TURNSTILE_SITE_KEY})

@app.route('/api/bypass', methods=['POST'])
def do_bypass():
    data = request.get_json()
    url = data.get('url')
    token = data.get('turnstileToken')

    if not url or not token:
        return jsonify({"success": False, "error": "参数不全"}), 400

    # 1. 向 Cloudflare 验证 Turnstile token 是否有效
    verify_url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    verify_data = {"secret": TURNSTILE_SECRET_KEY, "response": token}
    verify_res = requests.post(verify_url, data=verify_data).json()
    
    if not verify_res.get("success"):
        return jsonify({"success": False, "error": "验证码无效，请重试"}), 403

    # 2. 验证通过，调用 PyBypass 解析链接
    try:
        result = bypasser.bypass(url)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
from flask import send_file

@app.route('/')
def home():
    return send_file('index.html')
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)