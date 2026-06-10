import cv2

cap = cv2.VideoCapture("http://192.168.1.7:8080/video")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to connect")
        break
    cv2.imshow("Test", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()