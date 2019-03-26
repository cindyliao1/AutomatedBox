import automate
from boxsdk import Client

CLIENT_ID = "olimcmrgn874vgamn5m1t0g0fmaxmx38"
CLIENT_SECRET = "plmjJcE9JpSrQjJZU1GOYjz8yQzbAcBF"
auto = automate.Automate(CLIENT_ID, CLIENT_SECRET)
oauth = auto.authenticate()
client = Client(oauth[0])
print('Getting Box Users')
enterprise_users = client.users()
auto.write(enterprise_users)