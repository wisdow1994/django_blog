from django.shortcuts import render, redirect, reverse, HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import hashlib

from .models import Comment, Article, User
from .forms import (RegisterForm, LoginForm, ChangePasswordForm, ChangeEmailForm, PasswordResetForm,
                    PasswordResetRequestForm, EditProfileAdminForm, EditProfileForm, ArticleForm,
                    CommentForm)
from .EMAIL import send_html_mail


def global_settings(request):
    return {
        'NAME': 'Django',
    }


@login_required
def follow(request, username):
    follow_user = User.objects.get(username=username)
    if follow_user is None:
        messages.info(request, '用户不存在')
        return redirect(reverse('index'))
    if request.user.is_following(follow_user):
        messages.info(request, '你已经关注了该用户')
        return redirect(reverse('user', args=[username]))
    request.user.follow(follow_user)
    messages.success(request, '成功关注了该用户')
    return redirect(reverse('user', args=[username]))


@login_required
def unfollow(request, username):
    user = User.objects.get(username=username)
    if user is None:
        messages.info(request, '用户不存在')
        return redirect(reverse('index'))
    if not request.user.is_following(user):
        messages.info(request, '你已经取消关注该用户')
        return redirect(reverse('user', args=[username]))
    request.user.unfollow(user)
    messages.success(request, '取消关注了该用户')
    return redirect(reverse('user', args=[username]))


def followers(request, username):  # 显示this_user的粉丝列表的页面
    this_user = User.objects.get(username=username)
    print(type(this_user))
    if this_user is None:
        messages.error(request, '该用户不存在!')
        return redirect(reverse('index'))
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in this_user.follower_set.all()]
    return render(request, 'follow.html', {'follows': follows, 'user': this_user, 'title': '粉丝的列表'})


def followeds(request, username):  # this_user关注的列表
    this_user = User.objects.get(username=username)
    if this_user is None:
        messages.error(request, '该用户不存在!')
        return redirect(reverse('index'))
    # follows = this_user.followed_set.all()  # 返回的Follow对象,而且不能通用
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in this_user.followed_set.all()]
    return render(request, 'follow.html', {'follows': follows, 'user': this_user, 'title': '关注的列表'})


def index(request):
    show_followed = False  # 根据cookies,来决定显示all还是followed_articles
    if request.user.is_authenticated:
        show_followed = bool(request.COOKIES.get('show_followed', ''))
    if show_followed:
        article_list = request.user.followed_articles()
    else:
        article_list = Article.objects.all()
    # pagination = Paginator(article_list, 10)
    # posts = pagination.page(num)
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            Article.objects.create(content=form.cleaned_data['content'], user=request.user)
            return redirect(reverse('index'))
    return render(request, 'index.html', {'form': ArticleForm(), 'article_list': article_list,
                                          'show_followed': show_followed})


@login_required
def show_all(request):
    resp = HttpResponseRedirect(reverse('index'))
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
    print(request.COOKIES.get('show_followed'))
    return resp


@login_required
def show_followed(request):
    resp = HttpResponseRedirect(reverse('index'))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    print(request.COOKIES.get('show_followed'))
    return resp


def post(request, id):
    posts = Article.objects.get(pk=int(id))
    comments = posts.comment_set.all()
    # 只有一个对象,但是在_post文件中需要对内容进行迭代
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(content=form.cleaned_data['content'], user=request.user, article=posts)
        return redirect(reverse('post', args=[posts.id]))
    return render(request, 'post.html', {'article_list': [posts], 'form': CommentForm(), 'comments': comments})


def edit_post(request, id):
    post = Article.objects.get(pk=int(id))
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=post)
        form.save()
        return redirect(reverse('post', args=[post.id]))
    return render(request, 'edit_post.html', {'form': ArticleForm(instance=post)})


def user(request, username):
    user = User.objects.get(username=username)
    article_list = user.article_set.all()
    return render(request, 'user.html', {'user': user, 'article_list': article_list})


def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()  # instance可以让user实例和这个绑定起来,比flask方便许多
            messages.success(request, '资料修改成功!')
            return redirect(reverse('user', args=[request.user.username]))
    else:
        # 使用instance从数据库取出数据,成为表单的默认填充值
        return render(request, 'edit_profile.html', {'form': EditProfileForm(instance=request.user)})


def edit_profile_admin(request, username):
    user = User.objects.get(username=username)
    if request.method == 'POST':
        form = EditProfileAdminForm(request.POST, instance=user)
        if form.is_valid():
            form.save()  # instance可以让user实例和这个绑定起来,比flask方便许多
            messages.success(request, '资料修改成功!')
            # 参数要是args=[]的形式,没有flask中的url_for方便
            return redirect(reverse('user', args=[user.username, ]))
    else:
        # 使用instance从数据库取出数据,成为表单的默认填充值
        return render(request, 'edit_profile.html', {'form': EditProfileAdminForm(instance=user)})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            # Form的密码字段分别是password1和password2,最少浪费了我8小时
            email = form.cleaned_data.get('email')
            user = User.objects.create_user(username=username, email=email, password=password)
            user.avatar_hash = hashlib.md5(email.encode('utf-8')).hexdigest()
            user.save()  # User模型暂时不会使用构造函数,那么只能在视图中生成邮箱hash
            if user.email == settings.EMAIL_HOST_USER:
                user.is_superuser = True  # 超级管理员
                user.is_staff = True  # 访问admin
                user.save()
            # 用户模型必须使用create_user来创建才行
            # 一个大坑,浪费了我一小时的时间,他妈的
            login(request, user)
            token = user.generate_confirmation_token()  # 生成安全令牌
            send_html_mail('mail/confirm.html', [user.email], token=token)
            # 邮箱是一个列表
            messages.info(request, '一封含有激活令牌的邮箱发送给您,先激活才能登陆哦!')
            return redirect(reverse('auth:login'))
        else:
            return render(request, 'auth/register.html', {'form': form})
    else:
        return render(request, 'auth/register.html', {'form': RegisterForm()})


def auth_login(request):  # 防止函数重名
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            request_user = authenticate(username=username, password=password)
            if request_user is not None:
                # request_user.backend = 'django.contrib.auth.backends.ModelBackend'  # 指定默认的登录验证方式
                # 已经在settings中指定了
                login(request, request_user)
                messages.success(request, '登陆成功!')
                return redirect(reverse('index'))
        messages.info(request, '密码或用户名错误!')
        return render(request, 'auth/login.html', {'form': form})
    else:
        return render(request, 'auth/login.html', {'form': LoginForm()})


@login_required
def auth_logout(request):
    logout(request)
    messages.info(request, '你已经退出登陆!')
    return redirect(reverse('auth:login'))


@login_required
def confirmed_user(request, token):
    if request.user.confirm_bool:
        messages.success(request, '早已经激活了！')
        return redirect(reverse('index'))
    if request.user.confirm(token=token):
        messages.success(request, '令牌已经激活,您可以访问所有页面了！')
        return redirect(reverse('index'))
    messages.error(request, '安全令牌无效或者过期,请重新获取邮箱吧!')
    return redirect(reverse('auth:unconfirmed'))


@login_required
def unconfirmed(request):
    if request.user.is_anonymous or request.user.confirm_bool:
        messages.info(request, '你已经激活了令牌,不需要访问')
        return redirect(reverse('index'))
    return render(request, 'mail/unconfirmed.html')


@login_required
def resend_confirmed(request):
    token = request.user.generate_confirmation_token()  # 生成安全令牌
    send_html_mail('mail/confirm.html', [request.user.email], token=token)
    messages.success(request, '给你重新发送了一封含有安全令牌的邮件')
    return redirect(reverse('index'))


@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            if request.user.check_password(form.cleaned_data['old_password']):
                request.user.set_password(form.cleaned_data['password2'])
                messages.success(request, '密码修改成功!')
                return redirect(reverse('index'))
            else:
                messages.error(request, '原密码不正确')
                return render(request, 'auth/change_password.html', {'form': ChangePasswordForm()})
        else:
            return render(request, 'auth/change_password.html', {'form': form})
    else:
        return render(request, 'auth/change_password.html', {'form': ChangePasswordForm()})


@login_required
def change_email_request(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            if request.user.check_password(form.cleaned_data['password']):
                new_email = form.cleaned_data['email']
                token = request.user.generate_email_change_token(new_email=new_email)  # 生成安全令牌
                send_html_mail('mail/confirm_email.html', [new_email], token=token)
                messages.success(request, '给你发送了一封用于更换邮箱的邮件')
                return redirect(reverse('index'))
            else:
                return render(request, 'auth/change_email.html', {'form': form})
    else:
        return render(request, 'auth/change_email.html', {'form': ChangeEmailForm()})


@login_required
def change_email(request, token):
    if request.user.change_email(token=token):
        messages.success(request, '邮箱修改成功！')
        return redirect(reverse('index'))
    messages.error(request, '安全令牌无效或者过期,请重新获取邮箱吧!')
    return redirect(reverse('auth:change_email_request'))


def reset_password_request(request):
    if request.user.is_authenticated:
        return redirect(reverse('index'))
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            request_user = User.objects.get(email=form.cleaned_data['email'])
            token = request_user.generate_reset_token()
            send_html_mail('mail/reset_password.html', [request_user.email], token=token)
            messages.success(request, '给你重新发送了一封用来重置密码的邮件')
            return redirect(reverse('index'))
        else:
            return render(request, 'auth/reset_password.html', {'form': form})
    else:
        return render(request, 'auth/reset_password.html', {'form': PasswordResetRequestForm()})


def reset_password(request, token):
    if request.user.is_authenticated:
        return redirect(reverse('index'))
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            request_user = User.objects.get(email=form.cleaned_data['email'])
            if request_user.reset_password(token=token, new_password=form.cleaned_data['password2']):
                messages.success(request, '你的密码重置成功!')
                return redirect(reverse('auth:login'))
        else:
            return render(request, 'auth/reset_password.html', {'form': form})
    else:
        return render(request, 'auth/reset_password.html', {'form': PasswordResetForm()})
