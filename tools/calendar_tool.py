import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Wenn wir Daten ändern wollen (Termine erstellen), brauchen wir diesen Scope
SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarTool:
    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authentifiziert den User via Browser (OAuth2)."""
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # Wenn keine gültigen Credentials da sind, User einloggen lassen
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # Hier muss die credentials.json im Root liegen!
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Token speichern für den nächsten Run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('calendar', 'v3', credentials=self.creds)

    def list_upcoming_events(self, max_results=5):
        """Listet die nächsten X Termine auf."""
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=max_results, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        
        if not events:
            return "Keine anstehenden Termine gefunden."
        
        event_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_list.append(f"- {start}: {event['summary']}")
        
        return "\n".join(event_list)

    def create_event(self, summary, start_time_iso, duration_minutes=60):
        """
        Erstellt einen Termin.
        start_time_iso muss Format '2023-12-24T15:00:00' haben.
        """
        try:
            # Startzeit parsen
            start_dt = datetime.datetime.fromisoformat(start_time_iso)
            end_dt = start_dt + datetime.timedelta(minutes=duration_minutes)
            
            event = {
                'summary': summary,
                'location': 'Campus Schwarzwald / Online',
                'description': 'Erstellt vom KI Konkret Scheduler Agent via Llama 3',
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'Europe/Berlin',
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'Europe/Berlin',
                },
            }

            event = self.service.events().insert(calendarId='primary', body=event).execute()
            return f"✅ Termin erstellt: {event.get('htmlLink')}"
        except Exception as e:
            return f"❌ Fehler beim Erstellen: {str(e)}"