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


DESCRIBE = False
EXIT_APP = False
LAST_SPOKEN = ""




def speak(text):
    print("[ASSISTANT]:", text)
    
    file = f"voice_{uuid.uuid4()}.mp3"
    gTTS(text=text, lang="en").save(file)

    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()

    # Wait until audio finishes
    while pygame.mixer.music.get_busy():
        continue

    pygame.mixer.quit()
    os.remove(file)


# VOICE CONTROL 
def listen_commands():
    global DESCRIBE, EXIT_APP
    r = sr.Recognizer()
    mic = sr.Microphone()

    while not EXIT_APP:
        try:
            with mic as source:
                r.adjust_for_ambient_noise(source)
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

        except:
            pass


# LOAD ML MODEL 
print("Loading vision model...")
processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base",
    use_fast=True
)
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)
print("Model loaded.")


# CAMERA

cap = cv2.VideoCapture(2)
speak("Assistant ready. Say start to begin.")

# Start voice listener
threading.Thread(target=listen_commands, daemon=True).start()

last_time = 0


while not EXIT_APP:
    ret, frame = cap.read()
    if not ret:
        break

    if DESCRIBE and time.time() - last_time > 6:
        image = Image.fromarray(frame).convert("RGB")

        
        inputs = processor(image, return_tensors="pt")
        output = model.generate(**inputs, max_new_tokens=60)
        caption = processor.decode(output[0], skip_special_tokens=True)

        # Speak only if changed
        if caption.lower() != LAST_SPOKEN.lower():
            speak(caption)
            LAST_SPOKEN = caption
            last_time = time.time()

    
    cv2.imshow("Assistant Camera ", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows
speak("System stopped")