from django.shortcuts import render


def index(request):
    return render(request, 'website/index.html')



def index1(request):
    return render(request, 'website/index_test.html')