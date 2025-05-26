from textual.app import App
from textual.widgets import Static, Input, ListView, ListItem, Label
from textual.containers import Container
from textual import on
import requests
import asyncio


class OnlineSteam(App):
    CSS = """
        #game_input {
            border: wide round #983bbb;
            background: black;
        }

        #loading {
            dock: bottom;
            align: center bottom;
            padding: 1;
            color: yellow;
        }

        #lists_and_output {
            layout: horizontal;
            height: 20;
            margin: 1;
        }

        #assumed_game_list {
            width: 60;
            border: round #b55dd6;
            padding: 1;
        }

        #output {
            border: round #9902d1;
            padding: 1;
            width: 1fr;
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
        yield Static("", id='loading')
        with Container(id="lists_and_output"):
            filter_list_widget = ListView(id='assumed_game_list')
            filter_list_widget.border_title = 'Assumed'
            filter_list_widget.border_subtitle = 'min. 3 symbols'
            yield filter_list_widget
            output_static_widget = Static('', id='output')
            output_static_widget.border_title = 'output'
            yield output_static_widget

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
        appid = self.find_appid(self.apps, user_game)

        if appid is None:
            output.update(f'There is no such game with name: {user_game}.')
            return

        try:
            url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}"
            response = await asyncio.to_thread(requests.get, url)
            data = response.json()
            player_count = data['response'].get('player_count')
            if player_count is not None:
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
                self.filtered_games_list.append(ListItem(Label(app['name'], markup=False)))
            if not filtered:
                self.filtered_games_list.append(ListItem(Label('No suggested games')))
        else:
            self.filtered_games_list.clear()

    @on(ListView.Selected)
    async def on_filtered_game_selected(self, event: ListView.Selected):
        if event.list_view.id != 'assumed_game_list':
            return

        selected_item = event.item
        selected_label = selected_item.query_one(Label)
        selected_game_name = selected_label.renderable

        game_input = self.query_one('#game_input', Input)

        submit_event = Input.Submitted(game_input, selected_game_name)
        await self.on_game_input_submitted(submit_event)


if __name__ == '__main__':
    OnlineSteam().run()
