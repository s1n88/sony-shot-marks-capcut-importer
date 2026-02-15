import os
import configparser
import shutil
import json
import uuid
import xml.etree.ElementTree as ET

# ==============================
# LOAD CONFIG
# ==============================
def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.ini")

    if not os.path.exists(config_path):
        raise FileNotFoundError("config.ini not found!")

    config = configparser.ConfigParser()
    config.read(config_path, encoding="utf-8-sig")

    if "PATHS" not in config or "SETTINGS" not in config:
        raise Exception("Config sections missing!")

    capcut_folder = config["PATHS"]["capcut_projects_folder"]
    xml_folder = config["PATHS"]["xml_folder"]
    default_color = config["SETTINGS"]["default_color"]

    return capcut_folder, xml_folder, default_color

def generate_id():
    """Generates a CapCut-compliant UUID"""
    return str(uuid.uuid4()).upper()

# ==============================
# PROJECT SELECTION
# ==============================
def select_project(base_folder):
    projects = []
    for entry in os.listdir(base_folder):
        full_path = os.path.join(base_folder, entry)
        if os.path.isdir(full_path) and not entry.startswith("."):
            projects.append(entry)
    projects.sort()

    if not projects:
        raise Exception("No CapCut projects found!")

    print("\nAvailable CapCut Projects:\n")
    for i, project in enumerate(projects):
        print(f"[{i}] {project}")

    while True:
        try:
            selection = int(input("\nSelect project number: "))
            if 0 <= selection < len(projects):
                break
        except:
            pass
        print("Invalid selection.")

    selected_project = projects[selection]
    json_path = os.path.join(base_folder, selected_project, "draft_content.json")
    return selected_project, json_path

# ==============================
# XML PARSING (Filters Frame 0)
# ==============================
def parse_xml_for_markers(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        ns = {'ns': 'urn:schemas-professionalDisc:nonRealTimeMeta:ver.2.20'}
        
        # --- NEW: AUTO-DETECT FPS ---
        fps = 50.0  # Default fallback
        video_format = root.find(".//ns:VideoFormat", ns)
        if video_format is not None:
            video_frame = video_format.find("ns:VideoFrame", ns)
            if video_frame is not None:
                video_fps_str = video_frame.attrib.get("videoInPointsPerSecond", "50")
                # Format is often "50p", "25p" or just "50"
                fps = float(video_fps_str.replace('p', '').replace('i', ''))
                # print(f"DEBUG: Detected {fps} FPS for {os.path.basename(xml_path)}")
        # ----------------------------

        markers = []
        klv_table = root.find("ns:KlvPacketTable", ns)
        if klv_table is None: return []

        for klv in klv_table.findall("ns:KlvPacket", ns):
            if klv.attrib.get("status") == "spot":
                frame_count = int(klv.attrib.get("frameCount", 0))
                
                if frame_count <= 0:
                    continue
                
                length_val = klv.attrib.get("lengthValue", "")
                try:
                    title = bytes.fromhex(length_val).decode("utf-8")
                except:
                    title = "Shot Mark"
                
                # Calculation now uses the dynamic fps value
                time_us = int(frame_count * (1000000 / fps))
                markers.append({"start": time_us, "title": title})
        
        return markers
    except Exception as e:
        print(f"Error parsing {os.path.basename(xml_path)}: {e}")
        return []
# ==============================
# AUTOMATIC INJECTION
# ==============================
def auto_inject_all_markers(json_path, xml_folder, default_color="#00c1cd"):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    xml_files = [f for f in os.listdir(xml_folder) if f.lower().endswith(".xml")]
    if not xml_files:
        print("No XML files found in the source folder.")
        return

    total_added = 0
    
    for xml_name in xml_files:
        # Extract clip prefix (first 5 chars, e.g., C4176)
        video_prefix = os.path.splitext(xml_name)[0][:5]
        
        found_segments = []
        for track in data.get("tracks", []):
            if track["type"] != "video": continue
            for segment in track.get("segments", []):
                material_id = segment.get("material_id")
                
                for video in data.get("materials", {}).get("videos", []):
                    if video["id"] == material_id:
                        mat_name = video.get("material_name", "")
                        path_name = os.path.basename(video.get("path", ""))
                        
                        if video_prefix in mat_name or video_prefix in path_name:
                            found_segments.append(segment)

        if not found_segments:
            continue 

        markers = parse_xml_for_markers(os.path.join(xml_folder, xml_name))
        if not markers:
            continue

        print(f"-> Clip {video_prefix}: Found {len(markers)} Shot Marks.")

        for segment in found_segments:
            collection_id = generate_id()
            mark_items = []
            for m in markers:
                mark_items.append({
                    "id": generate_id(),
                    "time_range": {"start": m["start"], "duration": 0},
                    "color": default_color,
                    "title": m["title"]
                })

            time_marks_obj = {"id": collection_id, "mark_items": mark_items}

            if "extra_material_refs" not in segment:
                segment["extra_material_refs"] = []
            segment["extra_material_refs"].append(collection_id)

            if "time_marks" not in data["materials"] or data["materials"]["time_marks"] is None:
                data["materials"]["time_marks"] = []
            data["materials"]["time_marks"].append(time_marks_obj)
            
            total_added += len(markers)

    if total_added > 0:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"\nSuccess: {total_added} markers added to the clips in your timeline.")
    else:
        print("\nNo matching clips or relevant markers (Frame > 0) found.")

# ==============================
# MAIN
# ==============================
def main():
    print("=== Sony SHOT MARKS XML to CapCut TIME MARKER ===\n")
    try:
        capcut_folder, xml_folder, default_color = load_config()
        selected_project, json_path = select_project(capcut_folder)
        
        backup_path = json_path + "_backup.bak"
        shutil.copy2(json_path, backup_path)
        print(f"Backup created: {os.path.basename(backup_path)}")

        auto_inject_all_markers(json_path, xml_folder, default_color)
        
    except Exception as e:
        print(f"Error: {e}")

    print("\nProcess finished.")

if __name__ == "__main__":
    main()