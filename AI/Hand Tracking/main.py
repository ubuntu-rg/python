import cv2
import mediapipe as mp
import time

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils
pTime = 0
cTime = 0
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                # lm is equal to x, y, z of each finger
                # Get th width and height of the frame
                h, w, c = img.shape
                # Converting x, y, z to pixels
                cx, cy = int(lm.x * w), int(lm.y * h)
                print(id, cx, cy)
                # Catch specific finger and change it shape to bigger in order to track
                if id == 8:
                    cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
            # Draw all the dots and connect between them
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    # Display the image with a caption.
    cv2.imshow("Image", img)
    # Wait for x milliseconds
    cv2.waitKey(1)
