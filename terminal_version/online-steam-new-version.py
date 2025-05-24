from textual.app import App
from textual.widgets import Static, Input
from textual.containers import Container
from textual import on

class MyApp(App):
    CSS = """
        #output {
            padding: 1;
        }
    
    
    """
    def compose(self):
        yield Input(placeholder='Enter a game name...', id='game_input')
        yield Static('', id='output')

    @on(Input.Submitted)
    def on_game_input_submitted(self, event: Input.Submitted):
        user_game = event.value
        output = self.query_one('#output', Static)
        output.update(f"Вы ввели: {user_game}")

MyApp().run()
