# Telegram Sticker Maker

A simple GUI tool to create Telegram stickers from images. Removes backgrounds using the remove.bg API and resizes images to Telegram's 512px sticker format.

## Features

- Remove backgrounds using remove.bg API
- Create Telegram-ready stickers (512px WebP)
- Batch process multiple images or entire folders
- Option to keep backgrounds for stickers
- Export as PNG without resizing

## Installation

1. Get a free API key from [remove.bg](https://www.remove.bg/api)
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the app:
   ```
   python sticker_maker.py
   ```

Or download the pre-built `Sticker Maker.exe` from Releases.

## Usage

1. Enter your remove.bg API key and click Save
2. Select output type (sticker with/without background, or PNG)
3. Select image(s) or a folder to process
4. Processed files are saved to an `output` folder

## Author

Made by Bennett | @bbennctt
