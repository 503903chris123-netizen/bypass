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
        # 调用 bypass.vip 的公开接口
        payload = {"url": url}
        api_res = requests.post("https://api.bypass.vip/", data=payload, timeout=30)
    
        # 检查 HTTP 请求本身是否成功
        api_res.raise_for_status()
    
        # 解析返回的 JSON 数据
        result_data = api_res.json()
    
        # bypass.vip 的返回格式通常包含目标链接，这里做个兼容处理
        # 如果返回结果里有 'result' 或 'destination' 字段，就取出来
        if isinstance(result_data, dict):
            final_link = result_data.get('result') or result_data.get('destination') or result_data
        else:
            final_link = result_data

        return jsonify({"success": True, "result": final_link})

except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500
from flask import send_file

@app.route('/')
def home():
    return send_file('index.html')
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
