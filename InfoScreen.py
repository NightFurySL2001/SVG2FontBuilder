from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton

from kivy.properties import (
    ObjectProperty,
    StringProperty,
)

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp

from MDWarningSnackbar import MDWarningSnackbar

from localization import _

from datetime import date

Builder.load_file("InfoScreen.kv")

# page 2
class InfoScreen(MDScreen):
    # object to access text field
    info_lang = ObjectProperty()
    add_info_lang_btn = ObjectProperty()
    font_name = ObjectProperty()
    font_style = ObjectProperty()
    font_full_name = ObjectProperty()
    version_num_maj = ObjectProperty()
    version_num_min = ObjectProperty()
    version_text = ObjectProperty()
    copyright = ObjectProperty()
    license = ObjectProperty()
    license_url = ObjectProperty()
    trademark = ObjectProperty()
    designer_name = ObjectProperty()
    designer_url = ObjectProperty()
    vendor_code = ObjectProperty()
    vendor_url = ObjectProperty()
    manufacturer_name = ObjectProperty()
    description = ObjectProperty()
    sample_text = ObjectProperty()

    # code for current language
    current_info_lang_code = StringProperty()
    added_lang = ["en"]
    # menu for choosing langauge
    info_lang_menu = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

        # bind shortcut
        keyboard = Window.request_keyboard(self._keyboard_released, self)
        keyboard.bind(on_key_down=self._keyboard_on_key_down, on_key_up=self._keyboard_released)

        # initialise standard name in main app
        familyName = "My Font"
        styleName = "Regular"

        self.app.font_setup["names"] = dict(
            familyName = dict(en=familyName),
            styleName = dict(en=styleName),
            typographicFamily = dict(en=familyName),
            typographicSubfamily = dict(en=styleName),
            uniqueFontIdentifier = dict(en="SVG2FontBuilder:" + familyName + "-" + styleName),
            fullName = dict(en=familyName + "-" + styleName),
            psName = dict(en=familyName + "-" + styleName),
            version = dict(en="Version 1.000; {}; SVG2FontBuilder".format(date.today().strftime("%Y%m%d"))),
        )
        self.app.font_setup["headVersion"] = 1.000
        self.app.font_setup["OS_2VendID"] = ""

    # temporary variable to save the lang code chosen in menu
    dialog_current_selection = ""
    def show_add_info_lang_dialog(self):
        """
        Show the add font info language dialog.
        """
        # reset dialog selection
        self.dialog_current_selection == ""
        # dropdown button to show menu
        self.info_lang_dropdownbtn = MDDropDownItem(
            size_hint_x= 1,
            size_hint_y=None,
            on_release=lambda _: self.show_add_info_lang_menu(),
        )
        # show dialog
        self.info_lang_dialog = MDDialog(
            title=_("Add a new language"),
            type="custom",
            content_cls=MDBoxLayout(
                self.info_lang_dropdownbtn,
                orientation="vertical",
                spacing="12dp",
                padding="12dp",
                size_hint_y=0,
            ),
            buttons=[
                MDFlatButton(
                    text=_("CANCEL"),
                    theme_text_color="Custom",
                    text_color=self.app.theme_cls.primary_color,
                    on_release=lambda _: self.info_lang_dialog.dismiss(),
                ),
                MDFlatButton(
                    text=_("OK"),
                    theme_text_color="Custom",
                    text_color=self.app.theme_cls.primary_color,
                    on_release=lambda _: self.add_info_lang(),
                ),
            ],
        )
        self.info_lang_dialog.open()
    
    def show_add_info_lang_menu(self):
        """
        Show new language dropdown menu
        """
        # if not self.info_lang_add_menu: # no need because need to refresh items
        self.info_lang_add_menu = MDDropdownMenu(
            caller=self.info_lang_dropdownbtn,
            items=[
                # only languages that are not added yet
                {"text": name, "viewclass": "OneLineListItem", "on_release": lambda x=langcode: self.set_info_lang(x)} 
                for langcode, name in self.display_langname.items()
                if langcode not in self.added_lang
            ],
            width_mult=8,
            size_hint_y= None,
            height=0,
            max_height=dp(224),
        )
        self.info_lang_add_menu.open()

    def set_info_lang(self, info_lang_code):
        """
        Set the current selected font language, but does not trigger UI update
        """
        # dismiss add menu
        self.info_lang_add_menu.dismiss()
        # save selected language code
        self.dialog_current_selection = info_lang_code
        # update dropdown menu text choice
        self.info_lang_dropdownbtn.text = self.display_langname[info_lang_code]

    def add_info_lang(self):
        """
        Add the selected lang code into selected language list and update UI to new language
        """
        # dismiss dialog
        self.info_lang_dialog.dismiss()

        # skip if no language selected
        if self.dialog_current_selection == "":
            return
        
        # if new language code
        if self.dialog_current_selection not in self.added_lang:
            # add language to added list
            self.added_lang.append(self.dialog_current_selection)
            # refresh list items
            info_lang_menu_items = [
                {"text": self.display_langname[langcode], "viewclass": "OneLineListItem", "on_release": lambda x=langcode: self.set_info_lang(x)} 
                for langcode in self.added_lang
            ]
            self.info_lang_menu = MDDropdownMenu(
                caller=self.info_lang,
                items=info_lang_menu_items,
                width_mult=6,
                size_hint_y= None,
                height=0,
                max_height=dp(168),
            )

        # reset dialog selection
        self.dialog_current_selection == ""
        # change current language
        self.current_info_lang_code = self.dialog_current_selection
        self.info_lang.text = self.display_langname[self.current_info_lang_code]
        # call ui update function
        self.update_info_lang()
    
    def update_info_lang(self):
        """
        Update the language fields to current language code, blank fields if new language
        """
        lang_code = self.current_info_lang_code
        for id, field in [
            ("familyName", self.font_name),
            ("styleName", self.font_style),
            ("fullName", self.font_full_name),
            ("version", self.version_text),
            (0, self.copyright),
            (13, self.license),
            (14, self.license_url),
            (7, self.trademark),
            (9, self.designer_name),
            (12, self.designer_url),
            (11, self.vendor_url),
            (8, self.manufacturer_name),
            (10, self.description),
            (19, self.sample_text),
        ]:
            # skip names that are not existent yet
            if id not in self.app.font_setup["names"]:
                field.text = ""
                field.error = False
                continue

            if lang_code in self.app.font_setup["names"][id]:
                field.text = self.app.font_setup["names"][id][lang_code]
            elif id in ("familyName", "styleName", "fullName"):
                # dont need update these as they are required
                continue
            else:
                field.text = ""
    
    def show_delete_language_dialog(self):
        """
        Show delete language confirmation dialog
        """
        # check if english, do not allow remove english
        if self.current_info_lang_code == "en":
            self.del_en_error = MDDialog(
                title=_("Error"),
                text=_("English name records can not be removed."),
                buttons=[
                    MDFlatButton(
                        text=_("OK"),
                        theme_text_color="Custom",
                        text_color=self.app.theme_cls.primary_color,
                        on_release=lambda _: self.del_en_error.dismiss(),
                    ),
                ],
            )
            self.del_en_error.open()
            return
        
        # warn to confirm delete
        self.del_warning = MDDialog(
            title=_("Warning"),
            text=_("Are you sure you want to remove name records for {}?").format(self.display_langname[self.current_info_lang_code]),
            buttons=[
                MDFlatButton(
                    text=_("CANCEL"),
                    theme_text_color="Custom",
                    text_color=self.app.theme_cls.primary_color,
                    on_release=lambda _: self.del_warning.dismiss(),
                ),
                MDFlatButton(
                    text=_("OK"),
                    theme_text_color="Custom",
                    text_color=self.app.theme_cls.primary_color,
                    on_release=lambda _: self.delete_language(),
                ),
            ],
        )
        self.del_warning.open()
    
    # delete current language
    def delete_language(self):
        # dismiss delete warning message
        self.del_warning.dismiss()
        # get current language code
        lang_code = self.current_info_lang_code
        # delete language code in added list
        self.added_lang.remove(lang_code)
        if len(self.added_lang) == 1:
            # no need dropdown menu if only 1 language
            self.info_lang_menu = None
        else:
            # refresh language list items
            info_lang_menu_items = [
                {"text": self.display_langname[langcode], "viewclass": "OneLineListItem", "on_release": lambda x=langcode: self.set_info_lang(x)} 
                for langcode in self.added_lang
            ]
            # update language list items
            self.info_lang_menu = MDDropdownMenu(
                caller=self.info_lang,
                items=info_lang_menu_items,
                width_mult=6,
                size_hint_y= None,
                height=0,
                max_height=dp(168),
            )
        # delete keys in main setup variable
        for id in [
            "familyName", "styleName", "fullName", "version", 0, 13, 14, 7, 9, 12, 11, 8, 10, 19,
        ]:
            if id not in self.app.font_setup["names"]:
                continue
            elif lang_code in self.app.font_setup["names"][id]:
                del self.app.font_setup["names"][id][lang_code]

        # call set language function, pass default "en" value
        self.set_info_lang("en")
        # trigger ui update
        self.add_info_lang()

    # list of languages
    @property
    def display_langname(self):
        return {
            'en': "English, United States", 
            'zh': "中文，中国大陆 (Chinese, People’s Republic of China)",
            'zh-TW': "中文，臺灣 (Chinese, Taiwan)",
            'zh-HK': "中文，香港 (Chinese, Hong Kong S.A.R.)",
            'zh-MO': "中文，澳門 (Chinese, Macau S.A.R.)",
            'zh-SG': "中文，新加坡 (Chinese, Singapore)",
            'ja': "日本語 (Japanese)",
            'ko': "한국어 (Korean)",
            'fr': "Français, la France (French, France)",
            'es': "español, españa (Spanish, Spain)",
            'de': "Deutsches, Deutschland (German, Germany)",
            'el': "ελληνικά (Greek)",
            'ru': "русский язык (Russian)",
            'uk': "українська (Ukrainian)",
            'ar': "اَلْعَرَبِيَّةُ ، مصر (Arabic, Egypt)",
            'he': "עִברִית (Hebrew)",
            'bo': "བོད་སྐད་ (Tibetan)",
            'ug': "ئۇيغۇر (Uighur)",
            'ii': "ꆈꌠꁱꂷ (Yi)",
            'mn': "Монгол хэл, Монгол Улс (Mongolian (Cyrillic), Mongolia)",
            'mn-CN': "ᠮᠣᠩᠭᠣᠯ ᠬᠡᠯᠡ᠂ ᠪᠦᢉᠦᠳᠡ ᠨᠠᠶᠢᠷᠠᠮᠳᠠᠬᠤ ᠬᠢᠲᠠᠳ ᠠᠷᠠᠳ ᠤᠯᠤᠰ (Mongolian (Traditional), People’s Republic of China)",
        }
        
    def verify_ascii_name(self):
        """
        Verify if the font family name is ASCII for English when typing
        """
        if self.current_info_lang_code != "en":
            return
        text = self.font_name.text
        if text.isascii() and text.isprintable():
            self.font_name.error = False
        else:
            self.font_name.error = True

    # setting font style menu
    def init_style_menu(self):
        font_style_menu_items = [
            {"text": "Regular", "viewclass": "OneLineListItem", "on_release": lambda x="Regular": self.set_style_menu(x),},
            {"text": "Italic", "viewclass": "OneLineListItem", "on_release": lambda x="Italic": self.set_style_menu(x),},
            {"text": "Bold", "viewclass": "OneLineListItem", "on_release": lambda x="Bold": self.set_style_menu(x),},
            {"text": "Bold Italic", "viewclass": "OneLineListItem", "on_release": lambda x="Bold Italic": self.set_style_menu(x),},]
        self.font_style_menu = MDDropdownMenu(
            caller=self.font_style,
            items=font_style_menu_items,
            width_mult=3,
            max_height=dp(224),
        )

    # changing font style
    def set_style_menu(self, style_name):
        self.font_style_menu.dismiss()
        self.font_style.text = style_name

    # for undo, detect key release and clear stored keys
    def _keyboard_released(self, window=None, keycode=None):
        self.super = []

    # for undo, detect key press and store
    def _keyboard_on_key_down(self, window, keycode, text, super):
        if self.app.screen_manager.current == "infoscr2": # only this screen
            if 'lctrl' in self.super and keycode[1] == 's':
                # press ctrl + s
                self.make_name()
                self.super = []
                return False
            elif 'lctrl' not in self.super and keycode[1] in ["lctrl"]:
                self.super.append(keycode[1])
                return False
            # else:
            #     print("key {} pressed.".format(keycode))
            #     return False

    # build name
    def make_name(self):
        langCode = self.current_info_lang_code
        
        familyName = self.font_name.text
        styleName = self.font_style.text
        fullName = self.font_full_name.text

        #double check if name is english
        if langCode == "en":
            if familyName.isascii() and familyName.isprintable():
                pass
            else:
                self.font_name.error = True
                MDWarningSnackbar(
                    text = _("Only ASCII characters are accepted for English names."), icon="alert"
                ).open()
                return

        # get dict
        nameDict = self.app.font_setup["names"]

        #update dict information
        # must have for every language
        for id, text in [
            ("familyName", familyName),
            ("styleName", styleName),
            ("typographicFamily", familyName),
            ("typographicSubfamily", styleName),
            ("uniqueFontIdentifier", "SVG2FontBuilder:" + familyName + "-" + styleName),
            ("fullName", fullName),
            ("psName", fullName),
        ]:
            if langCode != "en" and id in ("uniqueFontIdentifier", "psName"):
                # do not assign unique font identifier and postscript name to non english names
                continue

            if text.strip() != "":
                # assign
                nameDict[id][langCode] = text
            elif langCode != "en" and langCode in nameDict[id]:
                # empty string and has lang code, remove it
                del nameDict[id][langCode]
            elif langCode == "en":
                MDWarningSnackbar(
                    text = _("Please check if all English names are present."), icon="alert"
                ).open()
                return

        # may not have for every language
        for id, field in [
            ("version", self.version_text),
            (0, self.copyright),
            (13, self.license),
            (14, self.license_url),
            (7, self.trademark),
            (9, self.designer_name),
            (12, self.designer_url),
            (11, self.vendor_url),
            (8, self.manufacturer_name),
            (10, self.description),
            (19, self.sample_text),
        ]:
            if field.text.strip() != "":
                # init dictionary if hvnt do it
                if id not in nameDict:
                    nameDict[id] = dict()
                #assign
                nameDict[id][langCode] = field.text
            elif langCode == "en" and id == "version":
                # warn if version string dont have text, return
                self.version_text.error = True
                return
            elif langCode != "en" and id in nameDict and langCode in nameDict[id]:
                # id might not be in nameDict yet (eg id 0)
                # empty string and has lang code, remove it
                del nameDict[id][langCode]
        
        self.app.font_setup["names"] = nameDict
        # only set these two with English
        if langCode == "en":
            self.app.font_setup["headVersion"] = int(self.version_num_maj.text[:3]) + int(self.version_num_min.text[:3]) / 1000
            self.app.font_setup["OS_2VendID"] = self.vendor_code.text
            
        MDWarningSnackbar(
            text = _("Font information saved."),
            icon="content-save",
        ).open()
