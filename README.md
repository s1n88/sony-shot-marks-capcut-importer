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

## How to use
Follow these steps to ensure the markers are imported correctly:

1. **Create a new CapCut project.**
2. **Import your video clips** (Ensure the corresponding `.XML` files are located in the `xml_folder` defined in your `config.ini`).
3. **Add the video clips to the timeline** (The script looks for clips that are actually placed in a track).
4. **Close CapCut completely.** > ⚠️ **Important:** CapCut must be closed so it can write the current project state to the disk and allow the script to modify it safely.
5. **Run the script:**
6. **Restart CapCut** and open your project. The Shot Marks should now appear directly on the clips in your timeline.

## Requirements
- Python 3.x

- CapCut Desktop (Windows)
