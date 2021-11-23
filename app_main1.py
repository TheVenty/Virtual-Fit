from logging import log
import sys
import os
import cv2
from PyQt5 import uic, QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt, QByteArray, QUrl, QDateTime
from PyQt5.QtGui import QImage, QPixmap, QMovie
from PyQt5.QtWidgets import QDialog, QApplication, QScrollArea, QWidget
from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtWebEngineCore
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
import logging.handlers
import mediapipe as mp
import numpy as np

#로그 생성
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
BG_COLOR = (192, 192, 192) # gray

try:  # 임포트 완료 - ui연결
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
    planPopup = uic.loadUiType(os.path.join(os.path.abspath('ui'), 's_planpopup.ui'))[0]

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
    planPopup = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 's_planpopup.ui'))[0]

def goNextPage():
    widget.setCurrentIndex(widget.currentIndex()+1)

def goBackPage():
    widget.setCurrentIndex(widget.currentIndex()-1)

def go6Page():
    widget.setCurrentIndex(widget.currentIndex() + 2)

def goHomePage(num):
    widget.setCurrentIndex(widget.currentIndex()-int(num))


#1 키패드 페이지
class KeypadPage(QDialog, keypadPage):
    def __init__(self):
        super(KeypadPage, self).__init__()
        self.setupUi(self)


#1 로그인 페이지
class LoginPage(QDialog, loginPage):
    def __init__(self):
        super(LoginPage, self).__init__()
        self.setupUi(self)

        self.login_btn.clicked.connect(self.loginKeypadPage)
        self.pass_btn.clicked.connect(goNextPage)

        datetime = QDateTime.currentDateTime()
        self.datetime_lb.setText(datetime.toString(Qt.DefaultLocaleLongDate))
        self.datetime_lb.repaint()


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

#3 운동자세 선택 페이지
class SelExercisePage(QDialog, selExercisePage):
    def __init__(self):
        super(SelExercisePage, self).__init__()
        self.setupUi(self)

        self.all_btn.clicked.connect(goNextPage)
        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(2))

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

        self.startCam()
        self.startCam2()

    def startCam(self):
        print("11")
        self.streamingThread.wait(1)
        self.streamingThread.setRtsp(0)
        self.streamingThread.setSize(self.label.size())
        self.streamingThread.changePixmap.connect(self.setImage)
        self.streamingThread.start()
        self.show()

    def startCam2(self):
        print("12")

        # vidfile = "/Users/kalo/Desktop/vscode/python/TestProject/newtonz_legpress.mp4"
        vidfile = 0
        self.streamingThread2.wait(1)
        self.streamingThread2.setRtsp(vidfile)
        self.streamingThread2.setSize(self.label_4.size())
        self.streamingThread2.pose_changePixmap.connect(self.setImage2)
        self.streamingThread2.start()
        self.show()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    @pyqtSlot(QImage)
    def setImage2(self, image):
        self.label_4.setPixmap(QPixmap.fromImage(image))

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

        self.gif1 = QMovie('img/gif1.gif', QByteArray(), self)
        self.gif2 = QMovie('img/gif2.gif', QByteArray(), self)

        self.gif1_label.setMovie(self.gif1)
        self.gif2_label.setMovie(self.gif2)

        self.gif1.start()
        self.gif2.start()

#6 중량 선택 페이지 순서 수정
class WeightPage(QDialog, weightPage):
    def __init__(self):
        super(WeightPage, self).__init__()
        self.setupUi(self)

        self.setplan_btn.clicked.connect(goNextPage)
        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(5))

#211111_윤성근_다이얼- 라벨 연결.
        self.weight_dial.valueChanged.connect(self.showWeight)        

    def showWeight(self) :
        self.kg_lb.setText(str(self.weight_dial.value()) + " KG")


#7 운동중 페이지
class ExercisingPage(QDialog, exercisingPage):
    def __init__(self):
        super(ExercisingPage, self).__init__()
        self.setupUi(self)

        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(6))

#8 휴식 페이지
class RestPage(QDialog, restPage):
    def __init__(self):
        super(RestPage, self).__init__()
        self.setupUi(self)

        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(7))

#9 운동 끝 페이지
class FinishPage(QDialog, finishPage):
    def __init__(self):
        super(FinishPage, self).__init__()
        self.setupUi(self)

        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(8))


#윤성근 운동 Plan Pop Up 창 삽입_211014 - resetPlan 버튼 누를 시 꺼짐 현상. 원인 모르겠음.
class PlanPopup(QDialog, planPopup):
    def __init__(self):
        super(PlanPopup, self).__init__()
        self.setupUi(self)

        self.back_btn.clicked.connect(goBackPage)
        self.reset_btn.clicked.connect(self.resetPlan)

        #슬라이드 바의 시그널 사용
        self.set_bar.valueChanged.connect(self.showSetValue)
        self.rep_bar.valueChanged.connect(self.showRepValue)

    #슬라이드 바의 시그널 이용 - 슬라이드 바의 값이 변경되면 해당 라벨에 값을 표시    
    def showSetValue(self):
     self.set_lb.setText(str(self.set_bar.value()))

    def showRepValue(self):
        self.rep_lb.setText(str(self.rep_bar.value()))

    def resetPlan(self):
        self.set_lb.setValue(4)
        self.rep_lb.setValue(12)

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
        self.quit()

class StreamingThread2(QThread):
    pose_changePixmap = pyqtSignal(QImage)
    global image

    flag = 0
    counter = 0 
    stage = None

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
        
        def calculate_angle(a,b,c):
            a = np.array(a) # First
            b = np.array(b) # Mid
            c = np.array(c) # End
            
            radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
            angle = np.abs(radians*180.0/np.pi)
            
            if angle >180.0:
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
                
                while self.cap.isOpened():
                    
                    success, frame = self.cap.read()
                    
                    if not success:
                        print("Ignoring empty camera frame.")
                        # If loading a video, use 'break' instead of 'continue'.
                        break
                    
                    
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # image = cv2.flip(image, 1)
                    
                    results = pose.process(image)
                    
                    image.flags.writeable = True
                    # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                    try:
                        landmarks = results.pose_landmarks.landmark
                        
                        # Get coordinates
                        hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                        knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                        ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                        
                        angle = calculate_angle(hip, knee, ankle)
                        
                        # Visualize angle
                        cv2.putText(image, "Angle = " + str(round(angle, 2)), 
                                    tuple(np.multiply(knee, [self.cap.get(3), self.cap.get(4)]).astype(int)), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3, cv2.LINE_AA
                                    )
                        
                        # Curl counter logic
                        if angle > 150 and self.stage =='down':
                            self.stage = "up"
                            self.counter +=1
                        if angle < 80 :
                            self.stage="down"
                    except:
                        pass
                    
                    # Render curl counter
                    # Setup status box
                    cv2.rectangle(image, (0,0), (225,73), (245,117,16), -1)

                    # Rep data
                    cv2.putText(image, 'REPS', (15,12), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
                    cv2.putText(image, str(self.counter), (10,60), 
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
                    
                    # Stage data
                    cv2.putText(image, 'STAGE', (65,12), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
                    cv2.putText(image, self.stage,(60,60), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
                    
                    mp_drawing.draw_landmarks(
                                            image,
                                            results.pose_landmarks,
                                            mp_pose.POSE_CONNECTIONS,
                                            mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                            mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
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
            print("stop")
        self.quit()

#이하 main 코드
if __name__ == '__main__':
    # Some setup for qt
    app = QApplication(sys.argv)

    #QstackedWidget 기능 연결 및 인스턴스 생성
    widget = QtWidgets.QStackedWidget()
    
    loginPage = LoginPage()
    aiFreePage = AiFreePage()
    selExercisePage = SelExercisePage()
    posePage = PosePage()
    trainerPage = TrainerPage()
    weightPage = WeightPage()
    exercisingPage = ExercisingPage()
    restpage = RestPage()
    fisishpage = FinishPage()
    planPopup = PlanPopup()
    
    #widget에 모든 페이지 추가
    widget.addWidget(loginPage)
    widget.addWidget(aiFreePage)
    widget.addWidget(selExercisePage)
    widget.addWidget(posePage)
    widget.addWidget(trainerPage)
    widget.addWidget(weightPage)
    widget.addWidget(exercisingPage)
    widget.addWidget(restpage)
    widget.addWidget(fisishpage)
    widget.addWidget(planPopup)  

    #widget 크기와 보여주는 함수
    widget.setFixedHeight(1920)  # 높이
    widget.setFixedWidth(1080)  # 너비
    
    widget.show()
    
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")