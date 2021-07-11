import zipfile
import os
import json
from pathlib import Path
from glob import glob
from bs4 import BeautifulSoup
from pydub import AudioSegment

bundle_path = os.path.dirname(os.path.abspath(__file__))
AUDIO_FILE_NAME = 'full_audio.mp3'
TEXT_FILE_NAME = 'deck.json'
AOZORA_TIMESTAMP_FILE = 'item/js/p-001.xhtml.smil.js'
AOZORA_TEXT_FILE = 'item/xhtml/p-001.xhtml'

def cut_audio(mp3_file, audio_timestamp, target_directory):
    song = AudioSegment.from_mp3(mp3_file)
    begin = float(audio_timestamp['begin'])*1000
    end = float(audio_timestamp['end'])*1000
    extract = song[begin:end]
    extract.export(Path(target_directory, audio_timestamp['id'] + '.mp3'), format="mp3")

def unpack_audio_from_epub(file, target_directory):
    with zipfile.ZipFile(file) as zip:
        for zip_info in zip.infolist():
            if zip_info.filename[-1] == '/':
                continue
            if 'm4a' in zip_info.filename:
                print('m4a detected. Exporting to mp3')
                zip_info.filename = 'temp.m4a'
                zip.extract(zip_info, target_directory)
                m4a_audio = AudioSegment.from_file(str(Path(target_directory, 'temp.m4a')), "m4a")
                m4a_audio.export(str(Path(target_directory, AUDIO_FILE_NAME)), format="mp3")
                os.remove(Path(target_directory, 'temp.m4a'))
                return str(Path(target_directory, AUDIO_FILE_NAME))
            if 'mp3' in zip_info.filename:
                zip_info.filename = AUDIO_FILE_NAME
                zip.extract(zip_info, target_directory)
                return str(Path(target_directory, AUDIO_FILE_NAME))

def get_audio_timestamps(file):
    items = []
    archive = zipfile.ZipFile(file, 'r')
    with archive.open(AOZORA_TIMESTAMP_FILE) as f:
        data = f.read()
        a = data.decode("utf-8").split('window.rb_smil_emulator.smil_data = [')[1].split(']')[0]
        timestamps = a.replace('\n', '').split('},')
        for timestamp in timestamps:
            item = {}
            item["id"] = timestamp.split("id: '")[1].split("',")[0]
            item["begin"] = timestamp.split("begin:")[1].split(",")[0]
            item["end"] = timestamp.split("end:")[1].split(' ')[0]
            if item["id"][0] == 'f':
                items.append(item)
    return items

def get_audio_timestamps_map(file):
    items_map = {}
    archive = zipfile.ZipFile(file, 'r')
    with archive.open(AOZORA_TIMESTAMP_FILE) as f:
        data = f.read()
        a = data.decode("utf-8").split('window.rb_smil_emulator.smil_data = [')[1].split(']')[0]
        timestamps = a.replace('\n', '').split('},')
        for timestamp in timestamps:
            item = {}
            item["id"] = timestamp.split("id: '")[1].split("',")[0]
            item["begin"] = timestamp.split("begin:")[1].split(",")[0]
            item["end"] = timestamp.split("end:")[1].split(' ')[0]
            if item["id"][0] == 'f':
                items_map[item["id"]] = item
    return items_map

def get_text(file):
    archive = zipfile.ZipFile(file, 'r')
    with archive.open(AOZORA_TEXT_FILE) as f:
        data = f.read()
        soup = BeautifulSoup(data, 'html.parser')
        # TODO: get spaces with paragraphs
        items = []
        audio_timestamps_map = get_audio_timestamps_map(file)
        # print(audio_timestamps_map)
        for span in soup.find_all('span'):
            if span.get("id"):
                if span.get("id")[0] == 'f':
                    item = {
                    "id": span.get("id"), 
                    "sentence": parse_sentence_to_anki_format(span.decode_contents().strip())["sentence"],
                    "sentence_with_furigana": parse_sentence_to_anki_format(span.decode_contents().strip())["sentence_with_furigana"],
                    } 
                    if item["id"] in audio_timestamps_map:
                        item["audio_begin"] = int(float(audio_timestamps_map[item["id"]]['begin'])*1000)
                        item["audio_end"] = int(float(audio_timestamps_map[item["id"]]['end'])*1000)
                    items.append(item)
        return items

def remove_class_from_sentence(s):
    if 'class=' in s:
        if '<' in s:
            pre = s.split('<')[0]
            content = s.split('>')[1].split('<')[0]
            post = s.split('>')[len(s.split('>'))-1]
            return pre + content + post
        else:
            print('parsing failed for ', s)
    return s

def parse_sentence_to_anki_format(s):
    pre = s.split("<ruby>")[0]
    objects_to_parse = s.split("<ruby>")
    temp_furigana = ""
    temp_sentence = ""
    for obj in objects_to_parse:
        if "</ruby>" in obj:
            parsed = " " + obj.split("<rt>")[0] + "[" + obj.split("<rt>")[1].split("</rt>")[0] + "]"
            obj_post = obj.split("</ruby>")[1]
            without_furigana = obj.split("<rt>")[0]
            temp_furigana += parsed + obj_post
            temp_sentence += without_furigana + obj_post
    sentence_with_furigana = (pre + temp_furigana).strip()
    sentence = (pre + temp_sentence).strip()
    return {
        "sentence": remove_class_from_sentence(sentence),
        "sentence_with_furigana": remove_class_from_sentence(sentence_with_furigana)
    }

def unpack_aozora_epub(file, skip_media=False):
    file_directory = Path(file).parent
    if not skip_media:
        target_directory = Path(file_directory, 'media')
        try:
            os.makedirs(target_directory)    
            print("Directory " , target_directory ,  " Created ")
        except FileExistsError:
            print("Directory " , target_directory ,  " already exists")  
        audio_file = unpack_audio_from_epub(file, target_directory)
        audio_timestamps = get_audio_timestamps(file)
        for audio_timestamp in audio_timestamps:
            print('cutting audio', audio_timestamp['id'])
            cut_audio(audio_file, audio_timestamp, target_directory)
    text_objects = get_text(file)
    with open(Path(file_directory, TEXT_FILE_NAME), 'w', encoding='utf-8') as f:
        json.dump(text_objects, f, indent=4, ensure_ascii=False)

def unpack_all(skip_media=True):
    deck_folders = glob(str(Path(bundle_path, 'resources', 'literature')) + '/*/')
    for deck_folder in deck_folders:
        deck_name = Path(deck_folder).name
        print('parsing', deck_name)
        unpack_aozora_epub(Path(bundle_path, 'resources', 'literature', deck_name, deck_name + '.epub'), skip_media)


unpack_all()
# name = "Ashi"
# file = Path(bundle_path, 'resources', 'literature', name, name + '.epub')
# unpack_aozora_epub(file, skip_media=True)