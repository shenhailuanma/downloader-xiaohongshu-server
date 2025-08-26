from flask import Flask, request, jsonify
import subprocess
import json

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)

        return_code = result.returncode
        stdout = result.stdout
        stderr = result.stderr
        
        return return_code, stdout, stderr
    except Exception as e:
        return -1, "", str(e)


app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# get video info
@app.route("/api/v1/xiaohongshu/video/info")
def get_video_info():
    video_url = request.args.get('video')
    if not video_url:
        return jsonify({"error": "no video url", "code": 400}), 400
    
    response_data = {}

    return jsonify(response_data)

# get channel video list info
@app.route("/api/v1/xiaohongshu/channel/info")
def get_channel_info():
    channel = request.args.get('channel')
    if not channel:
        return jsonify({"error": "no video channel", "code": 400}), 400
    
    response_data = {}
    
    return jsonify(response_data), 200


# download video
@app.route("/api/v1/xiaohongshu/video/download")
def download_video():
    response_data = {}

    return jsonify(response_data), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=15080)