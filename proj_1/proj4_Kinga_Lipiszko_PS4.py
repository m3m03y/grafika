import sys
import platform
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from datetime import datetime
from PIL import Image
import pathlib
import numpy as np
import re
import webbrowser

MODES = [
    "Addition",                             #0
    "Subtraction",                          #1
    "Multiplication",                       #2
    "Division",                             #3
    "Adjust brightness",                    #4
    "Convert to greyscale (ratio)",         #5
    "Convert to greyscale (average)",       #6
    "Average filter",                       #7
    "Median filter",                        #8
    "Sobel filter",                         #9
    "Highpass filter",                      #10
    "Gauss filter"                           #11
    ]

MIN_VAL = 0
MAX_VAL = 255
MAX_COLOR_VALUE = 255

class ImageConverter:
    def __processImage(self, func, image, val):
        for y in range (image.height()):
            for x in range (image.width()):
                pix = image.pixel(x,y)
                r,g,b = qRed(pix), qGreen(pix), qBlue(pix)
                r, g, b = func([r, g, b], val)
                image.setPixelColor(x,y, QColor(r,g,b))
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
        return image    
    
    def medianFilter(self, image, value):
        return image    
    
    def sobelFilter(self, image, value):
        return image    
    
    def highpassFilter(self, image, value):
        return image    
    
    def gaussFilter(self, image, value):
        return image

class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        openBtn = QPushButton("Open file")
        openBtn.clicked.connect(self.__open)
        self.converter = ImageConverter()
        self.img = None
        self.layout = QFormLayout()
        self.layout.addRow(openBtn)
        self.image_label = QLabel(" ")
        self.layout.addRow(self.image_label)
        self.menu = QComboBox()
        self.menu.addItems(MODES)
        self.menu.currentIndexChanged.connect(self.__changeMode)
        self.layout.addRow(self.menu)
        self.layout.addRow(self.__createInput())

        submitBtn = QPushButton("Submit")
        submitBtn.clicked.connect(self.__processImage)
        self.layout.addRow(submitBtn)
        self.setLayout(self.layout)

    def __open(self):
        filePath, _ = QFileDialog.getOpenFileName(self, 'Open File', "",
            "Images (*.ppm *.jpeg *.jpg)")
 
        if filePath == "":
            return False

        self.img = QImage(filePath)
        self.__fixScale()
        self.__showImage()

    def __showImage(self):
        self.image_label.setPixmap(QPixmap.fromImage(self.img))
        self.update()

    def __fixScale(self):
        if (self.img.height() > 720):
            self.img = self.img.scaledToHeight(720)
        elif (self.img.height() < 50):
            self.img = self.img.scaledToHeight(50)
        if (self.img.width() > 1280):
            self.img = self.img.scaledToWidth(1280)        
        elif (self.img.width() < 50):
            self.img = self.img.scaledToWidth(50)

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
            self.img = self.converter.sobelFilter(self.img,val)
        elif (int(pos) == 10):
            self.img = self.converter.highpassFilter(self.img,val)
        elif (int(pos) == 11):
            self.img = self.converter.gaussFilter(self.img,val)
        self.__fixScale()
        self.__showImage()

    def __changeMode(self):
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