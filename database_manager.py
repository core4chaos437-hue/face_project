import os
import json
import cv2
import shutil
from datetime import datetime

RECORDS_DIR = os.path.join("database", "records")
os.makedirs(RECORDS_DIR, exist_ok=True)

def get_person_dir(name):
    path = os.path.join(RECORDS_DIR, name)
    os.makedirs(path, exist_ok=True)
    return path

def load_record(record_file):
    try:
        with open(record_file, "r") as f:
            content = f.read().strip()
            if not content:
                return None
            return json.loads(content)
    except:
        return None

def create_record(name, original_photo_path=None,
                  original_frame=None):
    person_dir = get_person_dir(name)
    record_file = os.path.join(person_dir, "record.json")

    if original_photo_path:
        ext = os.path.splitext(original_photo_path)[1]
        dest = os.path.join(
            person_dir, f"original_photo{ext}"
        )
        shutil.copy(original_photo_path, dest)
        original_saved = dest
    elif original_frame is not None:
        dest = os.path.join(
            person_dir, "original_photo.jpg"
        )
        cv2.imwrite(dest, original_frame)
        original_saved = dest
    else:
        original_saved = None

    record = {
        "name": name,
        "registered_on": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "original_photo": original_saved,
        "total_sightings": 0,
        "last_seen": None,
        "first_seen": None,
        "sightings": []
    }

    with open(record_file, "w") as f:
        json.dump(record, f, indent=4)

    return record

def add_sighting(name, frame, confidence,
                 disguised=False):
    person_dir = get_person_dir(name)
    record_file = os.path.join(person_dir, "record.json")

    record = load_record(record_file)
    if not record:
        record = create_record(name)

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    sighting_count = record["total_sightings"] + 1
    photo_name = f"sighting_{sighting_count}_{timestamp}.jpg"
    photo_path = os.path.join(person_dir, photo_name)

    try:
        cv2.imwrite(photo_path, frame)
    except:
        photo_path = None

    sighting_entry = {
        "sighting_number": sighting_count,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "confidence": confidence,
        "disguised": disguised,
        "photo": photo_path
    }

    record["total_sightings"] = sighting_count
    record["last_seen"] = now.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    if record["first_seen"] is None:
        record["first_seen"] = now.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    record["sightings"].append(sighting_entry)

    with open(record_file, "w") as f:
        json.dump(record, f, indent=4)

    return sighting_entry

def get_record(name):
    record_file = os.path.join(
        RECORDS_DIR, name, "record.json"
    )
    return load_record(record_file)

def print_record(name):
    record = get_record(name)
    if not record:
        print(f"No record found for: {name}")
        return

    print("\n" + "="*45)
    print(f"  RECORD: {record['name']}")
    print("="*45)
    print(f"  Registered : {record['registered_on']}")
    print(f"  First seen : {record['first_seen']}")
    print(f"  Last seen  : {record['last_seen']}")
    print(f"  Sightings  : {record['total_sightings']}")

    for s in record["sightings"]:
        tag = "DISGUISED" if s["disguised"] else ""
        print(f"    #{s['sighting_number']} | "
              f"{s['date']} {s['time']} | "
              f"{s['confidence']}% {tag}")
    print("="*45)

def print_all_records():
    if not os.path.exists(RECORDS_DIR):
        print("No records found")
        return

    people = os.listdir(RECORDS_DIR)
    if not people:
        print("Database is empty")
        return

    print("\n" + "="*50)
    print("  ALL RECORDS")
    print("="*50)

    for name in people:
        record = get_record(name)
        if record:
            print(f"\n  👤 {record['name']}")
            print(f"     Registered : "
                  f"{record['registered_on']}")
            print(f"     Last seen  : "
                  f"{record['last_seen'] or 'Never'}")
            print(f"     Sightings  : "
                  f"{record['total_sightings']}")

    print("="*50)

def show_original_photo(name):
    record = get_record(name)
    if not record or not record["original_photo"]:
        print("No original photo found")
        return

    img = cv2.imread(record["original_photo"])
    if img is not None:
        cv2.imshow(f"Original - {name}", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def show_all_sightings(name):
    record = get_record(name)
    if not record:
        print("No record found")
        return

    for sighting in record["sightings"]:
        if sighting["photo"]:
            img = cv2.imread(sighting["photo"])
            if img is not None:
                label = (f"#{sighting['sighting_number']} | "
                        f"{sighting['date']} | "
                        f"{sighting['confidence']}%")
                cv2.putText(img, label, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX,
                           0.6, (0, 255, 0), 2)
                cv2.imshow(f"Sighting - {name}", img)
                key = cv2.waitKey(0)
                if key == ord('q'):
                    break

    cv2.destroyAllWindows()

def print_disguise_report():
    if not os.path.exists(RECORDS_DIR):
        print("No records found")
        return

    people = os.listdir(RECORDS_DIR)
    disguised_found = False

    print("\n" + "="*50)
    print("  DISGUISE REPORT")
    print("="*50)

    for name in people:
        record = get_record(name)
        if not record:
            continue

        disguised_sightings = [
            s for s in record["sightings"]
            if s["disguised"]
        ]

        if disguised_sightings:
            disguised_found = True
            print(f"\n  👤 {name}")
            print(f"     Disguised sightings: "
                  f"{len(disguised_sightings)}")
            for s in disguised_sightings:
                print(f"       #{s['sighting_number']} | "
                      f"{s['date']} {s['time']} | "
                      f"{s['confidence']}%")

    if not disguised_found:
        print("\n  No disguised sightings yet.")
    print("="*50)