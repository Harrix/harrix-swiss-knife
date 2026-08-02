# -*- coding: utf-8 -*-
from pathlib import Path
import re

p = Path(__file__).resolve().parent.parent / "app/src/main/res/values-ru/strings.xml"
t = p.read_text(encoding="utf-8")
replacements = {
    "settings_appearance_title": "Оформление",
    "settings_language_system": "Системный",
    "settings_theme_system": "Системная",
    "settings_theme_light": "Светлая",
    "settings_theme_dark": "Тёмная",
}
for key, value in replacements.items():
    t = re.sub(
        rf'(<string name="{key}">)[^<]*(</string>)',
        rf"\g<1>{value}\g<2>",
        t,
    )
p.write_text(t, encoding="utf-8")
print("ru appearance strings updated")
