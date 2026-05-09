import os
import cv2
import pickle
import shutil
import numpy as np
from utils import get_embedding

DB_FILE = "embeddings.pkl"
DB_FOLDER = "database"
os.makedirs(DB_FOLDER, exist_ok=True)

def load_db():
    try:
        with open(DB_FILE, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}

def save_db(db):
    with open(DB_FILE, "wb") as f:
        pickle.dump(db, f)

def register_person(name, image_source, is_path=True):
    db = load_db()
    records_dir = os.path.join(DB_FOLDER, "records", name)
    os.makedirs(records_dir, exist_ok=True)
    
    try:
        # Get face embedding from the FULL face
        embedding = get_embedding(image_source)
        
        if embedding is None:
            print("❌ Could not extract face embedding - no face detected")
            return False
        
        # Save the original photo
        if is_path:
            # Copy the photo file
            ext = os.path.splitext(image_source)[1]
            dest = os.path.join(records_dir, f"original_photo{ext}")
            shutil.copy(image_source, dest)
        else:
            # Save webcam frame
            dest = os.path.join(records_dir, "original_photo.jpg")
            cv2.imwrite(dest, image_source)
        
        # Update database
        if name in db:
            old = db[name]["embedding"]
            count = db[name]["count"]
            # Average the embeddings
            blended = (old * count + embedding) / (count + 1)
            db[name] = {"embedding": blended, "count": count + 1}
            print(f"✅ Updated: {name} (now has {count + 1} samples)")
        else:
            db[name] = {"embedding": embedding, "count": 1}
            print(f"✅ Registered: {name}")
        
        save_db(db)
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def register_via_webcam(name):
    # Try to open webcam
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("❌ Could not open webcam")
            return False
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print(f"📸 Press SPACE to capture | Q to cancel")
    print("📌 Look straight at the camera, good lighting")
    registered = False
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        cv2.putText(frame, "Press SPACE to capture",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                   0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Name: {name}",
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
                   0.7, (255, 255, 255), 2)
        cv2.imshow("Register", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            success = register_person(name, frame, is_path=False)
            if success:
                registered = True
            break
        elif key == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    return registered

def register_via_photo(name, photo_path):
    if not os.path.exists(photo_path):
        print(f"❌ Photo not found: {photo_path}")
        return False
    return register_person(name, photo_path, is_path=True)

def list_all_people():
    db = load_db()
    if not db:
        print("Database is empty")
        return
    print("\n👥 Registered People:")
    for i, (name, data) in enumerate(db.items(), 1):
        print(f"  {i}. {name} — {data['count']} photo(s)")

def delete_person(name):
    db = load_db()
    if name in db:
        del db[name]
        save_db(db)
        print(f"🗑️ Deleted: {name}")
    else:
        print(f"Not found: {name}")