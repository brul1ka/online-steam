import requests
import json
import os
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.utils import platform


class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        # initialize graphics immediately to avoid drawing issues
        Clock.schedule_once(self.update_graphics, 0)

    def update_graphics(self, *args):
        # create rounded button with blue background
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.2, 0.6, 1, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])


class ThemeManager:
    # define color schemes for dark and light themes
    THEMES = {
        'dark': {
            'bg_color': (0.1, 0.1, 0.1, 1),
            'card_color': (0.15, 0.15, 0.15, 1),
            'text_color': (1, 1, 1, 1),
            'accent_color': (0.2, 0.6, 1, 1),
            'button_color': (0.2, 0.6, 1, 1),
            'input_bg': (0.2, 0.2, 0.2, 1)
        },
        'light': {
            'bg_color': (0.95, 0.95, 0.95, 1),
            'card_color': (1, 1, 1, 1),
            'text_color': (0.1, 0.1, 0.1, 1),
            'accent_color': (0.2, 0.6, 1, 1),
            'button_color': (0.2, 0.6, 1, 1),
            'input_bg': (0.9, 0.9, 0.9, 1)
        }
    }

    def __init__(self):
        self.current_theme = 'dark'

    def get_color(self, color_name):
        return self.THEMES[self.current_theme][color_name]

    def switch_theme(self):
        # toggle between dark and light theme
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'


class SettingsPopup(Popup):
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app
        self.title = "Settings"
        self.size_hint = (0.9, 0.8)

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        # theme change section
        theme_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        theme_layout.add_widget(Label(text="Dark Theme", size_hint_x=0.7))

        self.theme_switch = Switch(active=main_app.theme_manager.current_theme == 'dark')
        self.theme_switch.bind(active=self.toggle_theme)
        theme_layout.add_widget(self.theme_switch)
        layout.add_widget(theme_layout)

        # sound effects on/off
        sound_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        sound_layout.add_widget(Label(text="Sound Effects", size_hint_x=0.7))

        self.sound_switch = Switch(active=main_app.settings.get('sound_enabled', True))
        self.sound_switch.bind(active=self.toggle_sound)
        sound_layout.add_widget(self.sound_switch)
        layout.add_widget(sound_layout)

        # auto refresh timer
        refresh_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        refresh_layout.add_widget(Label(text="Auto Refresh (seconds)", size_hint_x=0.7))

        self.refresh_slider = Slider(min=0, max=60, value=main_app.settings.get('auto_refresh', 0),
                                     step=5, size_hint_x=0.3)
        self.refresh_slider.bind(value=self.update_refresh)
        refresh_layout.add_widget(self.refresh_slider)
        layout.add_widget(refresh_layout)

        self.refresh_label = Label(text=f"{int(self.refresh_slider.value)}s",
                                   size_hint_y=None, height=dp(30))
        layout.add_widget(self.refresh_label)

        # close settings button
        close_btn = RoundedButton(text="Save", size_hint_y=None, height=dp(50))
        close_btn.bind(on_press=self.dismiss)
        layout.add_widget(close_btn)

        self.content = layout

    def toggle_theme(self, instance, value):
        # switch between themes when user changes setting
        self.main_app.theme_manager.current_theme = 'dark' if value else 'light'
        self.main_app.apply_theme()
        self.main_app.save_settings()

    def toggle_sound(self, instance, value):
        # turn sound on or off
        self.main_app.settings['sound_enabled'] = value
        self.main_app.save_settings()

    def update_refresh(self, instance, value):
        # change auto refresh time
        self.main_app.settings['auto_refresh'] = int(value)
        self.refresh_label.text = f"{int(value)}s"
        self.main_app.setup_auto_refresh()
        self.main_app.save_settings()


class GameCard(BoxLayout):
    def __init__(self, game_name, player_count, on_favorite=None, is_favorite=False, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=dp(80),
                         spacing=dp(10), padding=[dp(15), dp(10)], **kwargs)

        # game name and player count info
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.8)

        name_label = Label(text=game_name, font_size=dp(16), halign='left',
                           text_size=(None, None), bold=True)
        name_label.bind(texture_size=name_label.setter('text_size'))

        count_label = Label(text=f"{player_count:,} players", font_size=dp(14),
                            halign='left', color=(0.7, 0.7, 0.7, 1))

        info_layout.add_widget(name_label)
        info_layout.add_widget(count_label)
        self.add_widget(info_layout)

        # favorite star button
        fav_btn = Button(text="★" if is_favorite else "☆", size_hint_x=0.2,
                         font_size=dp(20), background_color=(0, 0, 0, 0))
        if on_favorite:
            fav_btn.bind(on_press=lambda x: on_favorite(game_name))
        self.add_widget(fav_btn)


class SteamApp(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_manager = ThemeManager()
        self.settings = self.load_settings()
        self.apps = []
        self.favorites = set(self.settings.get('favorites', []))
        self.search_history = self.settings.get('search_history', [])
        self.auto_refresh_event = None
        self.loading_apps = False

        self.build_ui()
        self.apply_theme()
        self.load_app_list()
        self.setup_auto_refresh()

    def get_app_data_path(self):
        # get correct path for storing app data on different platforms
        if platform == 'android':
            from android.storage import app_storage_path
            return app_storage_path()
        else:
            return os.getcwd()

    def build_ui(self):
        # main app layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # top part with title and settings button
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60))

        title = Label(text="Steam Player Counter", font_size=dp(20), bold=True,
                      size_hint_x=0.8, halign='left')
        title.bind(texture_size=title.setter('text_size'))
        header.add_widget(title)

        settings_btn = Button(text="Settings", size_hint=(None, None), size=(dp(80), dp(50)),
                              background_color=(0.3, 0.3, 0.3, 1), font_size=dp(12))
        settings_btn.bind(on_press=self.show_settings)
        header.add_widget(settings_btn)

        main_layout.add_widget(header)

        # loading status
        self.info_label = Label(text="Loading game list...", size_hint_y=None, height=dp(40),
                                font_size=dp(14))
        main_layout.add_widget(self.info_label)

        # search input and buttons
        search_layout = BoxLayout(orientation='vertical', spacing=dp(10),
                                  size_hint_y=None, height=dp(120))

        self.input = TextInput(hint_text="Enter game name", multiline=False,
                               size_hint_y=None, height=dp(50), font_size=dp(16))
        self.input.bind(text=self.on_text_change)
        search_layout.add_widget(self.input)

        button_layout = BoxLayout(orientation='horizontal', spacing=dp(10),
                                  size_hint_y=None, height=dp(50))

        search_btn = RoundedButton(text="Search", size_hint_x=0.7)
        search_btn.bind(on_press=self.get_players)
        button_layout.add_widget(search_btn)

        clear_btn = Button(text="Clear", size_hint_x=0.3, background_color=(0.8, 0.3, 0.3, 1))
        clear_btn.bind(on_press=self.clear_input)
        button_layout.add_widget(clear_btn)

        search_layout.add_widget(button_layout)
        main_layout.add_widget(search_layout)

        # tabs for results, favorites and history
        accordion = Accordion(orientation='vertical', size_hint_y=0.6)

        # search results tab
        results_item = AccordionItem(title='Search Results')
        self.result_scroll = ScrollView()
        self.result_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        self.result_layout.bind(minimum_height=self.result_layout.setter('height'))
        self.result_scroll.add_widget(self.result_layout)
        results_item.add_widget(self.result_scroll)
        accordion.add_widget(results_item)

        # favorite games tab
        favorites_item = AccordionItem(title='Favorites')
        self.favorites_scroll = ScrollView()
        self.favorites_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        self.favorites_layout.bind(minimum_height=self.favorites_layout.setter('height'))
        self.favorites_scroll.add_widget(self.favorites_layout)
        favorites_item.add_widget(self.favorites_scroll)
        accordion.add_widget(favorites_item)

        # search history tab
        history_item = AccordionItem(title='Recent Searches')
        self.history_scroll = ScrollView()
        self.history_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        self.history_scroll.add_widget(self.history_layout)
        history_item.add_widget(self.history_scroll)
        accordion.add_widget(history_item)

        main_layout.add_widget(accordion)

        self.add_widget(main_layout)
        self.update_favorites_display()
        self.update_history_display()

    def apply_theme(self):
        # change background color based on theme
        Window.clearcolor = self.theme_manager.get_color('bg_color')

    def load_settings(self):
        # load user settings from file
        try:
            settings_path = os.path.join(self.get_app_data_path(), 'steam_app_settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
        return {'theme': 'dark', 'sound_enabled': True, 'auto_refresh': 0,
                'favorites': [], 'search_history': []}

    def save_settings(self):
        # save current settings to file
        self.settings['theme'] = self.theme_manager.current_theme
        self.settings['favorites'] = list(self.favorites)
        self.settings['search_history'] = self.search_history[-20:]  # keep last 20 searches
        try:
            settings_path = os.path.join(self.get_app_data_path(), 'steam_app_settings.json')
            with open(settings_path, 'w') as f:
                json.dump(self.settings, f)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def setup_auto_refresh(self):
        # set up automatic refresh for favorites
        if self.auto_refresh_event:
            self.auto_refresh_event.cancel()

        refresh_interval = self.settings.get('auto_refresh', 0)
        if refresh_interval > 0:
            self.auto_refresh_event = Clock.schedule_interval(
                self.auto_refresh_favorites, refresh_interval)

    def auto_refresh_favorites(self, dt):
        # refresh favorite games automatically
        if self.favorites and not self.loading_apps:
            self.refresh_favorites()

    def show_settings(self, instance):
        # open settings popup
        popup = SettingsPopup(self)
        popup.open()

    def clear_input(self, instance):
        # clear search input and results
        self.input.text = ""
        self.result_layout.clear_widgets()

    def on_text_change(self, instance, text):
        # placeholder for future search suggestions feature
        pass

    def load_app_list(self):
        # load steam games list in background
        def load_in_background(dt):
            if self.loading_apps:
                return

            self.loading_apps = True
            try:
                self.info_label.text = "Loading game database..."
                url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                data = response.json()

                if 'applist' in data and 'apps' in data['applist']:
                    self.apps = data['applist']['apps']
                    Clock.schedule_once(lambda dt: setattr(self.info_label, 'text',
                                                           f"Loaded {len(self.apps)} games successfully"))
                else:
                    raise Exception("Invalid response format")

            except requests.exceptions.RequestException as e:
                error_msg = f"Network error: {str(e)[:30]}..."
                Clock.schedule_once(lambda dt: setattr(self.info_label, 'text', error_msg))
            except Exception as e:
                error_msg = f"Error loading games: {str(e)[:30]}..."
                Clock.schedule_once(lambda dt: setattr(self.info_label, 'text', error_msg))
            finally:
                self.loading_apps = False

        Clock.schedule_once(load_in_background, 0.1)

    def find_appid(self, name):
        # find steam app id by game name
        if not self.apps:
            return None

        name_lower = name.lower().strip()
        if not name_lower:
            return None

        # try exact match first
        for app in self.apps:
            if app.get('name', '').lower() == name_lower:
                return app.get('appid')

        # try partial match if exact not found
        for app in self.apps:
            app_name = app.get('name', '').lower()
            if name_lower in app_name and len(app_name) > 0:
                return app.get('appid')
        return None

    def get_players(self, instance):
        # get current player count for game
        game_name = self.input.text.strip()
        if not game_name:
            self.show_result("Please enter a game name")
            return

        if not self.apps:
            self.show_result("Game database not loaded yet. Please wait.")
            return

        # add to search history
        if game_name not in self.search_history:
            self.search_history.append(game_name)
            self.update_history_display()

        appid = self.find_appid(game_name)
        if appid is None:
            self.show_result(f"Game '{game_name}' not found in database")
            return

        self.show_result("Getting player count...")

        def get_players_background(dt):
            try:
                url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()

                if 'response' in data:
                    player_count = data['response'].get('player_count')
                    if player_count is not None:
                        Clock.schedule_once(lambda dt: self.show_game_result(game_name, player_count))
                        Clock.schedule_once(lambda dt: self.save_settings())
                    else:
                        Clock.schedule_once(lambda dt: self.show_result("Player count not available for this game"))
                else:
                    Clock.schedule_once(lambda dt: self.show_result("Invalid response from Steam API"))

            except requests.exceptions.RequestException as e:
                error_msg = f"Network error: {str(e)[:40]}..."
                Clock.schedule_once(lambda dt: self.show_result(error_msg))
            except Exception as e:
                error_msg = f"Error: {str(e)[:50]}..."
                Clock.schedule_once(lambda dt: self.show_result(error_msg))

        Clock.schedule_once(get_players_background, 0.1)

    def show_result(self, message):
        # show simple text result
        self.result_layout.clear_widgets()
        result_label = Label(text=message, size_hint_y=None, height=dp(60),
                             font_size=dp(14), text_size=(Window.width - dp(40), None),
                             halign='center', valign='middle')
        self.result_layout.add_widget(result_label)

    def show_game_result(self, game_name, player_count):
        # show game result with favorite option
        self.result_layout.clear_widgets()

        card = GameCard(game_name, player_count,
                        on_favorite=self.toggle_favorite,
                        is_favorite=game_name in self.favorites)

        # add rounded background to card
        with card.canvas.before:
            Color(*self.theme_manager.get_color('card_color'))
            card.rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])
        card.bind(pos=self.update_card_bg, size=self.update_card_bg)

        self.result_layout.add_widget(card)

    def update_card_bg(self, instance, *args):
        # update card background when size changes
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size

    def toggle_favorite(self, game_name):
        # add or remove game from favorites
        if game_name in self.favorites:
            self.favorites.remove(game_name)
        else:
            self.favorites.add(game_name)
        self.update_favorites_display()
        self.save_settings()
        # refresh the current result to update star icon
        if hasattr(self, 'result_layout') and self.result_layout.children:
            current_result = self.result_layout.children[0]
            if hasattr(current_result, 'children') and len(current_result.children) > 0:
                fav_btn = current_result.children[0]  # favorite button is last added
                if hasattr(fav_btn, 'text'):
                    fav_btn.text = "★" if game_name in self.favorites else "☆"

    def update_favorites_display(self):
        # refresh favorites list display
        self.favorites_layout.clear_widgets()
        if not self.favorites:
            label = Label(text="No favorites yet", size_hint_y=None, height=dp(50))
            self.favorites_layout.add_widget(label)
            return

        for game_name in sorted(self.favorites):
            btn = Button(text=f"★ {game_name}", size_hint_y=None, height=dp(50),
                         background_color=self.theme_manager.get_color('accent_color'),
                         halign='left')
            btn.bind(texture_size=btn.setter('text_size'))
            btn.bind(on_press=lambda x, name=game_name: self.search_favorite(name))
            self.favorites_layout.add_widget(btn)

    def update_history_display(self):
        # refresh search history display
        self.history_layout.clear_widgets()
        if not self.search_history:
            label = Label(text="No recent searches", size_hint_y=None, height=dp(50))
            self.history_layout.add_widget(label)
            return

        for game_name in reversed(self.search_history[-10:]):  # show last 10 searches
            btn = Button(text=f"• {game_name}", size_hint_y=None, height=dp(50),
                         background_color=(0.3, 0.3, 0.3, 1), halign='left')
            btn.bind(texture_size=btn.setter('text_size'))
            btn.bind(on_press=lambda x, name=game_name: self.search_from_history(name))
            self.history_layout.add_widget(btn)

    def search_favorite(self, game_name):
        # search for favorite game
        self.input.text = game_name
        self.get_players(None)

    def search_from_history(self, game_name):
        # search from history
        self.input.text = game_name
        self.get_players(None)

    def refresh_favorites(self):
        # update player counts for all favorite games
        if not self.apps:
            return

        for game_name in list(self.favorites):
            appid = self.find_appid(game_name)
            if appid:
                try:
                    url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}"
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        player_count = data.get('response', {}).get('player_count')
                        if player_count is not None:
                            # update could be implemented here for live refresh
                            pass
                except Exception as e:
                    print(f"Error refreshing {game_name}: {e}")


class SteamPlayerCounterApp(App):
    def build(self):
        # set window title and icon
        self.title = "Steam Player Counter"
        return SteamApp()

    def on_pause(self):
        # handle app pause on mobile
        return True

    def on_resume(self):
        # handle app resume on mobile
        pass


if __name__ == '__main__':
    SteamPlayerCounterApp().run()