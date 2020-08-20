from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView
from snc.forms import CPFPasswordResetForm
from django.contrib.auth.models import User

class CPFPasswordResetView(PasswordResetView):
    form_class = CPFPasswordResetForm
    template_name = 'registration/password_reset_form.html'

    def form_valid(self, form):
        cpf = form.cleaned_data['CPF']
        try:
            usuario = User.objects.get(username=cpf)
        except:
            form.add_error(field='CPF',error='CPF informado não esta cadastrado no SNC')
            return super().form_invalid(form)

        form.cleaned_data['email'] = usuario.email
        self.request.session['email'] = usuario.email
        return super().form_valid(form)

class CPFPasswordResetDoneView(PasswordResetDoneView):
    form_class = CPFPasswordResetForm
    template_name = 'registration/password_reset_done.html'

    def get_context_data(self, **kwargs):
        context = super(CPFPasswordResetDoneView, self).get_context_data(**kwargs)
        context['email'] = self.mask_email(self.request.session['email'])
        return context

    def mask_email(self, email):
        split = str(email).split('@')
        final_email = self.replace_with_asterisk(split[0])
        final_email += '@'
        final_email += self.replace_with_asterisk(split[1])
        return final_email

    def replace_with_asterisk(self, char):
        final_char = char[0:2]
        remaining = '*' * len(char[2:])
        return final_char + remaining