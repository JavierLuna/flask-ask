"""
Smoke test using the samples.
"""

import unittest
import os
import six
import sys
import time
import subprocess

from requests import post

import flask_ask
from flask_ask.test import AskTestClient


project_root = os.path.abspath(os.path.join(flask_ask.__file__, '../..'))


@unittest.skipIf(six.PY2, "Not yet supported on Python 2.x")
class SmokeTestUsingSamples(unittest.TestCase):
    """ Try launching each sample and sending some requests to them. """

    def setUp(self):
        self.python = sys.executable
        self.env = {'PYTHONPATH': project_root,
                    'ASK_VERIFY_REQUESTS': 'false'}
        if os.name == 'nt':
            self.env['SYSTEMROOT'] = os.getenv('SYSTEMROOT')
            self.env['PATH'] = os.getenv('PATH')

        self.host = 'http://127.0.0.1'
        self.port = 5000
        self.url = "{host}:{port}".format(host=self.host, port=self.port)

        class SmokeRequestClient:
            @staticmethod
            def post(skill_route, data=None, **kwargs):
                data = data or {}
                return post(self.url+skill_route, data=data, **kwargs)

        self.SmokeRequestClient = SmokeRequestClient

        self.test_client = AskTestClient(SmokeRequestClient)

    def _launch(self, sample):
        prefix = os.path.join(project_root, 'samples/')
        path = prefix + sample
        process = subprocess.Popen([self.python, path], env=self.env)
        time.sleep(1)
        self.assertIsNone(process.poll(),
                          msg='Poll should work,'
                          'otherwise we failed to launch')
        self.process = process

    @staticmethod
    def _get_reprompt(http_response):
        data = http_response.json()
        return data.get('response', {})\
                   .get('reprompt', {})\
                   .get('outputSpeech', {})\
                   .get('text', None)

    def tearDown(self):
        try:
            self.process.terminate()
            self.process.communicate(timeout=1)
        except Exception as e:
            try:
                print('[%s]...trying to kill.' % str(e))
                self.process.kill()
                self.process.communicate(timeout=1)
            except Exception as e:
                print('Error killing test python process: %s' % str(e))
                print('*** it is recommended you manually kill with PID %s',
                      self.process.pid)

    def test_helloworld(self):
        """ Test the HelloWorld sample project """
        self._launch('helloworld/helloworld.py')
        launch_response = self.test_client.perform_launch()
        self.assertTrue('hello' in launch_response.text)

    def test_session_sample(self):
        """ Test the Session sample project """
        self._launch('session/session.py')
        launch_response = self.test_client.perform_launch()
        self.assertTrue('favorite color' in launch_response.text)

    def test_audio_simple_demo(self):
        """ Test the SimpleDemo Audio sample project """
        self._launch('audio/simple_demo/ask_audio.py')
        launch_response = self.test_client.perform_launch()
        self.assertTrue('audio example' in launch_response.text)

    def test_audio_playlist_demo(self):
        """ Test the Playlist Audio sample project """
        self._launch('audio/playlist_demo/playlist.py')
        launch_response = self.test_client.perform_launch()
        self.assertTrue('playlist' in launch_response.text)

    def test_blueprints_demo(self):
        """ Test the sample project using Flask Blueprints """
        self._launch('blueprint_demo/demo.py')
        self.test_client = AskTestClient(self.SmokeRequestClient, skill_route='/ask')
        launch_response = self.test_client.perform_launch()
        self.assertTrue('hello' in launch_response.text)

    def test_history_buff(self):
        """ Test the History Buff sample """
        self._launch('historybuff/historybuff.py')
        launch_response = self.test_client.perform_launch()
        self.assertTrue('History buff' in launch_response.text)

    def test_spacegeek(self):
        """ Test the Spacegeek sample """
        self._launch('spacegeek/spacegeek.py')
        launch_response = self.test_client.perform_launch()
        # response is random
        self.assertTrue(len(launch_response.text) > 1)

    def test_tidepooler(self):
        """ Test the Tide Pooler sample """
        self._launch('tidepooler/tidepooler.py')
        launch_response = self.test_client.perform_launch()
        self.assertTrue('Which city' in launch_response.reprompt)
