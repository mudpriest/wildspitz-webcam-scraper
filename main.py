"""
Webcam Scraper

Usage:
    main.py [-w WEBCAM] [-q QUALITY] [-b BEGIN] [-e END] [-i INTERVAL]

Options:
-h, --help                        help

-w WEBCAM, --webcam WEBCAM        Select either 'wildspitz' or 'rigi' webcam
-q QUALITY, --quality QUALITY     Quality of the Image (full, default, half, quarter, eight)

-b BEGIN, --begin BEGIN           First image you want to download (hh-mm) or (YYYY-MM-DD_hh-mm)
-e END, --end END                 Last image you want to download (hh-mm) or (YYYY-MM-DD_hh-mm)
-i INTERVAL, --interval INTERVAL  Interval in minute steps (min. 10 min, and can only be increased in 10 min steps)
"""
import os
import json
from typing import List
from datetime import datetime, timedelta

from docopt import docopt

from scraper.request import create_url, ThreadedFetcher


curr_dir_path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(curr_dir_path, 'webcams.json'), 'r') as webcam_json:
    WEBCAMS = json.load(webcam_json)

QUALITIES = ['full', 'default', 'half', 'quarter', 'eight']


def main():
    # argument parsing
    args = docopt(__doc__, help=True)
    short_time_format = '%H-%M'
    time_format = '%Y-%m-%d_%H-%M'

    # settings default values
    start_time = datetime.now()
    end_time = datetime.now()
    interval = 10
    webcam_link = WEBCAMS['wildspitz']
    webcam_name = 'wildspitz'

    if args['--begin']:
        try:
            if len(args['--begin']) > 5:
                start_time = datetime.strptime(args['--begin'], time_format)
            else:
                new_time = datetime.strptime(args['--begin'], short_time_format)
                start_time = start_time.replace(
                    hour=new_time.hour, minute=new_time.minute
                )
                # should by default only download one image
                end_time = start_time
        except ValueError:
            print('Start parameter did not contain correct date format')

    if args['--end']:
        try:
            if len(args['--end']) > 5:
                end_time = datetime.strptime(args['--end'], time_format)
            else:
                new_time = datetime.strptime(args['--end'], short_time_format)
                end_time = end_time.replace(hour=new_time.hour, minute=new_time.minute)
        except ValueError:
            print('End parameter did not contain correct date format')

    if args['--interval']:
        interval = int(args['--interval'])
        if interval == 0:
            raise ValueError('Interval must at least be 10 minutes')
        elif interval % 10 > 0:
            raise ValueError('Interval can only be a value divisible by 10')

    if args['--webcam']:
        webcam_name = str(args['--webcam']).lower()

        if webcam_name not in WEBCAMS:
            raise ValueError('No valid Webcam was selected')

        webcam_link = WEBCAMS[webcam_name]

    # default quality is 'default'
    quality = QUALITIES[1]
    if args['--quality']:
        quality = str(args['--quality'])
        if quality not in QUALITIES:
            raise ValueError(f'Quality must be one of: {", ".join(QUALITIES)}')

    start_time = start_time.replace(
        minute=start_time.minute - (start_time.minute % 10), second=0, microsecond=0
    )

    total = (end_time - start_time) // timedelta(minutes=interval) + 1
    print(
        f'Downloading {max(total, 0)} image(s) for {webcam_name} ({quality}) '
        f'from {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M}. '
        'Each request is followed by a 10 s pause, this may take a while.'
    )

    # max 3 threads at a time
    active_threads: List = []
    while start_time <= end_time:
        if len(active_threads) < 3:
            t = ThreadedFetcher(
                create_url(webcam_link, start_time, quality), start_time, webcam_name
            )
            t.start()
            start_time += timedelta(minutes=interval)
            active_threads.append(t)
        else:
            active_threads[0].join()
            active_threads.pop(0)

    for t in active_threads:
        t.join()
    print('Done.')


if __name__ == '__main__':
    main()
