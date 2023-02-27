from django.conf import settings
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from google_auth_oauthlib.flow import Flow

# Set the required OAuth scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Set the path to your credentials JSON file
credentials_file = 'path/to/your/credentials.json'

# Create a flow to handle the OAuth2 authorization process
flow = Flow.from_client_secrets_file(
    credentials_file, scopes=SCOPES,
    redirect_uri=settings.GOOGLE_REDIRECT_URI)

@api_view(['POST'])
def create_event(request):
    # Load the credentials from the request header
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return Response({'error': 'Invalid authorization header'}, status=401)
    creds = Credentials.from_authorized_user_info({'access_token': auth_header[7:]})
    # Create a service object to access the Google Calendar API
    service = build('calendar', 'v3', credentials=creds)
    # Set the start and end times of the event
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=1)
    # Create a new event on the user's calendar
    event = {
        'summary': 'New Event',
        'location': 'San Francisco, CA',
        'description': 'A new event',
        'start': {
            'dateTime': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'timeZone': 'America/Los_Angeles',
        },
        'reminders': {
            'useDefault': True,
        },
    }
    calendar_id = 'primary'
    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    return Response({'message': f'Event created: {event.get("htmlLink")}'})