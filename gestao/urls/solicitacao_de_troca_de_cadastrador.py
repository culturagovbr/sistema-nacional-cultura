from django.conf.urls import url
from django.urls import path, re_path
from django.contrib.admin.views.decorators import staff_member_required

from gestao.views import views, solicitacao_de_troca_de_cadastrador

app_name = 'solicitacao_de_troca_de_cadastrador'

urlpatterns = [
    path('', 
        staff_member_required(solicitacao_de_troca_de_cadastrador.SolicitacaoDeTrocaDeCadastradorList.as_view()), 
        name='list'),

    path('<int:pk>',
         staff_member_required(solicitacao_de_troca_de_cadastrador.DetalharSolicitacao.as_view()),
         name='detalhar-solicitacao'),

    path('<int:pk>/aprovar/',
         staff_member_required(solicitacao_de_troca_de_cadastrador.aprovar_solicitacao),
         name='aprovar'),
         
    path('<int:pk>/rejeitar/',
         staff_member_required(solicitacao_de_troca_de_cadastrador.rejeitar_solicitacao),
         name='rejeitar'),
         
    url(r'^datatable-solicitacao-de-troca-de-cadastrador$', staff_member_required(solicitacao_de_troca_de_cadastrador.DataTableSolicitacaoDeTrocaDeCadastrador.as_view()),
        name='ajax_list'),
]

