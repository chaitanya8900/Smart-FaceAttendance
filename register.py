import cv2
import mediapipe as mp
import os
import pickle
import numpy as np


def register_user():
    if not os.path.exists("images"):
        os.makedirs("images")

    name = input("Enter your name: ")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot access camera.")
        return

    print("Capturing image... Look at the camera.")
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("❌ Failed to capture image.")
        return

    # Save image
    img_path = f"images/{name}.jpg"
    cv2.imwrite(img_path, frame)

    # Detect face using Mediapipe
    mp_face = mp.solutions.face_detection
    face_detection = mp_face.FaceDetection(
        model_selection=0, min_detection_confidence=0.5)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_detection.process(rgb_frame)

    if result.detections:
        for det in result.detections:
            box = det.location_data.relative_bounding_box
            h, w, _ = frame.shape
            x = int(box.xmin * w)
            y = int(box.ymin * h)
            w_box = int(box.width * w)
            h_box = int(box.height * h)

            face_crop = rgb_frame[y:y + h_box, x:x + w_box]
            if face_crop.size == 0:
                print("❌ Could not extract face region.")
                return

            # Create dummy "embedding"
            encoding = np.array(face_crop).flatten()[:5120]
            encoding = np.pad(encoding, (0, 5120 - len(encoding)),
                              mode='constant')  # ensure same size

            with open("encodings.pickle", "ab") as f:
                pickle.dump((name, encoding), f)

            print("✅ Face registered and encoding saved.")
            return
    else:
        print("⚠️ No face detected. Try again.")


if __name__ == "__main__":
    register_user()
