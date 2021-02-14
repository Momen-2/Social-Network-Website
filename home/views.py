from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    user = request.user
    context={"user":user}

    return render(request, "home/home.html", context)
