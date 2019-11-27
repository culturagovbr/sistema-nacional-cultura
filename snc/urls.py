from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings

from django.urls import include, path

from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetDoneView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetCompleteView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.views import PasswordChangeDoneView

from adesao import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^adesao/', include('adesao.urls', namespace="adesao")),

    url(r'^planotrabalho/',
        include('planotrabalho.urls', namespace="planotrabalho")),

    url(r'^gestao/', include('gestao.urls', namespace="gestao")),
    url(r'^admin/', admin.site.urls),

    url(r'^password_reset/$',
        PasswordResetView.as_view(),
        {'template_name': 'registration/password_reset_form.html'},
        name='password_reset'),

    url(r'^password_reset_done/$',
        PasswordResetDoneView.as_view(),
        {'template_name': 'registration/password_reset_done.html'},
        name='password_reset_done'),

    url(r'^password_reset_confirm/' +
        '(?P<uidb64>[0-9A-Za-z_\-]+)/' +
        '(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        PasswordResetConfirmView.as_view(),
        {'template_name': 'registration/password_reset_confirm.html'},
        name='password_reset_confirm'),

    url(r'^password_reset_complete/$',
        PasswordResetCompleteView.as_view(),
        {'template_name': 'registration/password_reset_complete.html'},
        name='password_reset_complete'),

    url(r'^mudar_senha/$',
        PasswordChangeView.as_view(),
        {'template_name': 'registration/mudar_senha.html'},
        name='mudar_senha'),

    url(r'^mudar_senha_sucesso/$',
        PasswordChangeDoneView.as_view(),
        {'template_name': 'registration/mudar_senha_concluido.html'},
        name='password_change_done'),

    url(r'^mudar_senha_gestao/$',
        PasswordChangeView.as_view(),
        {'template_name': 'registration/mudar_senha_gestao.html',
         'post_change_redirect': 'password_change_done_gestao'},
        name='mudar_senha_gestao'),

    url(r'^mudar_senha_gestao_sucesso/$',
        PasswordResetDoneView.as_view(),
        {'template_name': 'registration/mudar_senha_gestao_concluido.html'},
        name='password_change_done_gestao'),

    # url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^exportar/dados.csv', views.exportar_csv, name='exportar_csv'),
    url(r'^exportar/dados.ods', views.exportar_ods, name='exportar_ods'),
    url(r'^exportar/dados.xls', views.exportar_xls, name='exportar_xls'),

    # API URLS
    path('api/', include('apiv2.urls', namespace='api/')),

    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
