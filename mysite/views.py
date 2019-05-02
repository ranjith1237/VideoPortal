from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import TemplateView

class HomePage(TemplateView):
    template_name = "home.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request,'home.html')
        return super().get(request, *args, **kwargs)
