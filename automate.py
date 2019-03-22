from boxsdk import OAuth2
from boxsdk import Client
import bottle
import os
import csv
from threading import Thread, Event
import webbrowser
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler, make_server

CLIENT_ID = "olimcmrgn874vgamn5m1t0g0fmaxmx38"
CLIENT_SECRET = "plmjJcE9JpSrQjJZU1GOYjz8yQzbAcBF"
def authenticate(oauth_class=OAuth2):
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
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
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


# def convert_to_csv(users):
#     with open('users_space.csv', mode='w') as csv_file:
#         fieldnames = ['employee name', 'uid', 'total space', 'space used', 'percentage used']
#         writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#         writer.writeheader()
#         for user in users:



oauth = authenticate()
client = Client(oauth[0])
print('Getting Box Users')
enterprise_users = client.users()
# convert_to_csv(enterprise_users)
for user in enterprise_users:
    print(user, "\n\t space amount: ", user.space_amount, "\n\t space used:", user.space_used
      , "\n\t percentage used: ", user.space_used/user.space_amount * 100)
# print (enterprise_users)

