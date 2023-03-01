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

from selenium import webdriver
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


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

uri=  'https://web-production-df525.up.railway.app/apiV1/callback/'

class GoogleAuthView(APIView):
    permission_classes = (permissions.AllowAny, )
    def get(self, request, format=None):
        tutor_id = self.request.query_params.get('tutor_id', None)
        # Set up the Google OAuth2 flow
        data = GmeetConfig.objects.get(tutor_id=2)
        client_secret = eval(data.credentials)
        flow = InstalledAppFlow.from_client_config(
            client_secret,
            scopes=['https://www.googleapis.com/auth/calendar'],
            redirect_uri=uri,
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
        tutor_id = self.request.query_params.get('tutor_id', None)
        data = GmeetConfig.objects.get(tutor_id=2)
        client_secret = eval(data.credentials)
        code = self.request.query_params.get('code', None)
        flow = InstalledAppFlow.from_client_config(
            client_secret,
            scopes=[
                'https://www.googleapis.com/auth/calendar'
            ],
            redirect_uri=uri,
            )
        access_token = flow.fetch_token(code=code)


        print(client_secret['web']['client_id'])

        final = {
            "client_id": client_secret['web']['client_id'],
            "client_secret": client_secret['web']['client_secret'],
            "expiry": "2028-03-27T09:02:14.758344Z",
            "refresh_token": access_token['refresh_token'],
            "scopes": [
                "https://www.googleapis.com/auth/calendar"
            ],
            "token": access_token['access_token'],
            "token_uri": "https://oauth2.googleapis.com/token"
        }
        data.token = json.dumps(final)
        data.save()

        return Response({'message': 'Authentication successful', 'access_token': final})
        #in response we show html file or redirect to our homepage insteed of this


class Automation(APIView):
    def get(self, request, format=None):
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        browser1 = webdriver.Chrome(options=options)
        ID = "id"
        NAME = "name"
        CLASS_NAME = "class"
        TAG_NAME = "input"
        XPATH = "xpath"
        browser1.get(
            'https://console.cloud.google.com/')

        # email = browser1.find_elements(
        #     By.XPATH, "//*[@id='identifierId']")
        # email[0].send_keys('rahul.ranjan@orchids.edu.in')


        # button = browser1.find_elements(
        #     By.XPATH, '//*[@id="identifierNext"]/div/button')

        # button[0].click()

        # time.sleep(10)
        # password = browser1.find_elements(
        #     By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input')
        # password[0].send_keys('thinkranjan@1000')

        # button = browser1.find_elements(
        #     By.XPATH, '//*[@id="passwordNext"]/div/button')
        # button[0].click()


        time.sleep(60)
        # element = browser1.find_elements(By.XPATH, '//*[@id="pcc-purview-switcher"]/pcc-platform-bar-purview-switcher/pcc-purview-switcher/cfc-switcher-button/button')
        element = browser1.find_elements(By.XPATH, '//*[contains(@id,"pcc-purview-switcher")]')
        element[0].click()

        time.sleep(2)

        # project = browser1.find_elements(
        #     By.XPATH, '//*[@id="mat-dialog-0"]/ng-component/div[1]/mat-toolbar/mat-toolbar-row[1]/div[2]/button[1]')
        # project[0].click()
        # time.sleep(30)

        # project = browser1.find_elements(
        #     By.XPATH, '//*[@id="p6ntest-name-input"]')
        # project[0].send_keys('Orchids Gmeet')
        # button = browser1.find_elements(
        #     By.XPATH, '//*[@id="p6ntest-project-create-page"]/cfc-panel-body/cfc-virtual-viewport/div[1]/div/proj-creation-form/form/button[1]')
        # button[0].click()

        # time.sleep(10)

        # project = browser1.find_elements(
        #     By.XPATH, '//*[@id="mat-dialog-0"]/ng-component/div[1]/mat-toolbar/mat-toolbar-row[1]/div[2]/button[1]')
        # project[0].click()

        # time.sleep(20)

        project = browser1.find_elements(
            By.XPATH, '//*[@id="cfc-table-caption-0-row-0"]/td[4]')

        project[0].click()

        click = browser1.find_elements(
            By.XPATH, '//*[@id="mat-dialog-0"]/ng-component/div[2]/button[2]/span[2]')


        click[0].click()

        time.sleep(2)

        api_and_services = browser1.find_elements(
            By.XPATH, "//*[@class='quick-access-grid']/a[1]")

        print(api_and_services)

        api_and_services[0].click()

        time.sleep(5)

        enable_api_and_services = browser1.find_elements(
            By.XPATH, '//*[@id="_2rif_default-action-bar"]/mat-toolbar/div[3]/div/div/div[1]/div/a/span[2]')

        enable_api_and_services[0].click()

        time.sleep(10)

        search = browser1.find_element(By.XPATH, '//*[@id="_3rif_mat-input-0"]')
        actions = ActionChains(browser1)
        actions.move_to_element(search).click().send_keys("calender").send_keys(Keys.RETURN).perform()


        # select_calender = browser1.find_elements(
        #     By.XPATH, '')

        # select_calender[0].click()


        time.sleep(10)
        browser1.close()
        return Response({'message': 'Automation successful'})