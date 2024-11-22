import requests
import base64

# 将图像文件编码为Base64
with open(r"D:\game\QQ截图20240707110938.jpg", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

# 构造请求数据，确保字段名为'base64'
data = {
    'base64': encoded_string  # 更改字段名以匹配API要求
}

# 发送请求到端口9999
response = requests.post('http://localhost:9999/api/ocr', json=data)

# 输出识别结果
if response.status_code == 200:
    results = response.json()
    print(results)
else:
    print("Failed to recognize text:", response.status_code, response.text)
