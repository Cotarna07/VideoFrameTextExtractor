import os

def process_text_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            process_single_file(file_path)

def process_single_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    processed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().endswith('.mp4'):
            # 确保 .mp4 文件名行上方有且仅有一个空行
            if processed_lines and processed_lines[-1].strip() != '':
                processed_lines.append('\n')
            processed_lines.append(line)
            i += 1
            # 跳过所有下方的空行
            while i < len(lines) and lines[i].strip() == '':
                i += 1
        else:
            processed_lines.append(line)
            i += 1

    # 写回处理后的内容
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(processed_lines)

# 示例调用
directory = r"D:\software\工作文件夹\代码\视频文案识别\batches"
process_text_files(directory)
