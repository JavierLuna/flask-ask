import unittest

from flask_ask.test import AskTestClient


class HelloWorldSkillTests(unittest.TestCase):

    def setUp(self):
        from samples.helloworld.helloworld import app
        self.app = app
        self.app.config['ASK_VERIFY_REQUESTS'] = False
        self.request_client = self.app.test_client()
        self.client = AskTestClient(self.request_client, skill_route='/')

    def test_launch(self):
        response = self.client.perform_launch()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "Welcome to the Alexa Skills Kit, you can say hello")
        self.assertFalse(response.ends_session)

    def test_HelloWorldIntent(self):
        response = self.client.perform_intent("HelloWorldIntent")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "Hello world")
        self.assertTrue(response.ends_session)

    def test_AMAZON_HelpIntent(self):
        response = self.client.perform_intent("AMAZON.HelpIntent")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "You can say hello to me!")
        self.assertFalse(response.ends_session)
