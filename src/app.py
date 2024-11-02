#!/usr/bin/python3
from abc import ABC

import tornado.ioloop
import tornado.web
import tornado.netutil
import tornado.httpserver
import tornado.httpclient

import os
import signal
import subprocess
from datetime import datetime
import isodate

import json


startup_timestamp = datetime.now()


class HealthHandler(tornado.web.RequestHandler, ABC):
    # noinspection PyAttributeOutsideInit
    def initialize(self):
        self.git_version = self._load_git_version()

    @staticmethod
    def _load_git_version():
        v = None

        # try file git-version.txt first
        gitversion_file = "git-version.txt"
        if os.path.exists(gitversion_file):
            with open(gitversion_file) as f:
                v = f.readline().strip()

        # if not available, try git
        if v is None:
            try:
                v = subprocess.check_output(["git", "describe", "--always", "--dirty"],
                                            cwd=os.path.dirname(__file__)).strip().decode()
            except subprocess.CalledProcessError as e:
                print("Checking git version lead to non-null return code ", e.returncode)

        return v

    def get(self):
        health = dict()
        health['api_version'] = 'v0'

        if self.git_version is not None:
            health['git_version'] = self.git_version

        health['timestamp'] = isodate.datetime_isoformat(datetime.now())
        health['uptime'] = isodate.duration_isoformat(datetime.now() - startup_timestamp)

        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(health, indent=4))
        self.set_status(200)


class Oas3Handler(tornado.web.RequestHandler, ABC):
    def get(self):
        self.set_header("Content-Type", "text/plain")
        # This is the proposed content type,
        # but browsers like Firefox try to download instead of display the content
        # self.set_header("Content-Type", "text/vnd.yml")
        with open('OAS3.yml', 'r') as f:
            oas3 = f.read()
            self.write(oas3)
        self.finish()


def make_app():
    version_path = r"/v[0-9]"
    return tornado.web.Application([
        (version_path + r"/health", HealthHandler),
        (version_path + r"/oas3", Oas3Handler),
    ])


def load_env(key, default):
    if key in os.environ:
        return os.environ[key]
    else:
        return default


signal_received = False


def main():
    arg_port = load_env('PORT', 8080)

    # Setup

    app = make_app()
    sockets = tornado.netutil.bind_sockets(arg_port, '')
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)

    port = None

    for s in sockets:
        print('Listening on %s, port %d' % s.getsockname()[:2])
        if port is None:
            port = s.getsockname()[1]

    ioloop = tornado.ioloop.IOLoop.instance()

    def register_signal(sig, _frame):
        # noinspection PyGlobalUndefined
        global signal_received
        print("%s received, stopping server" % sig)
        server.stop()  # no more requests are accepted
        signal_received = True

    def stop_on_signal():
        # noinspection PyGlobalUndefined
        global signal_received
        if signal_received:
            ioloop.stop()
            print("IOLoop stopped")

    tornado.ioloop.PeriodicCallback(stop_on_signal, 1000).start()
    signal.signal(signal.SIGTERM, register_signal)
    print("Starting server")

    global signal_received
    while not signal_received:
        try:
            ioloop.start()
        except KeyboardInterrupt:
            print("Keyboard interrupt")
            register_signal(signal.SIGTERM, None)

    # Teardown

    print("Server stopped")


if __name__ == "__main__":
    main()
