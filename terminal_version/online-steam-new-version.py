from textual.app import App
from textual.widgets import Static, Input, ListView, ListItem, Label
from textual.containers import Container
from textual import on
import requests
import asyncio


class OnlineSteam(App):
    CSS = """
        #output {
            padding: 1;
        }
        #loading {
            dock: bottom;
            align: center bottom;
            padding: 1;
            color: yellow;
        }
        #assumed_game_list {
            width: 40;
            height: 24;
            dock: right;
            margin: 2 4;
            border: round #b55dd6;
            padding: 1;
        }
        #game_input {
            border: wide round #983bbb;
            background: black;
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

    def filter_games(self, query):
        return [app for app in self.apps if query.lower() in app['name'].lower()]

    def compose(self):
        yield Input(placeholder='Enter a game name...', id='game_input')
        yield Static('', id='output')
        yield Static("", id='loading')
        assumed_game_list = ListView(id='assumed_game_list')
        assumed_game_list.border_title = 'Assumed'
        assumed_game_list.border_subtitle = 'min. 3 symbols'
        yield assumed_game_list

    async def on_mount(self):
        loading_widget = self.query_one("#loading", Static)
        loading_widget.update("Loading list of games...")
        self.apps = await asyncio.to_thread(self.get_games_list)
        loading_widget.update(f"Loaded {len(self.apps)} games successfully.")
        self.filtered_games_list = self.query_one('#assumed_game_list')

    @on(Input.Submitted)
    async def on_game_input_submitted(self, event: Input.Submitted):
        output = self.query_one("#output", Static)
        user_game = event.value
        filtered_games = self.filter_games(user_game)
        filtered_games_list = self.query_one('#assumed_game_list')
        filtered_games_list.clear()
        appid = self.find_appid(self.apps, user_game)

        if appid is None:
            output.update(f'There is no such game with name: {user_game}.')

        try:
            url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}"
            response = await asyncio.to_thread(requests.get, url)
            data = response.json()
            player_count = data['response'].get('player_count')
            if appid and player_count is not None:
                output.update(f'{user_game} — {player_count} players online!')
        except Exception as e:
            output.update(f'Unexpected error: {e}')

    @on(Input.Changed)
    async def filter(self, event: Input.Changed):
        query = event.value
        if len(query) >= 3:
            filtered = [app for app in self.apps if query.lower() in app['name'].lower()]
            self.filtered_games_list.clear()
            for app in filtered[:20]:
                self.filtered_games_list.append(ListItem(Label(app['name'])))
            if not filtered:
                self.filtered_games_list.append(ListItem(Label('No suggested games')))
        else:
            self.filtered_games_list.clear()

if __name__ == '__main__':
    OnlineSteam().run()
