from django import forms
from django.forms import ValidationError
from .models import User, Comment, Article


class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': '请输入用户名', 'required': 'required', 'size': '30'}),
        label='用户昵称', error_messages={'required': '用户名不能为空'})

    email = forms.EmailField(
        max_length=30,
        label='电子邮箱', widget=forms.EmailInput(attrs={'placeholder': '请输入邮箱', 'size': '30'}))

    password1 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={'placeholder': '请输入密码', 'required': 'required', 'size': '30'}),
        label='密码', error_messages={'required': '密码不能为空'})

    password2 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={'placeholder': '请确认密码', 'required': 'required', 'size': '30'}),
        label='确认密码', error_messages={'required': '密码不能为空'})

    def clean(self):
        super(RegisterForm, self).clean()
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=username).first():
            raise ValidationError('此用户名已被注册!')
        if User.objects.filter(email=email).first():
            raise ValidationError('此邮箱已经被注册!')
        return self.cleaned_data

    def clean_password2(self):  # 验证两次密码是否相等
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError('两次输入的密码不一致!')
        return password2


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': '请输入用户名', 'required': 'required', 'size': '30'}),
        label='用户昵称', error_messages={'required': '用户名不能为空'})
    password = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={'placeholder': '请输入密码', 'required': 'required', 'size': '30'}),
        label='密码', error_messages={'required': '密码不能为空'})


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={'placeholder': '请输入旧密码', 'required': 'required', 'size': '30'}),
        label='旧密码', error_messages={'required': '密码不能为空'})

    password1 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={'placeholder': '请输入新密码', 'required': 'required', 'size': '30'}),
        label='新密码', error_messages={'required': '密码不能为空'})

    password2 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={'placeholder': '请确认新密码', 'required': 'required', 'size': '30'}),
        label='确认密码', error_messages={'required': '密码不能为空'})

    def clean_password2(self):  # 验证两次密码是否相等
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise ValidationError('两次输入的密码不一致!')
        return password2


class ChangeEmailForm(forms.Form):
    email = forms.EmailField(
        max_length=30,
        label='新的电子邮箱', widget=forms.EmailInput(attrs={'placeholder': '请新的邮箱地址', 'size': '30'}))

    password = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={'placeholder': '请输入密码', 'required': 'required', 'size': '30'}),
        label='密码', error_messages={'required': '密码不能为空'})

    def clean(self):
        super(ChangeEmailForm, self).clean()
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).first():
            raise ValidationError('此邮箱已经被注册!')
        return self.cleaned_data


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        max_length=30,
        label='新的电子邮箱', widget=forms.EmailInput(attrs={'placeholder': '请新的邮箱地址', 'size': '30'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).first():
            # get查询不到数据,会报DoesNotExist
            raise ValidationError('此用户不存在!')
        # return self.cleaned_data 这种写法是错误的,会返回一个字典
        return email


class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        max_length=30,
        label='电子邮箱', widget=forms.EmailInput(attrs={'placeholder': '请输入邮箱', 'size': '30'}))

    password1 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={'placeholder': '请输入密码', 'required': 'required', 'size': '30'}),
        label='密码', error_messages={'required': '密码不能为空'})

    password2 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={'placeholder': '请确认密码', 'required': 'required', 'size': '30'}),
        label='确认密码', error_messages={'required': '密码不能为空'})

    def clean_password2(self):  # 验证两次密码是否相等
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError('两次输入的密码不一致!')
        return password2


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['real_name', 'location', 'about_me']


class EditProfileAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['real_name', 'location', 'about_me', 'email', 'username', 'confirm_bool']


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['content', ]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', ]
