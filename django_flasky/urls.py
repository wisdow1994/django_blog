"""django_flasky URL Configuration

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
from django.conf.urls import url, include
from django.contrib import admin
from app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^tinymce/', include('tinymce.urls')),  # admin富文本支持


    url(r'^$', views.index, name='index'),
    url(r'^all/$', views.show_all, name='show_all'),  # 所有文章
    url(r'^show_followed/$', views.show_followed, name='show_followed'),  # user关注的followed_set们的文章

    url(r'^auth/', include('app.urls', namespace='app-auth')),

    url(r'post/(?P<id>\d+)/$', views.post, name='post'),  # 文章详情页

    url(r'edit/(?P<id>\d+)/$', views.edit_post, name='edit'),  # 修改文章

    url(r'follow/(?P<username>.*?)/$', views.follow, name='follow'),  # 关注用户
    url(r'unfollow/(?P<username>.*?)/$', views.unfollow, name='unfollow'),  # 取消关注

    url(r'followers/(?P<username>.*?)/$', views.followers, name='followers'),  # 粉丝数
    url(r'followeds/(?P<username>.*?)/$', views.followeds, name='followeds'),  # 关注的大神数量

    url(r'^user/(?P<username>.*?)/$', views.user, name='user'),
    url(r'^edit_profile/$', views.edit_profile, name='edit_profile'),
    url(r'edit_profile/(?P<username>[\u4e00-\u9fa5_a-zA-Z0-9]+)/', views.edit_profile_admin, name='edit_profile_admin'),
    # namespace='app-auth',这句代码不写也行,在user_app.urls中定义了一个app_name变量
    # Must specify a namespace if specifying app_name
    # 如果指定 app_name, 则必须指定namespace命名空间
    # 前半截是应用名,后半截类似于flask中的蓝图：二级路由的端点
]
