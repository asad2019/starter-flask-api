from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
import os
import cv2
from datetime import datetime
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, support_credentials=True)

VIDEOS_FOLDER = './backend/uploads/videos'
LOGS_FOLDER = './backend/uploads/videos'

if not os.path.exists(VIDEOS_FOLDER):
    os.makedirs(VIDEOS_FOLDER)

if not os.path.exists(LOGS_FOLDER):
    os.makedirs(LOGS_FOLDER)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/video_logs'
mongo = PyMongo(app)

def process_video(file):
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.mp4'
    file.filename = current_time
    filename = secure_filename(file.filename)
    file_path = os.path.join(VIDEOS_FOLDER, filename)
    file.save(file_path)

    return file_path

def parse_log(file):
    filename = secure_filename(file.filename)
    file_path = os.path.join(VIDEOS_FOLDER, filename)
    file.save(file_path)

    return file_path

@app.route('/process_video', methods=['POST'])
@cross_origin(supports_credentials=True)
def process_video_route():
    try:
        if 'video' not in request.files:
            return jsonify({"error": "No video file provided"}), 400
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({"error": "No video file selected"}), 400
        video_path = process_video(video_file)
        return jsonify({"message": "Video processed successfully", "video_path": video_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/parse_log', methods=['POST'])
def parse_log_route():
    try:
        if 'log' not in request.files:
            return jsonify({"error": "No log file provided"}), 400
        log_file = request.files['log']
        if log_file.filename == '':
            return jsonify({"error": "No log file selected"}), 400
        log_path = parse_log(log_file)
        return jsonify({"message": "Log parsed successfully", "log_path": log_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/process_video_metadata', methods=['POST'])
def process_video_metadata():
    video_name = request.json['video_name']
    video_path = os.path.join(VIDEOS_FOLDER, video_name)
    if os.path.exists(video_path):
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
        cap.release()
        return jsonify({'fps': fps, 'duration': duration})
    else:
        return jsonify({'error': 'Video not found'}), 404


@app.route('/parse_logs', methods=['POST'])
def parse_logs():
    log_type = request.json['log_type']
    log_file = os.path.join(LOGS_FOLDER, log_type + '.log')
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            logs = f.readlines()
        return jsonify({'logs': logs})
    else:
        return jsonify({'error': 'Log file not found'}), 404


@app.route('/videos')
def list_videos():
    videos = [file for file in os.listdir(VIDEOS_FOLDER) if file.endswith('.mp4')]
    video_links = [url_for('get_video', filename=video) for video in videos]
    links = []
    for link in zip(video_links):
        links.append(link)

    return jsonify(links)

@app.route('/uploads/videos/<path:filename>')
def get_video(filename):
    return send_from_directory('uploads/videos/', filename)