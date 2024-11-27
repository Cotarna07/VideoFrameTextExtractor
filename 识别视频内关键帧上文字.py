import os
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import requests
import base64
import hashlib
import time
from tqdm import tqdm
from difflib import SequenceMatcher

# 用于计算字符串相似性
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# 提取视频关键帧到临时文件夹
def extract_keyframes_with_ffmpeg(video_path, output_dir, fps=1):
    output_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg_command = [
        "ffmpeg",
        "-i", str(video_path),
        "-vf", f"fps={fps}",
        str(output_dir / "frame_%03d.jpg"),
        "-hide_banner",
        "-loglevel", "error"
    ]
    subprocess.run(ffmpeg_command, check=True)

# 对单张图片进行OCR识别
def ocr_image(image_path, max_retries=3):
    with open(image_path, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode("utf-8")
        data = {"base64": encoded_string, "lang": "eng"}
    for attempt in range(max_retries):
        try:
            response = requests.post("http://localhost:9999/api/ocr", json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            return [
                item["text"].strip()
                for item in result.get("data", [])
                if isinstance(item, dict) and "text" in item
            ]
        except requests.RequestException as e:
            print(f"Request failed: {e}, retrying {attempt + 1}/{max_retries}")
            time.sleep(1)
    return []

# 对视频进行OCR识别
def process_video(video_path, temp_dir, similarity_threshold=0.8):
    video_temp_dir = temp_dir / video_path.stem
    extracted_texts = []

    # 提取关键帧
    extract_keyframes_with_ffmpeg(video_path, video_temp_dir)

    # 对提取的关键帧逐一识别
    for frame_path in video_temp_dir.glob("*.jpg"):
        frame_texts = ocr_image(frame_path)
        for text in frame_texts:
            if not any(similar(text, recorded_text) > similarity_threshold for recorded_text in extracted_texts):
                extracted_texts.append(text)

    return extracted_texts

# 对单个视频的结果写入文件
def save_video_result(video_name, extracted_texts, output_file):
    if not extracted_texts:
        return
    if not output_file.exists():
        df = pd.DataFrame(columns=["Video", "Content"])
    else:
        df = pd.read_excel(output_file)
    new_data = pd.DataFrame([{"Video": video_name, "Content": " ".join(extracted_texts)}])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_excel(output_file, index=False)

# 计算文件哈希值
def file_hash(filepath):
    with open(filepath, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(4096):
            file_hash.update(chunk)
    return file_hash.hexdigest()

# 修改 process_folder 函数以支持记录处理进度
def process_folder(folder_path, output_file, temp_dir, record_file_path):
    video_files = list(Path(folder_path).glob("*.mp4"))
    temp_dir.mkdir(parents=True, exist_ok=True)

    # 读取已处理文件的哈希值
    processed_videos = set()
    if Path(record_file_path).exists():
        with open(record_file_path, "r") as rf:
            processed_videos = set(rf.read().splitlines())

    for video_file in tqdm(video_files, desc=f"Processing folder: {folder_path.name}"):
        try:
            video_hash = file_hash(video_file)
            if video_hash in processed_videos:
                # print(f"Skipping already processed video: {video_file.name}")
                continue

            # 提取文字并保存
            extracted_texts = process_video(video_file, temp_dir)
            # print(f"Extracted {len(extracted_texts)} texts from {video_file.name}")
            save_video_result(video_file.name, extracted_texts, output_file)

            # 更新记录文件
            with open(record_file_path, "a") as rf:
                rf.write(video_hash + "\n")
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg failed for {video_file.name}: {e}")
        except Exception as e:
            print(f"Error processing {video_file.name}: {e}")

# 主函数
def main(base_folder):
    base_path = Path(base_folder)
    temp_dir = base_path / "temp"
    record_file_path = "processed_videos.txt"  # 定义记录文件路径
    subfolders = [subfolder for subfolder in base_path.iterdir() if subfolder.is_dir()]

    with ThreadPoolExecutor(max_workers=10) as executor:
        for subfolder in subfolders:
            output_file = subfolder / f"{subfolder.name}_识别结果.xlsx"
            executor.submit(process_folder, subfolder, output_file, temp_dir / subfolder.name, record_file_path)

if __name__ == "__main__":
    base_folder = r"D:\software\工作文件夹\代码\instagram_crawl\下载视频2\en"
    main(base_folder)