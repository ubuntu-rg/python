import cv2
import numpy as np
import time
import AI.PoseMOdule as pm

cap = cv2.VideoCapture(0)
detector = pm.poseDetector()
# Count the amount of push-ups
count = 0
# direction will define if the person is going down or up, 0 = going down. 1 = going up
direction = 0
WIDTH, HEIGHT = 1920, 1080
while True:
    success, img = cap.read()
    img = cv2.resize(img, (WIDTH, HEIGHT))
    # img = cv2.imread("pushup.png")
    # Set find pose to False in order to remove the draw functionality
    img = detector.findPose(img, False)
    lmList = detector.findPosition(img, False)
    if len(lmList) != 0:
        # Right Arm
        angle_right = detector.findAngle(img, 12, 14, 16)
        # Left Arm
        angle_left = detector.findAngle(img, 11, 13, 15)
        # Creating a test for how good was the push up, converting the angle to scale of 0-100
        percentage = np.interp(angle_right, (95, 155), (0, 100))
        bar = np.interp(angle_right, (95, 155), (650, 100))
        print(percentage)

        color = (0, 0, 255)
        if percentage == 0:  # Going down
            color = (0, 0, 255)
            if direction == 0:
                count += 0.5
                direction = 1
        if percentage == 100:  # Going up
            color = (0, 255, 0)
            if direction == 1:
                count += 0.5
                direction = 0
        print(count)

        # Draw the bar progress
        print(percentage)
        cv2.rectangle(img, (WIDTH - 100, 100), (WIDTH - 25, 650), color, 3)
        cv2.rectangle(img, (WIDTH - 100, int(bar)), (WIDTH - 25, 650), color, cv2.FILLED)
        cv2.putText(img, f"{int(percentage)}%", (WIDTH - 130, 75), cv2.FONT_HERSHEY_PLAIN, 3, color, 4)

        cv2.putText(img, f"Push-Up: {int(count)}", (50, 100), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 5)


    cv2.imshow("Image", img)
    cv2.waitKey(20)
