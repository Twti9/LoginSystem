from django.shortcuts import render
from django.shortcuts import redirect
from . import models,forms
from django.conf import settings
import datetime
import hashlib
#使用hashlib模块构建一个用于密码加密的函数
def hash_code(s,salt='mysite'):
    h = hashlib.sha256()
    s+=salt
    h.update(s.encode())
    return h.hexdigest()#返回加密后的密码
#用于生成确认码
def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name,now)#以当前时间为盐
    models.ConfirmString.objects.create(code=code,user=user,)#将确认过的用户添加到确认用户表
    return code
#用于邮箱验证
def send_mail(email,code):
    from django.core.mail import EmailMultiAlternatives
    subject = '来自****的注册确认邮件'
    text_content = '''感谢注册，这里是***的站点，如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'''
    html_content = '''
                    <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>www.luoblog.com</a>，\
                    这里是****的博客和教程站点</p>
                    <p>请点击站点链接完成注册确认！</p>
                    <p>此链接有效期为{}天！</p>
                    '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)
    #指定邮件主题，默认内容，发送方，接收方列表
    msg = EmailMultiAlternatives(subject,text_content,settings.EMAIL_HOST_USER,[email])
    #指定邮件内容，附件格式
    msg.attach_alternative(html_content,"text/html")
    msg.send()
# Create your views here.
#主页
def index(request):
    #如果该用户没有登录过的记录，返回到登录界面
    if not request.session.get('is_login',None):
        return redirect('/login/')
    return render(request,'login/index.html')
#登录功能设计
def login(request):
    #如果用户已经登录过，直接跳转到主页，不允许重复登录
    if request.session.get('is_login',None):
        return redirect('/index/')
    if request.method == "POST":
        login_form = forms.UserForm(request.POST)
        message = '用户名或密码错误！！！'
        #验证码数据合法性
        if login_form.is_valid():
            #使用表单的cleaned_data方法获取数据
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            try:
                #在用户表中查找用户输入的用户名
                user = models.User.objects.get(name=username)
            except:
                message = '用户不存在'
                return render(request,'login/login.html',locals())
            #如果用户存在，则判断是否已经经过邮件确认
            if not user.has_confirmed:
                message = '该用户还未经过邮件确认!'
                return render(request,'login/login.html',locals())
            if user.password == hash_code(password):
                #使用会话记录用户状态
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                return redirect('/index/')
            else:
                message = '密码错误！'
                return render(request,'login/login.html',locals())
        else:
            return render(request,'login/login.html',locals())
    #如果用户没有提交数据，直接返回一个空表单，便于继续提交
    login_form = forms.UserForm()
    return render(request, 'login/login.html',locals())
#注册功能设计
def register(request):
    if request.session.get('is_login',None):
        return redirect('/index/')
    if request.method == 'POST':
        #根据用户的提交信息创建一个注册表单对象
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容!"
        if register_form.is_valid():
            #如果数据合法，将表单的数据读出，进行下一步判断
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')
            sex = register_form.cleaned_data.get('sex')

            if password1 != password2:
                message = "两次输入的密码不一致！！"
                return render(request,'login/register.html',locals())
            else:
                #在用户表中查找要注册的用户名与邮箱是否已经被注册了
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:
                    message = "用户已存在"
                    return render(request,'login/register.html',locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:
                    message = "该邮箱已经被注册了"
                    return render(request,'login/register.html',locals())
                #以上条件都满足，则将该用户加入用户表中
                new_user = models.User()
                new_user.name = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.sex = sex
                new_user.save()
                #生成一个确认码
                code = make_confirm_string(new_user)
                send_mail(email,code)
                message = "请前往邮箱确认！"
                return render(request,'login/confirm.html',locals())
        else:
            return render(request,'login/register.html',locals())
    register_form = forms.RegisterForm()
    return render(request, 'login/register.html',locals())
#邮件确认功能设计，点击链接时使用此功能
def user_confirm(request):
    code = request.GET.get('code',None)
    message = ''
    try:
        #判断确认码是否是正确的，相当于配对ConfirmString和make_confirm_string
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = "无效的确认请求！"
        return render(request,'login/confirm.html',locals())
    create_time = confirm.create_time
    now = datetime.datetime.now()
    if now > create_time+datetime.timedelta(settings.CONFIRM_DAYS):
        #确认码过期，则根据一对一查找确认表中对应用户，删除该用户
        confirm.user.delete()
        message = '您的邮件已经过期，请重新注册！'
        return render(request,'login/confirm.html',locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        #确认完后及时删除确认码，保证一码一人
        confirm.delete()
        message = '感谢确认，请使用账户登录！'
        return render(request,'login/confirm.html',locals())
#登出功能
def logout(request):
    if not request.session.get('is_login',None):
        return redirect('/login/')
    request.session.flush()

    return redirect("/login/")