import time
import os
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import subprocess

def start_edge_browser():
    try:
        subprocess.Popen([r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "--remote-debugging-port=9223"])
        time.sleep(10)
        edge_options = EdgeOptions()
        edge_options.add_argument("--disable-dev-shm-usage")
        edge_options.add_argument("--no-sandbox")
        edge_options.add_experimental_option("debuggerAddress", "127.0.0.1:9223")
        service = EdgeService()
        driver = webdriver.Edge(service=service, options=edge_options)
        return driver
    except Exception as e:
        print(f"Error starting Edge browser: {e}")
        return None

def wait_for_user_confirmation():
    input("请在浏览器中完成登录并导航到文心一言输入页面后按回车键继续...")

def process_text_batch(driver, batch_text):
    try:
        input_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[3]/div/div[2]/div/div[1]/div[3]/div[3]/div[3]/div[1]/div[1]/div[3]/div/div/div'))
        )
        input_box.clear()
        input_box.send_keys(batch_text)
        input_box.send_keys(Keys.RETURN)

        # 等待结果加载完毕，具体根据页面结构进行调整
        result_box = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//*[@class="response-class"]'))  # 替换为实际结果元素的XPath
        )
        
        results = driver.find_elements(By.XPATH, '//*[@class="response-class"]')  # 替换为实际结果元素的XPath
        return '\n'.join([result.text for result in results])
    except Exception as e:
        print(f"Error processing text batch: {e}")
        return "Error processing this batch"

def process_document(input_file_path, output_file_path, record_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    processed_texts = set()
    if os.path.exists(record_file_path):
        with open(record_file_path, 'r', encoding='utf-8') as record_file:
            processed_texts = set(record_file.read().splitlines())

    driver = start_edge_browser()
    wait_for_user_confirmation()

    with open(output_file_path, 'a', encoding='utf-8') as output_file:
        for i in tqdm(range(0, len(lines), 10), desc="Processing batches"):
            batch = lines[i:i+10]
            batch_text = ''.join(batch).strip()
            
            if batch_text not in processed_texts:
                result = process_text_batch(driver, batch_text)
                output_file.write(f"Results for batch starting at line {i+1}:\n{result}\n\n")
                with open(record_file_path, 'a', encoding='utf-8') as record_file:
                    record_file.write(f"{batch_text}\n")
                processed_texts.add(batch_text)
            else:
                print(f"Batch starting at line {i+1} has already been processed.")
    
    driver.quit()

if __name__ == '__main__':
    input_file_path = '测试文档.txt'
    output_file_path = 'translated_text_results.txt'
    record_file_path = 'processed_batches.txt'
    process_document(input_file_path, output_file_path, record_file_path)
