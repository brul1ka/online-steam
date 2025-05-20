import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


class SteamApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)

        self.info_label = Label(text="Loading game list...", size_hint_y=0.2)
        self.add_widget(self.info_label)

        self.input = TextInput(hint_text="Enter game name", multiline=False, size_hint_y=0.2)
        self.add_widget(self.input)

        self.button = Button(text="Check player count", size_hint_y=0.2)
        self.button.bind(on_press=self.get_players)
        self.add_widget(self.button)

        self.result = Label(text="", size_hint_y=0.4)
        self.add_widget(self.result)

        self.apps = []
        self.load_app_list()

    def load_app_list(self):
        try:
            url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
            response = requests.get(url)
            data = response.json()
            self.apps = data['applist']['apps']
            self.info_label.text = "Game list loaded successfully"
        except:
            self.info_label.text = "Failed to load game list"

    def find_appid(self, name):
        for app in self.apps:
            if app['name'].lower() == name.lower():
                return app['appid']
        return None

    def get_players(self, instance):
        game_name = self.input.text.strip()
        if not game_name:
            self.result.text = "Please enter a game name."
            return

        appid = self.find_appid(game_name)
        if appid is None:
            self.result.text = "Game not found."
            return

        try:
            url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}"
            response = requests.get(url)
            data = response.json()
            player_count = data['response'].get('player_count')

            if player_count is not None:
                self.result.text = f"{game_name} has {player_count:,} current players."
            else:
                self.result.text = "Could not retrieve player count."
        except Exception as e:
            self.result.text = f"Error: {e}"


class SteamAppChecker(App):
    def build(self):
        return SteamApp()


if __name__ == '__main__':
    SteamAppChecker().run()
