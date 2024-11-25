# 幸运色彩 - 双色球预测系统

# 完全使用 cursor AI 生成

## 项目简介

幸运色彩是一个基于Django开发的双色球预测系统，提供历史数据查询、随机选号和智能预测功能。系统采用现代化的Web技术栈，提供直观的用户界面和多种预测算法。

## 功能特点

### 历史数据查询
- 展示双色球历史开奖记录（2003年至今）
- 支持期号精确搜索
- 分页展示（每页20条记录）
- 每周二、四、日自动更新最新开奖数据
- 支持数据重置功能

### 随机选号功能
- 智能随机生成号码
- 支持红球范围筛选（全部/小号/中号/大号）
- 支持蓝球范围筛选（全部/小号/大号）
- 保存最近5次生成记录
- 动态号码生成动画效果

### 智能预测功能
- 频率分析预测：基于历史数据频率分析
- 规律分析预测：基于号码变化规律分析
- 智能算法预测：综合多种预测方法
- 每种预测方式提供10组推荐号码
- 页面加载自动预测

## 技术架构

### 前端技术
- HTML5 + CSS3
- JavaScript (原生)
- Font Awesome 图标库
- 响应式布局设计

### 后端技术
- Django 4.2+
- Python 3.8+
- MySQL 5.7+
- Nginx + Gunicorn

### 数据分析
- NumPy：数值计算和概率分析
- BeautifulSoup4：数据爬取
- Requests：HTTP请求处理

## 环境要求

### 服务器环境
- CPU: 1核+
- 内存: 1GB+
- 存储: 10GB+
- 操作系统: Ubuntu 18.04+ / CentOS 7+

### 软件环境
- Python 3.8+
- MySQL 5.7+
- Nginx 1.14+
- Git

## 快速开始


### 1. 克隆项目


```bash
git clone https://github.com/yourusername/lucky-color.git
cd lucky-color
```

### 2. 创建虚拟环境并安装依赖

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


### 3. 配置数据库
- 创建MySQL数据库并导入初始数据
- 在`settings.py`中配置数据库连接信息

### 4. 运行迁移

```bash
python manage.py migrate
```


### 5. 启动开发服务器

```bash
python manage.py runserver
```


### 6. 访问应用
在浏览器中打开 `http://127.0.0.1:8000` 查看应用。

## 部署指南

### 使用Nginx和Gunicorn部署
1. 安装Nginx和Gunicorn
2. 配置Nginx以代理到Gunicorn
3. 使用`supervisor`或`systemd`管理Gunicorn进程

## 贡献指南

欢迎贡献！请提交Pull Request或报告问题。

## 许可证

该项目采用MIT许可证。详情请参阅LICENSE文件。