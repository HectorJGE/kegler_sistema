from django.conf import settings
from post_office import mail
from django.core.files.base import ContentFile


def send_email(asunto, recipientes, prioridad, con_template=None, contexto=None, template=None, mensaje=None,
                mensaje_html=None, archivos=None):

    if con_template:
        context = contexto
        html_message = template.render(context)

        email = mail.send(
            subject=asunto,
            html_message=html_message,
            sender=settings.DEFAULT_FROM_EMAIL,
            recipients=recipientes,
            priority=prioridad,
            attachments=archivos
        )
        print(email)
    else:
        if len(archivos) > 1:
            xml_name = archivos[1]['name']
            attachments = {
                archivos[0].name: archivos[0].file,
                # xml_name: {'content': archivos[1]['file'].file, 'mime_type': 'text/xml'},
                archivos[1]['name']: archivos[1]['file'].file,
            }
        else:
            attachments = {
                archivos[0]['name']: archivos[0]['file'].file,
            }
        email = mail.send(
            subject=asunto,
            message=mensaje,
            html_message=mensaje_html,
            sender=settings.DEFAULT_FROM_EMAIL,
            recipients=recipientes,
            priority=prioridad,
            attachments=attachments
        )
        print(email)
    if email.status == 1:
        raise Exception(email.logs.all().first().message)
    return email
