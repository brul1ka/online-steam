from textual.app import App
from textual.widgets import Static, Input
from textual.containers import Container
from textual import on
import requests

class MyApp(App):
    CSS = """
        #output {
            padding: 1;
        }
        #loading {
            dock: bottom;
            align: center middle;
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

    def on_mount(self):
        loading_widget = self.query_one("#loading", Static)
        loading_widget.update("Loading list of games...")
        self.apps = self.get_games_list()
        loading_widget.update("Game list loaded successfully.")

    @on(Input.Submitted)
    def on_game_input_submitted(self, event: Input.Submitted):
        user_game = event.value

MyApp().run()
