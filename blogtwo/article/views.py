from django.shortcuts import render, redirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.http import JsonResponse
from article import models as model
from bs4 import BeautifulSoup
import logging
from user.models import *
import json
import os
from django.conf import settings
from django_redis import get_redis_connection
from django.db.models import F
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage


# Create your views here.
# 生成一个logger实例，专门用来记录日志
logger = logging.getLogger(__name__)


# def kong(request):
#     return redirect(reverse("article:index"))
#
#
# def index(request):
#     '''首页'''
#     return render(request,'index.html')

# 首页
class Index(View):
    def get(self, request,page=0):
        # 查询所有的文章列表
        article_list = model.Article.objects.all()
        user = request.user
        p = Paginator(article_list, 10)  # 每一页10篇
        page = request.GET.get('page')
        try:
            contacts = p.page(page)
        except PageNotAnInteger:
            # 如果page不是一个整数，则展示第一页
            contacts = p.page(1)
        except EmptyPage:
            # 如果page不在范围内，则展示结果的最后一页
            contacts = p.page(p.num_pages)
        print(p.count)  # 记录的是总的数量
        print(p.page_range)  # range(1,5)
        print(page)

        # return render(request, "index.html", {"article_list": article_list, "user": user})
        return render(request, 'index.html', {'p':p, 'contacts':contacts, 'user':user})


# 文章添加
class ArticleAdd(View):
    def get(self, request):
        return render(request, 'article_add.html')

    def post(self, request):
        title = request.POST.get('title')
        article_content = request.POST.get('article_content')
        user = request.user

        bs = BeautifulSoup(article_content, "html.parser")
        desc = bs.text[0:150] + "..."

        # 过滤非法标签
        for tag in bs.find_all():

            print(tag.name)

            if tag.name in ["script", "link"]:
                tag.decompose()

        article_obj = model.Article.objects.create(user=user, title=title, desc=desc)
        model.ArticleDetail.objects.create(content=str(bs), article=article_obj)

        return HttpResponse("添加成功")


# 文章详情页
class ArticleDetail(View):
    def get(self, request, username, pk):
        """
        :param username: 被访问的blog的用户名
        :param pk: 访问的文章的主键id值
        :return:
        """
        user = User.objects.filter(username=username).first()
        if not user:
            return HttpResponse("404")
        blog = user.blog
        # 找到当前的文章
        article_obj = model.Article.objects.filter(pk=pk).first()

        user_obj = request.user    # 当前登录用户对象
        if user_obj.is_authenticated():
            # 用户已登录
            # 添加用户的历史记录,即保存为   history_userid:[1,3,45,6]    # 列表中保存article的主键
            conn = get_redis_connection('default')
            history_key = 'history_%d'%user_obj.nid
            # 移除列表中的articles_id
            conn.lrem(history_key, 0, pk)
            # 把articles_id插入到列表的左侧
            conn.lpush(history_key, pk)
            # 只保存用户最新浏览的10条信息
            conn.ltrim(history_key, 0, 10)

        # 所有评论列表
        comment_list = model.Comment.objects.filter(article_id=pk)

        return render(
            request,
            "article_detail.html",
            {
                "username": username,
                "article": article_obj,
                "blog": blog,
                "comment_list": comment_list
            }
        )


# 文章点赞以及踩
class ArticleUpDown(View):
    def get(self, request):
        """
        文章点赞以及踩
        :param request:
        :return:
        """

        print(request.POST)
        article_id = request.POST.get('article_id')
        is_up = json.loads(request.POST.get('is_up'))
        user = request.user
        response = {"state": True}
        print("is_up", is_up)
        try:
            model.ArticleUpDown.objects.create(user=user, article_id=article_id, is_up=is_up)
            model.Article.objects.filter(pk=article_id).update(up_count=F("up_count") + 1)
        except:
            response["state"] = False
            response["first_action"] = model.ArticleUpDown.objects.filter(user=user, article_id=article_id).first().is_up

        return JsonResponse(response)


class ArticleComment(View):
    def post(self, request):
        """文章评论"""

        print(request.POST)

        pid = request.POST.get("pid")
        article_id = request.POST.get("article_id")
        content = request.POST.get("content")
        user_pk = request.user.pk
        response = {}
        if not pid:  # 根评论
            comment_obj = model.Comment.objects.create(article_id=article_id, user_id=user_pk, content=content)

        else:
            comment_obj = model.Comment.objects.create(article_id=article_id, user_id=user_pk, content=content, parent_comment_id=pid)

        model.Article.objects.filter(pk=article_id).update(comment_count=F("comment_count") + 1)

        response["create_time"] = comment_obj.create_time.strftime("%Y-%m-%d")
        response["content"] = comment_obj.content
        response["username"] = comment_obj.user.username

        return JsonResponse(response)


def upload(request):
    print(request.FILES)
    obj = request.FILES.get("upload_img")

    print("name", obj.name)

    path = os.path.join(settings.MEDIA_ROOT, "add_article_img", obj.name)

    with open(path, "wb") as f:
        for line in obj:
            f.write(line)

    res = {
        "error": 0,
        "url": "/article/media/add_article_img/" + obj.name
    }

    return HttpResponse(json.dumps(res))

