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
class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.sliderArr = []
        self.spinBoxArr = []
        openBtn = QPushButton("Open file")
        openBtn.clicked.connect(self.open)

        self.layout = QFormLayout()
        self.layout.addRow(openBtn)
        self.image_label = QLabel(" ")
        self.layout.addRow(self.image_label)
        self.layout.addRow(self.__createInput("Add",0,255,self.__customClick(0)))
        self.layout.addRow(self.__createInput("Sub",0,255,self.__customClick(1)))
        self.layout.addRow(self.__createInput("Mult",0,255,self.__customClick(2)))
        self.layout.addRow(self.__createInput("Div",0,255,self.__customClick(3)))
        self.setLayout(self.layout)

    def open(self):
        filePath, _ = QFileDialog.getOpenFileName(self, 'Open File', "",
            "Images (*.ppm *.jpeg *.jpg)")
 
        if filePath == "":
            return False

        self.img = QImage(filePath)
        if (self.img.height() > 720):
            self.img = self.img.scaledToHeight(720)
        if (self.img.width() > 1280):
            self.img = self.img.scaledToWidth(1280)
        self.image_label.setPixmap(QPixmap.fromImage(self.img))
        self.update()

    def __customClick(self, pos):
        val = self.sliderArr[pos].value()
        self.spinBoxArr[pos].setValue(val)

    def __createInput(self, name, minVal, maxVal, action):
        layout = QHBoxLayout()
        label = QLabel(name)
        slider = QSlider(Qt.Horizontal)
        spinBox = QSpinBox()
        slider.setMaximum(maxVal)
        slider.setMinimum(minVal)
        slider.valueChanged.connect(action)
        spinBox.setMaximum(maxVal)
        spinBox.setMinimum(minVal)
        spinBox.valueChanged.connect(action)
        self.sliderArr.append(slider)
        self.spinBoxArr.append(spinBox)
        layout.addWidget(label)
        layout.addWidget(slider)
        layout.addWidget(spinBox)
        return layout

if __name__=='__main__':
        app=QApplication(sys.argv)
        window=Form()
        window.show()
        app.exec()