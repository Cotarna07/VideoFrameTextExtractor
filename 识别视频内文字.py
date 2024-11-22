import cv2
import base64
import requests
from pathlib import Path
from tqdm import tqdm
import hashlib
import time

def similar(a, b):
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()

def file_hash(filepath):
    with open(filepath, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(4096):
            file_hash.update(chunk)
    return file_hash.hexdigest()

def extract_text_from_video(video_path, similarity_threshold=0.8, max_retries=3):
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Error: Cannot open video {video_path}")
        return []
    
    fps = int(cap.get(cv2.CAP_PROP_FPS))  # 获取视频的帧率
    frame_interval = fps  # 每秒处理一帧
    frame_number = 0
    extracted_texts = []
    last_text = ""  # 保存上一次识别的文本

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_number % frame_interval == 0:  # 每隔一秒提取一帧
            retval, buffer = cv2.imencode('.jpg', frame)
            if retval:
                encoded_string = base64.b64encode(buffer).decode('utf-8')
                # 这里指定语言为简体中文 'chi_sim'
                data = {'base64': encoded_string, 'lang': 'chi_sim'}

                for attempt in range(max_retries):
                    try:
                        response = requests.post('http://localhost:9999/api/ocr', json=data, timeout=10)
                        response.raise_for_status()  # 检查请求是否成功
                        result = response.json()

                        # 检查返回的结果
                        if result.get('code') == 101 and "No text found" in result.get('data', ''):
                            print(f"No text found in frame {frame_number // fps} (seconds).")
                        elif 'data' in result and isinstance(result['data'], list):
                            for item in result['data']:
                                if isinstance(item, dict) and 'text' in item:
                                    text = item['text'].strip()

                                    # 只添加与上一次不同的文本
                                    if text != last_text and not any(similar(text, recorded_text) > similarity_threshold for recorded_text in extracted_texts):
                                        extracted_texts.append(text)
                                        last_text = text  # 更新上一次识别的文本
                        else:
                            print(f"Unexpected response format: {result}")

                        break  # 成功则跳出重试循环
                    except requests.RequestException as e:
                        print(f"Request failed: {e}, retrying {attempt + 1}/{max_retries}")
                        time.sleep(2)  # 等待 2 秒后重试

            # 释放资源
            del buffer  # 释放内存中的图像编码缓冲区
            cv2.destroyAllWindows()  # 清除OpenCV中的窗口缓存

        frame_number += 1

    cap.release()  # 释放视频资源
    return extracted_texts

def process_videos(folder_path, output_file_path, record_file_path):
    video_files = list(Path(folder_path).glob('*.mp4'))
    processed_videos = set()

    if Path(record_file_path).exists():
        with open(record_file_path, 'r') as rf:
            processed_videos = set(rf.read().splitlines())

    for video_file in tqdm(video_files, desc="Processing Videos", unit="video"):
        video_hash = file_hash(video_file)
        if video_hash not in processed_videos:
            extracted_texts = extract_text_from_video(video_file)

            with open(output_file_path, 'a', encoding='utf-8') as output_file:
                output_file.write(f"Results for {video_file.name}:\n")
                for text in extracted_texts:
                    output_file.write(f"{text}\n")
                output_file.write("\n")  # 分隔不同视频的结果

            with open(record_file_path, 'a', encoding='utf-8') as record_file:
                record_file.write(f"{video_hash}\n")
            processed_videos.add(video_hash)

if __name__ == '__main__':
    folder_path = r"D:\software\工作文件夹\代码\视频文案识别\测试"
    output_file_path = '赡养上帝.txt'
    record_file_path = 'tese_record.txt'
    process_videos(folder_path, output_file_path, record_file_path)
