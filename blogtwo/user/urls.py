"""blogtwo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from user import views
from django.contrib.auth.decorators import login_required

# 每次匹配个人收藏的时候都会匹配到个人主页上去，注意修改正则相关内容
app_name = 'user'
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # url(r'^register/', views.register, name='register'),    # 注册函数
    url(r'^check_username_exist/$', views.CheckUsernameExist.as_view(), name='check_username'),  # 检查用户是否已存在
    url(r'^register/$', views.Register.as_view(), name='register'),   # 注册视图
    url(r'^active/(?P<token>.*)$', views.ActiveView.as_view(),name='active'),  # 账号激活
    url(r'^login/$', views.LoginView.as_view(), name='login'),  # 登录
    url(r'^logout/$', views.Logout.as_view(), name='logout'),  # 注销

    # # 如果在url中不想使用login_required进行封装，可以在view中进行操作
    # url(r'^article/collect/$', login_required(views.Collect.as_view()), name='collect'),  # 个人收藏
    # url(r'^account/set/$', login_required(views.Set.as_view()), name='set'),   # 个人账号设置,只有登录后才可以账号设置
    # url(r'^account/set/success/$', views.SetSucess.as_view(), name='set_success'),   # 个人账号设置成功
    # url(r'^focus/$', login_required(views.Focus.as_view()), name='focus'),    # 我的关注
    # url(r'^article/$', login_required(views.Article.as_view()), name='article'),    # 我的博客
    # url(r'(?P<username>.*?)/$', login_required(views.HomeView.as_view()), name='home'),  # 个人主页

    url(r'^article/collect/$', views.Collect.as_view(), name='collect'),  # 个人收藏
    url(r'^account/set/$', views.Set.as_view(), name='set'),  # 个人账号设置,只有登录后才可以账号设置
    url(r'^account/set/success/$', views.SetSucess.as_view(), name='set_success'),  # 个人账号设置成功
    url(r'^focus/$', views.Focus.as_view(), name='focus'),  # 我的关注
    url(r'^articles/$', views.Articles.as_view(), name='article'),  # 我的博客
    url(r'^(?P<username>.*?)/', views.HomeView.as_view(), name='home'),  # 个人主页

]
