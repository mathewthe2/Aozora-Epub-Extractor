# Aozora-Epub-Extractor
Extracts sentences and cuts audio for each sentence from [Aozora Epub files](https://aozoraroudoku.jp/epub/index.html).

## Prerequisities

### [ffmpeg](https://www.ffmpeg.org/)

#### Mac
```bash
brew install ffmpeg
```

## Installation

```bash
python -m venv .env
source env/bin/activate
pip install -r requirements.txt
```
## Extracting an epub file
Add the epub file with its parent folder under */resources/literature/*.

```python
from main import unpack_aozora_epub
directory_name = "Akatonbo"
file_name = "Akatonbo.epub"
file = Path(bundle_path, 'resources', 'literature', directory_name, file_name)
unpack_aozora_epub(file)
```

After extraction, you will get
- *deck.json* file contaiing each sentence with extracted furigana and matching id to the audio
- media folder containing al the mp3 files named *[id].mp3* as well as the full mp3 file *full_audio.mp3*

## Options

| Parameter  | Type | Use | Default |
| --------  | ------------------- | --------------------- | --------------------- |
| skip_media | Boolean     | Whether to extract and cut audio  | True
| normalization| Boolean | Whether to replace older writing styles with modern styles | True
