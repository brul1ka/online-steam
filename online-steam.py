import requests

appid = 367520  # Hollow Knight - just for a test

# getting the number of players at the moment
url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}"
response = requests.get(url)
data = response.json()
player_count = data['response']['player_count']

# getting app list with appid and their names
app_list_url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
app_list_response = requests.get(app_list_url)
apps_data = app_list_response.json()

# getting app name
app_name = None
for app in apps_data['applist']['apps']:
    if app['appid'] == appid:
        app_name = app['name']
        break

print(f"{app_name} current players: {player_count}")
