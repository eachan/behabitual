from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
import django.contrib.auth.views
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.http import base36_to_int
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView, FormView

from apps.habits.models import Habit
from apps.habits.forms import HabitEmailOptionsForm
from util.render_to_email import render_to_email

from .signals import user_changed_password

class LogoutView(TemplateView):
    """
    Logs the user out.
    """

    template_name = "accounts/logout.html"

    def get_next_url(self):
        next = self.request.POST.get("next", None)
        if next is None:
            next = reverse('homepage')
        return next

    def post(self, request):
        logout(self.request)
        return HttpResponseRedirect(self.get_next_url())


@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, uidb36=None, token=None,
                           template_name='registration/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           current_app=None, extra_context=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.

    NOTE: we adapt this because we want to automatically log them in
    once they've set their new password. Because this is correct behaviour.
    And it's IMPOSSIBLE to do this in a form, because forms don't get a
    Request object as context. Sigh.
    """
    UserModel = get_user_model()
    assert uidb36 is not None and token is not None  # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('django.contrib.auth.views.password_reset_complete')
    try:
        uid_int = base36_to_int(uidb36)
        user = UserModel.objects.get(pk=uid_int)
    except (ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                user = form.save()
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(None)
    else:
        validlink = False
        form = None
    context = {
        'form': form,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


def password_change(request, *args, **kwargs):
    response = django.contrib.auth.views.password_change(request, *args, **kwargs)
    if request.method == 'POST' and response.status_code == 302:
        user_changed_password.send(sender=password_change)
        render_to_email(
            text_template='emails/accounts/password_changed.txt',
            html_template='emails/accounts/password_changed.html',
            to=(request.user,),
            subject='Your password has been changed',
            opt_out=False,
        )
    return response


class SettingsView(FormView):
    template_name = 'accounts/settings.html'

    def get_success_url(self):
        return reverse('account_settings')

    def get_form_class(self):
        self.queryset = self.request.user.habits.all()
        return modelformset_factory(
            Habit,
            form=HabitEmailOptionsForm,
            max_num=self.queryset.count(),
            extra=0,
        )

    def get_form_kwargs(self):
        kwargs = super(SettingsView, self).get_form_kwargs()
        kwargs['queryset'] = self.queryset
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(SettingsView, self).form_valid(form)
