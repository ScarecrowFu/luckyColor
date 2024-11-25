import requests
import bs4
from datetime import datetime
import logging
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from .models import LotteryNumber

logger = logging.getLogger(__name__)

class LotteryDataCrawler:
    def __init__(self):
        self.base_url = 'http://tubiao.zhcw.com/tubiao/ssqNew/ssqJsp/ssqZongHeFengBuTuAsc.jsp'
        self.headers = {
            'Referer': 'http://tubiao.zhcw.com/tubiao/ssqNew/ssqInc/ssqZongHeFengBuTuAsckj_year=2016.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.setup_session()

    def setup_session(self):
        """配置请求会话，添加重试机制"""
        self.session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=5,  # 总重试次数
            backoff_factor=1,  # 重试间隔
            status_forcelist=[500, 502, 503, 504],  # 需要重试的HTTP状态码
            allowed_methods=["GET"]  # 允许重���的请求方法
        )
        
        # 配置适配器
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def fetch_data(self, year):
        """获取指定年份的数据"""
        url = f"{self.base_url}?kj_year={year}"
        logger.info(f"开始获取 {year} 年数据，URL: {url}")
        
        try:
            # 添加随机延时，避免请求过快
            time.sleep(2)
            
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"成功获取 {year} 年数据，状态码: {response.status_code}")
            return response.text
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"连接错误 ({year}年): {str(e)}")
            return None
        except requests.exceptions.Timeout as e:
            logger.error(f"请求超时 ({year}年): {str(e)}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常 ({year}年): {str(e)}")
            return None
        except Exception as e:
            logger.error(f"未知错误 ({year}年): {str(e)}")
            return None

    def parse_data(self, html, year):
        """解析HTML数据"""
        if not html:
            logger.warning(f"{year}年数据为空，跳过解析")
            return []
        
        results = []
        try:
            soup = bs4.BeautifulSoup(html, 'html.parser')
            rows = soup.find_all(class_='hgt')
            logger.info(f"找到 {len(rows)} 条 {year} 年的开奖记录")
            
            for index, row in enumerate(rows, 1):
                try:
                    if not isinstance(row, bs4.element.Tag):
                        continue
                        
                    issue = row.find(class_="qh7").string.strip()
                    if issue.startswith("模拟"):
                        continue
                        
                    red_balls = [int(ball.string) for ball in row.find_all(class_="redqiu")]
                    blue_ball = int(row.find(class_="blueqiu3").string)
                    
                    results.append({
                        'issue_number': issue,
                        'red_balls': red_balls,
                        'blue_ball': blue_ball
                    })
                    
                except Exception as e:
                    logger.error(f"解析第 {index} 行数据���败 ({year}年): {str(e)}")
                    continue
                    
            logger.info(f"成功解析 {len(results)} 条 {year} 年的开奖记录")
            
        except Exception as e:
            logger.error(f"解析 {year} 年数据失败: {str(e)}")
            
        return results

    def save_to_db(self, data, year):
        """保存数据到数据库"""
        success_count = 0
        error_count = 0
        
        logger.info(f"开始保存 {year} 年的 {len(data)} 条数据")
        
        for item in data:
            try:
                LotteryNumber.objects.update_or_create(
                    issue_number=item['issue_number'],
                    defaults={
                        'red_ball_1': item['red_balls'][0],
                        'red_ball_2': item['red_balls'][1],
                        'red_ball_3': item['red_balls'][2],
                        'red_ball_4': item['red_balls'][3],
                        'red_ball_5': item['red_balls'][4],
                        'red_ball_6': item['red_balls'][5],
                        'blue_ball': item['blue_ball']
                    }
                )
                success_count += 1
                
            except Exception as e:
                error_count += 1
                logger.error(f"保存期号 {item['issue_number']} 失败 ({year}年): {str(e)}")
                
        logger.info(f"{year}年数据保存完成: 成功 {success_count} 条，失败 {error_count} 条")

    def run(self):
        """运行爬虫"""
        current_year = datetime.now().year
        total_success = 0
        total_error = 0
        
        logger.info(f"开始抓取数据，年份范围: 2003-{current_year}")
        
        for year in range(2003, current_year + 1):
            try:
                logger.info(f"开始处理 {year} 年数据...")
                
                html = self.fetch_data(year)
                if html:
                    data = self.parse_data(html, year)
                    if data:
                        self.save_to_db(data, year)
                        total_success += 1
                    else:
                        total_error += 1
                else:
                    total_error += 1
                    
                # 年份之间添加较长延时
                time.sleep(5)
                
            except Exception as e:
                total_error += 1
                logger.error(f"处理 {year} 年数据时发生错误: {str(e)}")
                
        logger.info(f"数据抓取完成: 成功处理 {total_success} 年���失败 {total_error} 年") 