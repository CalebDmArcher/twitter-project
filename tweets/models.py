from django.db import models
from django.contrib.auth.models import User
# from datetime import datetime
from utils.time_helpers import utc_now


class Tweet(models.Model):
    # who posts this tweet
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text='who post this tweet',
        verbose_name='Poster',
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    @property
    def hours_to_now(self):
        # return (datetime.now() - self.created_at).seconds // 3600
        # datetime.now 不带时区信息，需要增加上 utc 的时区信息
        return (utc_now() - self.created_at).seconds // 3600

    def __str__(self):
        # 这里是你执行 print(tweet instance) 的时候会显示的内容
        return f'{self.created_at} {self.user}: {self.content}'