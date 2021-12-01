from logging import fatal, log
import sys
import os
from typing import Counter
import cv2
from PyQt5 import uic, QtCore, QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, Qt, QByteArray, QUrl, QDateTime
from PyQt5.QtGui import QImage, QPixmap, QMovie
# from PyQt5.QtWidgets import QDialog, QApplication, QScrollArea, QWidget, QLabel
from PyQt5.QtWidgets import *
from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtWebEngineCore
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
import logging.handlers
import mediapipe as mp
import numpy as np
from threading import Timer
import time
from numpy.core.fromnumeric import resize

# 로그 생성
logger = logging.getLogger()
fileMaxByte = 1024 * 1024 * 10
formatter = logging.Formatter("%(asctime)s;[%(levelname)s];%(message)s", "%Y-%m-%d %H:%M:%S")
fileHandler = logging.handlers.RotatingFileHandler('./virtual_Fit.log', maxBytes=fileMaxByte, backupCount=5)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
logger.setLevel(logging.DEBUG)

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

IMAGE_FILES = []
BG_COLOR = (192, 192, 192)  # gray

try:  # 임포트 완료 - ui 연결
    keypadPage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 'page1_keypad.ui'))[0]
    loginPage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 'page1_login.ui'))[0]
    aiFreePage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 'page2_aifree.ui'))[0]
    selExercisePage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 'page3_selectexercise.ui'))[0]
    posePage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 'page4_pose.ui'))[0]
    trainerPage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 'page5_trainer.ui'))[0]
    weightPage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 'page6_weight.ui'))[0]
    exercisingPage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 'page7_exercising.ui'))[0]
    restPage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 'page8_rest.ui'))[0]
    finishPage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 'page9_finish.ui'))[0]
    planPopup = uic.loadUiType(os.path.join(os.path.abspath('ui'), 'page6_planpopup.ui'))[0]

except FileNotFoundError:    # kimsungsoo 경로 예외 추가
    keypadPage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 'page1_keypad.ui'))[0]
    loginPage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 'page1_login.ui'))[0]
    aiFreePage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 'page2_aifree.ui'))[0]
    selExercisePage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 'page3_selectexercise.ui'))[0]
    posePage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 'page4_pose.ui'))[0]
    trainerPage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 'page5_trainer.ui'))[0]
    weightPage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 'page6_weight.ui'))[0]
    exercisingPage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 'page7_exercising.ui'))[0]
    restPage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 'page8_rest.ui'))[0]
    finishPage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 'page9_finish.ui'))[0]
    planPopup = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 'page6_planpopup.ui.ui'))[0]

def goNextPage():
    widget.setCurrentIndex(widget.currentIndex()+1)

def goBackPage():
    widget.setCurrentIndex(widget.currentIndex()-1)

def goBack2Page():
    widget.setCurrentIndex(widget.currentIndex()-2)

def go6Page():
    widget.setCurrentIndex(widget.currentIndex() + 2)

def goHomePage(num):
    widget.setCurrentIndex(widget.currentIndex()-int(num))

class Communicate(QObject):
    startCam = pyqtSignal()
    startMediapipe = pyqtSignal()

#1 키패드 페이지
class KeypadPage(QDialog, keypadPage):
    def __init__(self):
        super(KeypadPage, self).__init__()
        self.setupUi(self)

# 6-1. Plan Pop Up 창 이동 11/25 - resetPlan 버튼 누를 시 꺼짐 현상. 원인 모르겠음.
class PlanPopup(QDialog, planPopup):
    def __init__(self):
        super(PlanPopup, self).__init__()
        self.setupUi(self)

        self.reset_btn.clicked.connect(self.resetPlan)
        self.save_btn.clicked.connect(self.savePlan)
        # 슬라이드 바의 시그널 사용
        self.set_bar.valueChanged.connect(self.showSetValue)
        self.rep_bar.valueChanged.connect(self.showRepValue)

        self.set_num = ""
        self.req_num = ""

    # 슬라이드 바의 시그널 이용 - 슬라이드 바의 값이 변경되면 해당 라벨에 값을 표시
    def showSetValue(self):
        self.set_lb.setText(str(self.set_bar.value()))

    def showRepValue(self):
        self.rep_lb.setText(str(self.rep_bar.value()))

    def savePlan(self):
        self.set_num = self.set_bar.value()
        self.req_num = self.rep_bar.value()
        self.close()

    def resetPlan(self):
        self.set_bar.setValue(4)
        self.rep_bar.setValue(12)
        self.set_num = self.set_bar.value()
        self.req_num = self.rep_bar.value()

#1 로그인 페이지
class LoginPage(QDialog, loginPage):
    def __init__(self):
        super(LoginPage, self).__init__()
        self.setupUi(self)

        self.login_btn.clicked.connect(self.loginKeypadPage)
        self.pass_btn.clicked.connect(goNextPage)

        # 상단 날짜, 시간 표시 11/25
        self.showtime()

    def showtime(self):
        datetime = QDateTime.currentDateTime()
        self.datetime_lb.setText(datetime.toString(Qt.DefaultLocaleLongDate))

        # 타이머 설정  (1초마다, 콜백함수)
        timer = Timer(1, self.showtime)
        timer.start()

    def loginKeypadPage(self):
        keypadPage = KeypadPage()
        keypadPage.exec_()

#2 ai free 선택 페이지
class AiFreePage(QDialog, aiFreePage):
    def __init__(self):
        super(AiFreePage, self).__init__()
        self.setupUi(self)

        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(goBackPage)
        self.logout_btn.clicked.connect(goBackPage)
        self.ai_btn.clicked.connect(goNextPage)
        #self.free_btn.clicked.connect(goNextPage)

        # 상단 날짜, 시간 표시 11/25
        self.showtime()

    def showtime(self):
        datetime = QDateTime.currentDateTime()
        self.datetime_lb.setText(datetime.toString(Qt.DefaultLocaleLongDate))

        # 타이머 설정  (1초마다, 콜백함수)
        timer = Timer(1, self.showtime)
        timer.start()

#3 운동자세 선택 페이지
class SelExercisePage(QDialog, selExercisePage):
    def __init__(self):
        super(SelExercisePage, self).__init__()
        self.setupUi(self)

        self.all_btn.clicked.connect(self.moveNextPage)
        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(2))

        # 상단 날짜, 시간 표시 11/25
        self.showtime()

    def moveNextPage(self):
        goNextPage()

    def showtime(self):
        datetime = QDateTime.currentDateTime()
        self.datetime_lb.setText(datetime.toString(Qt.DefaultLocaleLongDate))

        # 타이머 설정  (1초마다, 콜백함수)
        timer = Timer(1, self.showtime)
        timer.start()

# --- 하체 전체 운동 관련 페이지 시작 ----------------------------------------------
#4 자세 피드백 영상 페이지
class PosePage(QDialog, posePage):
    def __init__(self):
        super(PosePage, self).__init__()
        self.setupUi(self)

        self.trainer_btn.clicked.connect(goNextPage)
        self.weight_btn.clicked.connect(go6Page)
        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(3))

        self.streamingThread = StreamingThread()
        self.streamingThread2 = StreamingThread2()

        # self.startCam()
        # self.startCam2()

    def startCam(self):
        print("startCam")
        self.streamingThread.wait(1)
        self.streamingThread.setRtsp(0)
        self.streamingThread.setSize(self.label.size())
        self.streamingThread.changePixmap.connect(self.setImage)
        self.streamingThread.start()
        self.show()

    def startCam2(self):
        print("12")
        #vidfile = "/Users/kalo/Desktop/vscode/python/TestProject/newtonz_legpress.mp4"
        vidfile = 0
        self.streamingThread2.wait(1)
        self.streamingThread2.setRtsp(vidfile)
        self.streamingThread2.setSize(self.label_4.size())
        self.streamingThread2.pose_changePixmap.connect(self.setImage2)
        self.streamingThread2.start()
        self.show()

    def stopCam(self):
        self.streamingThread.stop()

    def stopCam2(self):
        self.streamingThread2.stop()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    @pyqtSlot(QImage)
    def setImage2(self, image):
        self.label_4.setPixmap(QPixmap.fromImage(image))

        # 상단 날짜, 시간 표시 11/25
        self.showtime()

    def showtime(self):
        datetime = QDateTime.currentDateTime()
        self.datetime_lb.setText(datetime.toString(Qt.DefaultLocaleLongDate))

        # 타이머 설정  (1초마다, 콜백함수)
        timer = Timer(1, self.showtime)
        timer.start()

#5 트레이너 설명 페이지 삽입_211102
class TrainerPage(QDialog, trainerPage):
    def __init__(self):
        super(TrainerPage, self).__init__()
        self.setupUi(self)

        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(4))

        self.webview=QtWebEngineWidgets.QWebEngineView(self.widget)
        self.webview.setUrl(QUrl("https://www.youtube.com/embed/FQ_A97PMrcQ?autoplay=1"))
        self.webview.setGeometry(0, 0, 1000, 800)

        # self.gif1 = QMovie('img/gif1.gif', QByteArray(), self)
        # self.gif2 = QMovie('img/gif2.gif', QByteArray(), self)
        #
        # self.gif1_label.setMovie(self.gif1)
        # self.gif2_label.setMovie(self.gif2)
        #
        # self.gif1.start()
        # self.gif2.start()

        # 상단 날짜, 시간 표시 11/25
        self.showtime()

    def showtime(self):
        datetime = QDateTime.currentDateTime()
        self.datetime_lb.setText(datetime.toString(Qt.DefaultLocaleLongDate))

        # 타이머 설정  (1초마다, 콜백함수)
        timer = Timer(1, self.showtime)
        timer.start()

#6 중량 선택 페이지 순서 수정
class WeightPage(QDialog, weightPage):
    def __init__(self):
        super(WeightPage, self).__init__()
        self.setupUi(self)
        self.planPopup = PlanPopup()

        self.btn_list = []
        self.streamingThread = StreamingThread()
        self.TopViewFlag = False
        # self.startexercise_btn.clicked.connect(goNextPage)
        self.setplan_btn.clicked.connect(self.planpopupPage)
        self.back_btn.clicked.connect(goBack2Page)
        self.home_btn.clicked.connect(self.homeClear)
        self.showover_btn.clicked.connect(self.showTopCamera)
        self.lblTopCameraView.hide()
        self.initweight = 10

        self.weight_dial.setPageStep(100)
        self.weight_dial.setSingleStep(10)
        #211111_윤성근_다이얼- 라벨 연결.
        self.weight_dial.valueChanged.connect(self.showWeight)

        self.weightTable.verticalHeader().setVisible(False)  # 상단 헤더 없애기
        self.weightTable.horizontalHeader().setVisible(False)  # 좌측 헤더 없애기

        header = self.weightTable.horizontalHeader()
        self.weightTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        # self.weightTable.horizontalHeader().hide()
        # self.weightTable.setColumnCount(1)
        # self.weightTable.setColumnWidth(0,0)

        self.initweightValue()

    def initweightValue(self):
        self.kg_lb.setText(str(self.initweight) + " KG")
        self.weight_dial.setValue = self.initweight

    def startCam(self):
        print("topView on")
        self.streamingThread.wait(1)
        self.streamingThread.setRtsp(0)
        self.streamingThread.setSize(self.lblTopCameraView.size())
        self.streamingThread.changePixmap.connect(self.setImage)
        self.streamingThread.start()
        # self.show()

    def stopCam(self):
        print("topView stop")
        self.streamingThread.stop()
        # self.hide()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.lblTopCameraView.setPixmap(QPixmap.fromImage(image))

    def showWeight(self):
        weightValue = self.weight_dial.value()
        self.setWeightTableUI(weightValue)
        self.showtime()  # 상단 날짜, 시간 표시 11/25

    def setWeightTableUI(self, v):
        self.kg_lb.setText(str(v) + " KG")
        self.weightTable.setRowCount(0)
        self.procWeight = 0
        listValue = []
        maxcnt = 5
        minValue = v % maxcnt
        self.idx = 0
        self.procWeight = v - minValue
        # print(self.procWeight)

        def GetUnit200Value():
            if self.idx < 4:
                if self.procWeight >= 200:
                    self.procWeight = self.procWeight - 200
                    listValue.insert(self.idx, 200)
                    self.idx += 1
                    GetUnit200Value()
            else:
                return

        def GetUnit100Value():
            if self.idx < 4:
                if self.procWeight >= 100:
                    self.procWeight = self.procWeight - 100
                    listValue.insert(self.idx, 100)
                    self.idx += 1
                    GetUnit100Value()
            else:
                return

        def GetUnit50Value():
            if self.idx < 4:
                if self.procWeight >= 50:
                    self.procWeight = self.procWeight - 50
                    listValue.insert(self.idx, 50)
                    self.idx += 1
                    GetUnit50Value()
            else:
                return

        def GetUnit10Value():
            if self.idx < 4:
                if self.procWeight >= 10:
                    self.procWeight = self.procWeight - 10
                    listValue.insert(self.idx, 10)
                    self.idx += 1
                    GetUnit10Value()
            else:
                return

        def GetUnit5Value():
            if self.idx < 4:
                if self.procWeight >= 5:
                    self.procWeight = self.procWeight - 5
                    listValue.insert(self.idx, 5)
                    self.idx += 1
                    GetUnit5Value()
            else:
                return
        # print("v:" + str(v) + "   avg:" + str(averageWeight))

        if 0 < v < 5:
            listValue.insert(0, v)
        elif v >= 5:
            GetUnit200Value()
            GetUnit100Value()
            GetUnit50Value()
            GetUnit10Value()
            GetUnit5Value()
        else:
            return

        listValue.insert(self.idx, self.procWeight + minValue)  # 기본 바벨 기준으로 배열 추가 후에 남은 무게 추가

        # print(listValue)
        self.weightTable.setRowCount(len(listValue))

        for i in range(len(listValue)):
            self.weightTable.setItem(i, 0, QTableWidgetItem(str(listValue[i]) + "KG"))
            color = None
            font = None

            if listValue[i] < 5:
                self.weightTable.setRowHeight(i, 10)
                color = QtGui.QColor(100, 100, 150)
                font = QtGui.QFont('Arial', 15)
            elif 5 <= listValue[i] < 10:
                self.weightTable.setRowHeight(i, 20)
                color = QtGui.QColor(200, 100, 150)
                font = QtGui.QFont('Arial', 20)
            elif 10 <= listValue[i] < 50:
                self.weightTable.setRowHeight(i, 30)
                color = QtGui.QColor(100, 200, 150)
                font = QtGui.QFont('Arial', 30)
            elif 50 <= listValue[i] < 100:
                self.weightTable.setRowHeight(i, 45)
                color = QtGui.QColor(50, 155, 170)
                font = QtGui.QFont('Arial', 35)
            elif 100 <= listValue[i] < 200:
                self.weightTable.setRowHeight(i, 60)
                color = QtGui.QColor(150, 100, 200)
                font = QtGui.QFont('Arial', 40)
            else:
                self.weightTable.setRowHeight(i, 80)
                color = QtGui.QColor(190, 250, 210)
                font = QtGui.QFont('Arial', 50)

            self.weightTable.item(i, 0).setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
            self.weightTable.item(i, 0).setFont(font)  # 글꼴 크기
            self.weightTable.item(i, 0).setBackground(color)

    def showtime(self):
        datetime = QDateTime.currentDateTime()
        self.datetime_lb.setText(datetime.toString(Qt.DefaultLocaleLongDate))

        # 타이머 설정  (1초마다, 콜백함수)
        timer = Timer(1, self.showtime)
        timer.start()

    def planpopupPage(self):
        self.planPopup.exec_()
        print("set_bar : ", self.planPopup.set_num)
        print("rep_bar : ", self.planPopup.req_num)

    def homeClear(self):
        self.planPopup.resetPlan()
        widget.setCurrentIndex(widget.currentIndex() - 5)

    def showTopCamera(self):
        if self.TopViewFlag:
            self.lblTopCameraView.hide()
            self.TopViewFlag = False
            self.stopCam()
        else:
            self.lblTopCameraView.show()
            self.TopViewFlag = True
            self.startCam()

# --- 하체 전체 운동 관련 페이지 끝 ----------------------------------------------
#7 운동중 페이지
class ExercisingPage(QDialog, exercisingPage):
    def __init__(self):
        super(ExercisingPage, self).__init__()
        self.setupUi(self)

        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(6))

        # 상단 날짜, 시간 표시 11/25
        self.showtime()

    def showtime(self):
        datetime = QDateTime.currentDateTime()
        self.datetime_lb.setText(datetime.toString(Qt.DefaultLocaleLongDate))

        # 타이머 설정  (1초마다, 콜백함수)
        timer = Timer(1, self.showtime)
        timer.start()

#8 휴식 페이지
class RestPage(QDialog, restPage):
    def __init__(self):
        super(RestPage, self).__init__()
        self.setupUi(self)

        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(7))

        # 상단 날짜, 시간 표시 11/25
        self.showtime()

    def showtime(self):
        datetime = QDateTime.currentDateTime()
        self.datetime_lb.setText(datetime.toString(Qt.DefaultLocaleLongDate))

        # 타이머 설정  (1초마다, 콜백함수)
        timer = Timer(1, self.showtime)
        timer.start()

#9 운동 끝 페이지
class FinishPage(QDialog, finishPage):
    def __init__(self):
        super(FinishPage, self).__init__()
        self.setupUi(self)

        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(8))

        # 상단 날짜, 시간 표시 11/25
        self.showtime()

    def showtime(self):
        datetime = QDateTime.currentDateTime()
        self.datetime_lb.setText(datetime.toString(Qt.DefaultLocaleLongDate))

        # 타이머 설정  (1초마다, 콜백함수)
        timer = Timer(1, self.showtime)
        timer.start()

class StreamingThread(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self.running = True
        self.camUrl = ""
        self.Qsize = None
        self.cap = None

    def setRtsp(self, camUrl):
        self.camUrl = camUrl
        self.running = True

    def setSize(self, Qsize):
        self.Qsize = Qsize

    def run(self):
        try:
            if self.camUrl != "":
                self.cap = cv2.VideoCapture(self.camUrl)
                while self.running:
                    if self.cap.isOpened():
                        success, frame = self.cap.read()

                        if success:
                            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            rgbImage = cv2.flip(rgbImage, 1)
                            h, w, ch = rgbImage.shape
                            bytesPerLine = ch * w
                            convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                            p = convertToQtFormat.scaled(self.Qsize, Qt.KeepAspectRatio)
                            self.changePixmap.emit(p)
                            QApplication.processEvents()
            else:
                self.stop()
        except:
            self.stop()

    def stop(self):
        if self.running:
            self.running = False
            print("stop1")
        self.quit()

class StreamingThread2(QThread):
    pose_changePixmap = pyqtSignal(QImage)
    global image

    flag = 0
    counter = 0
    stage = None

    def __init__(self):
        print("init")
        super().__init__()
        self.running = True
        self.camUrl = ""
        self.Qsize = None
        self.cap = None

    def setRtsp(self, camUrl):
        self.camUrl = camUrl
        self.running = True

    def setSize(self, Qsize):
        self.Qsize = Qsize

    def run(self):
        def calculate_angle(a, b, c):
            a = np.array(a)  # First
            b = np.array(b)  # Mid
            c = np.array(c)  # End

            radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
            angle = np.abs(radians*180.0/np.pi)

            if angle > 180.0:
                angle = 360-angle

            return angle

        if self.camUrl != "":
            self.cap = cv2.VideoCapture(self.camUrl)

            with mp_pose.Pose(
                    static_image_mode=True,
                    model_complexity=2,
                    enable_segmentation=True,
                    min_detection_confidence=0.5) as pose:

                for idx, file in enumerate(IMAGE_FILES):
                    image = cv2.imread(file)
                    image_height, image_width, _ = image.shape
                    # Convert the BGR image to RGB before processing.
                    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

                    if not results.pose_landmarks:
                        continue
                    print(
                        f'Nose coordinates: ('
                        f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].x * image_width}, '
                        f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y * image_height})'
                    )

                    annotated_image = image.copy()
                    # Draw segmentation on the image.
                    # To improve segmentation around boundaries, consider applying a joint
                    # bilateral filter to "results.segmentation_mask" with "image".
                    condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.1
                    bg_image = np.zeros(image.shape, dtype=np.uint8)
                    #bg_image[:] = BG_COLOR
                    annotated_image = np.where(condition, annotated_image, bg_image)
                    # Draw pose landmarks on the image.
                    mp_drawing.draw_landmarks(
                        annotated_image,
                        results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
                    cv2.imwrite('/tmp/annotated_image' + str(idx) + '.png', annotated_image)
                    # Plot pose world landmarks.
                    mp_drawing.plot_landmarks(
                        results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)

            with mp_pose.Pose(
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5) as pose:

                while self.running:
                    print("mediapipe")
                    success, frame = self.cap.read()

                    if not success:
                        print("Ignoring empty camera frame.")
                        # If loading a video, use 'break' instead of 'continue'.
                        break

                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = cv2.flip(image, 1)

                    results = pose.process(image)

                    image.flags.writeable = True
                    # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                    try:
                        landmarks = results.pose_landmarks.landmark

                        # Get coordinates
                        hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                        knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                        ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                        angle = calculate_angle(hip, knee, ankle)

                        # Visualize angle
                        cv2.putText(image, "Angle = " + str(round(angle, 2)),
                                    tuple(np.multiply(knee, [self.cap.get(3), self.cap.get(4)]).astype(int)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3, cv2.LINE_AA
                                    )

                        # Curl counter logic
                        if angle > 150 and self.stage == 'down':
                            self.stage = "up"
                            self.counter += 1
                        if angle < 80:
                            self.stage = "down"
                    except:
                        pass

                    # Render curl counter
                    # Setup status box
                    cv2.rectangle(image, (0, 0), (225, 73), (245, 117, 16), -1)

                    # Rep data
                    cv2.putText(image, 'REPS', (15, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                    cv2.putText(image, str(self.counter), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

                    # Stage data
                    cv2.putText(image, 'STAGE', (65, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                    cv2.putText(image, self.stage, (60, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

                    mp_drawing.draw_landmarks(
                        image,
                        results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                        mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                    )

                    h, w, ch = image.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(image.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(self.Qsize, Qt.KeepAspectRatio)
                    self.pose_changePixmap.emit(p)
                    QApplication.processEvents()

        else:
            self.stop()

    def stop(self):
        if self.running:
            self.running = False
            print("stop2")
        self.quit()

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.scroll = QScrollArea()

        #QstackedWidget 기능 연결 및 인스턴스 생성
        # self.widget = QtWidgets.QStackedWidget()

        loginPage = LoginPage()
        aiFreePage = AiFreePage()
        selExercisePage = SelExercisePage()
        posePage = PosePage()
        trainerPage = TrainerPage()
        weightPage = WeightPage()
        exercisingPage = ExercisingPage()
        restpage = RestPage()
        fisishpage = FinishPage()

        #widget에 모든 페이지 추가
        widget.addWidget(loginPage)
        widget.addWidget(aiFreePage)
        widget.addWidget(selExercisePage)
        widget.addWidget(posePage)
        widget.addWidget(trainerPage)
        widget.addWidget(weightPage)
        # widget.addWidget(exercisingPage)
        widget.addWidget(restpage)
        widget.addWidget(fisishpage)

        #widget 크기와 보여주는 함수
        widget.setFixedHeight(1920)  # 높이
        widget.setFixedWidth(1080)  # 너비

        # self.c = Communicate()
        # self.c.startCam.connect(self.StartTopCam)

        # def StartTopCam():
        #     posePage.startCam()
        #     posePage.startCam2()
        # widget.show()

        #Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(widget)

        self.setCentralWidget(self.scroll)

        self.setGeometry(0, 0, 1080, 900)
        self.show()

        return


#이하 main 코드
if __name__ == '__main__':
    # Some setup for qt
    app = QApplication(sys.argv)

    #QstackedWidget 기능 연결 및 인스턴스 생성
    widget = QtWidgets.QStackedWidget()
    main = Window()

    # loginPage = LoginPage()
    # aiFreePage = AiFreePage()
    # selExercisePage = SelExercisePage()
    # posePage = PosePage()
    # trainerPage = TrainerPage()
    # weightPage = WeightPage()
    # exercisingPage = ExercisingPage()
    # restpage = RestPage()
    # fisishpage = FinishPage()

    # #widget에 모든 페이지 추가
    # widget.addWidget(loginPage)
    # widget.addWidget(aiFreePage)
    # widget.addWidget(selExercisePage)
    # widget.addWidget(posePage)
    # widget.addWidget(trainerPage)
    # widget.addWidget(weightPage)
    # # widget.addWidget(exercisingPage)
    # widget.addWidget(restpage)
    # widget.addWidget(fisishpage)

    # #widget 크기와 보여주는 함수
    # widget.setFixedHeight(1920)  # 높이
    # widget.setFixedWidth(1080)  # 너비

    # widget.show()

    # posePage.stopCam()
    # posePage.stopCam2()
    # weightPage.stopCam()

    # posePage.streamingThread.requestInterruption()
    # posePage.streamingThread2.requestInterruption()
    # weightPage.streamingThread.requestInterruption()
    try:
        sys.exit(app.exec_())
    except:
        print("Exit")
        # print(e)