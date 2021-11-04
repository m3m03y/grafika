import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import numpy as np

MODES = [
    "Extend histogram",         #0
    "Equalization histogram"          #1
    ]

MIN_VAL = 0
MAX_VAL = 255
MAX_COLOR_VALUE = 255

class ImageConverter:
    def __init__(self, originalImage):
        self.original = originalImage
        self.red_channel = np.zeros(256, dtype = int)
        self.green_channel = np.zeros(256, dtype = int)
        self.blue_channel = np.zeros(256, dtype = int)

    def setOriginalImage(self, originalImage):
        self.original = originalImage

    def __readHistogram(self):
        for y in range (self.original.height()):
            for x in range (self.original.width()):
                pix = self.original.pixel(x,y)
                r,g,b = qRed(pix), qGreen(pix), qBlue(pix)
                self.red_channel[r] += 1
                self.green_channel[g] += 1
                self.blue_channel[b] += 1
    
    def __findHistogramMinMax(self, histogram):
        minIdx = -1
        maxIdx = 0
        for i in range(len(histogram)):
            if (histogram[i] > 0):
                maxIdx = i
                if (minIdx < 0): minIdx = i
        return [minIdx, maxIdx]

    def __calculateHistogramCumulativeSum(self, histogram):
        cumulative_sum = np.zeros(256, dtype=int)
        for i in range(len(histogram)):
            if (i == 0):
                cumulative_sum[i] = histogram[i]
                continue
            cumulative_sum[i] = cumulative_sum[i-1] + histogram[i] 
        return cumulative_sum

    def __newHistogramValueMapping(self, cumulative_sum):
        mapping = np.zeros(256, dtype=int)
        size = len(cumulative_sum)
        for i in range(size):
            mapping[i] = max(0, round((size*cumulative_sum[i])/(self.original.width() * self.original.height()))-1)
        return mapping

    def extendHistogram(self, image):
        self.__readHistogram()
        rMin,rMax = self.__findHistogramMinMax(self.red_channel)
        gMin,gMax = self.__findHistogramMinMax(self.green_channel)
        bMin,bMax = self.__findHistogramMinMax(self.blue_channel)
        for y in range (image.height()):
            for x in range (image.width()):
                pix = image.pixel(x,y)
                r,g,b = qRed(pix), qGreen(pix), qBlue(pix)
                r = (r - rMin) / (rMax - rMin) * MAX_COLOR_VALUE
                g = (g - gMin) / (gMax - gMin) * MAX_COLOR_VALUE
                b = (b - bMin) / (bMax - bMin) * MAX_COLOR_VALUE
                image .setPixelColor(x,y, QColor(r,g,b))
        return image

    def equalizationHistogram(self, image):
        self.__readHistogram()
        r_cumulative_sum = self.__calculateHistogramCumulativeSum(self.red_channel)
        g_cumulative_sum = self.__calculateHistogramCumulativeSum(self.green_channel)
        b_cumulative_sum = self.__calculateHistogramCumulativeSum(self.blue_channel)
        r_mapping = self.__newHistogramValueMapping(r_cumulative_sum)
        g_mapping = self.__newHistogramValueMapping(g_cumulative_sum)
        b_mapping = self.__newHistogramValueMapping(b_cumulative_sum)
        for y in range (image.height()):
            for x in range (image.width()):
                pix = image.pixel(x,y)
                r,g,b = qRed(pix), qGreen(pix), qBlue(pix)
                r = r_mapping[r]
                g = g_mapping[g]
                b = b_mapping[b]
                image.setPixelColor(x,y, QColor(r,g,b))
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
        self.successLabel.setText(" ")
        self.update()
        if (self.img == None):
            self.__showErrorMessage("No image selected", "Invalid image")
            return
        pos = self.menu.currentIndex()
        val = self.slider.value()
        self.img = QPixmap.fromImage(self.original).toImage()
        print('Mode: {}, value: {}'.format(pos,val))

        if (int(pos) == 0):
            self.img = self.converter.extendHistogram(self.img)
        if (int(pos) == 1):
            self.img = self.converter.equalizationHistogram(self.img)
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
        if (pos == 13):
            self.__initMaskInput()


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