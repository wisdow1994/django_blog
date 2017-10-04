from django import template
# from app.models import User
register = template.Library()


@register.filter
def avatar(value, args):  # DTL中不能使用带参数的方法,注册一个过滤器,变相完成
    # 又是一个小坑,过滤器的func名也是不能喝函数体内的函数重名的
    # user = user.objects.get(username=value)
    return value.generate_avatar(int(args))


@register.filter
def is_following(value, args):
    return value.is_following(args)  # 返回布尔值




