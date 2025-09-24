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
from ftplib import FTP
import os
from colorama import init, Fore, Style
from dotenv import load_dotenv
init(autoreset=True) 
from netmiko import ConnectHandler


#os.chdir('C:/Users/ffang/Downloads/python')
#current_dir = os.getcwd()
#print(f"current work directory：{current_dir}")

#load_dotenv(dotenv_path=".env")
cisco_username = os.environ.get('CISCO_USERNAME')
cisco_password = os.environ.get('CISCO_PASSWORD')           
ftp_username = os.environ.get('FTP_USERNAME')
ftp_password = os.environ.get('FTP_PASSWORD') 

# 定义设备连接参数
cisco_device = [
    {
        'device_type': 'cisco_ios',  # 设备类型固定值
        'host': 'cnchen02wc01',
        'username': cisco_username,
        'password': cisco_password,
        'port': 22,  # 默认SSH端口
    },
    {
        'device_type': 'cisco_ios',  # 设备类型固定值
        'host': 'sgsing01wc01',
        'username': cisco_username,
        'password': cisco_password,
        'port': 22,  # 默认SSH端口
    },
    {
        'device_type': 'cisco_ios',  # 设备类型固定值
        'host': 'jptkyo01wc01',
        'username': cisco_username,
        'password': cisco_password,
        'port': 22,  # 默认SSH端口
    },
    {
        'device_type': 'cisco_ios',  # 设备类型固定值
        'host': 'inhdrb02wc01',
        'username': cisco_username,
        'password': cisco_password,
        'port': 22,  # 默认SSH端口
    },
    {
        'device_type': 'cisco_ios',  # 设备类型固定值
        'host': 'cnzyng02wc01',
        'username': cisco_username,
        'password': cisco_password,
        'port': 22,  # 默认SSH端口
    }
]


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
                    highlighted = line.replace(target, f"{target}{Style.RESET_ALL}")
                    def read_ftp_file(hostip, username, password, remote_path):
                        try:
                            with FTP(hostip) as ftp:
                                ftp.login(user=username, passwd=password)
                                
                                # 创建临时文件
                                temp_file = 'temp_ftp_download.txt'
                                
                                with open(temp_file, 'wb') as f:
                                    ftp.retrbinary(f'RETR {remote_path}', f.write)
                                
                                # 读取文件内容
                                with open(temp_file, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                # 删除临时文件
                                os.remove(temp_file)
                                
                                return content
                        except Exception as e:
                            print(f"读取文件失败: {str(e)}")
                            return None
                    
                    # 使用示例
                    content = read_ftp_file('10.133.10.115', ftp_username, ftp_password, f'/python/{host}output_previous.txt')
                    #if content:
                    #print("文件内容:", content)
                    with open("output_previous.txt", "w", encoding="utf-8") as f:  # 推荐指定编码
                        f.write(content)
                    with open("output.txt", 'r') as f1, open("output_previous.txt", 'r') as f2:    
                        lines_c = f1.readlines()
                        lines_p = [line.rstrip('\n') for line in f2.readlines()]
                        lines_cc = line.rstrip('\n')
                        line_count_c = len(lines_c)
                        line_count_p = len(lines_p)
                        print(f"line1={line_count_c} and line2={line_count_p}")
                        print(f"{lines_cc}")
                        print(f"{lines_p}")
                        if lines_cc in lines_p :           
                            print(f"RADIUS_DEAD is found on {host} last time ")  # :ml-citation{ref="3,7" data="citationList"}                                                                                   
                        else:
                            print(f"{Fore.RED}{target}{Fore.WHITE}在{Fore.GREEN}{host}{Fore.WHITE}第 {line_num} 行: {highlighted.strip()}")
                            found = True
                    #with open("output.txt", 'r') as f1:
                        #if f1.read() == content:                   
                            #print(f"RADIUS_DEAD is found on {host} last time ")  # :ml-citation{ref="3,7" data="citationList"}                                                               
                        #else:
                            #print(f"{Fore.RED}{target}{Fore.WHITE}在{Fore.GREEN}{host}{Fore.WHITE}第 {line_num} 行: {highlighted.strip()}")
                            #found = True
                            teams_webhook_url = "https://aligntech.webhook.office.com/webhookb2/7ed9a6c7-e811-4e71-956c-9e54f8b7d705@9ac44c96-980a-481b-ae23-d8f56b82c605/JenkinsCI/9ecff2f044b44cfcae37b0376ecd1540/9d21b513-f4ee-4b3b-995c-7a422a087a6c/V2-0LzN76qekmVrAPO1b9pX-4MwxVsHKo7lbMnV_iHFb81"
                            message = {
                            "text": f"WARNING: Detected NEW {target} in {host} Number {line_num} , The Log is : {highlighted.strip()}."
                            }
                            try:
                                teams_response = requests.post(
                                teams_webhook_url,
                                json=message,
                                headers={"Content-Type": "application/json"}
                            )
                                teams_response.raise_for_status()
                            except Exception as e:
                                print(f"Failed to send alert to MS Teams for {host}")       
                                
            if not found:
                print(f"No new RADIUS_DEAD is found on {host} ")  # :ml-citation{ref="3,7" data="citationList"}

        def upload_text_file(hostip, username, password, local_path, remote_path):
            try:
                with FTP(hostip) as ftp:
                    ftp.login(user=username, passwd=password)
                    
                    with open(local_path, 'rb') as f:
                        ftp.storbinary(f'STOR {remote_path}', f)
                    
                    print(f"文件 {local_path} 已上传到 {remote_path}")
                    return True
            except Exception as e:
                print(f"上传文件失败: {str(e)}")
                return False

        # 使用示例
        with open(f"{host}output_previous.txt", "w", encoding="utf-8") as f:  # 推荐指定编码
            f.write(text)
        upload_text_file('10.133.10.115', ftp_username, ftp_password, f'{host}output_previous.txt', f'/python/{host}output_previous.txt')
