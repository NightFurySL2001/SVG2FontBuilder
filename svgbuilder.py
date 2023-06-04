import os, sys, json, re
import traceback
import threading
# temporary fix for infinite looping when packaged by pyinstaller
# https://github.com/kivy/kivy/issues/8074
if sys.__stdout__ is None or sys.__stderr__ is None:
    os.environ['KIVY_NO_CONSOLELOG'] = '1'
    
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog

from kivy.clock import mainthread
from kivy.core.window import Window
from kivy.config import Config
from kivy.resources import resource_add_path
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty

from newfontbuild import build_font

from localization import _, list_languages, change_language_to, \
    current_language, language_code_to_translation

# individual screen & personal modules
from MDWarningSnackbar import MDWarningSnackbar
import SetupScreen
import InfoScreen
import MetricScreen
  

global APP_VERSION
APP_VERSION = "0.1.0"

# update about app
class AboutScreen(MDScreen):
    app_version_tag = StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_version_tag()
    
    def update_version_tag(self):
        self.app_version_tag = _("Version {}  ").format(APP_VERSION) 

class LoadingScreen(MDBoxLayout):
    pass

# Main class
class SVG2FontBuilder(MDApp):
    """The main application window."""
    # dialog during generating font
    loading_dialog = None
    # set icon
    icon = "S2F.png"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # set theme colour
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Yellow"
        self.theme_cls.primary_hue = "A400"
        # initialise setup configurations
        # must be here coz InfoScreen need init font info
        self.font_setup = {}

    # build ui, customisation here
    def build(self):
        # get screen manager
        self.screen_manager = self.root.ids.screen_manager

    # run after finish build() ui
    def on_start(self):
        super().on_start()

        # load config from file
        self.config.read("svg2fontbuilder.ini")

        # update ui language
        self.update_language_from_config()
        
        # update theme
        config_theme = self.config.get(APP_SECTION, APP_THEME_KEY)
        if config_theme in ["Dark", "Light"]:
            self.theme_cls.theme_style = config_theme

    # default config for settings
    def build_config(self, config, context=None):
        """
        Set the default values for the configs sections.
        """
        self.config.setdefaults(APP_SECTION, {APP_THEME_KEY: "Dark", APP_LANGUAGE_KEY: "en", APP_NORMALIZE_KEY: 1, APP_STRICT_KEY: 1})

    # app settings
    def build_settings(self, settings):
        settings.add_json_panel("Software", self.config, data=self.software_settings_specification)

    # for changing config
    def on_config_change(self, config, section, key, value):
        """The configuration was changed.

        :param kivy.config.ConfigParser config: the configuration that was
          changed
        :param str section: the section that was changed
        :param str key: the key in the section that was changed
        :param value: the value this key was changed to
        """
        if section == APP_SECTION and key == APP_LANGUAGE_KEY:
            change_language_to(value)
    
    # update labels
    def update_language_from_config(self):
        """Set the current language from the configuration.
        """
        config_language = self.config.get(APP_SECTION, APP_LANGUAGE_KEY)
        change_language_to(config_language)

    @property
    def software_settings_specification(self):
        """The settings specification as JSON string.

        :rtype: str
        :return: a JSON string
        """
        settings = [
            {
                "type": "options",
                "title": _("Theme"),
                "desc": _("Choose your theme"),
                "section": APP_SECTION,
                "key": APP_THEME_KEY,
                "options": ["Dark", "Light"],
            },
            {
                "type": "options",
                "title": _("Language"),
                "desc": _("Choose your language"),
                "section": APP_SECTION,
                "key": APP_LANGUAGE_KEY,
                "options": {code: language_code_to_translation(code) for code in list_languages()},
            },
            {
                "type": "bool",
                "title": _("Normalize SVG"),
                "desc": _("Normalize SVG before processing with picoSVG. Includes tracing strokes and clip paths to normal paths."),
                "section": APP_SECTION,
                "key": APP_NORMALIZE_KEY,
            },
            {
                "type": "bool",
                "title": _("Strict mode"),
                "desc": _("When reading from CSV file, ignore SVG files that are not listed in the CSV file."),
                "section": APP_SECTION,
                "key": APP_STRICT_KEY,
            },
        ]
        return json.dumps(settings)

    # for threading
    thread = None

    @mainthread
    def build_font_done(self, state, setupscreen, logs):
        self.loading_dialog.dismiss()
        # update setup screen with logs
        setupscreen.log_label.text = logs

        # popup for success failure
        if state == "pass":
            MDWarningSnackbar(
                text = _("Font generated! Location: {}").format(
                                self.font_setup["sources"]["out"]
                ),
                icon="check-bold",
            ).open()
            return
        
        MDWarningSnackbar(
            text = _("Font building failed."), icon="alert"
        ).open()
        
    def build_font(self, setupscreen: SetupScreen.SetupScreen):
        """
            Call to show loading dialog and start threading.
            Input SetupScreen (MDScreen class) to show log.
        """
        # initialise loading dialog
        if not self.loading_dialog:
            self.loading_dialog = MDDialog(
                size_hint=(.5, None),
                auto_dismiss=False,
                type="custom",
                content_cls=LoadingScreen(),
            )
        # show dialog
        self.loading_dialog.open()

        # start thread, pass argument thru it
        self.thread = threading.Thread(target=self.build_font_thread, args=(setupscreen,)).start()

    # font building method in thread
    def build_font_thread(self, setupscreen):
        """
            Build the font (using new thread)
            Include error reporting
        """
        try:
            logs = build_font(
                self.font_setup["sources"]["SVG"],
                self.font_setup["sources"]["CSV"],
                self.font_setup["sources"]["use_CSV"],
                self.font_setup["names"],
                self.font_setup["headVersion"],
                self.font_setup["sources"]["out"],
                metrics = self.font_setup["metrics"],
                vendorCode = self.font_setup["OS_2VendID"],
                picoNormalize = bool(int(self.config.get(APP_SECTION, APP_NORMALIZE_KEY))),
                strictMode = bool(int(self.config.get(APP_SECTION, APP_STRICT_KEY))),
            )

        except UnicodeEncodeError as ex:
            # get full traceback
            full_ex_string = traceback.format_exc()

            # more info for specific errors

            # match if warning about CFF name
            # eg: UnicodeEncodeError: 'ascii' codec can't encode characters in position 0-4: ordinal not in range(128)
            if re.search("'ascii' codec can't encode characters in position", str(ex)) and "cffLib" in full_ex_string:
                full_ex_string += '\nOnly ASCII characters are accepted for English names.\n'
                if current_language() != "en":
                    full_ex_string += _('Only ASCII characters are accepted for English names.')
                    full_ex_string += "\n"

            # output full string
            self.build_font_done("fail", setupscreen, full_ex_string)
            return

        except UnicodeDecodeError as ex:
            # get full traceback
            full_ex_string = traceback.format_exc()

            # more info for specific errors

            # match if warning about utf-8 file opening
            # eg: UnicodeDecodeError: 'utf-8' codec can't decode byte 0xd7 in position 3: invalid continuation byte
            if re.search("'utf-8' codec can't decode byte", str(ex)):
                full_ex_string += '\nPlease check your files are encoded using UTF-8 (especially CSV file!).\n'
                if current_language() != "en":
                    full_ex_string += _('Please check your files are encoded using UTF-8 (especially CSV file!).')
                    full_ex_string += "\n"

            # output full string
            self.build_font_done("fail", setupscreen, full_ex_string)
            return
        
        except ValueError as ex:
            # get full traceback
            full_ex_string = traceback.format_exc()

            # more info for specific errors

            # match if warning about internal style block (picosvg)
            # eg: ValueError: Unable to convert to picosvg: BadElement: /svg[0]/style[0]
            if re.search("/style\[\d+\]\s*$", str(ex)):
                full_ex_string += '\nIf you are using Adobe Illustrator, please use "Export As..." instead of "Save As...".\n'
                if current_language() != "en":
                    full_ex_string += _('If you are using Adobe Illustrator, please use "Export As..." instead of "Save As...".')
                    full_ex_string += "\n"
        
            # match if warning about image (picosvg)
            # eg: ValueError: Unable to convert to picosvg: BadElement: /svg[0]/image[0]
            if re.search("/image\[\d+\]\s*$", str(ex)):
                full_ex_string += '\nBitmap images are not allowed in SVG files.\n'
                if current_language() != "en":
                    full_ex_string += _('Bitmap images are not allowed in SVG files.')
                    full_ex_string += "\n"

            # output full string
            self.build_font_done("fail", setupscreen, full_ex_string)
            return
        
        except Exception:
            # generic exception, dont use except to catch KeyboardInterrupt
            full_ex_string = traceback.format_exc()
            self.build_font_done("fail", setupscreen, full_ex_string)
            return

        else:
            # no exception
            self.build_font_done("pass", setupscreen, logs)
            return


# Settings key
APP_SECTION = "UI Behaviour"  #: section name
APP_THEME_KEY = "theme"  #: theme
APP_LANGUAGE_KEY = "language"  #: language code name
APP_NORMALIZE_KEY = "normalize" #: strictly svg filenames in csv only
APP_STRICT_KEY = "strict" #: strictly svg filenames in csv only

Window.size = (1000, 600)
# disable right click multitouch simulation
# https://stackoverflow.com/questions/12692851/why-does-right-clicking-create-an-orange-dot-in-the-center-of-the-circle
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

# main program call
if __name__ == '__main__':
    try:
        if hasattr(sys, '_MEIPASS'):
            resource_add_path(os.path.join(sys._MEIPASS))
        app = SVG2FontBuilder()
        app.run()
    except Exception as e:
        print(e)
        input("Press enter.")