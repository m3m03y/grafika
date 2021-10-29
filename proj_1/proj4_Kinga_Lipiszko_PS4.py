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
    "Addition",             #0
    "Subtraction",          #1
    "Multiplication",       #2
    "Division",             #3
    "Brightness",           #4
    "To greyscale"          #5
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
                r = func(r, val)
                g = func(g, val)
                b = func(b, val)
                image.setPixelColor(x,y, QColor(r,g,b))
        return image

    def __add(self, current, val):
        return min((current + val), 255)

    def __subtract(self, current, val):
        return max((current - val), 0)

    def __multiply(self, current, val):
        return min((current * val), 255)

    def __divide(self, current, val):
        return max((round(current % val)), 0)

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
        self.__fixScale()
        self.__showImage()

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
        self.slider.setMaximum(MAX_VAL)
        self.slider.setMinimum(MIN_VAL)
        self.slider.valueChanged.connect(self.__sliderAction)
        self.spinBox.setMaximum(MAX_VAL)
        self.spinBox.setMinimum(MIN_VAL)
        self.spinBox.valueChanged.connect(self.__spinBoxAction)
        layout.addWidget(self.slider)
        layout.addWidget(self.spinBox)
        return layout

if __name__=='__main__':
        app=QApplication(sys.argv)
        window=Form()
        window.show()
        app.exec()