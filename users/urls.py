from django.urls import path
from .views import *
from .scripts import *

urlpatterns = [

    path('current-user/', Current_User),
    path('user/', UserList.as_view()),
    path('user/<pk>/', UserDetailed.as_view()),
    # path('apicall/', callApi.as_view()),
    path('create-meet/', CreateMeet.as_view()),
    path('google-oauth/', GoogleAuthView.as_view(), name='google_oauth'),
    path('callback/', GoogleAuthCallback.as_view(), name='google_oauth_callback'),

    # path('create-event/', create_event),
]
