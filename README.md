# Sony Shot-Marks to CapCut Importer

A Python tool that automatically imports Sony's Shot Marks (from XML files) directly onto video clips in the CapCut desktop timeline.

## Features
- **Clip-Level Markers:** Unlike other tools, this places markers directly on the clip, not the global timeline.
- **Auto-Matching:** Automatically matches XML files to clips in your CapCut project based on file prefixes.
- **Smart Filtering:** Ignores the default Sony "Frame 0" marker.
- **Safety:** Automatically creates a backup of your `draft_content.json` before making changes.

## Setup
1. Copy `config.ini.example` to `config.ini`.
2. Enter your CapCut projects folder path and the folder containing your Sony XMLs.
3. Run `python main.py`.

## Requirements
- Python 3.x
- CapCut Desktop (Windows)