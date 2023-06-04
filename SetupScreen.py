
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.app import MDApp

from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfilename
from kivy.properties import (
    ObjectProperty, 
    BooleanProperty
)

from kivy.lang import Builder

from MDWarningSnackbar import MDWarningSnackbar

from localization import _

import os

Builder.load_file("SetupScreen.kv")

# page 1
class SetupScreen(MDScreen):
    svg_folder_path = ObjectProperty()
    csv_file_path = ObjectProperty()
    use_csv = BooleanProperty()
    log_label = ObjectProperty()
    csv_info_dialog = None

    def on_click_svg_folder(self):
        path = askdirectory(
            title=_("Choose SVG folder"),
            mustexist=True
        )
        if path == "" and self.svg_folder_path.text.strip() == "":
            self.svg_folder_path.error = True
        else:
            self.svg_folder_path.text = path
            self.svg_folder_path.error = False

    def on_click_csv_file(self):
        path = askopenfilename(
            title=_("Choose CSV file"),
            filetypes=[(_("CSV file (.csv)"), "*.csv"), (_("Text file (.txt)"), "*.txt"), (_("All files"), "*")]
        )
        if path == "" and self.csv_file_path.text.strip() == "":
            self.csv_file_path.error = True
        else:
            self.csv_file_path.text = path
            self.csv_file_path.error = False

    def show_csv_info_dialog(self):
        if not self.csv_info_dialog:
            self.csv_info_dialog = MDDialog(
                text=_("""A comma-separated file containing a list of SVG filenames and their corresponding character/glyph name.\nExample: `Artboard 1.svg, uni0041`"""),
                buttons=[
                    MDFlatButton(
                        text=_("OK"),
                        theme_text_color="Custom",
                        text_color=MDApp.get_running_app().theme_cls.primary_color,
                        on_release=lambda _: self.csv_info_dialog.dismiss(),
                    ),
                ],
            )
        self.csv_info_dialog.open()

    def start_building(self):
        """
        Main function when click on "Generate" button
        """
        # verify preconditions are met
        svgpath = self.svg_folder_path.text
        csvfile = self.csv_file_path.text
        
        if not os.path.isdir(svgpath):
            MDWarningSnackbar(
                text=_("SVG folder does not exist."), icon="alert"
            ).open()
            self.svg_folder_path.error = True
            return
        elif not os.path.isfile(csvfile) and bool(self.use_csv):
            MDWarningSnackbar(
                text=_("CSV file does not exist."), icon="alert"
            ).open()
            self.csv_file_path.error = True
            return

        # get filename
        try:
            otffile = asksaveasfilename(
                title=_("Save font file to"),
                defaultextension='.',
                filetypes=[(_("OpenType/CFF font (.otf)"), "*.otf"), (_("All files"), "*")],
            )
            if otffile == "":
                raise ValueError
            if not otffile.lower().endswith(".otf"):
                otffile += ".otf"
        except ValueError:
            MDWarningSnackbar(
                text=_("No save location chosen. Font is not generated."), icon="alert"
            ).open()
            return
        
        # save into app dict
        app = MDApp.get_running_app()
        app.font_setup["sources"] = {
            "SVG": svgpath,
            "CSV": csvfile,
            "use_CSV": bool(self.use_csv),
            "out": otffile,
        }

        # call main app building function
        app.build_font(self)