from django.shortcuts import render
from django.contrib.auth.models import User

def home_view(request):
    return render(request, 'home.html')

def chat_list_view(request):
    admins = User.objects.filter(is_superuser=True)
    return render(request, 'chat_list.html',{'admins':admins})