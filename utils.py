import cv2
import numpy as np
import os
import insightface

# Load model once at module level
face_app = insightface.app.FaceAnalysis(name='buffalo_l')
face_app.prepare(ctx_id=0)  # 0 for GPU, -1 for CPU

def get_embedding(image):
    """
    Extract face embedding using insightface.
    Returns 512-dimensional list or None.
    """
    try:
        # Load image if path is given
        if isinstance(image, str):
            if not os.path.exists(image):
                raise FileNotFoundError(f"Image not found: {image}")
            img = cv2.imread(image)
        else:
            img = image  # assume already numpy array (BGR)
        
        faces = face_app.get(img)
        if len(faces) == 0:
            print("❌ No face detected in image")
            return None
        # insightface returns embedding as numpy array, convert to list
        return faces[0].embedding.tolist()
    except Exception as e:
        print(f"❌ Error getting embedding: {e}")
        return None

def match_face(encoding, db, tolerance=0.6):
    """
    Match using Euclidean distance
    """
    best_name = "Unknown"
    best_distance = 1.0
    
    for name, data in db.items():
        dist = np.linalg.norm(encoding - data["embedding"])
        if dist < best_distance:
            best_distance = dist
            best_name = name
    
    if best_distance <= tolerance:
        confidence = round((1 - best_distance) * 100, 1)
        return best_name, confidence, round(best_distance, 3)
    else:
        return "Unknown", 0, round(best_distance, 3)

def draw_box(frame, box, name, confidence=None, distance=None):
    """Draw bounding box with recognition result"""
    if name != "Unknown":
        color = (0, 255, 0)
        if confidence:
            label = f"✅ {name} ({confidence}%)"
        else:
            label = f"✅ {name}"
    else:
        color = (0, 0, 255)
        label = "❌ UNKNOWN"
    
    cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), color, 2)
    label_size = len(label) * 9
    cv2.rectangle(frame, (box[0], box[1]-35), (box[0]+label_size, box[1]), color, -1)
    cv2.putText(frame, label, (box[0]+4, box[1]-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)