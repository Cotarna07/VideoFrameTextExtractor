import os
import shutil
import pandas as pd

def move_folders_to_language_subfolders(excel_file):
    """
    根据 Excel 文件中的信息，将文件夹移动到主文件夹下的对应语言子文件夹中。
    
    参数：
    - excel_file: 包含文件夹语言分类的 Excel 文件路径。
    """
    # 读取 Excel 文件
    df = pd.read_excel(excel_file)

    # 遍历每一行，处理每个子文件夹
    for _, row in df.iterrows():
        base_folder = row["主文件夹"]
        folder_name = row["子文件夹"]
        detected_language = row["检测语言"]

        # 确定源文件夹路径
        source_folder = os.path.join(base_folder, folder_name)

        # 确定目标文件夹路径（语言子文件夹）
        target_folder = os.path.join(base_folder, detected_language)

        # 检查源文件夹是否存在
        if not os.path.exists(source_folder):
            print(f"警告: 源文件夹 {source_folder} 不存在，跳过。")
            continue

        # 如果目标语言子文件夹不存在，创建它
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
            print(f"创建了目标语言文件夹: {target_folder}")

        # 移动文件夹到目标语言子文件夹中
        target_path = os.path.join(target_folder, folder_name)
        try:
            shutil.move(source_folder, target_path)
            print(f"已移动文件夹: {source_folder} -> {target_path}")
        except Exception as e:
            print(f"错误: 移动文件夹 {source_folder} 到 {target_path} 时失败 - {e}")

# 主程序
if __name__ == "__main__":
    excel_file = r"D:\software\工作文件夹\代码\视频文案识别\folder_languages.xlsx"
    move_folders_to_language_subfolders(excel_file)
