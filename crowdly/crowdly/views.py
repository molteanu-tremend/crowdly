from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class HomeView(LoginRequiredMixin, TemplateView):

    template_name = 'crowdly/index.html'

    def get(self, request, *args, **kwargs):
        # redirect_path = SystemSetting.get('HOME_REDIRECT_PATH', False)
        # if redirect_path:
        #     return redirect(redirect_path)
        return super(HomeView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(HomeView, self).get_context_data(**kwargs)

        return context