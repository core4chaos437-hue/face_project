import cv2

print("Testing webcam with DSHOW backend...")

# Use DSHOW backend instead of MSMF (default)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("❌ Cannot open webcam with DSHOW")
    # Try alternative index
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("❌ Cannot open webcam at index 1 either")
        exit()
    else:
        print("✅ Webcam opened with index 1 (DSHOW)")
else:
    print("✅ Webcam opened with index 0 (DSHOW)")

# Set resolution for better compatibility
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

ret, frame = cap.read()
if ret:
    print(f"✅ Frame captured! Shape: {frame.shape}")
    cv2.imshow("Test", frame)
    cv2.waitKey(2000)
    cv2.destroyAllWindows()
else:
    print("❌ Cannot capture frame - check camera permissions")

cap.release()
print("Test complete")