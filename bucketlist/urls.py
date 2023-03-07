from django.urls import path
from .views import *

urlpatterns = [

    path('bucket-list/', BucketList.as_view()),
    path('bucket-list/<pk>/', BucketDetail.as_view()),
    # path('create-event/', create_event),
]
