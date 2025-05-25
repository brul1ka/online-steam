from textual.app import App
from textual.widgets import Static, Input
from textual.containers import Container
from textual import on
import requests
import asyncio


class MyApp(App):
    CSS = """
        #output {
            padding: 1;
        }
        #loading {
            dock: bottom;
            align: center bottom;
            padding: 1;
        }

    """

    def find_appid(self, apps, name):
        for app in apps:
            if app['name'].lower() == name.lower():
                return app['appid']
        return None

    def get_games_list(self):
        app_list_url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
        app_list_response = requests.get(app_list_url)
        apps_data = app_list_response.json()
        apps = apps_data['applist']['apps']
        return apps

    def compose(self):
        yield Input(placeholder='Enter a game name...', id='game_input')
        yield Static('', id='output')
        yield Static("", id='loading')

    async def on_mount(self):
        loading_widget = self.query_one("#loading", Static)
        loading_widget.update("Loading list of games...")
        self.apps = await asyncio.to_thread(self.get_games_list)
        loading_widget.update("Game list loaded successfully.")

    @on(Input.Submitted)
    async def on_game_input_submitted(self, event: Input.Submitted):
        output = self.query_one("#output", Static)
        user_game = event.value
        appid = self.find_appid(self.apps, user_game)

        if appid is None:
            output.update('There is no such game.')
            return

        try:
            url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}"
            response = await asyncio.to_thread(requests.get, url)
            data = response.json()
            player_count = data['response'].get('player_count')
            if appid and player_count is not None:
                output.update(f'{user_game} — {player_count} players online!')
        except Exception as e:
            output.update(f'Unexpected error: {e}')

MyApp().run()
