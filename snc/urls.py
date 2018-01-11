"""snc URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url, static
from django.contrib import admin
from django.conf import settings

from adesao import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^adesao/', include('adesao.urls', namespace="adesao")),
    url(r'^planotrabalho/',
        include('planotrabalho.urls', namespace="planotrabalho")),
    url(r'^gestao/', include('gestao.urls', namespace="gestao")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^chaining/', include('smart_selects.urls')),

    url(r'^password_reset/$',
        'django.contrib.auth.views.password_reset',
        {'template_name': 'registration/password_reset_form.html'},
        name='password_reset'),
    url(r'^password_reset_done/$',
        'django.contrib.auth.views.password_reset_done',
        {'template_name': 'registration/password_reset_done.html'},
        name='password_reset_done'),
    url(r'^password_reset_confirm/' +
        '(?P<uidb64>[0-9A-Za-z_\-]+)/' +
        '(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'template_name': 'registration/password_reset_confirm.html'},
        name='password_reset_confirm'),
    url(r'^password_reset_complete/$',
        'django.contrib.auth.views.password_reset_complete',
        {'template_name': 'registration/password_reset_complete.html'},
        name='password_reset_complete'),

    url(r'^mudar_senha/$',
        'django.contrib.auth.views.password_change',
        {'template_name': 'registration/mudar_senha.html'},
        name='mudar_senha'),
    url(r'^mudar_senha_sucesso/$',
        'django.contrib.auth.views.password_change_done',
        {'template_name': 'registration/mudar_senha_concluido.html'},
        name='password_change_done'),
    url(r'^mudar_senha_gestao/$',
        'django.contrib.auth.views.password_change',
        {'template_name': 'registration/mudar_senha_gestao.html',
         'post_change_redirect': 'password_change_done_gestao'},
        name='mudar_senha_gestao'),
    url(r'^mudar_senha_gestao_sucesso/$',
        'django.contrib.auth.views.password_change_done',
        {'template_name': 'registration/mudar_senha_gestao_concluido.html'},
        name='password_change_done_gestao'),

    url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^exportar/dados.csv', views.exportar_csv, name='exportar_csv'),
    url(r'^exportar/dados.ods', views.exportar_ods, name='exportar_ods'),
    url(r'^exportar/dados.xls', views.exportar_xls, name='exportar_xls'),

    # API URLS
    url(r'^api/', include('api.urls', namespace='api')),

    ] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
