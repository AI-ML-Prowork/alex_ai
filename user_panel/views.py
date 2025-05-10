from django.shortcuts import render
from xinfo_ai.utils import *

User = get_user_model()



@csrf_exempt
def register_user(request):
        if request.method == 'GET':
         return TemplateResponse(request,'authentication/signup.html')

        # Register User
        request.POST._mutable = True
        request.POST['account_type'] = 'Clients'
        request.POST._mutable = False
        # Ensure required fields are present
        request.POST._mutable = True
        request.POST['password'] = request.POST.get('password', 'user@#$123')
        request.POST['password2'] = request.POST['password']
        request.POST._mutable = False
        user_serializer = UserSignupSerializer(data=request.POST, context={"request": request})
        
        user_serializer.is_valid(raise_exception=True)
        
        if user_serializer.is_valid():
            try:
                with transaction.atomic():
                    # Create the user
                    user = user_serializer.save()
                    print("User created successfully!", user.id)
                    
                    # Create candidate record               
                    clients_data = request.POST.copy()
                    clients_data.update(request.FILES)
                    clients_data["user"] = user.id

                    # profile_image = request.FILES.get('profile_img', None)
                    # if profile_image:
                    #     file_name = profile_image.name.replace(" ", "_")
                    #     folder = "clients_data"
                    #     file_url = upload_file_to_vps(profile_image, file_name, folder)
                    #     clients_data['profile_image'] = file_url
                    #     ic(file_url)

                    # Generate clients_record_id
                    last_client = Clients.objects.order_by('id').last()
                    if not last_client:
                        clients_data["custom_id"] = 'UID100001'
                    else:
                        last_id = last_client.custom_id.split('UID')[1].strip()
                        clients_data["custom_id"] = f'UID{int(last_id) + 1:06d}'

                    clients_serializer = ClientSerializer(data=clients_data)                
                    if clients_serializer.is_valid():
                        client = clients_serializer.save()

                        # Access the clients object
                        print("Candidate created successfully!", client.id)
                        
                        # Send response for successful registration
                        if request.GET.get('api') == 'true':
                            return JsonResponse(
                                {"msg": "User added successfully!", "data": clients_data},
                                status=status.HTTP_201_CREATED,
                            )
                        else:
                            messages.success(request, "Candidate added successfully.")
                            return redirect('/user-login/')
                    else:
                        user.delete() 
                        return JsonResponse({"error": clients_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            except IntegrityError as e:
                print(f"Integrity error: {str(e)}")
                return JsonResponse({"error": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                return JsonResponse({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            





@csrf_exempt
def alex_ai(request):
    if request.user.is_authenticated:
        ic(request.user)
        ic(request.user.is_authenticated)
        ic(request.user.id)

        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                prompt = data.get('input', '')
                if not prompt:
                    return JsonResponse({'error': 'input is required'}, status=400)

                chat_client = OpenAIChatClient()
                conversation_history = request.session.get('conversation_history', [])
                chat_client.set_conversation_history(conversation_history)

                answer = chat_client.get_response(prompt)

                request.session['conversation_history'] = chat_client.get_conversation_history()
                return JsonResponse({
                    'answer': answer,
                    'conversation_history': request.session['conversation_history']
                }, status=200)

            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({'error': 'Invalid request method'}, status=405)

    return JsonResponse({'error': 'User is not authenticated'}, status=401)






def my_profile(request):
    if not request.user.is_authenticated:
        return redirect('/user-login/')
    if request.method == 'GET':
        ic(request.session.get('user_info'))
        ic(request.user)
        ic(request.user.is_authenticated)
        ic(request.user.id)
        # ic(dict(request.user))
        profile = Clients.objects.get(user=request.user.id)
        profile_data = ClientSerializer(profile).data
        ic(profile_data)
        return TemplateResponse(request,'user_panel/profile/my_profile.html', {"profile": profile_data})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    



@csrf_exempt
def my_profile_update(request):
    if not request.user.is_authenticated:
        return redirect('/user-login/')
    if request.method == 'POST':
        try:
            data = request.POST
            ic(data)
            profile = Clients.objects.get(user=request.user.id)
            serializer = ClientSerializer(profile, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                if request.GET.get('api') == 'true':
                    return JsonResponse({'message': 'Profile updated successfully', 'data': serializer.data}, status=200)
            else:
                return redirect('/user/profile/')

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Clients.DoesNotExist:
            return JsonResponse({'error': 'Profile not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)






# @csrf_exempt
# def alexai_img_gen(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             prompt = data.get('input', '')
#             if not prompt:
#                 return JsonResponse({'error': 'input is required'}, status=400)

#             chat_client = OpenAIChatClient()
#             conversation_history = request.session.get('conversation_history', [])
#             chat_client.set_conversation_history(conversation_history)

#             answer = chat_client.get_response(prompt)

#             request.session['conversation_history'] = chat_client.get_conversation_history()
#             return JsonResponse({
#                 'answer': answer,
#                 'conversation_history': request.session['conversation_history']
#             }, status=200)

#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON'}, status=400)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)







@csrf_exempt
def explore(request):
    if request.method == 'GET':
        return TemplateResponse(request,'user_panel/explore.html', {})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    

@csrf_exempt
def assets(request):
    if request.method == 'GET':
        return TemplateResponse(request,'user_panel/assets.html', {})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    

@csrf_exempt
def alexai_img_gen(request):
    if request.method == 'GET':
        return TemplateResponse(request,'user_panel/image_generation.html', {})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    


@csrf_exempt
def gallery(request):
    if request.method == 'GET':
        return TemplateResponse(request,'user_panel/gallery.html', {})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    

@csrf_exempt
def alexai_video_gen(request):
    if request.method == 'GET':
        return TemplateResponse(request,'user_panel/video_generation.html', {})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)