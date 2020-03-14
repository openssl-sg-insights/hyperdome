import os
import sys
import json
import locale
import subprocess
import urllib
import gi
from gi.repository import Nautilus
from gi.repository import GObject

gi.require_version("Nautilus", "3.0")


# Put me in /usr/share/nautilus-python/extensions/
class OnionShareExtension(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        # Get the localized string for "Share via OnionShare" label
        self.label = None
        default_label = "Share via OnionShare"

        try:
            # Re-implement localization in python2
            default_locale = "en"
            locale_dir = os.path.join(sys.prefix, "share/onionshare/locale")
            if os.path.exists(locale_dir):
                # Load all translations
                strings = {}
                translations = {}
                for filename in os.listdir(locale_dir):
                    abs_filename = os.path.join(locale_dir, filename)
                    lang, ext = os.path.splitext(filename)
                    if ext == ".json":
                        with open(abs_filename) as f:
                            translations[lang] = json.load(f)

                strings = translations[default_locale]
                lc, enc = locale.getdefaultlocale()
                if lc:
                    lang = lc[:2]
                    if lang in translations:
                        # if a string doesn't exist, fallback to English
                        for key in translations[default_locale]:
                            if key in translations[lang]:
                                strings[key] = translations[lang][key]

                self.label = strings["share_via_onionshare"]

        except BaseException:
            self.label = default_label

        if not self.label:
            self.label = default_label

    def url2path(self, url):
        file_uri = url.get_activation_uri()
        arg_uri = file_uri[7:]
        path = urllib.url2pathname(arg_uri)
        return path

    def exec_onionshare(self, filenames):
        path = os.path.join(os.sep, "usr", "bin", "onionshare-gui")
        cmd = [path, "--filenames"] + filenames
        subprocess.Popen(cmd)

    def get_file_items(self, _, files):
        menuitem = Nautilus.MenuItem(
            name="OnionShare::Nautilus", label=self.label, tip="", icon=""
        )
        menu = Nautilus.Menu()
        menu.append_item(menuitem)
        menuitem.connect("activate", self.menu_activate_cb, files)
        return (menuitem,)

    def menu_activate_cb(self, menu, files):
        file_list = [self.url2path(file) for file in files]
        self.exec_onionshare(file_list)

    # Workaround https://bugzilla.gnome.org/show_bug.cgi?id=784278
    def get_background_items(self, _, file):
        return None
