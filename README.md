# Wildspitz Webcam Scraper

Downloads Roundshot panorama webcam images (Wildspitz, Rigi) for a time range.

## Instructions

```bash
py -m venv .env
source .env/Scripts/activate   # Windows (Git Bash); on Linux/macOS: source .env/bin/activate
pip install -r requirements.txt

py main.py                                   # latest image, wildspitz, 'default' quality
py main.py -w rigi -q full -b 08-00 -e 12-00 -i 30
py main.py -b 2021-10-11_10-00 -e 12-00      # short end time uses the begin date
py main.py --help
```

Times are `hh-mm` (today) or `YYYY-MM-DD_hh-mm`. The interval is in minutes and must be a multiple of 10.
Images are saved to `images/{webcam}/`; existing files are skipped.
