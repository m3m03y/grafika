import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import numpy as np
from PySide6.QtCharts import * 
import math

MIN_VAL = 0
MAX_VAL = 255
MAX_COLOR_VALUE = 255

class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        openBtn = QPushButton("Open file")
        openBtn.clicked.connect(self.__open)
        self.img = None
        self.layout = QFormLayout()
        self.layout.addRow(openBtn)
        self.image_label = QLabel(" ")
        self.image_original_label = QLabel(" ")        
        self.percentage = QLabel(" ")
        self.layout.addRow(self.image_label , self.image_original_label)
        self.layout.addRow(self.percentage)
       
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

        self.__calculateColor()
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

    def __calculateColor(self):
        sum_pixels = 0
        pixels_count = self.original.width() * self.original.height()
        for y in range (self.original.height()):
            for x in range (self.original.width()):
                pix = self.original.pixel(x,y)
                r,g,b = qRed(pix), qGreen(pix), qBlue(pix)
                sum_one = r + g + b
                if (sum_one != 0):
                    r_perc = r/sum_one
                    g_perc = g/sum_one
                    b_perc = b/sum_one
                else: r_perc,g_perc,b_perc = 0,0,0
                if (g_perc > r_perc) and (g_perc > b_perc):
                    self.img.setPixelColor(x,y, QColor(min(r + 150,255),g,b))
                    sum_pixels += 1
        calc = round(sum_pixels/pixels_count * 100,2)
        print('Percentage {}%'.format(calc))
        self.percentage.setText('Percentage {}%'.format(calc))
        self.__showImage()
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