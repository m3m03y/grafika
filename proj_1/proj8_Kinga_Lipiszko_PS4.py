import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import numpy as np
from PySide6.QtCharts import * 

MODES = [
    "Dilation",                 #0
    "Erosion",                  #1
    "Opening",                  #2
    "Closing",                  #3
    "Hit-or-miss"              #4
    ]

MIN_VAL = 0
MAX_VAL = 255
MAX_COLOR_VALUE = 255

class ImageConverter:
    def __init__(self):
        ...

    def dilation(self, image):
        print("Dilation")
        return image

    def erosion(self,image):
        print("erosion")
        return image
    
    def opening(self,image):
        print("opening")
        return image

    def closing(self,image):
        print("closing")
        return image

    def hit_or_miss(self,image):
        print("hit or miss")
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
        self.image_original_label = QLabel(" ")
        self.layout.addRow(self.image_label , self.image_original_label)
        self.menu = QComboBox()
        self.menu.addItems(MODES)
        self.menu.currentIndexChanged.connect(self.__changeMode)
        self.layout.addRow(self.menu)

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
        self.successLabel.setText(" ")
        self.update()
        if (self.img == None):
            self.__showErrorMessage("No image selected", "Invalid image")
            return
        pos = self.menu.currentIndex()
        print('Mode: {}'.format(pos))

        if (int(pos) == 0):
            self.img = self.converter.dilation(QPixmap.fromImage(self.original).toImage())
        elif (int(pos) == 1):
            self.img = self.converter.erosion(QPixmap.fromImage(self.original).toImage())
        elif (int(pos) == 2):
            self.img = self.converter.opening(QPixmap.fromImage(self.original).toImage())
        elif (int(pos) == 3):
            self.img = self.converter.closing(QPixmap.fromImage(self.original).toImage())
        elif (int(pos) == 4):
            self.img = self.converter.hit_or_miss(QPixmap.fromImage(self.original).toImage())
        self.successLabel.setText("Done!")
        self.__fixScale(self.img)
        self.__showImage()

    def __changeMode(self):
        self.successLabel.setText(" ")
        self.update()

    def __showErrorMessage(self, msg, title):
        QMessageBox.critical(
            self,
            title,
            msg,
            buttons=QMessageBox.Ignore,
            defaultButton=QMessageBox.Ignore,
        )

if __name__=='__main__':
        app=QApplication(sys.argv)
        window=Form()
        window.show()
        app.exec()