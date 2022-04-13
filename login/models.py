from django.db import models

# Create your models here.
#用户表
class User(models.Model):
    gender = (
        ('boy','男'),
        ('girl','女'),
    )
    name = models.CharField(max_length=128,unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    sex = models.CharField(max_length=32,choices=gender,default="男")
    create_time = models.DateTimeField(auto_now_add=True)
    has_confirmed = models.BooleanField(default=False)#是否通过邮箱验证
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["-create_time"]#按用户注册时间排序，越早注册的用户排在越后
        verbose_name = "用户"#在admin管理界面显示中文
        verbose_name_plural = "用户"#中文复数，一般不做区别
#经过确认的用户表
class ConfirmString(models.Model):
    code = models.CharField(max_length=256)#确认码
    user = models.OneToOneField('User',on_delete=models.CASCADE)#与用户表是一对一关系，一个用户一个确认码
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name+"："+self.code
    class Meta:
        ordering = ["-create_time"]
        verbose_name = "确认码"
        verbose_name_plural = "确认码"