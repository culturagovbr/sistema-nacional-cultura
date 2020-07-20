from django.conf.urls import url
from django.urls import path, re_path
from django.contrib.admin.views.decorators import staff_member_required

from gestao.views import views, solicitacao_de_adesao

app_name = 'solicitacao_de_adesao'

urlpatterns = [
    path('', 
        staff_member_required(solicitacao_de_adesao.SolicitacaoDeAdesaoList.as_view()), 
        name='list'),

    path('<int:pk>',
         staff_member_required(solicitacao_de_adesao.DetalharSolicitacao.as_view()),
         name='detalhar-solicitacao'),

    path('<int:pk>/aprovar/',
         staff_member_required(solicitacao_de_adesao.aprovar_solicitacao),
         name='aprovar'),
         
    path('<int:pk>/rejeitar/',
         staff_member_required(solicitacao_de_adesao.rejeitar_solicitacao),
         name='rejeitar'),
         
    url(r'^datatable-solicitacao-de-adesao$', staff_member_required(solicitacao_de_adesao.DataTableSolicitacaoDeAdesao.as_view()),
        name='ajax_list'),
]

