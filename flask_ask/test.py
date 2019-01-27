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
        """
        Sets the target intent.
        :param intent_name: Target intent's name.
        :return: Self.
        """
        self._intent_name = intent_name
        self._request_type = "IntentRequest"
        return self

    def slot(self, slot_name, value, value_id=None):
        """
        Adds a slot to the request.
        :param slot_name: Name of the slot.
        :param value: Value of the slot.
        :param value_id: Value id of the slot. If not given, it will be set as value.upper().replace(' '. '_').
        :return: Self.
        """
        value_id = value_id or value.upper().replace(" ", "_")
        self._slots[slot_name] = {'value': value, 'id': value_id}
        return self

    def session_id(self, session_id):
        """
        Sets the session id.
        :param session_id: Desired session id.
        :return: Self.
        """
        self._session_id = session_id
        return self

    def version(self, version):
        """
        Sets the version.
        :param version: Desired version.
        :return: Self.
        """
        self._version = version
        return self

    def application_id(self, application_id):
        """
        Sets the application id.
        :param application_id: Desired application id.
        :return: Self.
        """
        self._application_id = application_id
        return self

    def user_id(self, user_id):
        """
        Sets the user id.
        :param user_id: Desired user id.
        :return: Self.
        """
        self._user_id = user_id
        return self

    def request_id(self, request_id):
        """
        Sets the request's id.
        :param request_id: Desired request's id.
        :return: Self.
        """
        self._request_id = request_id
        return self

    def timestamp(self, timestamp):
        """
        Sets the request's timestamp.
        :param timestamp: Desired timestamp.
        :return: Self.
        """
        self._request_timestamp = timestamp
        return self

    def locale(self, locale):
        """
        Sets the request's locale.
        :param locale: Desired request's locale.
        :return: Self.
        """
        self._locale = locale
        return self

    def new_session(self, is_new_session):
        """
        Determines whether this is the first request in the session or not.
        :param is_new_session: True if it is the first request in the session. False otherwise.
        :return: Self.
        """
        self._new_session = is_new_session
        return self

    def make(self):
        """
        Makes the request's envelope.
        :return: Dictionary representing the envelope.
        """
        return {'version': self._generate_version_envelope(), 'session': self._generate_session_envelope(),
                'context': self._generate_context_envelope(), 'request': self._generate_request_envelope()}

    def _generate_version_envelope(self):
        """
        Generates the version part of the envelope.
        :return: String containing the request version
        """
        return self._version

    def _generate_session_envelope(self):
        """
        Generates the session part of the envelope.
        :return: Dictionary containing the session envelope.
        """
        return {
            'new': self._new_session,
            'sessionId': self._session_id,
            'application': {'applicationId': self._application_id},
            'attributes': {},
            'user': {'userId': self._user_id},
        }

    def _generate_context_envelope(self):
        """
        Generates the context part of the envelope.
        :return: Dictionary containing the context envelope.
        """
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
        """
        Generates the request part of the envelope.
        :return: Dictionary containing the request envelope.
        """
        return {
            'type': self._request_type,
            'request_id': self._request_id,
            'timestamp': self._request_timestamp,
            'locale': self._locale,
            'intent': self._generate_intent_envelope(),
            'dialogState': "STARTED"
        }

    def _generate_intent_envelope(self):
        """
        Generates the intent part of the envelope, which is located inside the request envelope.
        :return: Dictionary containing the intent envelope.
        """
        return {
            'name': self._intent_name,
            'confirmationStatus': "NONE",
            'slots': self._generate_slots_envelope(),
        }

    def _generate_slots_envelope(self):
        """
        Generates the slot part of the envelope, which is located inside the intent envelope.
        :return: Dictionary containing the slot envelope.
        """
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
        """
        Creates a default launch-intent request envelope.
        :return: Dictionary containing the envelope to be sent to the skill.
        """
        return AlexaRequestBuilder().new_session(True).make()

    @staticmethod
    def create_intent_request(intent_name, slots=None):
        """
        Creates a default intent request envelope.
        :param intent_name: Name of the target intent.
        :param slots: Dictionary containing the slot's name and value as key and value.
        :return: Dictionary containing the envelope to be sent to the skill.
        """
        slots = slots or {}
        request_builder = AlexaRequestBuilder().new_session(False).intent(intent_name)
        for slot_name, slot_value in slots.items():
            request_builder = request_builder.slot(slot_name, slot_value)
        return request_builder.make()


class AskTestClient:

    def __init__(self, client, skill_route='/'):
        """
        Initializes the Ask test client.
        :param client: Client to make requests with. Originally designed to work with Flask test client.
        :param skill_route: Route where your skill is served within the Flask app.
        """
        self.client = client
        self.skill_route = skill_route

    def perform_launch(self):
        """
        Tests a Launch intent.
        :return: AlexaResponse with the information returned from the server.
        """
        request = AlexaRequestFactory.create_launch_request()
        return self.perform_request(request)

    def perform_intent(self, intent_name, slots=None):
        """
        Tests an Intent with/without slots.
        :param intent_name: Name of the intent you want to test.
        :param slots: Dictionary containing the slots the Intent admits.
        :return: AlexaResponse with the information returned from the server.
        """
        slots = slots or {}
        request = AlexaRequestFactory.create_intent_request(intent_name, slots=slots)
        return self.perform_request(request)

    def perform_request(self, request):
        """
        Sends a request to the endpoint where the skill is served.
        :param request: Alexa message envelope.
        :return: AlexaResponse with the information returned from the server.
        """
        return AlexaResponse(self.client.post(self.skill_route,
                                              data=json.dumps(request),
                                              headers={'Accept': 'application/json', 'Content-Type': 'application/json'}
                                              ))


class AlexaResponse:

    def __init__(self, raw_response):
        """
        Alexa response for accessing useful data easily.
        :param raw_response: Raw response object. Can be either requests's 'Response' object or Flask Response.
        """
        self.raw_response = raw_response
        if hasattr(raw_response, 'data'):
            self.response = json.loads(raw_response.data)  # Flask test client
        else:
            self.response = raw_response.json()  # requests client

    @property
    def text(self):
        """
        Text representing Alexa's reply.
        :return: Alexa's reply.
        """
        return self.response.get('response', {}) \
            .get('outputSpeech', {}) \
            .get('text', None)

    @property
    def reprompt(self):
        """
        Reprompt's text.
        :return: Reprompt's text.
        """
        return self.response.get('response', {}) \
            .get('reprompt', {}) \
            .get('outputSpeech', {}) \
            .get('text', None)

    @property
    def ends_session(self):
        """
        Whether the session has finished or not.
        :return: True if the session is considered to be over. False on the contrary.
        """
        return self.response.get('response', {}).get('shouldEndSession', True)

    @property
    def session_attributes(self):
        """
        Attributes stored in the session.
        :return: Dictionary of attributes.
        """
        return self.response.get('sessionAttributes', {})

    @property
    def status_code(self):
        """
        Response's HTTP status code.
        :return: Status code.
        """
        return self.raw_response.status_code
