from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse

@login_required
def home(request):
    return render(request, 'core/home.html', {'users': User.objects.all()})

@login_required
def update_name(request):
    if request.method == "POST":
        new_name = request.POST.get("name", "").strip()
        if new_name:
            request.user.first_name = new_name
            request.user.save()
            return HttpResponse(status=204)  # no content needed
    return HttpResponse("Invalid request", status=400)

@login_required
def users_list(request):
    users = User.objects.all()
    return render(request, 'core/partials/users_list.html', {'users': users})
