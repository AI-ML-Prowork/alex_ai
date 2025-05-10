from django.shortcuts import render
from xinfo_ai.utils import *

def index(request):
    return render(request, 'index.html')



def dashboard(request):
    return render(request, 'admin_panel/dashboard/dashboard.html')





# @csrf_exempt
# def admin_user_list(request):
#     clients = Clients.objects.all()
#     clients_data = ClientSerializer(clients, many=True).data
#     ic(clients_data)
#     if request.GET.get('api') == 'true':
#         return JsonResponse({"status": "success", "data": clients_data}, status=status.HTTP_200_OK)
#     return TemplateResponse(request, "admin_panel/all_users.html", {"clients": clients_data})




@csrf_exempt
def admin_user_list(request):
    clients = CustomUser.objects.all()
    clients_data = UserSerializer(clients, many=True).data
    ic(clients_data)
    if request.GET.get('api') == 'true':
        return JsonResponse({"status": "success", "data": clients_data}, status=status.HTTP_200_OK)
    return TemplateResponse(request, "admin_panel/all_users.html", {"clients": clients_data})