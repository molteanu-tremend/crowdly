from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic import View, ListView, DetailView, DeleteView, CreateView, TemplateView, UpdateView, DayArchiveView, MonthArchiveView, YearArchiveView
from models import Device

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


class DeviceList(LoginRequiredMixin, ListView):
    model = Device
    template_name = "crowdly/device_list.html"

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Device.objects.all()
        else:
            return Device.objects.filter(owners__in=[self.request.user])

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DeviceList, self).get_context_data(**kwargs)

        return context


class DeviceDetail(LoginRequiredMixin, DetailView):
    model = Device
    template_name = "crowdly/device_detail.html"
    slug_field = 'uuid'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DeviceDetail, self).get_context_data(**kwargs)

        context['device'] = self.get_object()

        # state_data = self.object.state_data_as_dict
        #
        # context['state_data_view'] = state_data

        return context
