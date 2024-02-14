import cv2
from cvzone.HandTrackingModule import HandDetector
import socket
import numpy as np

# parameters
width, height = 1280, 720

# Webcam
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Hand Detector
detector = HandDetector(maxHands=2, detectionCon=0.8)

# Communication
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverAddressPort = ("127.0.0.1", 5052)

while True:
    # Get the frame from the webcam
    success, img = cap.read()

    # Hands
    hands, img = detector.findHands(img)

    data = []

    # landmark values = (x,y,z)*21
    if hands:
        # Get the first hand detected
        hand = hands[0]
        # Get the landmark list
        lmList = hand['lmList']



        # Calculate center position of the hand
        center_x = sum([lm[0] for lm in lmList]) / len(lmList)
        center_y = sum([lm[1] for lm in lmList]) / len(lmList)
        center_z = sum([lm[2] for lm in lmList]) / len(lmList)

        # Calculate the distance between hand's z position and center position along z-axis
        z_position = lmList[0][2]  # Assuming the first landmark's z position is used
        z_distance = abs(z_position - center_z)

        # Map the distance to a desired range
        min_z_distance = 0  # Minimum distance between hand's z position and center position
        max_z_distance = 100  # Maximum distance between hand's z position and center position
        min_mapped_z = 0  # Minimum mapped Z position in Unity
        max_mapped_z = 10  # Maximum mapped Z position in Unity
        mapped_z = np.interp(z_distance, [min_z_distance, max_z_distance], [min_mapped_z, max_mapped_z])

        # print(mapped_z)
        # removing the brackets []
        for lm in lmList:
            data.extend([lm[0], height - lm[1], mapped_z]);
        # print(data)
        sock.sendto(str.encode(str(data)), serverAddressPort)


        # Send mapped_z to Unity
        # sock.sendto(str.encode(str(mapped_z)), serverAddressPort)

    img = cv2.resize(img, (0, 0), None, 0.5, 0.5)
    cv2.imshow("Image", img)
    cv2.waitKey(1)
