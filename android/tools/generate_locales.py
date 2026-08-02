import os
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
from deep_translator import GoogleTranslator
import concurrent.futures
import time

# Paths
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'src', 'main', 'res'))
SOURCE_XML = os.path.join(ROOT_DIR, 'values', 'strings.xml')

LOCALES = {
    'ru': 'ru',
    'es': 'es',
    'de': 'de',
    'fr': 'fr',
    'pt': 'pt',
    'zh-rCN': 'zh-CN',
    'ja': 'ja',
    'it': 'it'
}

# Strings that should not be translated
UNTRANSLATED_KEYS = {
    'app_name',
    'about_author',
    'about_license',
    'about_github_label',
    'settings_gallery_cleaner_title',
    'settings_video_cleaner_title',
    'gallery_cleaner_title',
    'video_cleaner_title',
    'nav_drawer_gallery_cleaner',
    'nav_drawer_video_cleaner'
}

def protect_text(text):
    placeholders = []
    
    for match in re.finditer(r'%\d+\$[sd]', text):
        placeholders.append(match.group(0))
        text = text.replace(match.group(0), f'__PH{len(placeholders)-1}__')
        
    if '\\n' in text:
        placeholders.append('\\n')
        text = text.replace('\\n', f'__PH{len(placeholders)-1}__')
        
    if "\\'" in text:
        placeholders.append("\\'")
        text = text.replace("\\'", f'__PH{len(placeholders)-1}__')
        
    brands = ['Gallery Cleaner', 'Video Cleaner', 'Harrix Swiss Knife', 'Harrix', 'MIT License', 'GitHub']
    for brand in brands:
        if brand in text:
            placeholders.append(brand)
            text = text.replace(brand, f'__PH{len(placeholders)-1}__')
            
    return text, placeholders

def restore_text(text, placeholders):
    for i, ph in enumerate(placeholders):
        text = text.replace(f'__PH{i}__', ph)
        text = text.replace(f'__ PH{i} __', ph)
        text = text.replace(f'__ PH {i} __', ph)
        text = text.replace(f'__PH {i}__', ph)
        text = text.replace(f'_ _PH{i}_ _', ph)
        text = text.replace(f'__ph{i}__', ph)
        text = text.replace(f'__ ph{i} __', ph)
    return text

def translate_string(name, text, target_lang_code):
    if not text:
        return name, text
        
    if name in UNTRANSLATED_KEYS:
        return name, text
        
    protected_text, placeholders = protect_text(text)
    
    try:
        if protected_text.strip() and not re.fullmatch(r'(__PH\d+__\s*)+', protected_text.strip()):
            translator = GoogleTranslator(source='en', target=target_lang_code)
            translated_protected = translator.translate(protected_text)
            final_text = restore_text(translated_protected, placeholders)
            return name, final_text
        else:
            return name, restore_text(protected_text, placeholders)
    except Exception as e:
        print(f"Error translating '{name}' to {target_lang_code}: {e}", flush=True)
        return name, text

def translate_xml(source_path, target_lang_code):
    tree = ET.parse(source_path)
    root = tree.getroot()
    
    strings_to_translate = []
    for string_elem in root.findall('string'):
        strings_to_translate.append((string_elem.get('name'), string_elem.text))
        
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(translate_string, name, text, target_lang_code): name for name, text in strings_to_translate}
        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            try:
                res_name, res_text = future.result()
                results[res_name] = res_text
            except Exception as exc:
                print(f"'{name}' generated an exception: {exc}", flush=True)
                
    for string_elem in root.findall('string'):
        name = string_elem.get('name')
        if name in results:
            string_elem.text = results[name]
            
    return tree

def main():
    if not os.path.exists(SOURCE_XML):
        print(f"Source XML not found: {SOURCE_XML}")
        return
        
    for locale_dir, lang_code in LOCALES.items():
        print(f"Translating to {locale_dir} ({lang_code})...", flush=True)
        
        target_dir = os.path.join(ROOT_DIR, f'values-{locale_dir}')
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, 'strings.xml')
        
        translated_tree = translate_xml(SOURCE_XML, lang_code)
        
        xml_str = ET.tostring(translated_tree.getroot(), encoding='utf-8', method='xml').decode('utf-8')
        
        parsed = minidom.parseString(xml_str)
        pretty_xml = parsed.toprettyxml(indent="    ")
        
        pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
        
        if not pretty_xml.startswith('<?xml'):
            pretty_xml = '<?xml version="1.0" encoding="utf-8"?>\n' + pretty_xml
            
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
            
        print(f"Saved {target_path}", flush=True)

if __name__ == '__main__':
    main()
