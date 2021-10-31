import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from datetime import datetime
from PIL import Image
import numpy as np
import statistics
import math

MODES = [
    "Addition",                             #0
    "Subtraction",                          #1
    "Multiplication",                       #2
    "Division",                             #3
    "Adjust brightness",                    #4
    "Convert to greyscale (ratio)",         #5-
    "Convert to greyscale (average)",       #6
    "Average/Mean filter",                  #7
    "Median filter",                        #8
    "Sobel filter (horizontal)",            #9
    "Sobel filter (vertical)",              #10
    "Highpass filter",                      #11
    "Gauss filter"                          #12
    ]

MIN_VAL = 0
MAX_VAL = 255
MAX_COLOR_VALUE = 255

class ImageConverter:
    def __init__(self, originalImage):
        self.original = originalImage

    def setOriginalImage(self, originalImage):
        self.original = originalImage
        
    def __processImage(self, func, image, val):
        for y in range (image.height()):
            for x in range (image.width()):
                pix = image.pixel(x,y)
                r,g,b = qRed(pix), qGreen(pix), qBlue(pix)
                r, g, b = func([r, g, b], val)
                image.setPixelColor(x,y, QColor(r,g,b))
        return image

    def __processImageFiltering(self, func, image, val, mask):
        if (mask is not None):
            mask_range = math.floor(len(mask) / 2)
        else: mask_range = 1
        for y in range (image .height()):
            for x in range (image .width()):
                pix = image .pixel(x,y)
                r,g,b = qRed(pix), qGreen(pix), qBlue(pix)
                if (x > 0) and (x < (image.width() - mask_range)) and (y > 0) and (y < (image.height() - mask_range)):
                    r, g, b = func([r, g, b], val, [x,y], image, mask)
                image .setPixelColor(x,y, QColor(r,g,b))
        return image 

    def __add(self, current, val): 
        for i in range(len(current)):
            current[i] = min((current[i] + val), 255)
        return current

    def __subtract(self, current, val):
        for i in range(len(current)):
            current[i] = max((current[i] - val), 0)
        return current

    def __multiply(self, current, val):
        for i in range(len(current)):
            current[i] = min((current[i] * val), 255)
        return current

    def __divide(self, current, val):
        for i in range(len(current)):
            current[i] = max((round(current[i] / val)), 0)
        return current

    def __findMiddle(self, arr):
        idx = -1
        maxValue = max(arr)
        minValue = min(arr)
        for i in range(len(arr)):
            if (maxValue != arr[i]) and (minValue != arr[i]):
                idx = i
        if idx == -1: idx = 0
        return idx

    def __roundColor(self, val):
        if (val > 255): return 255
        elif (val < 0): return 0
        return val

    def __calculateBrightness(self, current, val):
        if (val < 0):
            scale = (1.0 - (abs(val) / 100))
            for i in range(len(current)):
                current[i] = self.__roundColor(round(current[i] * scale))
        elif (val > 0):
            for i in range(len(current)):
                difference = MAX_VAL - current[i]
                current[i] = self.__roundColor(round(difference * (val / 100) + current[i]))
        return current

    def __convertToGrayscaleRatio(self, current, val):
        Y = round(0.299 * current[0] + 0.587 * current[1] + 0.114 * current[2])
        return [Y,Y,Y]    
    
    def __convertToGrayscaleAverage(self, current, val):
        avg = round((current[0] + current[1] + current[2]) / 3)
        return [avg,avg,avg]

    def __calculateMedianFilter(self, current, val, pos, image, mask = None):
        r_arr = []
        g_arr = []
        b_arr = []
        for x in range(pos[0] - 1, pos[0] + 2):
            for y in range(pos[1] - 1, pos[1] + 2):
                pix = image.pixel(x,y)
                r,g,b = qRed(pix), qGreen(pix), qBlue(pix)
                r_arr.append(r)
                g_arr.append(g)
                b_arr.append(b)
        r_arr = sorted(r_arr)
        g_arr = sorted(g_arr)
        b_arr = sorted(b_arr)

        r_val = round(statistics.median(r_arr))
        g_val = round(statistics.median(g_arr))
        b_val = round(statistics.median(b_arr))
        return [r_val,g_val,b_val]

    def __calculateAverageFilter(self, current, val, pos, image, mask):
        mask_range = math.floor(len(mask) / 2)
        r_sum = 0
        g_sum = 0
        b_sum = 0
        # mask without calculated boundries https://inst.eecs.berkeley.edu/~cs194-26/fa20/Lectures/ImageProcessingFilteringII.pdf
        for x in range(pos[0] - mask_range, pos[0] + (mask_range + 1)): # +2 because not included ended position
            for y in range(pos[1] - mask_range, pos[1] + (mask_range + 1)):
                idxX = x - (pos[0] - mask_range)
                idxY = y - (pos[1] - mask_range)
                maskVal = mask[idxX][idxY]
                pix = self.original.pixel(x,y)
                r,g,b = qRed(pix) * maskVal, qGreen(pix) * maskVal, qBlue(pix) * maskVal
                r_sum += r 
                g_sum += g 
                b_sum += b 
        r_val = round(abs(r_sum))
        g_val = round(abs(g_sum))
        b_val = round(abs(b_sum))
        r_val = max(min(r_val,255),0)
        g_val = max(min(g_val,255),0)
        b_val = max(min(b_val,255),0)
        return [r_val,g_val,b_val]

    def add(self, image, value):
        image = self.__processImage(self.__add, image, value)
        return image

    def subtract(self, image, value):
        image = self.__processImage(self.__subtract, image, value)
        return image

    def multiply(self, image, value):
        image = self.__processImage(self.__multiply, image, value)
        return image

    def divide(self, image, value):
        image = self.__processImage(self.__divide, image, value)
        return image

    def changeBrightness(self, image, value):
        image = self.__processImage(self.__calculateBrightness, image, value)
        return image
    
    def convertToGrayscaleRatio(self, image, value):
        image = self.__processImage(self.__convertToGrayscaleRatio, image, value)
        return image    
    
    def convertToGrayscaleAverage(self, image, value):
        image = self.__processImage(self.__convertToGrayscaleAverage, image, value)
        return image

    def averageFilter(self, image, value):
        mask = [
            [1/9,1/9,1/9],
            [1/9,1/9,1/9],
            [1/9,1/9,1/9]
        ]
        image = self.__processImageFiltering(self.__calculateAverageFilter, image, value, mask)
        return image    
    
    def medianFilter(self, image, value):
        image = self.__processImageFiltering(self.__calculateMedianFilter, image, value, None)
        return image    
    
    def sobelFilter(self, image, value, isHorizontal):
        if isHorizontal:
            mask = [
                [-1,-2,-1],
                [0,0,0],
                [1,2,1]
            ]
        else: 
            mask = [
                [-1,0,1],
                [-2,0,2],
                [-1,0,1]
            ]
        image = self.__processImageFiltering(self.__calculateAverageFilter, image, value, mask)
        return image    
    
    def highpassFilter(self, image, value):
        mask = [
            [-1,-1,-1],
            [-1,9,-1],
            [-1,-1,-1]
        ]
        image = self.__processImageFiltering(self.__calculateAverageFilter, image, value, mask)
        return image    
    
    def gaussFilter(self, image, value): #https://courses.cs.washington.edu/courses/cse455/09wi/Lects/lect2.pdf
        mask = np.array([
            [1,2,1],
            [2,4,2],
            [1,2,1]
        ]) * (1.0 / 16.0)
        image = self.__processImageFiltering(self.__calculateAverageFilter, image, value, mask)
        return image

class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        openBtn = QPushButton("Open file")
        openBtn.clicked.connect(self.__open)
        self.converter = ImageConverter(None)
        self.img = None
        self.layout = QFormLayout()
        self.layout.addRow(openBtn)
        self.image_label = QLabel(" ")
        self.image_original_label = QLabel(" ")
        self.layout.addRow(self.image_label , self.image_original_label)
        self.menu = QComboBox()
        self.menu.addItems(MODES)
        self.menu.currentIndexChanged.connect(self.__changeMode)
        self.layout.addRow(self.menu)
        self.layout.addRow(self.__createInput())

        submitBtn = QPushButton("Submit")
        submitBtn.clicked.connect(self.__processImage)
        self.layout.addRow(submitBtn)
        self.successLabel = QLabel(" ")
        self.layout.addRow(self.successLabel)
        self.setLayout(self.layout)

    def __open(self):
        filePath, _ = QFileDialog.getOpenFileName(self, 'Open File', "",
            "Images (*.ppm *.jpeg *.jpg *.png)")
 
        if filePath == "":
            return False

        self.img = QImage(filePath)
        self.img = self.__fixScale(self.img)
        self.__showImage()

        self.original = QImage(filePath)
        self.original = self.__fixScale(self.original)
        self.image_original_label.setPixmap(QPixmap.fromImage(self.original))
        self.converter.setOriginalImage(self.original)
        self.update()

    def __showImage(self):
        self.image_label.setPixmap(QPixmap.fromImage(self.img))
        self.update()

    def __fixScale(self, image):
        if (image.height() > 600):
            image = image.scaledToHeight(600)
        elif (image.height() < 50):
            image = image.scaledToHeight(50)
        if (image.width() > 800):
            image = image.scaledToWidth(800)        
        elif (image.width() < 50):
            image = image.scaledToWidth(50)
        return image

    def __processImage(self):
        if (self.img == None):
            self.__showErrorMessage("No image selected", "Invalid image")
            return
        pos = self.menu.currentIndex()
        val = self.slider.value()

        print('Mode: {}, value: {}'.format(pos,val))

        if (int(pos) == 0):
            self.img = self.converter.add(self.img,val)
        elif (int(pos) == 1):
            self.img = self.converter.subtract(self.img,val)
        elif (int(pos) == 2):
            self.img = self.converter.multiply(self.img,val)
        elif (int(pos) == 3):
            if (int(val) == 0):
                self.__showErrorMessage("Cannot divide by zero", "Invalid value")
                return
            self.img = self.converter.divide(self.img,val)        
        elif (int(pos) == 4):
            self.img = self.converter.changeBrightness(self.img,val)        
        elif (int(pos) == 5):
            self.img = self.converter.convertToGrayscaleRatio(self.img,val)        
        elif (int(pos) == 6):
            self.img = self.converter.convertToGrayscaleAverage(self.img,val)        
        elif (int(pos) == 7):
            self.img = self.converter.averageFilter(self.img,val)
        elif (int(pos) == 8):
            self.img = self.converter.medianFilter(self.img,val)
        elif (int(pos) == 9):
            self.img = self.converter.sobelFilter(self.img,val, True)
        elif (int(pos) == 10):
            self.img = self.converter.sobelFilter(self.img,val, False)
        elif (int(pos) == 11):
            self.img = self.converter.highpassFilter(self.img,val)
        elif (int(pos) == 12):
            self.img = self.converter.gaussFilter(self.img,val)
        self.successLabel.setText("Done!")
        self.__fixScale(self.img)
        self.__showImage()

    def __changeMode(self):
        self.successLabel.setText(" ")
        self.update()
        pos = self.menu.currentIndex()
        if (pos >= 0) and (pos <= 3):
            self.__setMinMaxValues(MIN_VAL,MAX_VAL)
        elif (pos == 4):
            self.__setMinMaxValues(-75,75)
        elif (pos >= 5):
            self.__setMinMaxValues(0,0)


    def __setMinMaxValues(self, minVal, maxVal):
        self.__setSliderMinMaxValues(minVal, maxVal)
        self.__setSpinBoxMinMaxValues(minVal, maxVal)

    def __setSliderMinMaxValues(self, minVal, maxVal):
        self.slider.setMaximum(maxVal)
        self.slider.setMinimum(minVal)    
    
    def __setSpinBoxMinMaxValues(self, minVal, maxVal):
        self.spinBox.setMaximum(maxVal)
        self.spinBox.setMinimum(minVal)

    def __sliderAction(self):
        val = self.slider.value()
        self.spinBox.setValue(val)

    def __spinBoxAction(self):
        val = self.spinBox.value()
        self.slider.setValue(val)

    def __showErrorMessage(self, msg, title):
        QMessageBox.critical(
            self,
            title,
            msg,
            buttons=QMessageBox.Ignore,
            defaultButton=QMessageBox.Ignore,
        )
    
    def __createInput(self):
        layout = QHBoxLayout()
        self.slider = QSlider(Qt.Horizontal)
        self.spinBox = QSpinBox()
        self.slider.valueChanged.connect(self.__sliderAction)
        self.spinBox.valueChanged.connect(self.__spinBoxAction)
        self.__setMinMaxValues(MIN_VAL,MAX_VAL)
        layout.addWidget(self.slider)
        layout.addWidget(self.spinBox)
        return layout

if __name__=='__main__':
        app=QApplication(sys.argv)
        window=Form()
        window.show()
        app.exec()