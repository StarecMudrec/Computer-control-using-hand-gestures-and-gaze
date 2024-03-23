import cv2
import mediapipe as mp
import torch
import time
from l2cs import Pipeline, render
import math
import pyautogui as pag
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class handDetector():
	def __init__(self, mode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, trackCon=0.5):
		self.mode = mode
		self.maxHands = maxHands
		self.modelComplexity = modelComplexity
		self.detectionCon = detectionCon
		self.trackCon = trackCon

		self.mpHands = mp.solutions.hands
		self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplexity, self.detectionCon, self.trackCon)
		self.mpDraw = mp.solutions.drawing_utils
		self.tipIds = [4, 8, 12, 16, 20] 

	def findHands(self, img, draw: True):
		imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		self.results = self.hands.process(imgRGB)

		if self.results.multi_hand_landmarks:
			for handLms in self.results.multi_hand_landmarks:
				if draw:
					self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
		return img

	def findPosition(self, img, handNo=0, draw=True):
		xList = []
		yList = []
		bbox = []
		self.lmList = []
		if self.results.multi_hand_landmarks:
			#print("jopa")
			myHand = self.results.multi_hand_landmarks[handNo]
			for id, lm in enumerate(myHand.landmark):
				#print(id, lm)
				h, w, c = img.shape
				cx, cy = int(lm.x*w), int(lm.y*h)
				xList.append(cx)
				yList.append(cy)
				self.lmList.append([id, cx, cy])
				if draw:
					cv2.circle(img, (cx, cy), 5, (255,0,255), cv2.FILLED)
			xmin, xmax = min(xList), max(xList)
			ymin, ymax = min(yList), max(yList)
			bbox = xmin, ymin, xmax, ymax

			if draw:
				cv2.rectangle(img, (bbox[0]-20, bbox[1]-20), (bbox[2]+20, bbox[3]+20), (0, 255, 0), 2)
		return self.lmList, bbox

	def findDistance(self, p1, p2, img, draw=True):
		x1, y1 = self.lmList[p1][1], self.lmList[p1][2]
		x2, y2 = self.lmList[p2][1], self.lmList[p2][2]
		cx, cy = (x1+x2)//2, (y1+y2)//2

		if draw:
			cv2.circle(img, (x1,y1), 15, (255,0,255), cv2.FILLED)
			cv2.circle(img, (x2,y2), 15, (255,0,255), cv2.FILLED)
			cv2.line(img, (x1,y1), (x2,y2), (255,0,255), 3)
			cv2.circle(img, (cx,cy), 15, (255,0,255), cv2.FILLED)

		length = math.hypot(x2-x1, y2-y1)
		return length, img, [x1, y1, x2, y2, cx, cy]

	def fingersUp(self):
		fingers = []

		# Thumb
		if self.lmList[self.tipIds[0]][1] < self.lmList[self.tipIds[0]-1][1]:
			fingers.append(1)
		else:
			fingers.append(0)

		# 4 Fingers
		for id in range(1,5):
			if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id]-2][2]:
				fingers.append(1)
			else:
				fingers.append(0)
		return fingers


wCam, hCam = 1280, 720 # размер окна

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = handDetector(detectionCon=0.7, maxHands=1)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
volume.SetMasterVolumeLevel(0, None)
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
area = 0
colorVol = (255, 0, 0)

gesture_data = {"LKM_press": False, "LKM_hold": False, "Media_pause": False, "Media_next": False, "Media_prev": False, "Volume_control": False, "Ctrl+S": False, "Prtscr": False}
gesture_activated = {"LKM_press": False, "LKM_hold": False, "Media_pause": False, "Media_next": False, "Media_prev": False, "Volume_control": False, "Ctrl+S": False, "Prtscr": False}
gesture_binds = {"Th_Ind_Touch": "LKM_hold", "Th_Mid_Touch": "LKM_press", "Th_Ind_Pinky_Control": "Volume_control", "Fist": "Media_pause", "C_hand": "Ctrl+S", "O_hand": "Prtscr"}
gesture_icons = {"Th_Ind_Touch": "Th_Ind_Touch", "Th_Mid_Touch": "Th_Mid_Touch", "Th_Ind_Pinky_Control": "Th_Ind_Pinky_Control", "Fist": "Fist", "C_hand": "C_hand", "O_hand": "O_hand"}

width, height = pag.size()

hands_size = 3 #размер руки (3 - норма)

sensetivity = 4 #чувствительмость курсора (чем выше тем меньше надо двигать рукой. 2 - норма)


if torch.cuda.is_available():
    gaze_pipeline = Pipeline(
        weights = 'models\L2CSNet_gaze360.pkl',
        arch = 'ResNet50',
        device = torch.device('cuda') # or 'gpu'
    )
else:
    gaze_pipeline = Pipeline(
        weights = 'models\L2CSNet_gaze360.pkl',
        arch = 'ResNet50',
        device = torch.device('cpu') # or 'gpu'
    )
	
'''while True :
    _, img = cap.read()
    
    img = detector.findHands(img, draw=True)
    lmList, bbox = detector.findPosition(img, draw=True)

    if lmList != [] :
        fingers = detector.fingersUp()
        length, img, lineInfo = detector.findDistance(4, 8, img)
    
        volBar = np.interp(length, [50,200], [400, 150])
        volPer = np.interp(length, [50,200], [0, 100])

        if not fingers[4]:
            volume.SetMasterVolumeLevelScalar(volPer/100, None)

        D711, _, _ = detector.findDistance(7, 11, img, False)
        D1115, _, _ = detector.findDistance(11, 15, img, False)
        D1519, _, _ = detector.findDistance(15, 19, img, False)
        D07, _, _ = detector.findDistance(0, 7, img, False)
        D011, _, _ = detector.findDistance(0, 11, img, False)
        D015, _, _ = detector.findDistance(0, 15, img, False)
        D019, _, _ = detector.findDistance(0, 19, img, False)
        D46, _, _ = detector.findDistance(4, 6, img, False)

        if ((D711 <= 15*2*hands_size) and (D1115 <= 15*2*hands_size) and (D1519 <= 15*2*hands_size)) and ((D07 <= 40*2*hands_size) and (D011 <= 30*2*hands_size) and (D015 <= 25*2*hands_size) and (D019 <= 30*2*hands_size)) :
            mouse_button_press = True
        else :
            mouse_button_press = False
        
        if (D46 <= 7*1.5*hands_size) : 
            ''''''and ((dist(p7_x, p7_y, p11_x, p11_y) <= 15*hands_size) and (dist(p11_x, p11_y, p15_x, p15_y) <= 15*hands_size) and (dist(p15_x, p15_y, p19_x, p19_y) <= 15*hands_size)) and ((dist(p0_x, p0_y, p7_x, p7_y) <= 40*hands_size) and (dist(p0_x, p0_y, p11_x, p11_y) <= 30*hands_size) and (dist(p0_x, p0_y, p15_x, p15_y) <= 25*hands_size) and (dist(p0_x, p0_y, p19_x, p19_y) <= 30*hands_size))''''''
            mouse_button_click = True
        else :
            mouse_button_click = False

        h, w, _ = img.shape

        dx = lmList[9][1] - w/2
        dy = lmList[9][2] - h/2
        mouse_x = width - (width/2 + dx * width / w * sensetivity)
        mouse_y = height/2 + dy * height / h * sensetivity

        if 0 < mouse_x < width and 0 < mouse_y < height :
            if mouse_button_press == True and mouse_button_click != True :
                autopy.mouse.toggle(autopy.mouse.Button.LEFT, True)
                autopy.mouse.move(mouse_x, mouse_y)
            else :
                autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)
                autopy.mouse.move(mouse_x, mouse_y)
            if mouse_button_click == True :
                autopy.mouse.click(autopy.mouse.Button.LEFT, 0.9)
                autopy.mouse.move(mouse_x, mouse_y)
            else :
                autopy.mouse.move(mouse_x, mouse_y)
    cv2.imshow("Hand image", img)
    cv2.waitKey(1)'''