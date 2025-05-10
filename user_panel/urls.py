from django.urls import path
from .views import *


urlpatterns = [
    path("register/", register_user, name= "register_user"),
    path("profile/", my_profile, name = "my_profile"),
    path("profile/update/", my_profile_update, name = "my_profile_update"),


    # AI CONTENT
    path("alex-ai/", alex_ai, name= "alex_ai"),
    path("alex-ai/image-generatation/", alexai_img_gen, name= "alexai_img_gen"),
    path("alex-ai/video-generatation/", alexai_video_gen, name= "alexai_video_gen"),
    path("alex-ai/explore/", explore, name= "explore"),
    path("alex-ai/assets/", assets, name= "assets"),
    path("alex-ai/gallery/", gallery, name= "gallery"),


    
    


]