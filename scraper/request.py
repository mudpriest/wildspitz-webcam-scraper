import os
import time
from requests import get
from pathlib import Path
from datetime import datetime
from shutil import copyfileobj

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/96.0.4664.110 Safari/537.36'
}


# url is formatted as follows
# https://storage.roundshot.com/5595515f75aba9.83008277/2021-10-11/10-10-00/2021-10-11-10-10-00_full.jpg
def create_url(pre_url: str, dt: datetime, quality: str) -> str:
    date_fragment = f'{dt.year}-{dt.month:02}-{dt.day:02}'
    time_fragment = f'{dt.hour:02}-{dt.minute:02}-00'
    return f'{pre_url}/{date_fragment}/{time_fragment}/{date_fragment}-{time_fragment}_{quality}.jpg'


def image_path(webcam: str, dt: datetime, quality: str) -> Path:
    return Path('images') / webcam / f'{dt:%Y%m%d-%H%M%S}-{quality}.jpg'


def download_image(url: str, dt: datetime, webcam: str, quality: str) -> None:
    img_path = image_path(webcam, dt, quality)
    part_path = img_path.with_name(img_path.name + '.part')
    os.makedirs(img_path.parent, exist_ok=True)

    try:
        print(f'Downloading {url} ...')
        with get(url, stream=True, headers=HEADERS, timeout=30) as response:
            if response.status_code == 200:
                # write to a temp file so an interrupted download is never mistaken for a finished one
                with open(part_path, mode='wb') as img:
                    copyfileobj(response.raw, img)
                os.replace(part_path, img_path)
                print(f"Successfully saved Image in '{img_path}'.")
            else:
                print(f'Skip {url} (status code: {response.status_code})')
    except Exception as e:
        print(f'Could not save Image from {dt}.\n{e}')
        part_path.unlink(missing_ok=True)
    finally:
        # avoid HTTP 429 rate limiting, also after failed requests
        time.sleep(10)
