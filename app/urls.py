from django.conf.urls import url

from . import views

app_name = 'auth'  # 相当于flask中二级路由的命名空间
urlpatterns = [
    url(r'register/$', views.register, name='register'),
    url(r'login/$', views.auth_login, name='login'),
    url(r'logout/$', views.auth_logout, name='logout'),

    url(r'resend_confirmed/$', views.resend_confirmed, name='resend_confirmed'),
    url(r'unconfirmed/$', views.unconfirmed, name='unconfirmed'),
    url(r'^confirm/(?P<token>\w+.[-_\w]*\w+.[-_\w]*\w+)/$', views.confirmed_user, name='confirm'),

    url(r'change_password', views.change_password, name='change_password'),

    url(r'reset_password_request/', views.reset_password_request, name='reset_password_request'),
    url(r'reset_password/(?P<token>\w+.[-_\w]*\w+.[-_\w]*\w+)/$', views.reset_password, name='reset_password'),

    url(r'change_email_request/$', views.change_email_request, name='change_email_request'),
    url(r'change_email/(?P<token>\w+.[-_\w]*\w+.[-_\w]*\w+)', views.change_email, name='change_email'),

]