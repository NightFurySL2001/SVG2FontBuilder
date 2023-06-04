from kivymd.uix.snackbar import BaseSnackbar

from kivy.properties import StringProperty, NumericProperty
from kivy.core.window import Window
from kivy.metrics import dp

class MDWarningSnackbar(BaseSnackbar):
    text = StringProperty()
    icon = StringProperty()
    font_size = NumericProperty("15sp")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.snackbar_x = "10dp"
        self.snackbar_y = "10dp"
        self.size_hint_x = (Window.width - (dp(10) * 2)) / Window.width