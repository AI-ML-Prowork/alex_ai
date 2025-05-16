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
        # ic(profile_data)
        if request.GET.get('api') == 'true':
            return JsonResponse({"status": "success", "data": profile_data}, status=status.HTTP_200_OK)
        return TemplateResponse(request,'user_panel/profile/my_profile.html', {"profile": profile_data})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    



@csrf_exempt
def my_profile_update(request):
    if not request.user.is_authenticated:
        return redirect('/user-login/')
    if request.method == 'POST':
        try:
            profile = Clients.objects.get(user=request.user.id)
            data = request.POST.copy()  # Make a mutable copy of the QueryDict
            ic(data)
            profile_img = request.FILES.get('profile_img', None)
            if profile_img:
                file_name = profile_img.name.replace(" ", "_")
                folder = "profile_images"
                file_url = upload_file_to_vps(profile_img, file_name, folder)
                data['profile_img'] = file_url
                ic(data)
                ic(data['profile_img'])

            
            serializer = ClientSerializer(profile, data=data, partial=True)
            if serializer.is_valid():
                try:
                    serializer.save()
                    if request.GET.get('api') == 'true':
                        return JsonResponse({'message': 'Profile updated successfully', 'data': serializer.data}, status=200)
                    else:
                        messages.success(request, 'Profile updated successfully')
                except Exception as e:
                    return JsonResponse({'error': f"Failed to update profile: {str(e)}"}, status=500)
            else:
                return JsonResponse({'error': 'Invalid data', 'details': serializer.errors}, status=400)
                    

            return redirect('/user/profile/')

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Clients.DoesNotExist:
            return JsonResponse({'error': 'Profile not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)





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
