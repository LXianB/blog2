"""
Django settings for blogtwo project.

Generated by 'django-admin startproject' using Django 1.11.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-j+rr+kitca7kzk%$y4x67h3lt)na)$ge*p+*qhc$vc-v4x-i^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'haystack',        # 注册全文检索框架
    'tinymce',
    'user.apps.UserConfig',
    'cart',
    'article',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'blogtwo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'blogtwo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'djangotwo',
        'USER': 'root',
        'PASSWORD': '.......',
        'HOST': '127.0.0.1',
        'POST': 3306,
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# 富文本编辑器的配置
TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',
    'width': 600,
    'height': 400,
}

# 静态文件路径
STATICFILES_DIRS = [os.path.join(BASE_DIR,'static'),]

# Django用户上传的都叫media文件
MEDIA_URL = "/media/"
# media配置，用户上传的文件都默认放在这个文件夹下
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# 告诉Django项目用哪张表做认证
AUTH_USER_MODEL = 'user.User'


# 项目级别的日志配置
BASE_LOG_DIR = os.path.join(BASE_DIR, "log")

LOGGING = {
    'version': 1,  # 保留的参数，默认是1
    'disable_existing_loggers': False,  # 是否禁用已经存在的logger示例，不禁用
    'formatters': {
        'standard': {  # 定义一个标准的日志格式化
            'format': '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d]'
                      '[%(levelname)s][%(message)s]'
        },
        'simple': {  # 定义一个简单的日志格式化
            'format': '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s'
        },
        'collect': {  # 定义一个特殊的日志格式化
            'format': '%(message)s'
        }
    },
    # 过滤器
    'filters': {
        # 只有在deubg=True的过滤器
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    # 处理器
    'handlers': {
        # 定义一个专门往终端打印日志的控制器
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],  # 只有在Django debug为True时才在屏幕打印日志
            'class': 'logging.StreamHandler',  # 使用什么类去处理日志流
            'formatter': 'simple'
        },
        # 定义一个默认的日志处理器
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
            'filename': os.path.join(BASE_LOG_DIR, "bbs_info.log"),  # 日志文件
            'maxBytes': 1024 * 1024 * 50,  # 日志大小 50M
            'backupCount': 5,  # 日志文件备份的数量
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        # 定义一个专门及错误日志的处理器
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
            'filename': os.path.join(BASE_LOG_DIR, "bbs_err.log"),  # 日志文件
            'maxBytes': 1024 * 1024 * 50,  # 日志大小 50M
            'backupCount': 5,
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
    },


    'loggers': {
       # 默认的logger应用如下配置
        '': {
            'handlers': ['default', 'console', 'error'],  # 上线之后可以把'console'移除
            'level': 'DEBUG',
            'propagate': True,  # 如果有父级的logger示例，表示要不要向上传递日志流
        }
    },
}

# 全文检索框架的配置
HAYSTACK_CONNECTIONS = {
    'default': {
        # 使用whoosh引擎
        'ENGINE': 'haystack.backends.whoosh_cn_backend.WhooshEngine',
        # 索引文件路径，自动生成，不用单独创建
        'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
    }
}

# 当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
# 指定每一页的搜索结果显示条数
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 5

# qq发送邮件
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # 确保你使用的是smtp
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = '964961377@qq.com'  # 你的 QQ 账号
EMAIL_HOST_PASSWORD = 'qlhevwlfvngmbehe' # 刚刚复制的授权码（不是你的 QQ 密码！！！）
EMAIL_USE_TLS = True  # 这里必须是 True，否则发送不成功
EMAIL_FROM = '博客<964961377@qq.com>' # 收件人看到的发件人(<必须与上面的qq邮箱一致>)

# django的缓存配置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
# 配置session存储
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# login_required装饰器设置相关，配置登录url地址
LOGIN_URL = "/user/login/"