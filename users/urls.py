from django.urls import path
from .views import *
from .scripts import *

urlpatterns = [

    path('current-user/', Current_User),
    path('user/', UserList.as_view()),
    path('user/<pk>/', UserDetailed.as_view()),
    path('gmeet/', GoogleAuthView.as_view(), name='google_oauth'),
    path('callback/', GoogleCallbackView.as_view(), name='google_oauth_callback'),
    path('meet/', gmeet.as_view()),
    # path('GoogleAuthLocal/', GoogleAuthLocal.as_view()),
    # path('callback/', GoogleAuthCallback.as_view()),


]
