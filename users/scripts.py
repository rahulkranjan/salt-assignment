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
from rest_framework import filters, permissions, status
from .models import GmeetConfig

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
        data = GmeetConfig.objects.get(tutor_id=self.tutor)
        if data.credentials is not None:
            client_secret = json.loads(data.credentials)

        
        if data.token != "":
            token = json.loads(data.token)
            token = Credentials.from_authorized_user_info(token, self.scopes)
        else:
            token = None
        
        # If there are no (valid) credentials available, let the user log in.
        if not token or not token.valid:
            if token and token.expired and token.refresh_token:
                token.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(
                    client_secret,
                    scopes=self.scopes,
                    redirect_uri="http://127.0.0.1:8000/apiV1/callback"
                    )
                token = flow.run_local_server()
            data.token = token.to_json()
            data.save()
        
        return token
        


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
    

class Gmeet(APIView):
    def get(self, request, format=None):
        tutor_id = 1
        start_time = datetime(2023, 2, 10, 13, 36, 0)
        end_time = start_time + timedelta(minutes=10)
        summary = "GMeet Test"
        location = "xyz"
        description = "test"
        attendees = [
                {
                    "email": "kjrahul21@gmail.com",

                },
            ]
        calendar = GoogleCalendar(tutor_id, start_time, end_time,summary, location,description, attendees)
        result = calendar.create_event(start_time,end_time)
        return Response(result['hangoutLink'])



def get_credentials(self):
        data = GmeetConfig.objects.get(tutor_id=self.tutor)
        if data.credentials is not None:
            client_secret = json.loads(data.credentials)

        
        # if data.token != "":
        #     token = json.loads(data.token)
        #     token = Credentials.from_authorized_user_info(token, self.scopes)
        # else:
        #     token = None
        
        # # If there are no (valid) credentials available, let the user log in.
        # if not token or not token.valid:
        #     if token and token.expired and token.refresh_token:
        #         token.refresh(Request())
        #     else:
        flow = InstalledAppFlow.from_client_config(client_secret, scopes=self.scopes)
        creds = flow.run_console()

        return creds
        
        # return token


class GoogleAuthLocal(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request, format=None):
        data = GmeetConfig.objects.get(tutor_id=1)
        if data.credentials is not None:
            client_secret = json.loads(data.credentials)
        import pdb
        pdb.set_trace()
        flow = flow = InstalledAppFlow.from_client_config(
                client_secret,
            scopes=[
                "https://www.googleapis.com/auth/calendar",
            ],
            redirect_uri="http://127.0.0.1:8000/apiV1/callback/")

        flow.run_local_server()

        return Response("Done")
        # {'name': '...',  'email': '...', ...}

class GoogleAuthCallback(APIView):
    permission_classes = (permissions.AllowAny, )
    def get(self, request, format=None):
        data = GmeetConfig.objects.get(tutor_id=1)
        if data.credentials is not None:
            client_secret = json.loads(data.credentials)
        code = self.request.query_params.get('code', None)
        flow = flow = InstalledAppFlow.from_client_config(
                client_secret,
            scopes=[
                "https://www.googleapis.com/auth/calendar",
            ],
            redirect_uri="http://127.0.0.1:8000/apiV1/callback")
        flow.fetch_token(code=code)
        print(code)

        return Response("Done final")
