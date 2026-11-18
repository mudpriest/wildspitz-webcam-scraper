# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

CLI that downloads Roundshot panorama webcam images (Wildspitz, Rigi) for a time range. Dependencies: `requests`, `docopt`. No tests, linter config, or build step.

## Commands

```bash
py -m venv .env
source .env/Scripts/activate
pip install -r requirements.txt

py main.py                                   # latest image, wildspitz, 'default' quality
py main.py -w rigi -q full -b 08-00 -e 12-00 -i 30
py main.py -b 2021-10-11_10-00 -e 2021-10-11_12-00
py main.py --help
```

Times are `hh-mm` (today) or `YYYY-MM-DD_hh-mm`. Interval must be a multiple of 10 minutes (Roundshot captures every 10 min).

## Architecture

- `main.py` — CLI. The module docstring **is** the docopt spec, so changing flags means editing the docstring. Options are declared as bare flags and values are positional (`args['--webcam']` is a bool, the value is in `args['WEBCAM']`). Builds the time loop, rounds the start down to a 10-minute boundary, and runs at most 3 `ThreadedFetcher` threads concurrently. Iteration is `while start < end`, so the end time is exclusive.
- `webcams.json` — webcam name → Roundshot storage base URL. Adding a webcam = adding an entry here (the `-w` docstring text is just help text).
- `scraper/request.py`
  - `create_url()` builds `{base}/{YYYY-MM-DD}/{HH-MM-00}/{YYYY-MM-DD}-{HH-MM-00}_{quality}.jpg`.
  - `ThreadedFetcher` downloads one image to `images/{webcam}/{YYYYmmdd-HHMMSS}-{quality}.jpg` (gitignored), relative to the current working directory. It parses quality back out of the URL, skips files that already exist, and sleeps 10 s after each request to avoid HTTP 429 rate limiting.

