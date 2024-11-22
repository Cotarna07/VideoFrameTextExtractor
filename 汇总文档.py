import os

def process_text_files(directory, output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for filename in os.listdir(directory):
            if filename.endswith('.txt'):
                file_path = os.path.join(directory, filename)
                process_single_file(file_path, outfile)

def process_single_file(file_path, outfile):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    processed_lines = []
    for i, line in enumerate(lines):
        if line.strip().endswith('.mp4:'):
            # 确保 .mp4 文件名行上方有且仅有一个空行
            if processed_lines and processed_lines[-1].strip():
                processed_lines.append('\n')
            processed_lines.append(line)
        else:
            # 保证不添加多余的空行
            if not (line.strip() == '' and (i + 1 < len(lines) and lines[i + 1].strip().endswith('.mp4:'))):
                processed_lines.append(line)

    # 将处理后的内容追加到总的输出文件
    outfile.writelines(processed_lines)
    outfile.write('\n')  # 每个文件之间添加一个空行

# 示例调用
directory = r"D:\software\工作文件夹\代码\视频文案识别\batches"
output_file = r"D:\software\工作文件夹\代码\视频文案识别\汇总文档.txt"
process_text_files(directory, output_file)
