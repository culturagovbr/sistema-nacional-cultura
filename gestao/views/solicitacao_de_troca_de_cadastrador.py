from django_datatables_view.base_datatable_view import BaseDatatableView
from django.views.generic import DetailView, TemplateView
from django.utils.html import escape
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from templated_email import send_templated_mail

from django.http import HttpResponse, HttpResponseRedirect
from gestao.views.views import LookUpAnotherFieldMixin
from adesao.models import SolicitacaoDeTrocaDeCadastrador, SistemaCultura, Usuario

from gestao.views.solicitacao import BaseDataTableSolicitacao

class DataTableSolicitacaoDeTrocaDeCadastrador(BaseDataTableSolicitacao):

    def get_initial_queryset(self):
        return SolicitacaoDeTrocaDeCadastrador.objects.all()


class DetalharSolicitacao(DetailView, LookUpAnotherFieldMixin):
    model = SolicitacaoDeTrocaDeCadastrador
    template_name = "solicitacaodetrocadecadastrador_detail.html"

def processar_solicitacao(request, pk, status_solicitacao, email_template):
    solicitacao = SolicitacaoDeTrocaDeCadastrador.objects.get(pk=pk)
    solicitacao.avaliador = Usuario.objects.get(user__pk=request.user.id) 
    solicitacao.data_analise = timezone.now()
    solicitacao.status = status_solicitacao
    solicitacao.save()
    
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
    solicitacao = processar_solicitacao(request, pk, '1', 'solicitacaodetroca_aprovada')
    sc = SistemaCultura.sistema.get(ente_federado__cod_ibge=solicitacao.ente_federado.cod_ibge)
    sc.cadastrador = solicitacao.alterado_por
    sc.oficio_cadastrador = solicitacao.oficio
    sc.save()
    return HttpResponseRedirect(reverse('gestao:solicitacao_de_troca_de_cadastrador:list'))

def rejeitar_solicitacao(request, pk):
    solicitacao = processar_solicitacao(request, pk, '2', 'solicitacaodetroca_reprovada')
    solicitacao.laudo = request.POST['justificativa']
    solicitacao.save()

    return HttpResponseRedirect(reverse('gestao:solicitacao_de_troca_de_cadastrador:list'))


class SolicitacaoDeTrocaDeCadastradorList(TemplateView):
    template_name = 'solicitacaodetrocadecadastrador_list.html'