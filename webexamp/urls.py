from django.urls import path
from django.urls import include
from .views import *

urlpatterns = [
    path('', post_list, name='webexamp'),
    path('webexamp_sq/', vk_frend, name='R'),
    path('instructions/', instructions),
    path('lesions/', lesions),
    path('git/', git),
]
