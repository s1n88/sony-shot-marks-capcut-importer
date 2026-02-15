# Sony Shot-Marks to CapCut Importer
A Python tool that automatically imports Sony's Shot Marks (from XML files) directly onto video clips in the CapCut desktop timeline.

## ✨ Features
- **Clip-focused:** Markers stick to the clip, not the global timeline.
- **Multi-Color Support:** Differentiate between **ShotMark1** and **ShotMark2** with custom colors.
- **Custom Labels:** Rename markers (e.g., "Good Take" or "SlowMo") directly in the config.
- **Smart Sync:** Auto-detects FPS and matches XML files to clips in your CapCut project based on file prefixes.
- **Sony Optimized:** Automatically filters out the default "Frame 0" marker.
- **Safety:** Automatically creates a backup of your `draft_content.json` before making changes.

## Setup
1. **Download:** Clone or download this repository.
2. **Configure:** Rename `config.ini.example` to `config.ini`.
3. **Paths:** Open `config.ini` and set your paths:
   - `capcut_projects_folder`: Where your projects live. 
   - `xml_folder`: Where your Sony XML files are stored.
4. **Customize (Optional):** Set your preferred colors and labels for ShotMark1 and ShotMark2.

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