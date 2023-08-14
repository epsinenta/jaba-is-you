import json
import threading
from pathlib import Path

from typing import Final, Optional, List

LANGUAGES_PATH: Final[Path] = Path("./lang/")


class LanguageError(Exception):
    def __init__(self, language: str, *args):
        super().__init__(*args)
        self.language: str = language

    def __str__(self):
        result = f"Language Error with language: {self.language}"
        return result


class LanguageFileError(LanguageError):
    """Error with language file. That error should not be caught. If that error occurs then language file is invalid"""


class LanguageManager:
    def __init__(self):
        self._current_language_file: Optional[Path] = None
        self._parse_thread: Optional[threading.Thread] = None
        self._language_strings: Optional[dict] = None

    def _parse_json(self):
        with open(self._current_language_file, "rb") as file:
            data = file.read()
        self._language_strings: dict = json.loads(data)
        if not self._language_strings:
            raise LanguageFileError(f"Language file {self._current_language_file.with_suffix('')} is empty")
        if not isinstance(self._language_strings, dict):
            raise LanguageFileError(f"Language file {self._current_language_file.with_suffix('')} is invalid")

    @property
    def available_languages(self) -> List[str]:
        return [language_file_path.stem for language_file_path in LANGUAGES_PATH.glob("*.json")]

    @property
    def current_language(self) -> Optional[str]:
        if self._current_language_file is None:
            return None
        return self._current_language_file.name

    @current_language.setter
    def current_language(self, value: str):
        self._current_language_file = LANGUAGES_PATH / f"{value.lower()}.json"
        if not self._current_language_file.exists():
            raise LanguageError(
                f"File with language {self._current_language_file.name} not found. Maybe language is invalid?\n"
                f"All available languages:\n"
                "\n".join(self.available_languages),
            )
        self._parse_thread = threading.Thread(target=self._parse_json)
        self._parse_thread.start()

    def __getitem__(self, item: str) -> str:
        if self._current_language_file is None:
            raise NotImplementedError("Set current language first")
        if self._parse_thread is not None and self._parse_thread.is_alive():
            self._parse_thread.join(timeout=0.2)
            if self._parse_thread.is_alive():
                return ""
        if self._language_strings is None:
            raise RuntimeError("Can't get language strings. "
                               "Most likely some error occurred while processing the language file")
        return str(self._language_strings[item])
