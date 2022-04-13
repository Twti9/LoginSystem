#开发时间：2022/4/11 16:17

from django import forms
from captcha.fields import CaptchaField
#用户登录界面，以表单形式构建更快捷
class UserForm(forms.Form):
    username = forms.CharField(label="用户名",max_length=128,widget=forms.TextInput(attrs={'class':'form-control','placeholder':"Username",'autofocus':''}))
    password = forms.CharField(label="密码",max_length=256,widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':"Password"}))
    captcha = CaptchaField(label='验证码')
#用户注册界面
class RegisterForm(forms.Form):
    gender = (
        ('boy','男'),
        ('girl','女'),
    )
    username = forms.CharField(label="用户名",max_length=128,widget=forms.TextInput(attrs={'class':'form-control'}))
    password1 = forms.CharField(label="密码",max_length=256,widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password2 = forms.CharField(label="确认密码",max_length=256,widget=forms.PasswordInput(attrs={'class':'form-control'}))
    email = forms.EmailField(label="邮箱地址",widget=forms.EmailInput(attrs={'class':'form-control'}))
    sex = forms.ChoiceField(label="性别",choices=gender)
    captcha = CaptchaField(label="验证码")