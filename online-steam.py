import requests

error_player_count = 25188734
game_name = 'Portal 2' # Portal 2 - for a tests

# getting app list with appid and their names
app_list_url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
app_list_response = requests.get(app_list_url)
apps_data = app_list_response.json()

# getting appid by app name
appid = None
for app in apps_data['applist']['apps']:
    if app['name'] == game_name:
        appid = app['appid']
        break
    else:
        appid = 'no data'

# getting the number of players at the moment
try:
    url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}"
    response = requests.get(url)
    data = response.json()
    player_count = data['response']['player_count']
    if player_count == error_player_count:
        player_count = '!!an error occurred while searching for the game!!'
except KeyError:
    print('No such a game by this appid')
    player_count = 'no data'

print(f"{game_name} current players: {player_count}")
