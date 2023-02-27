from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
import os.path
import uuid
import sys
import django
import json
from rest_framework.views import APIView
from rest_framework.response import Response

from users.models import GmeetConfig

sys.path.append("../..")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oncls_apims.settings')

if __name__ == "__main__":
    django.setup()

import logging
# connection.schema_name = "olvorchidnaigaon_schema"

class GoogleCalendar:
    def __init__(self,tutor, start_time,end_time,summary,location,description , attendees):
        self.scopes = ['https://www.googleapis.com/auth/calendar']
        self.start_time = start_time
        self.end_time = end_time
        self.summary = summary
        self.location = location
        self.description = description
        self.attendees = attendees
        self.tutor = tutor

    def get_credentials(self):
        logger = logging.getLogger(__name__)
        try:

            data = GmeetConfig.objects.get(tutor_id=self.tutor)
            if data.credentials is not None:
                client_secret = eval(data.credentials)

            # if data.token != "" or data.token is not None:
            if data.token:
                token = json.loads(data.token)
                token = Credentials.from_authorized_user_info(token, self.scopes)
            else:
                token = None
            
            # If there are no (valid) credentials available, let the user log in.
            if not token or not token.valid:
                if token and token.expired and token.refresh_token:
                    token.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_config(client_secret, scopes=self.scopes)
                    token = flow.run_local_server(port=0)
                data.token = token.to_json()
                data.save()
            return token
        except Exception as e:
            logger.exception("Error getting GmeetConfig: %s", str(e))
            return 0


    def create_event(self, start_time, end_time):

        credentials = self.get_credentials()
        service = build("calendar", "v3", credentials=credentials)
        result = service.calendarList().list().execute()
        calendar_id = result['items'][0]['id']

        event = {
            'summary': self.summary,
            'location': self.location,
            'description': self.description,
            'start': {
                'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': 'Asia/Kolkata',
            },
            'attendees': self.attendees,
            'conferenceData': {
                'conferenceSolutionKey': {"type": "hangoutsMeet"},
                'createRequest': {
                    'requestId': str(uuid.uuid1())
                }
            },
        }
        result = service.events().insert(calendarId=calendar_id, body=event, conferenceDataVersion=1).execute()
        return result
    

if __name__ == "__main__":
    '''Use this code to test the above class'''

    # gmeet_config = GmeetUserConfig.objects.latest('id')
    tutor_id = 1
    start_time = datetime(2023, 2, 26, 14, 45, 0)
    end_time = start_time + timedelta(minutes=10)
    summary = "GMeet Test"
    location = "xyz"
    description = "test"
    attendees = [
            {
                "email": "sadathmogal777@gmail.com",
            
            },
        ]
    calendar = GoogleCalendar(tutor_id, start_time, end_time,summary, location,description, attendees)
    result = calendar.create_event(start_time,end_time)
    # result = calendar.get_credentials()
    print(result)


class CreateMeet(APIView):
    def get(self, request, format=None):
        tutor_id = 2
        start_time = datetime(2023, 2, 26, 15, 00, 0)
        end_time = start_time + timedelta(minutes=10)
        summary = "GMeet Test ----  "
        location = "xyz"
        description = "test"
        attendees = [
                {
                    "email": "kjrahul21@gmail.com",
                    "organizer": True,
                
                },
            ]
        calendar = GoogleCalendar(tutor_id, start_time, end_time,summary, location,description, attendees)
        result = calendar.create_event(start_time,end_time)
        return Response(result)


from rest_framework import filters, permissions, status
from django.urls import reverse
class GoogleAuthView(APIView):
    permission_classes = (permissions.AllowAny, )
    def get(self, request, format=None):
        # Set up the Google OAuth2 flow
        data = GmeetConfig.objects.get(tutor_id=2)
        client_secret = eval(data.credentials)
        flow = InstalledAppFlow.from_client_config(
            client_secret,
            scopes=['https://www.googleapis.com/auth/calendar'],
            redirect_uri='http://web-production-df525.up.railway.app/apiV1/callback/',
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            prompt='consent',
        )
        # Store the state parameter in the session
        request.session['google_oauth_state'] = state

        # Redirect the user to the Google OAuth consent screen
        return Response({'url': authorization_url})

class GoogleAuthCallback(APIView):
    permission_classes = (permissions.AllowAny, )
    def get(self, request, format=None):
        data = GmeetConfig.objects.get(tutor_id=2)
        client_secret = eval(data.credentials)
        code = self.request.query_params.get('code', None)
        flow = InstalledAppFlow.from_client_config(
            client_secret,
            scopes=[
                'https://www.googleapis.com/auth/calendar'
            ],
            redirect_uri='http://web-production-df525.up.railway.app/apiV1/callback/',)
        access_token = flow.fetch_token(code=code)

        final = {
            'token': access_token['access_token'],
            'refresh_token': access_token['refresh_token'],
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": "7065572801-kj0pp2ce2ti9hlju4raj4o51a5a26cns.apps.googleusercontent.com",
            "client_secret": "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", 
            "scopes": [
                "https://www.googleapis.com/auth/calendar"
            ],
            "expiry_date": datetime.fromtimestamp(access_token['expires_at'])

        }
        data.token = final
        data.save()
        from django.shortcuts import render
        return Response(render(request, 'template/thankyou.html'))
    
