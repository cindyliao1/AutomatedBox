from boxsdk import OAuth2

import bottle
import os
import csv
from threading import Thread, Event
import webbrowser
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler, make_server


class Automate:

    def __init__(self, C_ID, C_secret):
        self.CLIENT_ID = C_ID
        self.CLIENT_SECRET = C_secret

    def authenticate(self, oauth_class=OAuth2):
        class StoppableWSGIServer(bottle.ServerAdapter):
            def __init__(self, *args, **kwargs):
                super(StoppableWSGIServer, self).__init__(*args, **kwargs)
                self._server = None

            def run(self, app):
                server_cls = self.options.get('server_class', WSGIServer)
                handler_cls = self.options.get('handler_class', WSGIRequestHandler)
                self._server = make_server(self.host, self.port, app, server_cls, handler_cls)
                self._server.serve_forever()

            def stop(self):
                self._server.shutdown()

        auth_code = {}
        auth_code_is_available = Event()

        local_oauth_redirect = bottle.Bottle()

        @local_oauth_redirect.get('/')
        def get_token():
            auth_code['auth_code'] = bottle.request.query.code
            auth_code['state'] = bottle.request.query.state
            auth_code_is_available.set()

        local_server = StoppableWSGIServer(host='localhost', port=8080)
        server_thread = Thread(target=lambda: local_oauth_redirect.run(server=local_server))
        server_thread.start()

        oauth = oauth_class(
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET,
        )
        auth_url, csrf_token = oauth.get_authorization_url('http://localhost:8080')
        webbrowser.open(auth_url)

        auth_code_is_available.wait()
        local_server.stop()
        assert auth_code['state'] == csrf_token
        access_token, refresh_token = oauth.authenticate(auth_code['auth_code'])

        print('access_token: ' + access_token)
        print('refresh_token: ' + refresh_token)

        return oauth, access_token, refresh_token


    # convert_to_csv(enterprise_users)
    # for user in enterprise_users:
    #     print(user, "\n\t space amount: ", user.space_amount, "\n\t space used:", user.space_used
    #       , "\n\t percentage used: ", user.space_used/user.space_amount * 100)
    # print (enterprise_users)
    def write(self, users):
        with open('space_usage.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['User ID', 'User Name', 'Space amount', 'Space used', 'Percentage used'])
            for user in users:
                writer.writerow([user.id, user.name, user.space_amount, user.space_used, user.space_used/user.space_amount * 100])
