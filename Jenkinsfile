pipeline {
    agent any  // 使用任意可用节点
    stages {
        stage('Enable virtual environment pyats') {
            steps {
                echo 'Setup PYATS environment'
                sh 'python3 -m venv pyats'
                sh 'source pyats/bin/activate'
            }
        }
        stage('Install dotenv') {
            steps {
                sh 'pip3 install dotenv'
            }
        }
        stage('Install dotenv') {
            steps {
                sh 'pip3 install netmiko'
            }
        }
         stage('Install dotenv') {
            steps {
                sh 'pip3 install colorama'
            }
        }
    stages {
        stage('Checkout') {
            steps {
                checkout scm  // 拉取 GitHub 代码
            }
        }



        stage('Setup Python') {
            steps {
                sh 'python3 --version'  // 检查 Python 环境
                // 可选：安装依赖（如 pip install -r requirements.txt）
            }
        }



        stage('Run Python Script') {
            steps {
                sh 'python3 get_WLC_log_RADIUS_DEAD.py'  // 运行 Python 文件
            }
        }
    }
}
