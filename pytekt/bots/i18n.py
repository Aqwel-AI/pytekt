"""
Internationalization (i18n) Engine for PyTekt Bots.
Provides multi-language string lookup, JSON/YAML locale loading, and placeholder interpolation.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

logger = logging.getLogger("pytekt.bots.i18n")


class I18nManager:
    """
    Manages multi-language translations and string interpolation.

    Parameters
    ----------
    default_lang : str
        Fallback language code (default 'en').
    """

    def __init__(self, default_lang: str = "en") -> None:
        self.default_lang = default_lang.lower().strip()
        self.translations: Dict[str, Dict[str, Any]] = {}

    def add_translations(self, lang: str, table: Dict[str, Any]) -> None:
        """Add a translation mapping table for a specific language."""
        code = lang.lower().strip()
        if code not in self.translations:
            self.translations[code] = {}
        self.translations[code].update(table)

    def load_directory(self, dir_path: Union[str, Path]) -> None:
        """
        Load all JSON / YAML translation files from a directory.
        Files should be named like en.json, es.json, ru.json, fr.yaml.
        """
        p = Path(dir_path)
        if not p.is_dir():
            logger.warning("Translation directory not found: %s", dir_path)
            return

        for f in p.iterdir():
            if f.suffix.lower() == ".json":
                lang_code = f.stem.lower()
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    if isinstance(data, dict):
                        self.add_translations(lang_code, data)
                except Exception as e:
                    logger.error("Failed to load translation file %s: %s", f, e)
            elif f.suffix.lower() in (".yaml", ".yml"):
                lang_code = f.stem.lower()
                try:
                    import yaml
                    data = yaml.safe_load(f.read_text(encoding="utf-8"))
                    if isinstance(data, dict):
                        self.add_translations(lang_code, data)
                except Exception as e:
                    logger.error("Failed to load translation file %s: %s", f, e)

    def _resolve_nested_key(self, table: Dict[str, Any], key: str) -> Optional[str]:
        """Lookup key with dot-notation support ('menu.buttons.start')."""
        if key in table and isinstance(table[key], str):
            return table[key]

        parts = key.split(".")
        curr: Any = table
        for part in parts:
            if isinstance(curr, dict) and part in curr:
                curr = curr[part]
            else:
                return None
        return curr if isinstance(curr, str) else None

    def translate(
        self,
        key: str,
        lang: Optional[str] = None,
        default_lang: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        Lookup translated string with fallback and string interpolation.

        Parameters
        ----------
        key : str
            Translation key (e.g. 'welcome' or 'menu.help').
        lang : str, optional
            Target language code (e.g. 'es', 'fr', 'en_US').
        default_lang : str, optional
            Fallback language if target language has no match.
        **kwargs : Any
            Named parameters to interpolate into the template string (e.g. name='Alice').
        """
        fallback_lang = (default_lang or self.default_lang).lower().strip()
        target_lang = (lang or fallback_lang).lower().strip()

        # Handle 'en-US' / 'en_US' -> try 'en-us', 'en_us', and 'en'
        lang_candidates = [target_lang]
        if "-" in target_lang:
            lang_candidates.append(target_lang.split("-")[0])
        elif "_" in target_lang:
            lang_candidates.append(target_lang.split("_")[0])

        template_str: Optional[str] = None

        # 1. Try target language candidates
        for lc in lang_candidates:
            if lc in self.translations:
                template_str = self._resolve_nested_key(self.translations[lc], key)
                if template_str is not None:
                    break

        # 2. Try default fallback language
        if template_str is None and fallback_lang in self.translations:
            template_str = self._resolve_nested_key(self.translations[fallback_lang], key)

        # 3. If still not found, return the key itself
        if template_str is None:
            template_str = key

        # 4. Interpolate variables
        if kwargs:
            try:
                return template_str.format(**kwargs)
            except Exception:
                return template_str

        return template_str
