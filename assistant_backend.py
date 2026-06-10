import cv2
import time
import uuid
import os
import threading
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from gtts import gTTS
import pygame
import speech_recognition as sr

# ---------------- GLOBAL FLAGS ----------------
DESCRIBE = False
EXIT_APP = False
LAST_SPOKEN = ""

# ---------------- LOAD MODEL (ONLY ONCE) ----------------
print("Loading vision model...")
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
print("Model loaded successfully!")

# ---------------- SPEAK FUNCTION ----------------
pygame.mixer.init()

def speak(text):
    print("[ASSISTANT]:", text)

    file = f"voice_{uuid.uuid4()}.mp3"
    gTTS(text=text, lang="en").save(file)

    pygame.mixer.music.load(file)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.music.stop()
    pygame.mixer.music.unload()   # important

    time.sleep(0.2)

    try:
        os.remove(file)
    except PermissionError:
        print("File still in use, skipping delete")

# ---------------- VOICE COMMAND LISTENER ----------------
def listen_commands():
    global DESCRIBE, EXIT_APP
    r = sr.Recognizer()
    mic = sr.Microphone()

    while not EXIT_APP:
        try:
            with mic as source:
                r.adjust_for_ambient_noise(source)
                print("Listening...")
                audio = r.listen(source, timeout=3)

            command = r.recognize_google(audio).lower()
            print("[VOICE]:", command)

            if "start" in command:
                DESCRIBE = True
                speak("I am describing your surroundings")

            elif "stop" in command:
                DESCRIBE = False
                speak("Description paused")

            elif "exit" in command or "close" in command:
                speak("Assistant closed")
                DESCRIBE = False
                EXIT_APP = True

        except Exception as e:
            # print error if needed
            # print("Voice error:", e)
            pass

# ---------------- MAIN FUNCTION ----------------
def run_assistant():
    global DESCRIBE, EXIT_APP, LAST_SPOKEN

    print("[CAMERA] Trying DroidCam...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[CAMERA] Trying laptop webcam...")
        cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("[ERROR] No camera found!")
        speak("No camera found")
        return

    print("[CAMERA] Camera connected!")
    speak("Assistant ready. Say start to begin.")

    # Start voice thread
    threading.Thread(target=listen_commands, daemon=True).start()

    last_time = 0

    while not EXIT_APP:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Cannot read frame")
            break

        if DESCRIBE and time.time() - last_time > 6:
            try:
                image = Image.fromarray(frame).convert("RGB")

                inputs = processor(image, return_tensors="pt")
                output = model.generate(**inputs, max_new_tokens=30)
                caption = processor.decode(output[0], skip_special_tokens=True)

                if caption and caption.lower() != LAST_SPOKEN.lower():
                    speak(caption)
                    LAST_SPOKEN = caption
                    last_time = time.time()

            except Exception as e:
                print("[ERROR]:", e)

        cv2.imshow("Assistant Camera", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            EXIT_APP = True

    cap.release()
    cv2.destroyAllWindows()
    speak("System stopped")

# ---------------- RUN ----------------
if __name__ == "__main__":
    run_assistant()