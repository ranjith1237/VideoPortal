from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views.generic import TemplateView




def index(request):
    print("############ => ",request.user,request.user.is_staff)
    if request.user.is_staff:
        return redirect('/upload')
    else:
        return render(request,'home.html')