import json


class AlexaRequestBuilder:

    def __init__(self):
        self._session_id = "amzn1.echo-api.session.0000000-0000-0000-0000-00000000000"
        self._version = "1.0"
        self._application_id = "fake-application-id"
        self._user_id = "amzn1.account.AM3B00000000000000000000000"
        self._request_id = "amzn1.echo-api.request.00000000-0000-0000-0000-000000000000"
        self._request_timestamp = "2019-01-22T21:00:26Z"
        self._locale = "en-US"
        self._envelope = {}
        self._slots = {}
        self._request_type = "LaunchRequest"
        self._intent_name = "TestIntent"
        self._new_session = True

    def intent(self, intent_name):
        self._intent_name = intent_name
        self._request_type = "IntentRequest"
        return self

    def slot(self, slot_name, value, value_id=None):
        value_id = value_id or value.upper().replace(" ", "_")
        self._slots[slot_name] = {'value': value, 'id': value_id}
        return self

    def session_id(self, session_id):
        self._session_id = session_id
        return self

    def version(self, version):
        self._version = version
        return self

    def application_id(self, application_id):
        self._application_id = application_id
        return self

    def user_id(self, user_id):
        self._user_id = user_id
        return self

    def request_id(self, request_id):
        self._request_id = request_id
        return self

    def timestamp(self, timestamp):
        self._request_timestamp = timestamp
        return self

    def locale(self, locale):
        self._locale = locale
        return self

    def new_session(self, is_new_session):
        self._new_session = is_new_session
        return self

    def make(self):
        return {'version': self._generate_version_envelope(), 'session': self._generate_session_envelope(),
                'context': self._generate_context_envelope(), 'request': self._generate_request_envelope()}

    def _generate_version_envelope(self):
        return self._version

    def _generate_session_envelope(self):
        return {
            'new': self._new_session,
            'sessionId': self._session_id,
            'application': {'applicationId': self._application_id},
            'attributes': {},
            'user': {'userId': self._user_id},
        }

    def _generate_context_envelope(self):
        return {
            'System': {
                'application': {'applicationId': self._application_id},
                'user': {'userId': self._user_id},
                'device': {'supportedInterfaces': {'AudioPlayer': {}}},
            },
            'AudioPlayer': {
                'offsetInMilliseconds': 0,
                'playerActivity': 'IDLE'
            }
        }

    def _generate_request_envelope(self):
        return {
            'type': self._request_type,
            'request_id': self._request_id,
            'timestamp': self._request_timestamp,
            'locale': self._locale,
            'intent': self._generate_intent_envelope(),
            'dialogState': "STARTED"
        }

    def _generate_intent_envelope(self):
        return {
            'name': self._intent_name,
            'confirmationStatus': "NONE",
            'slots': self._generate_slots_envelope(),
        }

    def _generate_slots_envelope(self):
        return {slot_name: {
            "name": slot_name,
            "value": slot_value['value'],
            "resolutions": {
                "resolutionsPerAuthority": [
                    {
                        "authority": "amzn1.er-authority.echo-sdk.amzn1.ask.skill.00000000-0000-0000-0000-000000000000.TestSkill",
                        "status": {
                            "code": "ER_SUCCESS_MATCH"
                        },
                        "values": [
                            {
                                "value": {
                                    "name": slot_value['value'],
                                    "id": slot_value['id']
                                }
                            }
                        ]
                    }
                ]
            },
            "confirmationStatus": "NONE",
            "source": "USER"
        } for slot_name, slot_value in self._slots.items()}


class AlexaRequestFactory:

    @staticmethod
    def create_launch_request():
        return AlexaRequestBuilder().new_session(True).make()

    @staticmethod
    def create_intent_request(intent_name, slots=None):
        slots = slots or {}
        request_builder = AlexaRequestBuilder().new_session(False).intent(intent_name)
        for slot_name, slot_value in slots.items():
            request_builder = request_builder.slot(slot_name, slot_value)
        return request_builder.make()


class AskTestClient:

    def __init__(self, client, skill_route='/'):
        self.client = client
        self.skill_route = skill_route

    def perform_launch(self):
        request = AlexaRequestFactory.create_launch_request()
        return self.perform_request(request)

    def perform_intent(self, intent_name, slots=None):
        slots = slots or {}
        request = AlexaRequestFactory.create_intent_request(intent_name, slots=slots)
        return self.perform_request(request)

    def perform_request(self, request):
        return AlexaResponse(self.client.post(self.skill_route,
                                              data=json.dumps(request),
                                              headers={'Accept': 'application/json', 'Content-Type': 'application/json'}
                                              ))


class AlexaResponse:

    def __init__(self, raw_response):
        self.raw_response = raw_response
        if hasattr(raw_response, 'data'):
            self.response = json.loads(raw_response.data)  # Flask test client
        else:
            self.response = raw_response.json()  # requests client

    @property
    def text(self):
        return self.response.get('response', {}) \
            .get('outputSpeech', {}) \
            .get('text', None)

    @property
    def reprompt(self):
        return self.response.get('response', {}) \
            .get('reprompt', {}) \
            .get('outputSpeech', {}) \
            .get('text', None)

    @property
    def ends_session(self):
        return self.response.get('response', {}).get('shouldEndSession', True)

    @property
    def session_attributes(self):
        return self.response.get('sessionAttributes', {})

    @property
    def status_code(self):
        return self.raw_response.status_code
