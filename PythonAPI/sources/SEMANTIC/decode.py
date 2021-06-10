import math
import cv2
import numpy as np
from matplotlib import pyplot as plt


#Constante:

DATA_SET = [("VideoOutput.avi", "SemanticVideoOutput.avi"), ("2VideoOutput.avi", "2SemanticVideoOutput.avi")]
DATA_SET_SELECTOR = 1
orange = [0, 165, 255]
galben = [0, 255, 255]
alb = [255, 255, 255]

class ImageClassifier():
    def __init__(self):
        pass

    #ToDo: polyfill intre benzi
    @staticmethod
    def detecteaza_marcaje_stradale(frame):
        lower_VAL = np.array([30, 220, 140], np.uint8)
        upper_VAL = np.array([60, 240, 160], np.uint8)
        mask = cv2.inRange(frame, lower_VAL, upper_VAL)

        numar_marcaje = list()
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            if w > 50 and h > 50: numar_marcaje.append((x, y, w, h))

        if len(numar_marcaje) > 8:
            for coords in numar_marcaje:
                cv2.rectangle(frame, (coords[0], coords[1]), (coords[0] + coords[2], coords[1] + coords[3]), orange, 2)
            cv2.putText(frame, "Trecere de pietoni", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, alb, 3)
            cv2.waitKey(500)

        cv2.imshow("Marcaje stradale", cv2.resize(mask, (990, 540)))

    @staticmethod
    def detecteaza_masini(frame):
        # BGR
        cv2.line(frame, (300, 700), (700, 700), (0, 255, 0), thickness=3, lineType=8)
        centru_sensor = (500, 700)

        lower_VAL = np.array([140, 0, 0], np.uint8)
        upper_VAL = np.array([160, 0, 0], np.uint8)
        mask = cv2.inRange(frame, lower_VAL, upper_VAL)

        min_x, min_y, _ = frame.shape
        max_x = max_y = 0

        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            min_x, max_x = min(x, min_x), max(x + w, max_x)
            min_y, max_y = min(y, min_y), max(y + h, max_y)
            centru_obiect = (int((2 * x + w) / 2), int((2 * y + h) / 2))
            distanta = ImageClassifier.distanta(centru_obiect, centru_sensor) / 100

            if w > 50 and h > 50:
                if distanta < 2:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), orange, 2)
                elif 2 < distanta < 4:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), galben, 2)
                else:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), alb, 2)

                cv2.circle(frame, centru_obiect, 1, (255, 255, 255), 5)
                cv2.line(frame, centru_obiect, centru_sensor, (0, 255, 0), thickness=3, lineType=8)
                cv2.putText(frame, "Vehicul {} metri".format(distanta), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, alb)
        # cv2.imshow("Vehicul", mask)

    # To be reworked
    @staticmethod
    def detecteaza_pieton(frame):
        lower_VAL = np.array([40, 20, 180], np.uint8)
        upper_VAL = np.array([60, 50, 220], np.uint8)
        blur = cv2.blur(frame, (5, 5))
        mask = cv2.inRange(blur, lower_VAL, upper_VAL)

        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            if w > 20 and h > 20:
                cv2.rectangle(frame, (x, y), (x + w, y + h), alb, 2)
        # cv2.imshow("Pietoni", mask)

    @staticmethod
    def distanta(punct1, punct2):
        return math.sqrt((punct2[0] - punct1[0]) ** 2 + (punct2[1] - punct2[1]) ** 2)

    @staticmethod
    def decodeaza_R(frame):
        imagine_decodata_R = frame[:, :, 2]
        red_img = np.zeros(frame.shape)
        red_img[:, :, 2] = imagine_decodata_R
        cv2.imshow("Decodata", cv2.resize(red_img, (990, 540)))

    @staticmethod
    def HAAR_Classifier(frame):
        stop = cv2.CascadeClassifier('..\HAAR\HAAR_DATA\STOP\Stop_HAAR\Stop_HAAR_19.xml')
        cedeaza = cv2.CascadeClassifier('..\HAAR\HAAR_DATA\CEDEAZA\Cedeaza_HAAR\Cedeaza_HAAR_12.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        s_stop = stop.detectMultiScale(gray, 1.3, 5)
        s_cedeaza = cedeaza.detectMultiScale(gray, 1.3, 5)
        detected = False
        for (x, y, h, w) in s_stop:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(frame, "STOP", (x + 10, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            # cv2.imshow("STOP", frame)
            # cv2.waitKey(1)
            detected = True

        for (x1, y1, h1, w1) in s_cedeaza:
            cv2.rectangle(frame, (x1, y1), (x1 + w1, y1 + h1), (255, 0, 0), 2)
            cv2.putText(frame, "CEDEAZA", (x1 + 20, y1 + 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            # cv2.imshow("CEDEAZA", frame)
            # cv2.waitKey(1)
            detected = True

        if not detected:
            cv2.putText(frame, "Nerecunoscut", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        cv2.imshow("Normala", cv2.resize(frame, (990, 540)))


# Functie SYS
def mouseRGB(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Rosu: {}, Verde: {}, Albastru: {}".format(frame_SS[y, x, 2], frame_SS[y, x, 1], frame_SS[y, x, 0]))
        print("Coordinates of pixel: X: {}, Y: {}".format(x, y))


cv2.namedWindow('Segmentata')
cv2.setMouseCallback('Segmentata', mouseRGB)

# Driver

if __name__ == "__main__":
    cap_SS = cv2.VideoCapture(DATA_SET[DATA_SET_SELECTOR][1])
    cap_NM = cv2.VideoCapture(DATA_SET[DATA_SET_SELECTOR][0])

    while (cap_SS.isOpened()):
        ret, frame_SS = cap_SS.read()
        ret, frame_NM = cap_NM.read()

        if ret is False: break

        #ToDo multiprocess
        ImageClassifier.detecteaza_masini(frame_SS)
        ImageClassifier.detecteaza_marcaje_stradale(frame_SS)
        ImageClassifier.detecteaza_pieton(frame_SS)
        ImageClassifier.decodeaza_R(frame_SS)
        ImageClassifier.HAAR_Classifier(frame_NM)

        cv2.imshow("Segmentata", cv2.resize(frame_SS, (990, 540)))

        cv2.waitKey(1)