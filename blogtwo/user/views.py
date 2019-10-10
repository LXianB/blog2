from django.shortcuts import render, redirect,HttpResponse
from django.views.generic import View
from django.http import JsonResponse
from django.contrib import auth
from user import forms, models
import logging
# from django.contrib.auth.forms import PasswordChangeForm    修改密码时需要用到
# from django.contrib.auth import update_session_auth_hash   # 修改密码后当前登录对象保存登录状态需要用到
from utils.mixin import LoginRequiredMixin
from celery_tasks.tasks import send_register_active_email
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired   # 超时异常处理
from django.core.urlresolvers import reverse            # 反向解析
from django_redis import get_redis_connection
from article import models as Article_Model
from django.contrib.auth.decorators import login_required    # 访问需要登录后的页面时的装饰器
from django.core.mail import send_mail
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage

# from django.db.models import Count
# from django.db.models import F


# 生成一个logger实例，专门用来记录日志
logger = logging.getLogger(__name__)
# logger_s10 = logging.getLogger("collect")

# Create your views here.

def login(request):
    # if request.is_ajax():  # 如果是AJAX请求
    if request.method == "POST":
        # 初始化一个给AJAX返回的数据
        ret = {"status": 0, "msg": ""}
        # 从提交过来的数据中 取到用户名和密码
        username = request.POST.get("username")
        pwd = request.POST.get("password")

        user = auth.authenticate(username=username, password=pwd)
        if user:
            # 用户名密码正确
            # 给用户做登录
            auth.login(request, user)  # 将登录用户赋值给 request.user
            ret["msg"] = "/article/index/"
        else:
            # 用户名密码错误
            ret["status"] = 1
            ret["msg"] = "用户名或密码错误！"

        return JsonResponse(ret)
    return render(request, "login2.html")


# 注销
def logout(request):
    auth.logout(request)
    return redirect("/article/index/")


# 注册的视图函数
def register(request):
    if request.method == "POST":
        ret = {"status": 0, "msg": ""}
        form_obj = forms.RegForm(request.POST)
        # 帮我做校验
        if form_obj.is_valid():
            # 校验通过，去数据库创建一个新的用户
            form_obj.cleaned_data.pop("re_password")
            avatar_img = request.FILES.get("avatar")         # 这是头像
            print(avatar_img.name)
            models.User.objects.create_user(**form_obj.cleaned_data, avatar=avatar_img)
            ret["msg"] = "/article/index/"
            return JsonResponse(ret)
        else:
            print(form_obj.errors)
            ret["status"] = 1
            ret["msg"] = form_obj.errors
            print(ret)
            print("=" * 120)
            return JsonResponse(ret)
    # 生成一个form对象
    form_obj = forms.RegForm()
    # print(form_obj.fields)
    return render(request, "register.html", {"form_obj": form_obj})


# 校验用户名是否已被注册
class CheckUsernameExist(View):
    def get(self, request):
        ret = {"status": 0, "msg": ""}
        username = request.GET.get("username")
        # print(username)
        is_exist = models.User.objects.filter(username=username)
        if is_exist:
            ret["status"] = 1
            ret["msg"] = "用户名已被注册！"
        return JsonResponse(ret)


class Register(View):
    form_obj = forms.RegForm()

    def get(self,request):
        '''显示注册页面'''
        return render(request, 'register.html', {"form_obj": self.form_obj})

    def post(self,request):
        '''注册页面逻辑处理'''
        ret = {"status": 0, "msg": ""}
        form_obj = forms.RegForm(request.POST)
        # 帮我做校验
        if form_obj.is_valid():
            # 校验通过，去数据库创建一个新的用户
            form_obj.cleaned_data.pop("re_password")
            avatar_img = request.FILES.get("avatar")  # 这是头像
            print(avatar_img.name)
            models.User.objects.create_user(**form_obj.cleaned_data, avatar=avatar_img)
            user_name = form_obj.cleaned_data.get('username')
            user = models.User.objects.filter(username=user_name).first()
            # print(user.nid)
            # print(user.username)

            # 发送激活邮件：包含激活链接：http://127.0.0.1:8000/user/active/(user_id)
            # 激活链接中需要包含用户信息(并且要把身份信息加密)

            # 加密用户的身份信息，生成激活token
            serializer = Serializer(settings.SECRET_KEY,300)    # 加密的秘钥，过期时间300秒
            info = {'confirm':user.nid}
            token = serializer.dumps(info).decode('utf8')
            # print(token)

            # # 发邮件
            # subject = '博客欢迎信息'
            # message = ''
            # send = settings.EMAIL_FROM
            # recipient = [user.email]    # 收件人邮箱，一次可以发送给多个邮箱
            # html_message = "<h2>%s,欢迎注册本博客，恭喜您成为本博客用户</h2>,请点击以下链接激活账号<a href='http://127.0.0.1:8000/user/active/%s'>http://127.0.0.1:8000/user/active/%s</a>"%(user.username,token,token)
            # # send_mail阻塞执行，等到邮件发送了，页面才能跳转到index，可以使用celery异步执行，
            # send_mail(subject, message, send, recipient_list=recipient,html_message=html_message)

            # 采用celery发送邮件
            send_register_active_email.delay(user, token)
            # 处理者：Linux系统中，把项目文件导过去
            # 在项目目录下，执行 celery -A celery_tasks.tasks worker -l info

            ret["msg"] = "/article/index/"
            return JsonResponse(ret)

        else:
            print(form_obj.errors)
            ret["status"] = 1
            ret["msg"] = form_obj.errors
            print(ret)
            print("=" * 120)
            return JsonResponse(ret)


class ActiveView(View):
    """用户激活"""
    def get(self,request,token):
        """进行用户激活"""
        # 进行解密，获取要激活的用户信息，300秒内激活
        serializer = Serializer(settings.SECRET_KEY,300)
        try:
            info = serializer.loads(token)
            # 获取待激活用户的id
            user_id = info['confirm']

            # 根据id获取用户信息
            user = models.User.objects.get(nid=user_id)
            user.is_active = True
            user.save()

            # 跳转到登录页面  重定向反向解析地址
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')


class LoginView(View):
    '''登录'''
    def get(self,request):
        '''显示登录页面'''
        # 判断是否记住用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request,'login2.html',{'username':username,'checked':checked})

    def post(self,request):
        '''登录校验'''
        if request.method == "POST":
            # 初始化一个给AJAX返回的数据
            ret = {"status": 0, "msg": ""}
            # 从提交过来的数据中 取到用户名和密码
            username = request.POST.get("username")
            pwd = request.POST.get("password")
            # 登录校验
            user = auth.authenticate(username=username, password=pwd)
            remember = request.POST.get('remember')
            # print(request.POST.get("remember"))  # on
            if user:
                # 用户名密码正确
                # 给用户做登录
                if user.is_active:
                    auth.login(request, user)  # 将登录用户赋值给 request.user
                    # 获取登录后所要跳转的url地址
                    next_url = request.GET.get("next","/article/index/")    # 如果拿不到next,默认跳转到/article/index/
                    print(next_url)
                    ret["msg"] = next_url
                    response = JsonResponse(ret)
                    if remember == 'on':
                        response.set_cookie("username",username,max_age=7*24)
                    else:
                        response.delete_cookie("username")
                    return response
                else:
                    ret['status'] = 1
                    ret['msg'] = "用户未激活"
                    return JsonResponse(ret)
            else:
                # 用户名密码错误
                ret["status"] = 1
                ret["msg"] = "用户名或密码错误！"

            return JsonResponse(ret)





# --------------- 下面的是需要登录后才可以访问的内容--------------------

# request.user.is_authenticated()  返回True,说明已经登录，返回False,说明未登录

# class LoginRequiredMixin(object):
#     @classmethod
#     def as_view(cls,**initkwargs):
#         view=super(LoginRequiredMixin, cls).as_view(**initkwargs)
#         return login_required(view)


class Logout(View):
    def get(self,request):
        auth.logout(request)
        # return redirect("/article/index/")
        return redirect(reverse("article:index"))   # 重定向


class HomeView(LoginRequiredMixin, View):
    def get(self,request,username,page=0):

        # 从redis中获取历史浏览记录   user_id:[1,3,5,7,6]    列表中保存的是文章的主键
        user = models.User.objects.filter(username=username).first()
        con = get_redis_connection('default')

        history_key = 'history_%d' % user.nid
        # 获取用户最新浏览的40篇博客
        article_ids = con.lrange(history_key, 0, 40)

        # Article_Model.Article.objects.filter(id__in=article_ids)
        article_list = []
        for id in article_ids:
            articles = Article_Model.Article.objects.get(nid=id)
            article_list.append(articles)
        p = Paginator(article_list,4)   # 每一页4篇
        page = request.GET.get('page')
        try:
            contacts = p.page(page)
        except PageNotAnInteger:
            # 如果page不是一个整数，则展示第一页
            contacts = p.page(1)
        except EmptyPage:
            # 如果page不在范围内，则展示结果的最后一页
            contacts = p.page(p.num_pages)
        print(p.count)   # 记录的是总的数量40
        print(p.page_range)   # range(1,5)
        print(page)

        # 组织上下文
        context = {'username':username,
                   # 'article_list':article_list,
                   "contacts": contacts,
                   "p":p,
                   }

        return render(request,'home.html',context)


# 账号设置
class Set(LoginRequiredMixin, View):
    form_obj = forms.RegForm()

    def get(self,request):
        return render(request,'user_set.html',{"form_obj": self.form_obj})

    def post(self,request):
        pass
        


class SetSucess(LoginRequiredMixin, View):
    def get(self,request):
        return HttpResponse("修改成功")


# 个人收藏
class Collect(LoginRequiredMixin, View):
    def get(self,request):
        return render(request,'user_collect.html')


# 个人关注
class Focus(LoginRequiredMixin, View):
    def get(self,request):
        return render(request,'user_focus.html')


# 我的博客
class Articles(LoginRequiredMixin, View):
    def get(self,request):
        user = request.user
        user_obj = models.User.objects.filter(username=user.username).first()
        articles_list = user_obj.article.all()
        # print(articles_list)
        # print(len(articles_list))
        p = Paginator(articles_list, 4)  # 每一页5篇
        page = request.GET.get('page')
        try:
            contacts = p.page(page)
        except PageNotAnInteger:
            # 如果page不是一个整数，则展示第一页
            contacts = p.page(1)
        except EmptyPage:
            # 如果page不在范围内，则展示结果的最后一页
            contacts = p.page(p.num_pages)
        print(p.count)  # 记录的是总的数量40
        print(p.page_range)  # range(1,5)
        print(page)

        # 组织上下文
        context = {
                   "contacts": contacts,
                   "p": p,
                   }

        return render(request,'user_article.html',context)




