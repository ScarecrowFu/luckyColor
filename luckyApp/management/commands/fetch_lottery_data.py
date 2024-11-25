from django.core.management.base import BaseCommand
from luckyApp.tasks import LotteryDataCrawler

class Command(BaseCommand):
    help = '抓取双色球历史数据'

    def handle(self, *args, **options):
        crawler = LotteryDataCrawler()
        crawler.run()
        self.stdout.write(self.style.SUCCESS('数据抓取完成')) 