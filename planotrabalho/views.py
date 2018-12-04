import json


from django.shortcuts import redirect
from django.http import Http404
from django.http import HttpResponse
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic import ListView
from django.views.generic import DetailView
from django.urls import reverse_lazy

from .models import PlanoTrabalho
from .models import CriacaoSistema
from .models import OrgaoGestor
from .models import Conselheiro
from .models import ConselhoCultural
from .models import FundoCultura
from .models import FundoDeCultura
from .models import PlanoCultura
from .models import Componente
from adesao.models import SistemaCultura

from .forms import CriarComponenteForm
from .forms import CriarFundoForm
from .forms import ConselhoCulturalForm
from .forms import DesabilitarConselheiroForm
from .forms import CriarConselheiroForm
from .forms import AlterarConselheiroForm


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
    template_name = 'planotrabalho/cadastrar_componente.html'
    success_url = reverse_lazy("adesao:home")

    def dispatch(self, *args, **kwargs):
        sistema_id = self.request.session['sistema_cultura_selecionado']['id']
        self.sistema = SistemaCultura.objects.get(id=sistema_id)
        componente = getattr(self.sistema, self.kwargs['tipo'])
        if componente:
            if self.kwargs['tipo'] == 'fundo_cultura':
                return redirect('planotrabalho:alterar_fundo', pk=componente.id)
            else:
                return redirect('planotrabalho:alterar_componente', pk=componente.id,
                    tipo=self.kwargs['tipo'])

        return super(CadastrarComponente, self).dispatch(*args, **kwargs)

    def get_form_class(self):
        if self.kwargs['tipo'] == 'fundo_cultura':
            form_class = CriarFundoForm
        else:
            form_class = CriarComponenteForm

        return form_class

    def get_form_kwargs(self):
        kwargs = super(CadastrarComponente, self).get_form_kwargs()
        kwargs['sistema'] = self.sistema
        kwargs['tipo'] = self.kwargs['tipo']
        return kwargs


class AlterarComponente(UpdateView):
    model = Componente
    form_class = CriarComponenteForm
    template_name = 'planotrabalho/cadastrar_componente.html'

    def get_form_kwargs(self):
        kwargs = super(AlterarComponente, self).get_form_kwargs()
        sistema_id = self.request.session['sistema_cultura_selecionado']['id']
        self.sistema = SistemaCultura.objects.get(id=sistema_id)
        kwargs['sistema'] = self.sistema
        kwargs['tipo'] = self.kwargs['tipo']
        return kwargs

    def get_success_url(self):
        return reverse_lazy('planotrabalho:planotrabalho', kwargs={'pk': self.sistema.id})


class AlterarFundoCultura(UpdateView):
    model = FundoDeCultura
    form_class = CriarFundoForm
    template_name = 'planotrabalho/alterar_fundo.html'

    def get_form_kwargs(self):
        kwargs = super(AlterarFundoCultura, self).get_form_kwargs()
        sistema_id = self.request.session['sistema_cultura_selecionado']['id']
        self.sistema = SistemaCultura.objects.get(id=sistema_id)
        kwargs['sistema'] = self.sistema
        kwargs['tipo'] = 'fundo_cultura'
        return kwargs

    def get_success_url(self):
        return reverse_lazy('planotrabalho:planotrabalho', kwargs={'pk': self.sistema.id})


class CadastrarConselho(CreateView):
    form_class = ConselhoCulturalForm
    template_name = 'planotrabalho/cadastrar_conselho.html'

    def get_form_kwargs(self):
        kwargs = super(CadastrarConselho, self).get_form_kwargs()
        kwargs['user'] = self.request.user.usuario
        return kwargs

    def dispatch(self, *args, **kwargs):
        conselho = self.request.user.usuario.plano_trabalho.conselho_cultural
        if conselho:
            return redirect('planotrabalho:alterar_conselho', pk=conselho.id)

        return super(CadastrarConselho, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        trabalho = self.request.user.usuario.plano_trabalho.id
        return reverse_lazy('planotrabalho:planotrabalho', args=[trabalho])


class CriarConselheiro(CreateView):
    form_class = CriarConselheiroForm
    template_name = 'planotrabalho/cadastrar_conselheiros.html'

    def get_form_kwargs(self):
        kwargs = super(CriarConselheiro, self).get_form_kwargs()
        kwargs['user'] = self.request.user.usuario
        return kwargs

    def get_success_url(self):
        return reverse_lazy('planotrabalho:listar_conselheiros')


class ListarConselheiros(ListView):
    model = Conselheiro
    template_name = 'planotrabalho/listar_conselheiros.html'
    paginate_by = 12

    def get_queryset(self):
        q = self.request.user.usuario.plano_trabalho.conselho_cultural.id
        conselheiros = Conselheiro.objects.filter(conselho=q, situacao=1)  # 1 = Habilitado

        return conselheiros


class AlterarConselheiro(UpdateView):
    form_class = AlterarConselheiroForm
    template_name = 'planotrabalho/alterar_conselheiro.html'

    def get_queryset(self):
        pk = self.kwargs['pk']
        conselheiro = Conselheiro.objects.filter(id=pk)

        return conselheiro

    def get_form_kwargs(self):
        kwargs = super(AlterarConselheiro, self).get_form_kwargs()
        kwargs['user'] = self.request.user.usuario
        return kwargs

    def get_success_url(self):
        return reverse_lazy('planotrabalho:listar_conselheiros')


class DesabilitarConselheiro(UpdateView):
    form_class = DesabilitarConselheiroForm
    template_name = 'planotrabalho/desabilitar_conselheiro.html'

    def get_queryset(self):
        pk = self.kwargs['pk']
        conselheiro = Conselheiro.objects.filter(id=pk)

        return conselheiro

    def get_form_kwargs(self):
        kwargs = super(DesabilitarConselheiro, self).get_form_kwargs()
        kwargs['user'] = self.request.user.usuario
        return kwargs

    def get_success_url(self):
        return reverse_lazy('planotrabalho:listar_conselheiros')


class AlterarConselho(UpdateView):
    form_class = ConselhoCulturalForm
    model = ConselhoCultural
    template_name = 'planotrabalho/cadastrar_conselho.html'

    def get_form_kwargs(self):
        kwargs = super(AlterarConselho, self).get_form_kwargs()
        kwargs['user'] = self.request.user.usuario
        return kwargs

    def get_success_url(self):
        trabalho = self.request.user.usuario.plano_trabalho.id
        return reverse_lazy('planotrabalho:planotrabalho', args=[trabalho])


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
