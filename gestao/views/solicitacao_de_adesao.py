from django_datatables_view.base_datatable_view import BaseDatatableView
from django.views.generic import DetailView, TemplateView
from django.utils.html import escape
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from templated_email import send_templated_mail

from django.http import HttpResponse, HttpResponseRedirect
from gestao.views.views import LookUpAnotherFieldMixin
from adesao.models import SolicitacaoDeAdesao, SistemaCultura, Usuario
from gestao.views.solicitacao import BaseDataTableSolicitacao

class DataTableSolicitacaoDeAdesao(BaseDataTableSolicitacao):

    def get_initial_queryset(self):
        return SolicitacaoDeAdesao.objects.all()

class DetalharSolicitacao(DetailView, LookUpAnotherFieldMixin):
    model = SolicitacaoDeAdesao
    template_name = "solicitacaodeadesao_detail.html"

def processar_solicitacao(request, pk, status_solicitacao, status_sistema, email_template):
    solicitacao = SolicitacaoDeAdesao.objects.get(pk=pk)
    solicitacao.avaliador = Usuario.objects.get(user__pk=request.user.id) 
    solicitacao.data_analise = timezone.now()
    solicitacao.status = status_solicitacao
    solicitacao.save()
    '''
    sc = SistemaCultura.sistema.get(ente_federado__cod_ibge=solicitacao.ente_federado.cod_ibge)
    sc.estado_processo = status_sistema
    sc.save()
    '''
    send_templated_mail(
        template_name=email_template,
        from_email='naoresponda@turismo.gov.br',
        recipient_list=[solicitacao.alterado_por.user.email],
        context={
            'cadastrador':solicitacao.alterado_por.nome_usuario,
            'ente_federado':solicitacao.ente_federado.nome,
            'motivo':request.POST.get('justificativa'),
        },)

    return solicitacao

def aprovar_solicitacao(request, pk):
    processar_solicitacao(request, pk, '1', '6', 'adesao_aprovada')
    
    return HttpResponseRedirect(reverse('gestao:solicitacao_de_adesao:list'))


def rejeitar_solicitacao(request, pk):
    solicitacao = processar_solicitacao(request, pk, '2', '1', 'adesao_reprovada')
    solicitacao.laudo = request.POST['justificativa']
    solicitacao.save()
    
    return HttpResponseRedirect(reverse('gestao:solicitacao_de_adesao:list'))

class SolicitacaoDeAdesaoList(TemplateView):
    template_name = 'solicitacaodeadesao_list.html'

