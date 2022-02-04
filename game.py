from numpy import imag
import pygame
import sys
import math

import HandTrackingModule as htm
import cv2


class Car:
    def __init__(self) -> None:
        self.x = 15
        self.y = 210
        self.w = 30
        self.vel = 3
        self.image = self.resize(car_image)  
        self.orig = self.image
        self.rect = self.image.get_rect()
        self.collision = False      

    def draw(self):
        w, h = self.get_size(car_image)
        cenx, ceny = self.x + w // 4, self.y + h // 4

        if cenx > 480: self.x = 0
        if ceny > 480: self.y = 0
        if cenx < 0: self.x = 480
        if ceny < 0: self.y = 480

        if (cenx - 240) ** 2 + (ceny - 240) ** 2 > 230 ** 2 or (cenx - 240) ** 2 + (ceny - 240) ** 2 < 160 ** 2: 
            self.collision = True

        screen.blit(self.image, (self.x, self.y))
    
    def get_size(self, car_image):
        image_size = car_image.get_rect().size
        return image_size[0], image_size[1]
    
    def resize(self, car_image):
        w, h = self.get_size(car_image)
        image_size = (self.w, int(h * self.w / w))
        return pygame.transform.scale(car_image, image_size)
    
    def move(self, phi):
        self.x += self.vel * math.sin(2 * phi)
        self.y += self.vel * math.cos(2 * phi)
        
    def rotate(self, surface, phi):
        pass


pygame.init()
pygame.font.init()
pygame.display.set_caption('Car On The Road')

screen = pygame.display.set_mode((480, 480))
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 20)

pygame.display.update()

car_image = pygame.image.load('car2.png')
car = Car()

cam = cv2.VideoCapture(0)

wCam, hCam = 640, 480
cam.set(3, wCam)
cam.set(4, hCam)
wScr = 800
hScr = 600

lastPosX, lastPosY = 0, 0
phi = math.pi/2
pause = False
x0, y0 = 15, 210
level = 1

detector = htm.HandDetector(detectionCon = 0.8, maxHands = 1)

def angle_detecting(lastPosX, lastPosY, phi, show):
    _, img = cam.read()
    img = cv2.flip(img, 1)
    
    img = detector.findHands(img, draw=True)
    lnList, bBox = detector.findPosition(img, draw=True)
    
    if lnList:
        cx, cy = lnList[9][1], lnList[9][2]
        radius = int(math.hypot(lnList[12][1] - cx, lnList[12][2] - cy))
        eps = 20

        cv2.circle(img, (cx, cy), 2, (255, 255, 255), cv2.FILLED)
        cv2.circle(img, (cx, cy), radius, (255, 255, 255), 3)
        cv2.line(img, (cx, cy), (cx, cy - radius), (255,255,255), 3)
        cv2.line(img, (cx, cy), (lnList[12][1], lnList[12][2]), (255,255,255), 3)

        PosX, PosY = lnList[12][1], lnList[12][2]

        if not ((lastPosX - eps < PosX < lastPosX + eps) and (lastPosY - eps < PosY < lastPosY + eps)):
            lastPosX, lastPosY = lnList[12][1], lnList[12][2]

            distance = math.hypot(cx + radius - PosX, cy - PosY)
            length = math.hypot(lnList[12][1] - cx, lnList[12][2] - cy)
            res = (length ** 2 + radius ** 2 - distance ** 2) / (2 * length * radius)
            
            if abs(res) <= 1:
                phi = round(math.acos(res), 3)
                if cy < PosY: phi = -phi
    
    cv2.imshow("Test", img)
    return phi

while True:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                pause = False
                phi = math.pi/2
                car.x, car.y = x0, y0
                car.collision = False

    if not pause:
        phi = angle_detecting(lastPosX, lastPosY, phi, show=False)

        screen.fill((0, 0, 0))

        pygame.draw.circle(screen, (255, 255, 255), (240, 240), 230, 70)
        pygame.draw.circle(screen, (255, 0, 0), (240, 240), 233, 3)
        pygame.draw.circle(screen, (255, 0, 0), (240, 240), 160, 3)

        text = font.render(f'Level {level}', False, (255, 0, 0))
        screen.blit(text, (210, 225))
        
        car.draw()
        if car.collision == True: 
            pause = True
            level = 1
        car.move(phi)

        if 10 < car.x < 80 and 240 < car.y < 240 + car.vel:
            level += 1
            car.vel += 0.5

        pygame.display.update()