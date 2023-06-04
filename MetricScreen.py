from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

from kivy.properties import (
    ObjectProperty,
)

from kivy.core.window import Window, Keyboard
from kivy.lang import Builder
from kivy.metrics import dp

from MDWarningSnackbar import MDWarningSnackbar

from localization import _

Builder.load_file("MetricScreen.kv")

# page 2
class MetricScreen(MDScreen):
    # MDDropdownMenu object
    font_upm_menu = None
    # MDDialog object
    metric_warning_dialog = None
    # object to access text field
    font_upm = ObjectProperty()
    ascender = ObjectProperty()
    descender = ObjectProperty()
    line_gap = ObjectProperty()
    auto_calc_safebox = ObjectProperty()
    safe_ascender = ObjectProperty()
    safe_descender = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

        # put metric dict to prevent no key error
        self.app.font_setup["metrics"] = None

        # bind shortcut
        keyboard = Window.request_keyboard(self._keyboard_released, self)
        keyboard.bind(on_key_down=self._keyboard_on_key_down, on_key_up=self._keyboard_released)
    
    # auto calculate safe box
    def calc_safe_box(self):
        """
        Auto calculate safe box
        Called when changing ascender/descender value and toggling safebox
        """
        if self.auto_calc_safebox.active == True:
            upm = int(self.font_upm.text or 0)
            scale = upm / 1000
            ascender = int(self.ascender.text or 0)
            descender = int(self.descender.text or 0)

            # shift safe box with ascender/descender height
            self.safe_ascender.text = str(round(upm * 1.1 + ascender - 880 * scale))
            self.safe_descender.text = str(round(upm * 0.25 + descender - 120 * scale))

    # setting font upm menu
    def init_upm_menu(self):
        font_upm_menu_items = [
            {"text": "1000", "viewclass": "OneLineListItem", "on_release": lambda x=1000: self.set_upm_menu(x),},
            {"text": "1024", "viewclass": "OneLineListItem", "on_release": lambda x=1024: self.set_upm_menu(x),},
            {"text": "2048", "viewclass": "OneLineListItem", "on_release": lambda x=2048: self.set_upm_menu(x),},]
        self.font_upm_menu = MDDropdownMenu(
            caller=self.font_upm,
            items=font_upm_menu_items,
            width_mult=3,
            max_height=dp(160),
        )
    
    # changing font upm
    def set_upm_menu(self, upm):
        ori_upm = int(self.font_upm.text or 0)
        # didnt change value
        if upm == ori_upm:
            return
        # calculate values
        scale = upm / ori_upm
        
        new_ascender = round(int(self.ascender.text or 0) * scale)
        new_descender = round(int(self.descender.text or 0) * scale)
        new_linegap = round(int(self.line_gap.text or 0) * scale)
        if self.auto_calc_safebox.active == True:
            # shift safe box with ascender/descender height
            new_safe_ascender = round(upm * 1.1 + new_ascender - 880 * upm / 1000)
            new_safe_descender = round(upm * 0.25 + new_descender - 120 * upm / 1000)
        else:
            new_safe_ascender = round(int(self.safe_ascender.text or 0) * scale)
            new_safe_descender = round(int(self.safe_descender.text or 0) * scale)
        
        # udpate text field
        self.font_upm.text = str(upm)
        self.ascender.text = str(new_ascender)
        self.descender.text = str(new_descender)
        self.line_gap.text = str(new_linegap)
        self.safe_ascender.text = str(new_safe_ascender)
        self.safe_descender.text = str(new_safe_descender)
        
        # check metric and save
        self.prepare_metrics()


    # for undo, detect key release and clear stored keys
    def _keyboard_released(self, window=None, keycode=None):
        self.super = []

    # for undo, detect key press and store
    def _keyboard_on_key_down(self, window, keycode, text, super):
        if self.app.screen_manager.current == "metricscr3": # only this screen
            if 'lctrl' in self.super and keycode[1] == 's':
                # press ctrl + s
                self.prepare_metrics()
                self.super = []
                return False
            elif 'lctrl' not in self.super and keycode[1] in ["lctrl"]:
                self.super.append(keycode[1])
                return False
            # else:
            #     print("key {} pressed.".format(keycode))
            #     return False

    def warn_asc_dsc(self):
        self.metric_warning_dialog.dismiss()
        self.ascender.error = True
        self.descender.error = True

    # build metrics
    def prepare_metrics(self):
        metricDict = {
            "upm": int(self.font_upm.text or 0),
            "ascender": int(self.ascender.text or 0),
            "descender": int(self.descender.text or 0),
            "line_gap": int(self.line_gap.text or 0),
            "safe_ascender": int(self.safe_ascender.text or 0),
            "safe_descender": int(self.safe_descender.text or 0),
        }

        # check value is sensible
        if metricDict["ascender"] > metricDict["upm"] or metricDict["descender"]  > metricDict["upm"]:
            # ascender or descender greater than UPM
            self.metric_warning_dialog = MDDialog(
                title=_("Warning"),
                text=_("Ascender or descender value is greater than UPM value. Are you sure?"),
                buttons=[
                    MDFlatButton(
                        text=_("Continue"),
                        theme_text_color="Custom",
                        text_color=MDApp.get_running_app().theme_cls.primary_color,
                        on_release=lambda _: self.save_metrics(metricDict),
                    ),
                    MDFlatButton(
                        text=_("Fix"),
                        theme_text_color="Custom",
                        text_color=MDApp.get_running_app().theme_cls.primary_color,
                        on_release=lambda _: self.warn_asc_dsc(),
                    ),
                ],
            )
            self.metric_warning_dialog.open()

        elif metricDict["ascender"] + metricDict["descender"] != metricDict["upm"]:
            # ascender + descender doesnt match UPM
            self.metric_warning_dialog = MDDialog(
                title=_("Warning"),
                text=_("Ascender and descender value doesn't sum up to UPM value. This might cause issue in CJK fonts. Are you sure?"),
                buttons=[
                    MDFlatButton(
                        text=_("Continue"),
                        theme_text_color="Custom",
                        text_color=MDApp.get_running_app().theme_cls.primary_color,
                        on_release=lambda _: self.save_metrics(metricDict),
                    ),
                    MDFlatButton(
                        text=_("Fix"),
                        theme_text_color="Custom",
                        text_color=MDApp.get_running_app().theme_cls.primary_color,
                        on_release=lambda _: self.warn_asc_dsc(),
                    ),
                ],
            )
            self.metric_warning_dialog.open()
        else:
            self.save_metrics(metricDict)

    # confirm to save metric
    def save_metrics(self, metricDict):
        # dismiss dialog if there
        if self.metric_warning_dialog is not None:
            self.metric_warning_dialog.dismiss()
        
        # save metric to main app dict
        self.app.font_setup["metrics"] = metricDict
        #inform
        MDWarningSnackbar(
            text = _("Font metrics saved."),
            icon="content-save",
        ).open()