from django.core.mail import EmailMessage
from django.template import loader
from django.conf import settings


def send_html_mail(template_path, recipient_list, token, form_email=settings.EMAIL_HOST_USER, subject='[Django]'):
    html_content = loader.render_to_string(
        template_path,  # 需要渲染的html模板
        {'token': token}  # 需要传给模板的参数
    )
    msg = EmailMessage(subject=subject, body=html_content, from_email=form_email, to=recipient_list)
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()
