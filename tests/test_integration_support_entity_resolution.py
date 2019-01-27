import unittest

from flask_ask import Ask, statement
from flask import Flask

from flask_ask.test import AskTestClient


class CustomSlotTypeIntegrationTests(unittest.TestCase):
    """ Integration tests of the custom slot type """

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['ASK_VERIFY_REQUESTS'] = False
        self.ask = Ask(app=self.app, route='/ask')
        self.request_client = self.app.test_client()
        self.client = AskTestClient(self.request_client, skill_route='/ask')

        @self.ask.intent('TestCustomSlotTypeIntents')
        def custom_slot_type_intents(child_info):
            return statement(child_info)

    def tearDown(self):
        pass

    def test_custom_slot_type_intent(self):
        """ Test to see if custom slot type value is correct """
        response = self.client.perform_intent("TestCustomSlotTypeIntents", slots={'child_info': "friend_info"})
        self.assertEqual(200, response.status_code)
        self.assertEqual('friend_info',response.text)


if __name__ == '__main__':
    unittest.main()
