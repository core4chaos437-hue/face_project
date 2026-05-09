import face_recognition
import cv2
import numpy as np
import os

def get_embedding(image):
    """
    Extract face encoding using face_recognition library
    Returns 128-dimensional encoding
    """
    try:
        # Convert image to RGB if needed
        if isinstance(image, str):
            # Image path
            if not os.path.exists(image):
                raise FileNotFoundError(f"Image not found: {image}")
            img = face_recognition.load_image_file(image)
        else:
            # BGR to RGB conversion (OpenCV uses BGR)
            if len(image.shape) == 3 and image.shape[2] == 3:
                img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                img = image
        
        # Get face encodings
        encodings = face_recognition.face_encodings(img)
        
        if len(encodings) > 0:
            return encodings[0]
        else:
            print("❌ No face detected in image")
            return None
            
    except Exception as e:
        print(f"❌ Error getting embedding: {e}")
        return None

def match_face(encoding, db, tolerance=0.6):
    """
    Match using face_recognition's built-in comparison
    tolerance: 0.6 is default, lower = stricter, higher = more forgiving
    """
    best_name = "Unknown"
    best_distance = 1.0
    
    for name, data in db.items():
        # Calculate Euclidean distance
        dist = np.linalg.norm(encoding - data["embedding"])
        if dist < best_distance:
            best_distance = dist
            best_name = name
    
    # Check if within tolerance
    if best_distance <= tolerance:
        # Convert distance to confidence percentage (inverse relationship)
        confidence = round((1 - best_distance) * 100, 1)
        return best_name, confidence, round(best_distance, 3)
    else:
        return "Unknown", 0, round(best_distance, 3)

def draw_box(frame, box, name, confidence=None, distance=None):
    """Draw bounding box with recognition result"""
    if name != "Unknown":
        color = (0, 255, 0)  # Green for recognized
        if confidence:
            label = f"✅ {name} ({confidence}%)"
        else:
            label = f"✅ {name}"
    else:
        color = (0, 0, 255)  # Red for unknown
        label = "❌ UNKNOWN"
    
    # Draw bounding box
    cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), color, 2)
    
    # Draw label background
    label_size = len(label) * 9
    cv2.rectangle(frame, (box[0], box[1]-35), (box[0]+label_size, box[1]), color, -1)
    
    # Draw label text
    cv2.putText(frame, label, (box[0]+4, box[1]-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)