import cv2
import os
from utils import get_embedding, match_face, draw_box
from register import load_db

def recognize_live():
    """Live webcam face recognition"""
    db = load_db()
    if not db:
        print("⚠️ Database is empty. Please register a person first.")
        return
    
    print("🔍 Opening webcam...")
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print("Trying camera index 1...")
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("❌ Could not open webcam")
            return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("✅ Live recognition started | Press Q to quit")
    print("📌 Tolerance = 0.5 (stricter matching)")
    
    # Simple face detection using OpenCV (faster)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    # Tolerance: lower = stricter, higher = more forgiving
    TOLERANCE = 0.5  # Start with this, adjust as needed
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Failed to grab frame")
            continue
        
        # Detect faces (fast)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            # Extract face ROI (FULL face, not just upper)
            face_roi = frame[y:y+h, x:x+w]
            
            try:
                # Get face encoding
                encoding = get_embedding(face_roi)
                
                if encoding is not None:
                    # Match against database
                    name, confidence, distance = match_face(encoding, db, TOLERANCE)
                    
                    if name != "Unknown":
                        print(f"✅ RECOGNIZED: {name} ({confidence}%, distance: {distance})")
                        draw_box(frame, (x, y, x+w, y+h), name, confidence, distance)
                    else:
                        print(f"🚫 REJECTED: Unknown (distance: {distance} > {TOLERANCE})")
                        draw_box(frame, (x, y, x+w, y+h), "UNKNOWN", None, None)
                else:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 255), 2)
                    cv2.putText(frame, "No face", (x, y-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    
            except Exception as e:
                print(f"⚠️ Error: {e}")
        
        # Display instructions
        cv2.putText(frame, "Press Q to quit", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"People in DB: {len(db)}", (10, 55),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Tolerance: {TOLERANCE} (lower=stricter)", (10, 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        cv2.imshow("Live Recognition", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("👋 Recognition stopped")

def recognize_from_photo(photo_path):
    """Test a single photo"""
    if not os.path.exists(photo_path):
        print(f"❌ Photo not found: {photo_path}")
        return
    
    db = load_db()
    if not db:
        print("⚠️ Database is empty")
        return
    
    print(f"🔍 Testing photo: {photo_path}")
    
    img = cv2.imread(photo_path)
    if img is None:
        print("❌ Could not load image")
        return
    
    # Get encoding directly from the photo
    encoding = get_embedding(photo_path)
    
    if encoding is not None:
        name, confidence, distance = match_face(encoding, db, tolerance=0.5)
        
        if name != "Unknown":
            print(f"✅ Recognized: {name} ({confidence}%)")
            cv2.putText(img, f"✅ {name} ({confidence}%)", (30, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            print(f"❌ Not recognized (distance: {distance})")
            cv2.putText(img, "❌ UNKNOWN", (30, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    else:
        print("❌ No face detected in photo")
    
    cv2.imshow("Result", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()