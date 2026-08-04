# -*- coding: utf-8 -*-
from pathlib import Path
import re

p = Path(__file__).resolve().parent.parent / "app/src/main/res/values-ru/strings.xml"
t = p.read_text(encoding="utf-8")
replacements = {
    "settings_appearance_title": "Оформление",  # ignore: HP001
    "settings_language_system": "Системный",  # ignore: HP001
    "settings_theme_system": "Системная",  # ignore: HP001
    "settings_theme_light": "Светлая",  # ignore: HP001
    "settings_theme_dark": "Тёмная",  # ignore: HP001
}
for key, value in replacements.items():
    t = re.sub(
        rf'(<string name="{key}">)[^<]*(</string>)',
        rf"\g<1>{value}\g<2>",
        t,
    )
p.write_text(t, encoding="utf-8")
print("ru appearance strings updated")
