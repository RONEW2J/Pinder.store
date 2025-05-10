from django.shortcuts import render

def home_view(request):
    return render(request, 'home.html')

def terms_view(request):
    return render(request, 'legal/terms.html')

def privacy_view(request):
    return render(request, 'legal/privacy.html')