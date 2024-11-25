from django.db import models

class LotteryNumber(models.Model):
    issue_number = models.CharField(max_length=20, unique=True, verbose_name='期号')
    red_ball_1 = models.IntegerField(verbose_name='红球1')
    red_ball_2 = models.IntegerField(verbose_name='红球2')
    red_ball_3 = models.IntegerField(verbose_name='红球3')
    red_ball_4 = models.IntegerField(verbose_name='红球4')
    red_ball_5 = models.IntegerField(verbose_name='红球5')
    red_ball_6 = models.IntegerField(verbose_name='红球6')
    blue_ball = models.IntegerField(verbose_name='蓝球')
    draw_date = models.DateTimeField(auto_now_add=True, verbose_name='开奖时间')

    class Meta:
        ordering = ['-issue_number']
        verbose_name = '开奖号码'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.issue_number}"
