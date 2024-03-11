import cv2
import sys
import os
import HandDetector as HD
import pyautogui as pag
from HandDetector import hands_size, width, height, sensetivity, cap, gesture_data, gesture_binds, gesture_icons, gesture_activated
from PyQt5.QtWidgets import  QWidget, QLabel, QApplication, QPushButton, QDesktopWidget, QComboBox
from PyQt5.QtCore import QObject, QThread, Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QImage, QPixmap, QIcon
from extract import mtx, dist

detection_is_on = False

swipe = False
swiped = False
swipe_left = False
swipe_right = False
index_f_lm = (0, 0)

class Thread(QThread):
    changePixmap = pyqtSignal(QImage)

    def run(self):
        #cap = cv2.VideoCapture(0)
        while True:
            #print(gesture_binds)
            if "ex" in globals():
                #print(gesture_binds)
                ex.hand_settings_window.static_gestures_settings_window.set_gesture_binds()
            if detection_is_on == True :
                ret, img_undist = cap.read()

                h, w = img_undist.shape[:2]
                newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
                # undistort
                dst = cv2.undistort(img_undist, mtx, dist, None, newcameramtx)
                # crop the image
                x, y, w, h = roi
                img = dst[y:y+h, x:x+w]

                img = HD.detector.findHands(img, draw=True)
                lmList, bbox = HD.detector.findPosition(img, draw=True)

                '''global swipe, swiped, swipe_left, swipe_right, index_f_lm

                if swipe == True:
                    print("swipe")
                    if lmList == []:
                        print("no hands")
                        swipe = False
                        swiped = True
                        if lmList[8][0] in lmList and index_f_lm[0] > lmList[8][0] :
                            print("right")
                        else :
                            print("left")'''

                if lmList != [] :
                    fingers = HD.detector.fingersUp()
                    
                    '''D711, _, _ = HD.detector.findDistance(7, 11, img, False)
                    D1115, _, _ = HD.detector.findDistance(11, 15, img, False)
                    D1519, _, _ = HD.detector.findDistance(15, 19, img, False)
                    D07, _, _ = HD.detector.findDistance(0, 7, img, False)
                    D011, _, _ = HD.detector.findDistance(0, 11, img, False)
                    D015, _, _ = HD.detector.findDistance(0, 15, img, False)
                    D019, _, _ = HD.detector.findDistance(0, 19, img, False)
                    D58, _, _ = HD.detector.findDistance(5, 8, img, False)'''
                    #D46, _, _ = HD.detector.findDistance(4, 6, img, False)
                    D310, _, _ = HD.detector.findDistance(3, 10, img, False)
                    D48, _, _, = HD.detector.findDistance(4, 8, img, False)
                    D412, _, _ = HD.detector.findDistance(4, 12, img, False)
                    D416, _, _ = HD.detector.findDistance(4, 16, img, False)
                    D420, _, _ = HD.detector.findDistance(4, 20, img, False)
                    D2019, _, _ = HD.detector.findDistance(20, 19, img, False)
                    D411, _, _ = HD.detector.findDistance(4, 11, img, False)

                    d_min = 3
                    d_max = 4.5
                    if D2019 != 0 and (d_max >= D48/D2019 >= d_min) and (d_max >= D412/D2019 >= d_min) and (d_max >= D416/D2019 >= d_min) and (d_max >= D420/D2019 >= d_min) :
                        gesture_data[gesture_binds["C_hand"]] = True
                    else :
                        gesture_data[gesture_binds["C_hand"]] = False

                    if (2 >= D48/D2019) and (2 >= D412/D2019) and (2 >= D416/D2019) and (2 >= D420/D2019) :
                        gesture_data[gesture_binds["O_hand"]] = True
                    else :
                        gesture_data[gesture_binds["O_hand"]] = False
                    
                    if not fingers[1] and not fingers[2] and not fingers[3] and not fingers[4] and not gesture_data[gesture_binds["C_hand"]] and not gesture_data[gesture_binds["O_hand"]]:
                        gesture_data[gesture_binds["Fist"]] = True
                    else :
                        gesture_data[gesture_binds["Fist"]] = False

                    global index_f_lm, swipe

                    '''12 10 9
                    abs(lmList[9][0] - lmList[10][0]) - (lmList[10][0] - lmList[12][0]) > '''

                    '''if (D310 <= 23*hands_size and fingers[1] and not fingers[2] and not fingers[3] and not fingers[4]) and (abs(lmList[5][1] - lmList[8][1]) <= 16*hands_size) :
                        swipe_speed = index_f_lm[0] - lmList[8][0]
                        index_f_lm = lmList[8]
                        print(swipe_speed)'''

                    #((D711 <= 15*2*hands_size) and (D1115 <= 15*2*hands_size) and (D1519 <= 15*2*hands_size)) and ((D07 <= 40*2*hands_size) and (D011 <= 30*2*hands_size) and (D015 <= 25*2*hands_size) and (D019 <= 30*2*hands_size))
                    if D48 <= D2019*0.5*hands_size and gesture_data["Volume_control"] != True and gesture_data[gesture_binds["Fist"]] != True and not gesture_data[gesture_binds["C_hand"]] and not gesture_data[gesture_binds["O_hand"]] :
                        gesture_data[gesture_binds["Th_Ind_Touch"]] = True
                        #cv2.putText(img, "Gesture: Mouse LB push", (15, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5, 2)
                    else :
                        gesture_data[gesture_binds["Th_Ind_Touch"]] = False
                    
                    if (D412 <= D2019*0.45*hands_size) and gesture_data[gesture_binds["Fist"]] != True and not gesture_data[gesture_binds["C_hand"]] and not gesture_data[gesture_binds["O_hand"]] : 
                        '''and ((dist(p7_x, p7_y, p11_x, p11_y) <= 15*hands_size) and (dist(p11_x, p11_y, p15_x, p15_y) <= 15*hands_size) and (dist(p15_x, p15_y, p19_x, p19_y) <= 15*hands_size)) and ((dist(p0_x, p0_y, p7_x, p7_y) <= 40*hands_size) and (dist(p0_x, p0_y, p11_x, p11_y) <= 30*hands_size) and (dist(p0_x, p0_y, p15_x, p15_y) <= 25*hands_size) and (dist(p0_x, p0_y, p19_x, p19_y) <= 30*hands_size))'''
                        gesture_data[gesture_binds["Th_Mid_Touch"]] = True
                        #cv2.putText(img, "Gesture: Mouse LB click", (15, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5, 2)
                    else :
                        gesture_data[gesture_binds["Th_Mid_Touch"]] = False

                    #gesture annotations
                    gestures_showing = 0
                    for gesture in gesture_data:
                        if gesture_data[gesture] == True:
                            gestures_showing += 1
                            cv2.putText(img, "Gesture: " + gesture, (15, 50 + 50*gestures_showing), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5, 2)

                    #volume control
                    length, img, lineInfo = HD.detector.findDistance(4, 8, img)
                
                    volBar = HD.np.interp(length, [50,200], [400, 150])
                    volPer = HD.np.interp(length, [50,200], [0, 100])

                    if not fingers[4] and gesture_data[gesture_binds["Fist"]] != True and not gesture_data[gesture_binds["C_hand"]] and not gesture_data[gesture_binds["O_hand"]] :
                        HD.volume.SetMasterVolumeLevelScalar(volPer/100, None)
                        gesture_data[gesture_binds["Th_Ind_Pinky_Control"]] = True
                    else :
                        gesture_data[gesture_binds["Th_Ind_Pinky_Control"]] = False

                    cv2.putText(img, "Volume: " + str(int(volPer)), (15, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5, 2)


                    #applying gestures' actions
                    h, w, _ = img.shape

                    dx = lmList[9][1] - w/2
                    dy = lmList[9][2] - h/2
                    mouse_x = width - (width/2 + dx * width / w * sensetivity)
                    mouse_y = height/2 + dy * height / h * sensetivity

                    if 0 < mouse_x < width and 0 < mouse_y < height :
                        if gesture_data["LKM_hold"] == True and gesture_data["LKM_press"] != True :
                            HD.pag.mouseDown(mouse_x, mouse_y, button='left')
                            #HD.pag.moveTo(mouse_x, mouse_y)
                        else :
                            HD.pag.mouseUp(mouse_x, mouse_y, button='left')
                            #HD.pag.moveTo(mouse_x, mouse_y)
                        if gesture_data["LKM_press"] == True and not gesture_activated["LKM_press"] :
                            HD.pag.click(mouse_x, mouse_y, 1, button='left')
                            gesture_activated["LKM_press"] = True
                        elif not gesture_data["LKM_press"] :
                            gesture_activated["LKM_press"] = False
                            #HD.pag.moveTo(mouse_x, mouse_y)
                        #else :
                            #HD.pag.moveTo(mouse_x, mouse_y)
                    if gesture_data["Media_pause"] == True :
                        pag.press("playpause")
                    if gesture_data["Media_next"] == True :
                        pag.press("nexttrack")
                    if gesture_data["Media_prev"] == True :
                        pag.press("prevtrack")
                    if gesture_data["Ctrl+S"] == True and not gesture_activated["Ctrl+S"] :
                        pag.hotkey('ctrl', 's')
                        gesture_activated["Ctrl+S"] = True
                    elif not gesture_data["Ctrl+S"] :
                        gesture_data["Ctrl+S"] = False
                        #print("ctrl+s")
                    if gesture_data["Prtscr"] == True :
                        pag.press("printscreen")
                        #pag.hotkey('ctrl', 's', interval= 0.5)
                        #print("prtscr")

                #converting image to pixmap (pixmap is used to display the image in the interface)
                if ret and detection_is_on == True:
                    rgbImage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(int(width*4/9), int(height*4/9), Qt.KeepAspectRatio)
                    self.changePixmap.emit(p)
                    '''if detection_is_on == True:
                        self.changePixmap.emit(p)
                    else :
                        self.changePixmap.emit(convertToQtFormat.scaled(0, 0, Qt.KeepAspectRatio))'''
            else :
                empty_cam_img = QImage('No cam.png').scaled(int(width*4/9), int(height*4/9), Qt.KeepAspectRatio)
                self.changePixmap.emit(empty_cam_img)

#Interface
class StaticGesturesSettings(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 Video'
        self.left = int(width*1/6)
        self.top = int(height*1/6)
        self.width = int(width*2/3)
        self.height = int(height*2/3)
        self.initUI()
    
    def back_to_hand_settings_window(self):
        hand_settings_window_g.show()
        hand_settings_window_g.move(self.geometry().x() - 1, self.geometry().y() - 45)
        self.hide()
    
    def set_gesture_binds(self):
        for i in range(len(list(gesture_binds))):
            gesture_binds[list(gesture_binds)[i]] = self.B_G_array[i].currentText()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(int(width*2/3), int(height*2/3))
        self.setStyleSheet('background-color: #f2f2f2;')
        
        B_back = QPushButton('', self)
        #B_back = QPushButton('Show|Hide'+ os.linesep + 'Camera', self)
        B_back.setToolTip('Назад')
        B_back_w = int(self.width/24)
        B_back_h = int(self.width/24)
        B_back.resize(B_back_w, B_back_h)
        B_back.setIcon(QIcon('Arrow left.png'))
        B_back.setIconSize(QSize(B_back_w - 16, B_back_h - 16))
        B_back.move(15, 15)
        B_back.setStyleSheet('QPushButton {background-color: #d6d6d6; color: black;}')
        B_back.clicked.connect(self.back_to_hand_settings_window)

        B_G_w = int(self.width/10*1.6)
        B_G_h = int(self.width/24*1.70)
        self.B_G_array = []
        
        #левая колонка
        for i in range(len(list(gesture_binds))):
            coeff = i % 5
            B_G_x = 300 + 360*int(i / 5)

            icon = QLabel(self)
            icon.resize(int(B_G_h*1.5), int(B_G_h*1.5))
            icon.move(B_G_x - icon.width() - 16, 16 + 135*coeff)
            pixmap = QPixmap(gesture_icons[list(gesture_binds)[i]]).scaled(icon.width(), icon.height())
            icon.setPixmap(pixmap)
            
            B_G = QComboBox(self)
            B_G.addItems(list(gesture_data))
            B_G.setToolTip('Назначить действие жесту')
            B_G.resize(B_G_w, B_G_h)
            B_G.move(B_G_x, 35 + 138*coeff)
            B_G.setStyleSheet('QPushButton {background-color: #d6d6d6; color: black; font-size: 32px;}')
            B_G.setCurrentText(gesture_binds[list(gesture_binds)[i]])
            self.B_G_array.append(B_G)

class DynamicGesturesSettings(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 Video'
        self.left = int(width*1/6)
        self.top = int(height*1/6)
        self.width = int(width*2/3)
        self.height = int(height*2/3)
        self.initUI()
    
    def back_to_hand_settings_window(self):
        hand_settings_window_g.show()
        hand_settings_window_g.move(self.geometry().x() - 1, self.geometry().y() - 45)
        self.hide()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(int(width*2/3), int(height*2/3))
        self.setStyleSheet('background-color: #f2f2f2;')
        
        B_back = QPushButton('', self)
        #B_back = QPushButton('Show|Hide'+ os.linesep + 'Camera', self)
        B_back.setToolTip('Назад')
        B_back_w = int(self.width/24)
        B_back_h = int(self.width/24)
        B_back.resize(B_back_w, B_back_h)
        B_back.setIcon(QIcon('Arrow left.png'))
        B_back.setIconSize(QSize(B_back_w - 16, B_back_h - 16))
        B_back.move(15, 15)
        B_back.setStyleSheet('QPushButton {background-color: #d6d6d6; color: black;}')
        B_back.clicked.connect(self.back_to_hand_settings_window)

class HandSettings(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 Video'
        self.left = int(width*1/6)
        self.top = int(height*1/6)
        self.width = int(width*2/3)
        self.height = int(height*2/3)
        self.initUI()
    
    def back_to_main_window(self):
        main_window.show()
        main_window.move(self.geometry().x() - 1, self.geometry().y() - 45)
        self.hide()
    
    def show_static_gestures_settings_window(self):
        self.static_gestures_settings_window.show()
        self.static_gestures_settings_window.move(self.geometry().x() - 1, self.geometry().y() - 45)
        self.hide()
        global hand_settings_window_g
        hand_settings_window_g = self

    def show_dynamic_gestures_settings_window(self):
        self.dynamic_gestures_settings_window.show()
        self.dynamic_gestures_settings_window.move(self.geometry().x() - 1, self.geometry().y() - 45)
        self.hide()
        global hand_settings_window_g
        hand_settings_window_g = self

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(int(width*2/3), int(height*2/3))
        self.setStyleSheet('background-color: #f2f2f2;')

        self.label = QLabel(self)
        self.label.setText("Настройки отслеживания рук")
        self.label.move(int(self.geometry().width()/2) - 150*2, 15)
        self.label.resize(self.width, 15*4)
        self.label.setStyleSheet("QLabel {font-size: 46px; color: black;}")

        self.static_gestures_settings_window = StaticGesturesSettings()
        self.dynamic_gestures_settings_window = DynamicGesturesSettings()

        B_back = QPushButton('', self)
        #B_back = QPushButton('Show|Hide'+ os.linesep + 'Camera', self)
        B_back.setToolTip('Назад')
        B_back_w = int(self.width/24)
        B_back_h = int(self.width/24)
        B_back.resize(B_back_w, B_back_h)
        B_back.setIcon(QIcon('Arrow left.png'))
        B_back.setIconSize(QSize(B_back_w - 16, B_back_h - 16))
        B_back.move(15, 15)
        B_back.setStyleSheet('QPushButton {background-color: #d6d6d6; color: black;}')
        B_back.clicked.connect(self.back_to_main_window)
        
        B_static_gestures_settings = QPushButton('Изменить назначения'+ os.linesep + 'статических жестов', self)
        #B_static_gestures_settings = QPushButton('Show|Hide'+ os.linesep + 'Camera', self)
        B_static_gestures_settings.setToolTip('Изменить назначения статических жестов')
        B_static_gestures_settings_w = int(self.width/23*8)
        B_static_gestures_settings_h = int(self.width/23*2)
        B_static_gestures_settings.resize(B_static_gestures_settings_w, B_static_gestures_settings_h)
        B_static_gestures_settings.setIconSize(QSize(B_static_gestures_settings_w - 16, B_static_gestures_settings_h - 16))
        B_static_gestures_settings.move(int(self.width/2 - B_static_gestures_settings_w/2), int(self.height*3/24))
        B_static_gestures_settings.setStyleSheet('QPushButton {background-color: #d6d6d6; color: black; font-size: 32px; border-radius: 15px}')
        B_static_gestures_settings.clicked.connect(self.show_static_gestures_settings_window)
        
        B_dynamic_gestures_settings = QPushButton('Изменить назначения'+ os.linesep + 'динамических жестов', self)
        #B_dynamic_gestures_settings = QPushButton('Show|Hide'+ os.linesep + 'Camera', self)
        B_dynamic_gestures_settings.setToolTip('Изменить назначения статических жестов')
        B_dynamic_gestures_settings_w = int(self.width/23*8)
        B_dynamic_gestures_settings_h = int(self.width/23*2)
        B_dynamic_gestures_settings.resize(B_dynamic_gestures_settings_w, B_dynamic_gestures_settings_h)
        B_dynamic_gestures_settings.setIconSize(QSize(B_dynamic_gestures_settings_w - 16, B_dynamic_gestures_settings_h - 16))
        B_dynamic_gestures_settings.move(int(self.width/2 - B_dynamic_gestures_settings_w/2), int(self.height*3/24) + B_dynamic_gestures_settings_h + 15)
        B_dynamic_gestures_settings.setStyleSheet('QPushButton {background-color: #d6d6d6; color: black; font-size: 32px; border-radius: 15px}')
        B_dynamic_gestures_settings.clicked.connect(self.show_dynamic_gestures_settings_window)

class EyeSettings(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 Video'
        self.left = int(width*1/6)
        self.top = int(height*1/6)
        self.width = int(width*2/3)
        self.height = int(height*2/3)
        self.initUI()
    
    def back_to_main_window(self):
        main_window.show()
        main_window.move(self.geometry().x() - 1, self.geometry().y() - 45)
        self.hide()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(int(width*2/3), int(height*2/3))
        self.setStyleSheet('background-color: #f2f2f2;')

        self.label = QLabel(self)
        self.label.setText("Настройки отслеживания глаз")
        self.label.move(int(self.geometry().width()/2) - 150*2, 15)
        self.label.resize(self.width, 15*4)
        self.label.setStyleSheet("QLabel {font-size: 46px; color: black;}")

        B_back = QPushButton('', self)
        #B_back = QPushButton('Show|Hide'+ os.linesep + 'Camera', self)
        B_back.setToolTip('Назад')
        B_back_w = int(self.width/24)
        B_back_h = int(self.width/24)
        B_back.resize(B_back_w, B_back_h)
        B_back.setIcon(QIcon('Arrow left.png'))
        B_back.setIconSize(QSize(B_back_w - 16, B_back_h - 16))
        B_back.move(15, 15)
        B_back.setStyleSheet('QPushButton {background-color: #d6d6d6; color: black;}')
        B_back.clicked.connect(self.back_to_main_window)
        
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 Video'
        self.left = int(width*1/6)
        self.top = int(height*1/6)
        self.width = int(width*2/3)
        self.height = int(height*2/3)
        self.initUI()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))
    
    @pyqtSlot()
    def show_cam(self):
        global detection_is_on
        if detection_is_on == False :
            detection_is_on = True
        else :
            detection_is_on = False
    
    def show_hand_settings(self):
        self.hand_settings_window.show()
        self.hand_settings_window.move(self.geometry().x() - 1, self.geometry().y() - 45)
        self.hide()
        global main_window
        main_window = self
    
    def show_eye_settings(self):
        self.eye_settings_window.show()
        self.eye_settings_window.move(self.geometry().x() - 1, self.geometry().y() - 45)
        self.hide()
        global main_window
        main_window = self

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        '''self.width = self.geometry().width()
        self.height = self.geometry().height()
        print("resize")'''
        self.resize(int(width*2/3), int(height*2/3))
        self.setStyleSheet('background-color: #f2f2f2;')
        self.label = QLabel(self)
        self.label.move(int(self.width*1/6) - 100, int(self.height*1/12))
        self.label.resize(int(self.width*2/3), int(self.height*2/3))
        th = Thread(self)
        th.changePixmap.connect(self.setImage)
        th.start()
        
        self.hand_settings_window = HandSettings()
        self.eye_settings_window = EyeSettings()

        B_detection_is_on = QPushButton('', self)
        #B_detection_is_on = QPushButton('Show|Hide'+ os.linesep + 'Camera', self)
        B_detection_is_on.setToolTip('Включить|Выключить отслеживание')
        B_detection_is_on_w = int(self.width*2.8/24)
        B_detection_is_on_h = int(self.width*2.8/24)
        B_detection_is_on.resize(B_detection_is_on_w, B_detection_is_on_h)
        B_detection_is_on.setIcon(QIcon('B_cam_show.png'))
        B_detection_is_on.setIconSize(QSize(B_detection_is_on_w - 16, B_detection_is_on_h - 16))
        B_detection_is_on.move(int(self.width/2)-int(B_detection_is_on_w/2) - 100, int(self.height*21/24)-int(B_detection_is_on_h/2))
        B_detection_is_on.setStyleSheet('QPushButton {background-color: #d6d6d6; color: black;}')
        B_detection_is_on.clicked.connect(self.show_cam)
        
        B_hand_detection_settings = QPushButton('', self)
        #B_hand_detection_settings = QPushButton('Show|Hide'+ os.linesep + 'Camera', self)
        B_hand_detection_settings.setToolTip('Настройки отслеживания рук')
        B_hand_detection_settings_w = int(self.width*2.7/24)
        B_hand_detection_settings_h = int(self.width*2.7/24)
        B_hand_detection_settings.resize(B_hand_detection_settings_w, B_hand_detection_settings_h)
        B_hand_detection_settings.setIcon(QIcon('Настройки рук.png'))
        B_hand_detection_settings.setIconSize(QSize(B_hand_detection_settings_w - 15*2, B_hand_detection_settings_h - 15*2))
        B_hand_detection_settings.move(int(self.width)-int(B_hand_detection_settings_w*1.5), int(self.height*21/24)-int(B_hand_detection_settings_h/2))
        B_hand_detection_settings.setStyleSheet('QPushButton {background-color: #d6d6d6; color: black;}')
        B_hand_detection_settings.clicked.connect(self.show_hand_settings)
        
        B_eye_detection_settings = QPushButton('', self)
        #B_eye_detection_settings = QPushButton('Show|Hide'+ os.linesep + 'Camera', self)
        B_eye_detection_settings.setToolTip('Настройки отслеживания глаз')
        B_eye_detection_settings_w = int(self.width*2.7/24)
        B_eye_detection_settings_h = int(self.width*2.7/24)
        B_eye_detection_settings.resize(B_eye_detection_settings_w, B_eye_detection_settings_h)
        B_eye_detection_settings.setIcon(QIcon('Настройки глаз.png'))
        B_eye_detection_settings.setIconSize(QSize(B_eye_detection_settings_w - 15*2, B_eye_detection_settings_h - 15*2))
        B_eye_detection_settings.move(int(self.width)-int(B_eye_detection_settings_w*2.5) - 15*2, int(self.height*21/24)-int(B_eye_detection_settings_h/2))
        B_eye_detection_settings.setStyleSheet('QPushButton {background-color: #d6d6d6; color: black;}')
        B_eye_detection_settings.clicked.connect(self.show_eye_settings)
        
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())