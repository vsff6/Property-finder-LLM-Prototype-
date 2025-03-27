from django.urls import path
from .views import property_chat, submit_correction, submit_rating

urlpatterns = [
    path('chat/', property_chat, name='property_chat'),  
    path('ratings/', submit_rating, name='submit_rating'),  
    path('corrections/', submit_correction, name='submit_correction'),  
]