import requests

def find_appid(apps, name):
    for app in apps:
        if app['name'].lower() == name.lower():
            return app['appid']
    return None

# get the app list once
print("Loading list of games...")
app_list_url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
app_list_response = requests.get(app_list_url)
apps_data = app_list_response.json()
apps = apps_data['applist']['apps']
print("Game list loaded successfully.")

while True:
    game_name = input("\nEnter a game name (or type 'exit' to quit): ").strip()
    if game_name.lower() == "exit":
        break

    appid = find_appid(apps, game_name)
    if appid is None:
        print("Game not found.")
        continue

    try:
        url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}"
        response = requests.get(url)
        data = response.json()
        player_count = data['response'].get('player_count')

        if player_count is not None:
            print(f"Current number of players for {game_name}: {player_count}")
        else:
            print("Could not retrieve the player count.")
    except Exception as e:
        print("An error occurred while retrieving data:", e)
