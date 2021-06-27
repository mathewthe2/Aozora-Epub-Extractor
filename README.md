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
Add the epub file with its parent folder under */resources*.

```python
from main import unpack_aozora_epub
directory_name = "Akatonbo"
file_name = "Akatonbo.epub"
file = Path(bundle_path, 'resources', 'literature', directory_name, file_name)
unpack_aozora_epub(file)
```
