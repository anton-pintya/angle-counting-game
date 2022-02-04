import HandTrackingModule as htm
import cv2
import math


cam = cv2.VideoCapture(0)

wCam, hCam = 640, 480
cam.set(3, wCam)
cam.set(4, hCam)
wScr = 800
hScr = 600
phi1 = 0
phi2 = 0
lastPosX, lastPosY = 0, 0

detector = htm.HandDetector(detectionCon = 0.8, maxHands = 1)

while True:
    success, img = cam.read()
    img = cv2.flip(img, 1)

    degrees = round((math.pi/2 - phi1) * 180 / math.pi)
    cv2.putText(img, f'{degrees} degrees',  (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
    
    img = detector.findHands(img, draw=True)
    lnList, bBox = detector.findPosition(img, draw=False)
    
    if lnList:
        cx, cy = lnList[9][1], lnList[9][2]
        radius = int(math.hypot(lnList[12][1] - cx, lnList[12][2] - cy))
        eps = 20
        dphi = 0.05

        cv2.circle(img, (cx, cy), 2, (255, 255, 255), cv2.FILLED)
        cv2.circle(img, (cx, cy), radius, (255, 255, 255), 3)
        cv2.line(img, (cx, cy), (cx, cy - radius), (255,255,255), 3)
        cv2.line(img, (cx, cy), (lnList[12][1], lnList[12][2]), (255,255,255), 3)

        PosX, PosY = lnList[12][1], lnList[12][2]

        if not ((lastPosX - eps < PosX < lastPosX + eps) and (lastPosY - eps < PosY < lastPosY + eps)):
            lastPosX, lastPosY = lnList[12][1], lnList[12][2]

            distance = math.hypot(cx - PosX, cy - radius - PosY)
            length = math.hypot(lnList[12][1] - cx, lnList[12][2] - cy)
            res = (length ** 2 + radius ** 2 - distance ** 2) / (2 * length * radius)
            
            if abs(res) <= 1:
                phi1 = round(math.acos(res), 3)
                if phi2:
                    if phi1 > phi2:
                        print('Forward')
                    if phi1 < phi2:
                        print('Back')
                
                phi2 = phi1
     
    
    cv2.imshow("Test", img)

    if cv2.waitKey(1) == 27:
        break
