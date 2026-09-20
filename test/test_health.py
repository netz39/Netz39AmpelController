import json

import tornado.testing

from app import make_app


class FakeMqttObserver:
    def __init__(self, loop_running, connected):
        self.loop_running = loop_running
        self.connected = connected

    def is_loop_running(self):
        return self.loop_running

    def is_connected(self):
        return self.connected


class TestHealthHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app(self.observer)

    def setUp(self):
        self.observer = FakeMqttObserver(
            loop_running=True,
            connected=True,
        )
        super().setUp()

    def test_health_when_loop_running_and_connected(self):
        response = self.fetch("/v0/health")

        assert response.code == 200

        body = json.loads(response.body)
        assert body["mqtt_loop_running"] is True
        assert body["mqtt_connected"] is True

    def test_health_when_loop_running_and_disconnected(self):
        self.observer.connected = False

        response = self.fetch("/v0/health")

        assert response.code == 200

        body = json.loads(response.body)
        assert body["mqtt_loop_running"] is True
        assert body["mqtt_connected"] is False

    def test_health_when_loop_not_running(self):
        self.observer.loop_running = False
        self.observer.connected = False

        response = self.fetch("/v0/health")

        assert response.code == 503

        body = json.loads(response.body)
        assert body["mqtt_loop_running"] is False
        assert body["mqtt_connected"] is False

    def test_health_when_loop_not_running_but_connected(self):
        self.observer.loop_running = False
        self.observer.connected = True

        response = self.fetch("/v0/health")

        assert response.code == 503

        body = json.loads(response.body)
        assert body["mqtt_loop_running"] is False
        assert body["mqtt_connected"] is True
