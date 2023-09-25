from translations.placeholder_translations import available_placeholder_translations
import os

class Translator:

    def __init__(self):
        self.system_language = os.getenv("LANG").split(".")[0]
        # self.system_language = "en_US"

    def get_translation(self, string: str):
        # get the dictionary of the current locale if exist or return the default one otherwise
        locale_dictionary = available_placeholder_translations.get(self.system_language, available_placeholder_translations["en_US"])
        # return the translated string or the default one in case the string doesn't exist.
        translated_string = locale_dictionary.get(string, available_placeholder_translations["en_US"][string])
        return translated_string

