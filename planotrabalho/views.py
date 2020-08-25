import json

from django.shortcuts import redirect
from django.http import Http404, HttpResponseRedirect, request
from django.http import HttpResponse
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic import ListView
from django.views.generic import DetailView
from django.urls import reverse_lazy

from .models import PlanoTrabalho
from .models import CriacaoSistema
from .models import OrgaoGestor2
from .models import Conselheiro
from .models import ConselhoCultural
from .models import FundoCultura
from .models import FundoDeCultura
from .models import PlanoCultura
from .models import PlanoDeCultura
from .models import Componente
from .models import ConselhoDeCultura
from adesao.models import SistemaCultura

from .forms import CriarComponenteForm
from .forms import CriarFundoForm
from .forms import CriarPlanoForm
from .forms import CriarConselhoForm
from .forms import DesabilitarConselheiroForm
from .forms import CriarConselheiroForm
from .forms import AlterarConselheiroForm
from .forms import CriarOrgaoGestorForm

from adesao.utils import atualiza_session


class PlanoTrabalho(DetailView):
    model = SistemaCultura
    template_name = 'planotrabalho/plano_trabalho.html'

    def get_context_data(self, **kwargs):
        try:
            context = super(PlanoTrabalho, self).get_context_data(**kwargs)
            sistema_id = self.request.session['sistema_cultura_selecionado']['id']
            context['sistema'] = SistemaCultura.objects.get(id=sistema_id)
        except:
            return context
        return context


class CadastrarComponente(CreateView):
    model = Componente
    form_class = CriarComponenteForm

    def get_form_kwargs(self):
        kwargs = super(CadastrarComponente, self).get_form_kwargs()
        sistema_id = self.request.session['sistema_cultura_selecionado']['id']
        self.sistema = SistemaCultura.objects.get(id=sistema_id)
        kwargs['sistema'] = self.sistema
        kwargs['logged_user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('planotrabalho:planotrabalho', kwargs={'pk': self.sistema.id})

    def form_valid(self, form):
        super(CadastrarComponente, self).form_valid(form)
        sistema_atualizado = SistemaCultura.sistema.get(ente_federado__id=self.sistema.ente_federado.id)
        atualiza_session(sistema_atualizado, self.request)
        return redirect(reverse_lazy('planotrabalho:planotrabalho', kwargs={'pk': self.sistema.id}))


class CadastrarLegislacao(CadastrarComponente):
    template_name = 'planotrabalho/cadastrar_legislacao.html'

    def get_form_kwargs(self):
        kwargs = super(CadastrarLegislacao, self).get_form_kwargs()
        kwargs['tipo'] = 'legislacao'

        return kwargs


class CadastrarPlanoDeCultura(CadastrarComponente):
    model = PlanoDeCultura
    form_class = CriarPlanoForm
    template_name = 'planotrabalho/cadastrar_plano.html'


class CadastrarOrgaoGestor(CadastrarComponente):
    model = OrgaoGestor2
    form_class = CriarOrgaoGestorForm
    template_name = 'planotrabalho/cadastrar_orgao.html'

    def get_form_kwargs(self):
        kwargs = super(CadastrarOrgaoGestor, self).get_form_kwargs()
        kwargs['tipo'] = 'orgao_gestor'

        return kwargs

    def form_valid(self, form):
        obj=super().form_valid(form)

        return HttpResponseRedirect('/adesao/home/')



class CadastrarFundoDeCultura(CadastrarComponente):
    model = FundoDeCultura
    form_class = CriarFundoForm
    template_name = 'planotrabalho/cadastrar_fundo.html'

    def get_context_data(self, **kwargs):
        context = super(CadastrarFundoDeCultura, self).get_context_data(**kwargs)
        context['is_edit'] = False
        return context


class CadastrarConselhoDeCultura(CadastrarComponente):
    model = ConselhoDeCultura
    form_class = CriarConselhoForm
    template_name = 'planotrabalho/cadastrar_conselho.html'


class AlterarLegislacao(UpdateView):
    model = Componente
    form_class = CriarComponenteForm
    template_name = 'planotrabalho/cadastrar_legislacao.html'

    def get_form_kwargs(self):
        kwargs = super(AlterarLegislacao, self).get_form_kwargs()
        sistema_id = self.request.session['sistema_cultura_selecionado']['id']
        self.sistema = SistemaCultura.objects.get(id=sistema_id)
        kwargs['tipo'] = 'legislacao'
        kwargs['sistema'] = self.sistema
        kwargs['logged_user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AlterarLegislacao, self).get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def get_success_url(self):
        return reverse_lazy('planotrabalho:planotrabalho', kwargs={'pk': self.sistema.id})


class AlterarPlanoCultura(UpdateView):
    model = PlanoDeCultura
    form_class = CriarPlanoForm
    template_name = 'planotrabalho/cadastrar_plano.html'

    def get_form_kwargs(self):
        kwargs = super(AlterarPlanoCultura, self).get_form_kwargs()
        sistema_id = self.object.plano.last().id
        self.sistema = SistemaCultura.objects.get(id=sistema_id)
        kwargs['sistema'] = self.sistema
        kwargs['logged_user'] = self.request.user

        kwargs['initial']['local_monitoramento'] = self.object.local_monitoramento
        kwargs['initial']['ano_inicio_curso'] = self.object.ano_inicio_curso
        kwargs['initial']['ano_termino_curso'] = self.object.ano_termino_curso
        kwargs['initial']['esfera_federacao_curso'] = self.object.esfera_federacao_curso
        kwargs['initial']['tipo_oficina'] = self.object.tipo_oficina
        kwargs['initial']['perfil_participante'] = self.object.perfil_participante
        kwargs['initial']['anexo_na_lei'] = self.object.anexo_na_lei
        kwargs['initial']['metas_na_lei'] = self.object.metas_na_lei

        if self.object.anexo_na_lei:
            kwargs['initial']['possui_anexo'] = True
        elif not self.object.anexo_na_lei and self.object.anexo and self.object.anexo.arquivo:
            kwargs['initial']['possui_anexo'] = True
            kwargs['initial']['anexo_lei'] = self.object.anexo.arquivo
        else:
            kwargs['initial']['possui_anexo'] = False

        if self.object.metas_na_lei:
            kwargs['initial']['possui_metas'] = True
        elif not self.object.metas_na_lei and self.object.metas and self.object.metas.arquivo:
            kwargs['initial']['possui_metas'] = True
            kwargs['initial']['arquivo_metas'] = self.object.metas.arquivo
        else:
            kwargs['initial']['possui_metas'] = False

        if self.object.local_monitoramento:
            kwargs['initial']['monitorado'] = True
        else:
            kwargs['initial']['monitorado'] = False

        if self.object.ano_inicio_curso:
            kwargs['initial']['participou_curso'] = True
        else:
            kwargs['initial']['participou_curso'] = False

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AlterarPlanoCultura, self).get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def get_success_url(self):
        return reverse_lazy('planotrabalho:planotrabalho', kwargs={'pk': self.sistema.id})


class AlterarOrgaoGestor(UpdateView):
    model = OrgaoGestor2
    form_class = CriarOrgaoGestorForm
    template_name = 'planotrabalho/cadastrar_orgao.html'

    def get_form_kwargs(self):
        kwargs = super(AlterarOrgaoGestor, self).get_form_kwargs()
        sistema_id = self.object.orgao_gestor.last().id
        self.sistema = SistemaCultura.objects.get(id=sistema_id)
        kwargs['tipo'] = 'orgao_gestor'
        kwargs['sistema'] = self.sistema
        kwargs['logged_user'] = self.request.user

        if self.sistema.orgao_gestor and self.sistema.orgao_gestor.perfil:
            kwargs['initial']['perfil'] = self.sistema.orgao_gestor.perfil

        if self.object.comprovante_cnpj is None:
            kwargs['initial']['possui_cnpj'] = False
        else:
            kwargs['initial']['possui_cnpj'] = True
            kwargs['initial']['comprovante_cnpj'] = self.object.comprovante_cnpj.arquivo
            kwargs['initial']['cnpj'] = self.sistema.orgao_gestor.cnpj
            kwargs['initial']['banco'] = self.sistema.orgao_gestor.banco
            kwargs['initial']['agencia'] = self.sistema.orgao_gestor.agencia
            kwargs['initial']['conta'] = self.sistema.orgao_gestor.conta
            kwargs['initial']['termo_responsabilidade'] = True

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AlterarOrgaoGestor, self).get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def get_success_url(self):
        return reverse_lazy('planotrabalho:planotrabalho', kwargs={'pk': self.sistema.id})


class AlterarFundoCultura(UpdateView):
    model = FundoDeCultura
    form_class = CriarFundoForm
    template_name = 'planotrabalho/cadastrar_fundo.html'

    def get_form_kwargs(self):
        kwargs = super(AlterarFundoCultura, self).get_form_kwargs()
        sistema_id = self.object.fundo_cultura.last().id
        self.sistema = SistemaCultura.objects.get(id=sistema_id)
        kwargs['sistema'] = self.sistema
        kwargs['logged_user'] = self.request.user

        if self.sistema.legislacao and self.sistema.legislacao.arquivo == self.object.arquivo:
            kwargs['initial']['mesma_lei'] = True
        else:
            kwargs['initial']['mesma_lei'] = False

        if self.object.comprovante_cnpj is None:
            kwargs['initial']['possui_cnpj'] = False
        else:
            kwargs['initial']['possui_cnpj'] = True
            kwargs['initial']['comprovante'] = self.object.comprovante_cnpj.arquivo
            kwargs['initial']['banco'] = self.object.banco
            kwargs['initial']['agencia'] = self.object.agencia
            kwargs['initial']['conta'] = self.object.conta
            kwargs['initial']['termo_responsabilidade'] = True
            
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AlterarFundoCultura, self).get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def get_success_url(self):
        return reverse_lazy('planotrabalho:planotrabalho', kwargs={'pk': self.sistema.id})


class AlterarConselhoCultura(UpdateView):
    model = ConselhoDeCultura
    form_class = CriarConselhoForm
    template_name = 'planotrabalho/cadastrar_conselho.html'

    def get_form_kwargs(self):
        kwargs = super(AlterarConselhoCultura, self).get_form_kwargs()
        sistema_id = self.object.conselho.first().id
        self.sistema = SistemaCultura.objects.get(id=sistema_id)
        kwargs['sistema'] = self.sistema
        kwargs['logged_user'] = self.request.user

        if self.object.lei:
            kwargs['initial']['arquivo_lei'] = self.object.lei.arquivo
            kwargs['initial']['data_publicacao_lei'] = self.object.lei.data_publicacao

            if self.sistema.legislacao and self.sistema.legislacao.arquivo == self.object.lei.arquivo:
                kwargs['initial']['mesma_lei'] = True
            else:
                kwargs['initial']['mesma_lei'] = False

        if self.object.arquivo:
            kwargs['initial']['possui_ata'] = True
        else:
            kwargs['initial']['possui_ata'] = False

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AlterarConselhoCultura, self).get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def get_success_url(self):
        return reverse_lazy('planotrabalho:planotrabalho', kwargs={'pk': self.sistema.id})


class CriarConselheiro(CreateView):
    form_class = CriarConselheiroForm
    template_name = 'planotrabalho/cadastrar_conselheiros.html'

    def get_form_kwargs(self):
        kwargs = super(CriarConselheiro, self).get_form_kwargs()
        kwargs['conselho'] = self.request.session['sistema_cultura_selecionado']['conselho']
        return kwargs

    def get_success_url(self):
        return reverse_lazy('planotrabalho:listar_conselheiros')


class ListarConselheiros(ListView):
    model = Conselheiro
    template_name = 'planotrabalho/listar_conselheiros.html'
    paginate_by = 12

    def get_queryset(self):
        q = self.request.session['sistema_cultura_selecionado']['conselho']
        conselheiros = Conselheiro.objects.filter(conselho__id=q, situacao=1)  # 1 = Habilitado

        return conselheiros


class AlterarConselheiro(UpdateView):
    form_class = AlterarConselheiroForm
    template_name = 'planotrabalho/cadastrar_conselheiros.html'

    def get_queryset(self):
        pk = self.kwargs['pk']
        conselheiro = Conselheiro.objects.filter(id=pk)

        return conselheiro

    def get_success_url(self):
        return reverse_lazy('planotrabalho:listar_conselheiros')


class DesabilitarConselheiro(UpdateView):
    form_class = DesabilitarConselheiroForm
    template_name = 'planotrabalho/desabilitar_conselheiro.html'

    def get_queryset(self):
        pk = self.kwargs['pk']
        conselheiro = Conselheiro.objects.filter(id=pk)

        return conselheiro

    def get_success_url(self):
        return reverse_lazy('planotrabalho:listar_conselheiros')


def get_conselheiros(request):
    if request.is_ajax() and request.GET.get('id', None):
        pk = request.GET.get('id')
        conselheiros = Conselheiro.objects.filter(conselho__pk=pk)
        response = {}
        response['conselheiros'] = list(conselheiros.values_list('nome', 'email', 'segmento'))
        return HttpResponse(
            json.dumps(response),
            content_type="application/json")
    else:
        return Http404()
