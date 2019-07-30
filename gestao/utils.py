from threading import Thread

from django.core.mail import send_mail
from django.template.loader import render_to_string
from adesao.models import UFS


def enviar_email_alteracao_situacao(usuario, historico=None):
    if usuario.estado_processo == '2':
        message_txt = render_to_string(
            'emails/documentacao_recebida.txt', {'usuario': usuario})
        message_html = render_to_string(
            'emails/documentacao_recebida.html', {'usuario': usuario})
        subject = 'Sistema Nacional de Cultura - Documentação Recebida'
    elif usuario.estado_processo == '3':
        message_txt = render_to_string(
            'emails/aviso_pendencia.txt',
            {'usuario': usuario, 'historico': historico})
        message_html = render_to_string(
            'emails/aviso_pendencia.html',
            {'usuario': usuario, 'historico': historico})
        subject = 'Sistema Nacional de Cultura - Aviso de Pendência'
    elif usuario.estado_processo == '6':
        message_txt = render_to_string(
            'emails/acordo_publicado.txt', {'usuario': usuario})
        message_html = render_to_string(
            'emails/acordo_publicado.html', {'usuario': usuario})
        subject = 'Sistema Nacional de Cultura - Acordo Publicado'
    else:
        return

    Thread(target=send_mail, args=(
        subject,
        message_txt,
        'naoresponda@cultura.gov.br',
        [usuario.user.email],),
        kwargs={'fail_silently': 'False', 'html_message': message_html}
    ).start()


def enviar_email_aprovacao_plano(user, message_txt, message_html):
    Thread(target=send_mail, args=(
        'Sistema Nacional de Cultura - Aprovação do Plano de Trabalho',
        message_txt,
        'naoresponda@cultura.gov.br',
        [user.email],),
        kwargs={'fail_silently': 'False', 'html_message': message_html}
        ).start()


def empty_to_none(value):
    if not value:
        return None
    return value


def get_uf_by_mun_cod(municipio_cod):
    return UFS[int((str(municipio_cod))[:2])]


def scdc_user_group_required(user):
    if user:
        return not user.groups.filter(name='usuario_scdc').count() == 0
    return True