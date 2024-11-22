import os
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from collections import Counter
from pathlib import Path
import re
import pandas as pd

# 设定随机种子，保证结果一致性
DetectorFactory.seed = 0

# 噪音关键词过滤列表
KEYWORDS_TO_REMOVE = ["TikTok video", "video", "mp4", "clip"]

def clean_filename(filename):
    """去掉文件名中的噪音关键词和特殊字符"""
    for keyword in KEYWORDS_TO_REMOVE:
        filename = re.sub(rf"\b{re.escape(keyword)}\b", "", filename, flags=re.IGNORECASE)
    filename = re.sub(r"[^\w\s]", "", filename)  # 去掉非字母数字和空格
    return filename.strip()

def detect_language_from_text(text):
    """根据关键词和字符集检测文本语言"""
    try:
        # 使用langdetect尝试检测语言
        detected_language = detect(text)
        return detected_language
    except LangDetectException:
        # 如果langdetect检测失败，根据规则默认判定语言
        arabic_keywords = [
            "السلام", "مرحبا", "شكرا", "الله", "محمد", "السعودية", 
            "إسلام", "قرآن", "مسلم", "جميل", "العربية", "اللغة"
        ]
        spanish_keywords = [
            "hola", "gracias", "por", "amigo", "buenos", "dias", 
            "mañana", "fiesta", "adiós", "familia", "feliz", "navidad"
        ]
        portuguese_keywords = [
            "obrigado", "oi", "de", "amigo", "bom", "dia", 
            "português", "feliz", "brasil", "carnaval", "gosto", "saúde"
        ]

        # 检测是否包含关键词
        if any(keyword in text for keyword in arabic_keywords):
            return "ar"
        elif any(keyword in text for keyword in spanish_keywords):
            return "es"
        elif any(keyword in text for keyword in portuguese_keywords):
            return "pt"
        
        # 检测字符集特征
        if any("\u0600" <= char <= "\u06FF" for char in text):  # 阿拉伯字母范围
            return "ar"
        elif any(char in "áéíóúñ" for char in text):  # 常见西班牙语字符
            return "es"
        elif any(char in "ãõçêéá" for char in text):  # 常见葡萄牙语字符
            return "pt"

        # 默认返回英语
        return "en"

def detect_folder_language(folder_path):
    """根据文件夹中的文本文档或文件名，检测文件夹的语言"""
    print(f"正在处理文件夹: {folder_path}")
    language_counts = Counter()  # 统计语言分布
    video_files = []
    text_files = []
    logic_used = ""  # 保存使用的判断逻辑

    # 支持的语言列表
    supported_languages = ["en", "ar", "es", "pt"]

    # 遍历文件夹，分类文件
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):  # 只处理文件
            if item.endswith(".mp4"):
                video_files.append(item_path)
            elif item.endswith(".txt"):
                text_files.append(item_path)

    print(f"找到视频文件: {len(video_files)} 个，文本文档: {len(text_files)} 个")

    # 判断使用逻辑
    if len(text_files) > len(video_files) * 0.9:  # 文本文档数量超过视频数量的90%
        logic_used = "文本文档汇总"
        print(f"使用逻辑: {logic_used}")
        for text_file in text_files:
            try:
                with open(text_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    language = detect_language_from_text(content)
                    if language != "unknown":
                        language_counts[language] += 1
            except (PermissionError, FileNotFoundError) as e:
                print(f"警告: 无法读取文件 {text_file} - {e}")
    else:  # 否则使用视频文件名判断语言
        logic_used = "视频文件名"
        print(f"使用逻辑: {logic_used}")
        for video in video_files:
            video_name = Path(video).stem
            clean_name = clean_filename(video_name)
            language = detect_language_from_text(clean_name)
            if language != "unknown":
                language_counts[language] += 1

    # 获取语言分布统计
    total_count = sum(language_counts.values())
    if total_count == 0:
        detected_language = "en"  # 默认返回英语
    else:
        # 筛选支持的语言并按频率排序
        filtered_languages = [
            lang for lang, count in language_counts.most_common() if lang in supported_languages
        ]
        if filtered_languages:  # 如果有支持的语言
            detected_language = filtered_languages[0]
        else:  # 如果没有支持的语言，默认返回英语
            detected_language = "en"

    print(f"检测结果: {detected_language}")
    return logic_used, detected_language

def process_folders(base_folders):
    """处理主文件夹中的所有子文件夹，并为每个子文件夹定性语言"""
    results = []

    # 遍历主文件夹及其子文件夹
    for base_folder in base_folders:
        print(f"开始处理主文件夹: {base_folder}")
        for folder_name in os.listdir(base_folder):
            folder_path = os.path.join(base_folder, folder_name)
            if os.path.isdir(folder_path):  # 只处理子文件夹
                print(f"开始处理子文件夹: {folder_name}")
                logic_used, detected_language = detect_folder_language(folder_path)
                results.append([base_folder, folder_name, logic_used, detected_language])

    # 将结果保存为 Excel
    output_file = "folder_languages.xlsx"
    df = pd.DataFrame(results, columns=["主文件夹", "子文件夹", "判断逻辑", "检测语言"])
    df.to_excel(output_file, index=False)  # 删除 encoding 参数
    print(f"所有文件夹语言信息已保存到 {output_file}")

# 主程序
if __name__ == "__main__":
    base_folders = [
        r"D:\software\工作文件夹\代码\tiktok_crawl\下载视频",
        r"D:\software\工作文件夹\代码\instagram_crawl\下载视频2"
    ]
    process_folders(base_folders)
