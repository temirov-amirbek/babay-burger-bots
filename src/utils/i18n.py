import os
from typing import Dict
from fluent.runtime import FluentBundle, FluentResource

class I18n:
    def __init__(self, locales_path: str):
        self.locales_path = locales_path
        self.bundles: Dict[str, FluentBundle] = {}
        self._load_locales()

    def _load_locales(self):
        for locale in ["uz", "ru", "en"]:
            path = os.path.join(self.locales_path, f"{locale}.ftl")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    resource = FluentResource(f.read())
                    bundle = FluentBundle([locale])
                    bundle.add_resource(resource)
                    self.bundles[locale] = bundle

    def get(self, locale: str, key: str, **kwargs) -> str:
        bundle = self.bundles.get(locale, self.bundles.get("uz"))
        if not bundle:
            return key
        
        message = bundle.get_message(key)
        if not message or not message.value:
            return key
            
        pattern = message.value
        result, errors = bundle.format_pattern(pattern, kwargs)
        return result

i18n = I18n(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "locales"))
