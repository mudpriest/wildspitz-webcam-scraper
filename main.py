"""
Webcam Scraper

Usage:
    main.py [-w WEBCAM] [-q QUALITY] [-b BEGIN] [-e END] [-i INTERVAL]

Options:
-h, --help                        help

-w WEBCAM, --webcam WEBCAM        Select either 'wildspitz' or 'rigi' webcam
-q QUALITY, --quality QUALITY     Quality of the Image (full, default, half, quarter, medium)

-b BEGIN, --begin BEGIN           First image you want to download (hh-mm) or (YYYY-MM-DD_hh-mm)
-e END, --end END                 Last image you want to download (hh-mm) or (YYYY-MM-DD_hh-mm)
-i INTERVAL, --interval INTERVAL  Interval in minute steps (min. 10 min, and can only be increased in 10 min steps)
"""
import os
import sys
import json
from typing import List
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from docopt import docopt

from scraper.request import create_url, image_path, download_image


curr_dir_path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(curr_dir_path, 'webcams.json'), 'r') as webcam_json:
    WEBCAMS = json.load(webcam_json)

QUALITIES = ['full', 'default', 'half', 'quarter', 'medium']


def parse_time(value: str, base: datetime, option: str) -> datetime:
    """Parse 'YYYY-MM-DD_hh-mm', or 'hh-mm' on the date of `base`."""
    try:
        if len(value) > 5:
            return datetime.strptime(value, '%Y-%m-%d_%H-%M')
        t = datetime.strptime(value, '%H-%M')
        return base.replace(hour=t.hour, minute=t.minute)
    except ValueError:
        sys.exit(f'{option} must be hh-mm or YYYY-MM-DD_hh-mm, got {value!r}')


def main():
    args = docopt(__doc__, help=True)

    now = datetime.now()
    start_time = now
    end_time = now
    interval = 10
    webcam_name = 'wildspitz'

    if args['--begin']:
        start_time = parse_time(args['--begin'], now, '--begin')
        if len(args['--begin']) <= 5:
            # by default only download one image
            end_time = start_time

    if args['--end']:
        # a short end time takes its date from the start time
        end_time = parse_time(args['--end'], start_time, '--end')

    if args['--interval']:
        try:
            interval = int(args['--interval'])
        except ValueError:
            sys.exit('Interval must be an integer')
        if interval < 10:
            sys.exit('Interval must at least be 10 minutes')
        if interval % 10:
            sys.exit('Interval can only be a value divisible by 10')

    if args['--webcam']:
        webcam_name = str(args['--webcam']).lower()
        if webcam_name not in WEBCAMS:
            sys.exit(f'No valid Webcam was selected, use one of: {", ".join(WEBCAMS)}')
    webcam_link = WEBCAMS[webcam_name]

    # default quality is 'default'
    quality = QUALITIES[1]
    if args['--quality']:
        quality = str(args['--quality'])
        if quality not in QUALITIES:
            sys.exit(f'Quality must be one of: {", ".join(QUALITIES)}')

    start_time = start_time.replace(
        minute=start_time.minute - (start_time.minute % 10), second=0, microsecond=0
    )
    if end_time < start_time:
        sys.exit('End time must not be before start time')

    # only fetch images that are not on disk yet
    pending: List[datetime] = []
    skipped = 0
    t = start_time
    while t <= end_time:
        if image_path(webcam_name, t, quality).exists():
            skipped += 1
        else:
            pending.append(t)
        t += timedelta(minutes=interval)

    print(
        f'{webcam_name} ({quality}) {start_time:%Y-%m-%d %H:%M} to '
        f'{end_time:%Y-%m-%d %H:%M}: {len(pending)} image(s) to download, '
        f'{skipped} already downloaded (skipped).'
    )
    if pending:
        print('Each request is followed by a 10 s pause, this may take a while.')

    # max 3 downloads at a time
    with ThreadPoolExecutor(max_workers=3) as pool:
        for dt in pending:
            pool.submit(
                download_image, create_url(webcam_link, dt, quality), dt, webcam_name, quality
            )
    print('Done.')


if __name__ == '__main__':
    main()
