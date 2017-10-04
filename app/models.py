from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from tinymce.models import HTMLField
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import hashlib

# 用户模型.
# 第一种：采用的继承方式扩展用户信息（本系统采用）
# 扩展：关联的方式去扩展用户信息,一对一关联Django自带的User模型


class User(AbstractUser):
    confirm_bool = models.BooleanField(default=False)  # 记录用户确认令牌

    real_name = models.CharField(max_length=30, verbose_name='姓名', default='未填写')
    location = models.CharField(max_length=30, verbose_name='城市', default='未填写')
    about_me = models.TextField(verbose_name='关于我', default='未填写')

    member_since = models.DateField(auto_now_add=True, verbose_name='注册时间')
    # auto_now_add, 会在model对象第一次被创建时，将字段的值设置为创建时的时间，以后修改对象时，字段的值不会再更新
    last_seen = models.DateField(auto_now=True, verbose_name='最后访问时间')
    # auto_now, 能够在保存该字段时，将其值设置为当前时间，并且每次修改model，都会自动更新

    avatar_hash = models.CharField(max_length=64)  # 图像hash

    class Meta(AbstractUser.Meta):
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-id']  # id从高到低排序
        swappable = 'AUTH_USER_MODEL'  # 继承了AbstractUser的权限

    def generate_avatar(self, size=100, default='identicon', rating='g'):  # 后台生成图像的hash
        # if request.is_secure():
        #     url = 'https://secure.gravatar.com/avatar'
        # else:
        url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def generate_confirmation_token(self, expiration=3600):  # 生成用于激活账户的安全令牌
        s = Serializer(settings.SECRET_KEY, expires_in=expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):  # 账户确认,令牌符合时,更新当前用户confirm_bool
        s = Serializer(settings.SECRET_KEY)
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            # 除了检验令牌,检查令牌中的 id 是否和request中的user的已登录用户匹配
            return False
        self.confirm_bool = True
        self.save()
        return True

    def generate_reset_token(self, expiration=3600):  # 重置密码时使用的安全令牌
        s = Serializer(settings.SECRET_KEY, expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):  # 令牌通过,重置密码
        s = Serializer(settings.SECRET_KEY)
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.set_password(new_password)
        self.save()
        return True

    def generate_email_change_token(self, new_email, expiration=3600):  # 生成用于修改邮箱时使用的令牌
        s = Serializer(settings.SECRET_KEY, expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):  # 验证令牌
        s = Serializer(settings.SECRET_KEY)
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if User.objects.filter(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()  # 邮箱修改后,hash也需要重新计算
        self.save()
        return True

    def followed_articles(self):  # 属性函数,获取该用户关注的用户们的所有文章
        from django.db.models import Q
        followed = Follow.objects.filter(follower=self).values('followed')  # 粉丝为self的被关注者们
        articles = Article.objects.filter(Q(user__in=followed) | Q(user=self))
        # 狗书中,先添加一个关注自己的
        return articles

    @staticmethod
    def generate_fake(count=100):  # 生成虚拟数据,先不用管它的写法
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirm_bool=True,
                     real_name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            try:
                u.save()
            except Exception:
                pass

    def is_following(self, user):  # 是否关注了这个用户
        return self.followed_set.filter(followed_id=user.id).first() is not None

    def is_followed_by(self, user):  # 是否为我的粉丝
        return self.follower_set.filter(follower_id=user.id).first() is not None

    def follow(self, user):  # 关注用户
        if not self.is_following(user):  # 还没有关注这个用户
            Follow.objects.create(follower=self, followed=user)

    def unfollow(self, user):  # 取消关注
        f = self.followed_set.get(followed_id=user.id)
        if f:
            f.delete()

    def __repr__(self):
        return f'用户名:{self.username}'


class Follow(models.Model):
    timestamp = models.DateField(auto_now_add=True)
    follower = models.ForeignKey(User, related_name='followed_set', on_delete=models.CASCADE)
    # 一个粉丝--->关注了多个大神
    followed = models.ForeignKey(User, related_name='follower_set', on_delete=models.CASCADE)
    # 级联删除

    def __repr__(self):
        return f'followed:{self.followed}, follower:{self.follower}'


class Article(models.Model):  # 文章的模型
    # content = models.TextField(verbose_name='文章正文')
    content = HTMLField(verbose_name='文章正文')
    # click_count = models.IntegerField(default=0, verbose_name='点击次数')
    date_publish = models.DateField(auto_now_add=True, verbose_name='发布时间')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='用户', on_delete=models.CASCADE)

    # objects = ArticleManager()  # 替换默认的管理器

    @staticmethod
    def generate_fake(count=100):  # 生成虚拟数据,先不用管它的写法
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.objects.count()
        for i in range(count):
            u = User.objects.all()[(randint(0, user_count - 1))]
            p = Article(content=forgery_py.lorem_ipsum.sentences(randint(1, 5)), user=u)
            try:
                p.save()
            except Exception:
                pass

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        ordering = ['-date_publish']

    def __repr__(self):
        return f'正文:{self.content}'


class Comment(models.Model):  # 评论模型
    content = models.TextField(verbose_name='发表评论内容')
    date_publish = models.DateField(auto_now_add=True, verbose_name='发布时间')
    disabled = models.BooleanField(default=False, verbose_name='禁用状态')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='用户', on_delete=models.CASCADE)
    article = models.ForeignKey(Article, verbose_name='所属文章', on_delete=models.CASCADE)

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = verbose_name

    def __repr__(self):
        return f'{self.id}'
