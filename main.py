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

    paths = config["PATHS"]
    settings = config["SETTINGS"]

    return {
        "capcut_folder": paths["capcut_projects_folder"],
        "xml_folder": paths["xml_folder"],
        "default_color": settings.get("default_color", "#00c1cd"),
        "sm1": {
            "color": settings.get("color_shotmark1", "#00c1cd"),
            "label": settings.get("label_shotmark1", "ShotMark1")
        },
        "sm2": {
            "color": settings.get("color_shotmark2", "#FC7265"),
            "label": settings.get("label_shotmark2", "ShotMark2")
        }
    }

def generate_id():
    return str(uuid.uuid4()).upper()

# ==============================
# XML PARSING
# ==============================
def parse_xml_for_markers(xml_path, conf):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        ns = {'ns': 'urn:schemas-professionalDisc:nonRealTimeMeta:ver.2.20'}
        
        # Auto-detect FPS
        fps = 50.0
        video_format = root.find(".//ns:VideoFormat", ns)
        if video_format is not None:
            video_frame = video_format.find("ns:VideoFrame", ns)
            if video_frame is not None:
                fps_str = video_frame.attrib.get("videoInPointsPerSecond", "50")
                fps = float(fps_str.replace('p', '').replace('i', ''))

        markers = []
        klv_table = root.find("ns:KlvPacketTable", ns)
        if klv_table is None: return []

        for klv in klv_table.findall("ns:KlvPacket", ns):
            if klv.attrib.get("status") == "spot":
                frame_count = int(klv.attrib.get("frameCount", 0))
                if frame_count <= 0: continue
                
                # Check lengthValue for specific ShotMarks
                length_val = klv.attrib.get("lengthValue", "")
                
                # Standard-Werte
                marker_title = "ShotMark"
                marker_color = conf["default_color"]

                # Zuordnung basierend auf deinen Hex-Werten
                if "53686F744D61726B31" in length_val: # ShotMark1
                    marker_title = conf["sm1"]["label"]
                    marker_color = conf["sm1"]["color"]
                elif "53686F744D61726B32" in length_val: # ShotMark2
                    marker_title = conf["sm2"]["label"]
                    marker_color = conf["sm2"]["color"]
                
                time_us = int(frame_count * (1000000 / fps))
                markers.append({
                    "start": time_us, 
                    "title": marker_title, 
                    "color": marker_color
                })
        
        return markers
    except Exception as e:
        print(f"Error parsing {os.path.basename(xml_path)}: {e}")
        return []

# ... (Rest des Skripts bleibt identisch zu der vorherigen Version) ...

def auto_inject_all_markers(json_path, conf):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    xml_files = [f for f in os.listdir(conf["xml_folder"]) if f.lower().endswith(".xml")]
    if not xml_files:
        print("No XML files found.")
        return

    total_added = 0
    for xml_name in xml_files:
        video_prefix = os.path.splitext(xml_name)[0][:5]
        found_segments = []
        
        for track in data.get("tracks", []):
            if track["type"] != "video": continue
            for segment in track.get("segments", []):
                material_id = segment.get("material_id")
                for video in data.get("materials", {}).get("videos", []):
                    if video["id"] == material_id:
                        if video_prefix in video.get("material_name", "") or video_prefix in os.path.basename(video.get("path", "")):
                            found_segments.append(segment)

        if not found_segments: continue 

        markers = parse_xml_for_markers(os.path.join(conf["xml_folder"], xml_name), conf)
        if not markers: continue

        print(f"-> Clip {video_prefix}: Found {len(markers)} marks.")

        for segment in found_segments:
            collection_id = generate_id()
            mark_items = []
            for m in markers:
                mark_items.append({
                    "id": generate_id(),
                    "time_range": {"start": m["start"], "duration": 0},
                    "color": m["color"],
                    "title": m["title"]
                })

            if "extra_material_refs" not in segment: segment["extra_material_refs"] = []
            segment["extra_material_refs"].append(collection_id)

            if "time_marks" not in data["materials"] or data["materials"]["time_marks"] is None:
                data["materials"]["time_marks"] = []
            data["materials"]["time_marks"].append({"id": collection_id, "mark_items": mark_items})
            total_added += len(markers)

    if total_added > 0:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"\nSuccess: {total_added} markers added.")

def main():
    print("=== Sony FX3 Multi-Color & Custom Label Importer ===\n")
    try:
        conf = load_config()
        
        projects = sorted([d for d in os.listdir(conf["capcut_folder"]) if os.path.isdir(os.path.join(conf["capcut_folder"], d)) and not d.startswith(".")])
        if not projects: raise Exception("No projects found.")
        
        for i, p in enumerate(projects): print(f"[{i}] {p}")
        sel = int(input("\nSelect project number: "))
        json_path = os.path.join(conf["capcut_folder"], projects[sel], "draft_content.json")
        
        shutil.copy2(json_path, json_path + ".bak")
        print(f"Backup created.")

        auto_inject_all_markers(json_path, conf)
        
    except Exception as e:
        print(f"Error: {e}")
    print("\nProcess finished.")

if __name__ == "__main__":
    main()