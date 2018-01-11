from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from snc.urls import *
from api import views

urlpatterns = [
    url(r'^$',views.swagger_index, name='swagger-index'),

    url(r'^v1/sistemadeculturalocal/$', views.MunicipioList.as_view(), name='municipio-list'),
    url(r'^v1/sistemadeculturalocal/(?P<pk>[0-9]+)/$', views.MunicipioDetail.as_view(), name='municipio-detail'),

    
    url(r'^v1/acoesplanotrabalho/$', views.PlanoTrabalhoList.as_view(), name='planotrabalho-list'),
    url(r'^v1/acoesplanotrabalho/(?P<pk>[0-9]+)/$', views.PlanoTrabalhoDetail.as_view(), name='planotrabalho-detail'),

]

urlpatterns = format_suffix_patterns(urlpatterns)
