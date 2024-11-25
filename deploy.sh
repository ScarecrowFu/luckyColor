#!/bin/bash

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}开始部署幸运色彩双色球预测系统...${NC}"

# 检查Python3是否安装
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 未安装，开始安装...${NC}"
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
fi

# 检查MySQL是否安装
if ! command -v mysql &> /dev/null; then
    echo -e "${RED}MySQL 未安装，开始安装...${NC}"
    sudo apt-get install -y mysql-server mysql-client libmysqlclient-dev
    sudo systemctl start mysql
    sudo systemctl enable mysql
fi

# 创建项目目录
PROJECT_DIR="lucky_color"
if [ ! -d "$PROJECT_DIR" ]; then
    mkdir -p $PROJECT_DIR
fi

cd $PROJECT_DIR

# 创建并激活虚拟环境
echo -e "${GREEN}创建虚拟环境...${NC}"
python3 -m venv env
source env/bin/activate

# 安装依赖包
echo -e "${GREEN}安装依赖包...${NC}"
pip install -r requirements.txt

# 配置MySQL数据库
echo -e "${GREEN}配置数据库...${NC}"
mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS lucky_color DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'lucky'@'localhost' IDENTIFIED BY 'lucky123456';
GRANT ALL PRIVILEGES ON lucky_color.* TO 'lucky'@'localhost';
FLUSH PRIVILEGES;
EOF

# 执行数据库迁移
echo -e "${GREEN}执行数据库迁移...${NC}"
python manage.py makemigrations
python manage.py migrate

# 抓取历史数据
echo -e "${GREEN}开始抓取历史数据...${NC}"
python manage.py fetch_lottery_data

# 配置定时任务
echo -e "${GREEN}配置定时任务...${NC}"
(crontab -l 2>/dev/null; echo "30 19 * * 2,4,7 cd $(pwd) && source env/bin/activate && python manage.py fetch_lottery_data") | crontab -

# 配置Gunicorn服务
echo -e "${GREEN}配置Gunicorn服务...${NC}"
sudo tee /etc/systemd/system/lucky_color.service <<EOF
[Unit]
Description=Lucky Color Gunicorn daemon
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/env/bin/gunicorn --workers 3 --bind unix:lucky_color.sock luckyColor.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# 启动Gunicorn服务
sudo systemctl start lucky_color
sudo systemctl enable lucky_color

# 配置Nginx
echo -e "${GREEN}配置Nginx...${NC}"
if ! command -v nginx &> /dev/null; then
    sudo apt-get install -y nginx
fi

sudo tee /etc/nginx/sites-available/lucky_color <<EOF
server {
    listen 80;
    server_name _;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root $(pwd);
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$(pwd)/lucky_color.sock;
    }
}
EOF

# 创建符号链接并重启Nginx
sudo ln -sf /etc/nginx/sites-available/lucky_color /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# 收集静态文件
echo -e "${GREEN}收集静态文件...${NC}"
python manage.py collectstatic --noinput

# 设置文件权限
echo -e "${GREEN}设置文件权限...${NC}"
sudo chown -R $USER:$USER $(pwd)
sudo chmod -R 755 $(pwd)

echo -e "${GREEN}部署完成！${NC}"
echo -e "请访问 http://服务器IP 查看网站。"

# 显示部署日志路径
echo -e "${GREEN}部署日志路径：${NC}"
echo "Nginx 日志: /var/log/nginx/"
echo "应用日志: $(pwd)/lottery_crawler.log"

# 显示常用命令
echo -e "${GREEN}常用命令：${NC}"
echo "重启应用: sudo systemctl restart lucky_color"
echo "查看应用状态: sudo systemctl status lucky_color"
echo "查看应用日志: sudo journalctl -u lucky_color"
echo "重启Nginx: sudo systemctl restart nginx" 