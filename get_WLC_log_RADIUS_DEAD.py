#!usr/bin/python3

"""
This script is to check the AAD graph flow on the specific Silver Peak appliance.
Jenkins will run the job and send message to MS Teams for the graph flow down.
Set the Orchestrator and Token in environment
export ORCHESTRATOR_HOST="your.orchestrator.host"
export ORCH_TOKEN="your_secret_token_here"
"""
import base64
import json
import requests
from urllib3.exceptions import InsecureRequestWarning
import os
from colorama import init, Fore, Style
from dotenv import load_dotenv
init(autoreset=True) 
from netmiko import ConnectHandler


#os.chdir('C:/Users/ffang/Downloads/python')
#current_dir = os.getcwd()
#print(f"current work directory：{current_dir}")

load_dotenv(dotenv_path=".env")
cisco_username = os.getenv("CISCO_USERNAME")
cisco_password = os.getenv("CISCO_PASSWORD")

# 定义设备连接参数
cisco_device = [
    {
        'device_type': 'cisco_ios',  # 设备类型固定值
        'host': '10.133.20.119',
        'username': cisco_username,
        'password': cisco_password,
        'port': 22,  # 默认SSH端口
    },
    {
        'device_type': 'cisco_ios',  # 设备类型固定值
        'host': '10.127.230.5',
        'username': cisco_username,
        'password': cisco_password,
        'port': 22,  # 默认SSH端口
    },
    {
        'device_type': 'cisco_ios',  # 设备类型固定值
        'host': '10.121.230.9',
        'username': cisco_username,
        'password': cisco_password,
        'port': 22,  # 默认SSH端口
    },
    {
        'device_type': 'cisco_ios',  # 设备类型固定值
        'host': '10.152.230.5',
        'username': cisco_username,
        'password': cisco_password,
        'port': 22,  # 默认SSH端口
    },
    {
        'device_type': 'cisco_ios',  # 设备类型固定值
        'host': '10.146.230.253',
        'username': cisco_username,
        'password': cisco_password,
        'port': 22,  # 默认SSH端口
    }
]

# 建立连接并执行命令
for device in cisco_device:
        host = device['host']
        
        try:
            with ConnectHandler(**device) as conn:
                text = conn.send_command('sho logging | in RADIUS_DEAD')  # 执行单条命令
                #print(text)
                        
                # 执行多条配置命令
                #config_commands = ['interface GigabitEthernet0/1', 'description Python-configured']
                #output = conn.send_config_set(config_commands)
                #print(output)
                
        except Exception as e:
            print(f"连接失败: {str(e)}")

        target = "RADIUS_DEAD"


        # 覆盖写入模式（文件存在则清空后保存）
        with open("output.txt", "w", encoding="utf-8") as f:  # 推荐指定编码
            f.write(text)


        with open("output.txt", 'r') as f:
            found = False
            for line_num, line in enumerate(f, 1):
                if target in line:
                    highlighted = line.replace(target, f"{Fore.RED}{target}{Style.RESET_ALL}")
                    with open(f"{host}output_previous.txt", 'r') as f1, open("output.txt", 'r') as f:
                        if f1.read() == f.read():                  
                            print(f"RADIUS_DEAD is found on {host} last time ")  # :ml-citation{ref="3,7" data="citationList"}                                                               
                        else:
                            print(f"{Fore.RED}{target}{Fore.WHITE}在{Fore.GREEN}{host}{Fore.WHITE}第 {line_num} 行: {highlighted.strip()}")
                            found = True
                            #teams_webhook_url = "https://aligntech.webhook.office.com/webhookb2/7ed9a6c7-e811-4e71-956c-9e54f8b7d705@9ac44c96-980a-481b-ae23-d8f56b82c605/JenkinsCI/9ecff2f044b44cfcae37b0376ecd1540/9d21b513-f4ee-4b3b-995c-7a422a087a6c/V2-0LzN76qekmVrAPO1b9pX-4MwxVsHKo7lbMnV_iHFb81"
                            #message = {
                            #"text": f"WARNING: RADIUS_DEAD is detected on {host}，please check RADIUS status on {host}."
                            #}
                            #try:
                                #teams_response = requests.post(
                                #teams_webhook_url,
                                #json=message,
                                #headers={"Content-Type": "application/json"}
                            #)
                                #teams_response.raise_for_status()
                            #except Exception as e:
                                #print(f"Failed to send alert to MS Teams for {host}")       
                                
            if not found:
                print(f"No new RADIUS_DEAD is found on {host} ")  # :ml-citation{ref="3,7" data="citationList"}

with open(f"{host}output_previous.txt", "w", encoding="utf-8") as f:  # 推荐指定编码
    f.write(text)
        
GITHUB_TOKEN = "GITHUB_TOKEN"
REPO_NAME = "forlynfang/radius_dead"  # 例如 "yourusername/yourrepo"
FILE_PATH = "{host}output_previous.txt"  # 要更新的txt文件路径
BRANCH = "main"  # 默认分支名
def update_txt_with_api():
    # 设置请求头
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 获取文件当前内容的URL
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}?ref={BRANCH}"
    
    try:
        # 获取当前文件信息
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        file_data = response.json()
        
        # 解码内容
        current_content = base64.b64decode(file_data['content']).decode('utf-8')
        print("当前文件内容:")
        print(current_content)
        
        # 修改内容
        new_content = f.read()
        # 准备更新数据
        update_data = {
            "message": "通过REST API更新txt文件",
            "content": base64.b64encode(new_content.encode('utf-8')).decode('utf-8'),
            "sha": file_data['sha"],
            "branch": BRANCH
        }
        
        # 发送更新请求
        update_response = requests.put(url, headers=headers, json=update_data)
        update_response.raise_for_status()
        
        print("文件更新成功！")
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"错误详情: {e.response.json()}")

if __name__ == "__main__":
    update_txt_with_api()
