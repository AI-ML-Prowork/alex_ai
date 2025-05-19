from .image_model import generate_image
from .video_model import generate_video
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
                            return redirect('/auth/user-login')
                    else:
                        user.delete() 
                        return JsonResponse({"error": clients_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            except IntegrityError as e:
                print(f"Integrity error: {str(e)}")
                return JsonResponse({"error": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                return JsonResponse({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            







def my_profile(request):
    if not request.user.is_authenticated:
        return redirect('/auth/user-login')
    if request.method == 'GET':
        ic(request.session.get('user_info'))
        ic(request.user.username, request.user.id, request.user.email)
        ic(request.user.is_authenticated)
        profile = Clients.objects.get(user=request.user.id)
        profile_data = ClientSerializer(profile).data
        username = request.user.username
        profile_data['username'] = username
        # ic(profile_data)
        if request.GET.get('api') == 'true':
            return JsonResponse({"status": "success", "data": profile_data}, status=status.HTTP_200_OK)
        return TemplateResponse(request,'user_panel/profile/my_profile.html', {"profile": profile_data})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    



@csrf_exempt
def my_profile_update(request):
    if not request.user.is_authenticated:
        return redirect('/auth/user-login')
    
    if request.method == 'POST':
        try:
            profile = Clients.objects.get(user=request.user.id)
            data = request.POST.copy()
            username = data.get('username')
            full_name = data.get('full_name', '')
            first_name = ''
            last_name = ''
            if full_name:
                name_parts = full_name.strip().split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ''
            profile_img = request.FILES.get('profile_img')
            if profile_img:
                file_name = profile_img.name.replace(" ", "_")
                folder = "profile_images"
                file_url = upload_file_to_vps(profile_img, file_name, folder)
                data['profile_img'] = file_url
            else:
                data['profile_img'] = profile.profile_img

            user = request.user
            user_updated = False
            if username and username != user.username:
                user.username = username
                user_updated = True
            if profile_img and profile_img != user.profile_img:
                user.profile_img = file_url
                user_updated = True
            if full_name and full_name!= user.full_name:
                user.full_name = data['full_name']
                user_updated = True
            if data.get('phone') and data.get('phone') != user.phone_number:
                user.phone_number = data['phone']
                user_updated = True
            if first_name and first_name != user.first_name:
                user.first_name = first_name
                user_updated = True
            if last_name and last_name != user.last_name:
                user.last_name = last_name
                user_updated = True
            if user_updated:
                user.save()

            serializer = ClientSerializer(profile, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                if request.GET.get('api') == 'true':
                    return JsonResponse({'message': 'Profile updated successfully', 'data': serializer.data}, status=200)
                else:
                    messages.success(request, 'Profile updated successfully')
                    return redirect('/user/profile/')
            else:
                return JsonResponse({'error': 'Invalid data', 'details': serializer.errors}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Clients.DoesNotExist:
            return JsonResponse({'error': 'Profile not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)





# @csrf_exempt
# def my_profile_update(request):
#     if not request.user.is_authenticated:
#         return redirect('/auth/user-login')

#     if request.method != 'POST':
#         return JsonResponse({'error': 'Invalid request method'}, status=405)

#     user = request.user
#     data = request.POST.copy()
#     files = request.FILES

#     updated = False

#     user_fields = {
#         'username': 'username',
#         'full_name': 'full_name',
#         'phone': 'phone_number',  # phone comes from form, maps to user.phone_number
#     }

#     for form_field, user_attr in user_fields.items():
#         new_value = data.get(form_field)
#         if new_value and getattr(user, user_attr, None) != new_value:
#             setattr(user, user_attr, new_value)
#             updated = True

#     profile_img = files.get('profile_img')
#     if profile_img:
#         file_name = profile_img.name.replace(" ", "_")
#         file_url = upload_file_to_vps(profile_img, file_name, "profile_images")
#         user.profile_img = file_url
#         updated = True
#     # If no new image, keep the existing one (do nothing)

#     if updated:
#         user.save()
#     try:
#         profile = Clients.objects.get(user=user.id)
#     except Clients.DoesNotExist:
#         return JsonResponse({'error': 'Client profile not found'}, status=404)

#     if profile_img:
#         profile.profile_img = user.profile_img
#     else:
#         if not profile.profile_img or profile.profile_img != user.profile_img:
#             profile.profile_img = user.profile_img

#     for field in ['username', 'full_name', 'phone', 'profile_img']:
#         data.pop(field, None)

#     serializer = ClientSerializer(profile, data=data, partial=True)
#     ic(data)
#     if serializer.is_valid():
#         serializer.save()
#         profile.save()

#         profile_img_url = (
#             profile.profile_img
#             or user.profile_img
#             or "https://img.freepik.com/free-psd/contact-icon-illustration-isolated_23-2151903337.jpg?t=st=1745986690~exp=1745990290~hmac=e8ead49e66b05d3548c4753495720c210ea9b40870580e90211908df0684ab43&w=826"
#         )

#         if request.GET.get('api') == 'true':
#             return JsonResponse({
#                 'message': 'Profile updated successfully',
#                 'data': {**serializer.data, "profile_img": profile_img_url},
#                 'user': {
#                     "username": user.username,
#                     "full_name": getattr(user, 'full_name', ''),
#                     "phone_number": getattr(user, 'phone_number', ''),
#                     "profile_img": profile_img_url,
#                 }
#             }, status=200)
#         else:
#             messages.success(request, 'Profile updated successfully')
#             return redirect('/user/profile/')
#     else:
#         return JsonResponse({'error': 'Invalid data', 'details': serializer.errors}, status=400)





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




@csrf_exempt
def generate_image_view(request):
    prompt = request.POST.get("prompt")
    image_type = request.POST.get("image_type")
    full_prompt = f"{prompt} and image should be {image_type}"
    ic(full_prompt)
    client = OpenAIChatClient()
    image_url = client.generate_image(full_prompt)
    return JsonResponse({"image_url": image_url})



@csrf_exempt
def edit_image_view(request):
    prompt = request.POST.get("prompt")
    image_file = request.FILES["image"]
    mask_file = request.FILES["mask"]

    with open("temp_image.png", "wb") as f:
        f.write(image_file.read())
    with open("temp_mask.png", "wb") as f:
        f.write(mask_file.read())

    client = OpenAIChatClient()
    edited_url = client.edit_image("temp_image.png", "temp_mask.png", prompt)
    return JsonResponse({"image_url": edited_url})




@csrf_exempt
def alexai_img_gen(request):
    if request.method == 'GET':
        return render(request, 'user_panel/image_generation.html')

    elif request.method == 'POST':
        prompt = request.POST.get('prompt')
        image_type = request.POST.get('image_type')

        final_prompt = f"{prompt} and image should be {image_type}"
        if not prompt:
            return render(request, 'user_panel/image_generation.html', {
                'error': 'Please enter a prompt.'
            })

        try:
            image_url = generate_image(final_prompt)
            if request.GET.get('api') == 'true':
                return JsonResponse({"status": "success", "data": image_url}, status=status.HTTP_200_OK)
            return render(request, 'user_panel/image_generation.html', {
                'image_url': image_url,
                'prompt': final_prompt
            })
        except Exception as e:
            return render(request, 'user_panel/image_generation.html', {
                'error': f"Failed to generate image: {str(e)}"
            })

    return JsonResponse({'error': 'Invalid request method'}, status=405)

    

@csrf_exempt
def alexai_video_gen(request):
    if request.method == 'GET':
        return TemplateResponse(request,'user_panel/video_generation.html', {})


    elif request.method == 'POST':
        prompt = request.POST.get('prompt')
        if not prompt:
            return render(request, 'user_panel/video_generation.html', {
                'error': 'Please enter a prompt.'
            })

        try:
            video_url = generate_video(prompt)
            if request.GET.get('api') == 'true':
                return JsonResponse({"status": "success", "data": video_url}, status=status.HTTP_200_OK)
            return render(request, 'user_panel/video_generation.html', {
                'video_url': video_url,
                'prompt': prompt
            })
        except Exception as e:
            return render(request, 'user_panel/video_generation.html', {
                'error': f"Failed to generate video: {str(e)}"
            })

    return JsonResponse({'error': 'Invalid request method'}, status=405)





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
def gallery(request):
    if request.method == 'GET':
        return TemplateResponse(request,'user_panel/gallery.html', {})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)



    



    
from django.http import JsonResponse

@csrf_exempt
def upload_file_view(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        ic(file)
        file_name = file.name

        ic(file_name)
        folder = "user_data" 

        file_url = upload_file_to_vps(file, file_name, folder)
        ic(file_url)
        return JsonResponse({'message': 'File uploaded successfully!', 'file_url': file_url})

    return JsonResponse({'error': 'No file uploaded'}, status=400)
