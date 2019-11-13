from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'api'

urlpatterns = [
    path('', views.swagger_index, name='swagger-index'),

    path('v2/sistemadeculturalocal/', views.SistemaCulturaAPIList.as_view(), name='sistemacultura-list'),
    path('v2/sistemadeculturalocal/<int:pk>/', views.SistemaCulturaDetail.as_view(), name='sistemacultura-detail'),

    path('v2/acoesplanotrabalho/', views.PlanoTrabalhoList.as_view(), name='planotrabalho-list'),
    path('v2/acoesplanotrabalho/<int:pk>/', views.PlanoTrabalhoDetail.as_view(), name='planotrabalho-detail'),

]

urlpatterns = format_suffix_patterns(urlpatterns)
