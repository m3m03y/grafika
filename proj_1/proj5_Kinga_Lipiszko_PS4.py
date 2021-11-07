import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import numpy as np
from PySide6.QtCharts import * 

MODES = [
    "Extend histogram",                 #0
    "Equalization histogram",           #1
    "Binarization",                     #2
    "Percent Black Selection",          #3
    "Mean Iterative Selection"          #4
    ]

MIN_VAL = 0
MAX_VAL = 255
MAX_COLOR_VALUE = 255

class ImageConverter:
    def __init__(self):
        self.red_channel = np.zeros(256, dtype = int)
        self.green_channel = np.zeros(256, dtype = int)
        self.blue_channel = np.zeros(256, dtype = int)
        self.gray_channel = np.zeros(256, dtype = int)

    def __readHistogram(self, image):
        self.red_channel = np.zeros(256, dtype = int)
        self.green_channel = np.zeros(256, dtype = int)
        self.blue_channel = np.zeros(256, dtype = int)
        self.gray_channel = np.zeros(256, dtype = int)

        for y in range (image.height()):
            for x in range (image.width()):
                pix = image.pixel(x,y)
                r,g,b = qRed(pix), qGreen(pix), qBlue(pix)
                avg = round((r + g + b) / 3)
                self.red_channel[r] += 1
                self.green_channel[g] += 1
                self.blue_channel[b] += 1
                self.gray_channel[avg] += 1
        return [self.red_channel, self.green_channel, self.blue_channel]

    def __findHistogramMinMax(self, histogram):
        minIdx = -1
        maxIdx = 0
        for i in range(len(histogram)):
            if (histogram[i] > 0):
                maxIdx = i
                if (minIdx < 0): minIdx = i
        return [minIdx, maxIdx]

    def __findThreshold(self, image, percentage):
        count = (image.width() * image.height()) * (percentage / 100)
        current = 0
        idx = 0
        for i in range(len(self.gray_channel)):
            if (current >= count ): break
            idx = i
            current += self.gray_channel[i]
        return idx    
    
    def __findMean(self, image):
        sum_colors = 0
        count = 0
        for i in range(len(self.gray_channel)):
            count += self.gray_channel[i]
            sum_colors += i * self.gray_channel[i]

        avg = round(sum_colors / count)
        print('Average: {}'.format(avg))
        return avg

    def __calculateHistogramCumulativeSum(self, histogram):
        cumulative_sum = np.zeros(256, dtype=int)
        for i in range(len(histogram)):
            if (i == 0):
                cumulative_sum[i] = histogram[i]
                continue
            cumulative_sum[i] = cumulative_sum[i-1] + histogram[i] 
        return cumulative_sum

    def extendHistogram(self, image):
        self.__readHistogram(image)
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
        self.__readHistogram(image)
        r_cumulative_sum = self.__calculateHistogramCumulativeSum(self.red_channel)
        g_cumulative_sum = self.__calculateHistogramCumulativeSum(self.green_channel)
        b_cumulative_sum = self.__calculateHistogramCumulativeSum(self.blue_channel)
        for y in range (image.height()):
            for x in range (image.width()):
                pix = image.pixel(x,y)
                r,g,b = qRed(pix), qGreen(pix), qBlue(pix)
                r = min(max(0, round((MAX_COLOR_VALUE*r_cumulative_sum[r])/(image.width() * image.height()))-1), MAX_COLOR_VALUE)
                g = min(max(0, round((MAX_COLOR_VALUE*g_cumulative_sum[g])/(image.width() * image.height()))-1), MAX_COLOR_VALUE)
                b = min(max(0, round((MAX_COLOR_VALUE*b_cumulative_sum[b])/(image.width() * image.height()))-1), MAX_COLOR_VALUE)
                image.setPixelColor(x,y, QColor(r,g,b))
        return image

    def binarization(self, image, val):
        for y in range (image.height()):
            for x in range (image.width()):
                pix = image.pixel(x,y)
                r,g,b = qRed(pix), qGreen(pix), qBlue(pix)
                avg = (r + g + b) / 3
                if (avg > val):
                    r,g,b = [255,255,255]
                else:
                    r,g,b = [0,0,0]
                image.setPixelColor(x,y, QColor(r,g,b))
        return image    
    
    def percentBlackSelectionBinarization(self, image, percentage):
        self.__readHistogram(image)
        val = self.__findThreshold(image,percentage)
        return self.binarization(image, val)    
        
    def meanIterativeSelectionBinarization(self, image):
        self.__readHistogram(image)
        val = self.__findMean(image)
        return self.binarization(image, val)

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
        # self.proccessed_image_chart = QChartView()
        # self.original_image_chart = QChartView()
        # self.layout.addRow(self.proccessed_image_chart, self.original_image_chart)
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

        # self.proccessed_image_chart = self.__createBarChart(self.img)
        # self.original_image_chart = self.__createBarChart(self.original)
        # self.layout.addRow(self.proccessed_image_chart, self.original_image_chart)

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
        # self.img = QPixmap.fromImage(self.original).toImage()
        print('Mode: {}, value: {}'.format(pos,val))

        if (int(pos) == 0):
            self.img = self.converter.extendHistogram(QPixmap.fromImage(self.original).toImage())
        elif (int(pos) == 1):
            self.img = self.converter.equalizationHistogram(QPixmap.fromImage(self.original).toImage())        
        elif (int(pos) == 2):
            self.img = self.converter.binarization(QPixmap.fromImage(self.original).toImage(), val)        
        elif (int(pos) == 3):
            self.img = self.converter.percentBlackSelectionBinarization(QPixmap.fromImage(self.original).toImage(), val)        
        elif (int(pos) == 4):
            self.img = self.converter.meanIterativeSelectionBinarization(QPixmap.fromImage(self.original).toImage())
        self.successLabel.setText("Done!")
        self.__fixScale(self.img)
        # self.proccessed_image_chart = self.__createBarChart(self.img)
        self.__showImage()

    def __changeMode(self):
        self.successLabel.setText(" ")
        self.update()
        pos = self.menu.currentIndex()
        if (pos == 2):
            self.__setMinMaxValues(MIN_VAL,MAX_VAL)
        elif (pos == 0) or (pos == 1) or (pos == 4):
            self.__setMinMaxValues(0,0)
        elif (pos == 3):
            self.__setMinMaxValues(0, 100)

    # def __createBarChart(self, image):
    #     red = QBarSet("Red")
    #     green = QBarSet("Green")
    #     blue = QBarSet("Blue")

    #     r,g,b = self.converter.readHistogram(image)
    #     # for i in range(len(r)):
    #     #     red.append(*r)
    #     #     green.append(g[i])
    #     #     blue.append(b[i])
    #     red.append([*r])
    #     green.append([*g])
    #     blue.append([*b])


    #     bar_series = QBarSeries()
    #     bar_series.append(red)
    #     bar_series.append(green)
    #     bar_series.append(blue)

    #     chart = QChart()
    #     chart.addSeries(bar_series)
    #     chart.setTitle("Histogram")

    #     # axis_x = QBarCategoryAxis()
    #     # chart.setAxisX(axis_x, bar_series)
    #     # axis_x.setRange(0, 255)

    #     # axis_y = QValueAxis()
    #     # chart.setAxisY(axis_y, bar_series)
    #     # axis_y.setRange(0, (image.width() * image.height()))

    #     # chart.legend().setVisible(True)
    #     # chart.legend().setAlignment(Qt.AlignBottom)

    #     chart_view = QChartView(chart)
    #     chart_view.setRenderHint(QPainter.Antialiasing)

    #     return chart_view

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
        self.__setMinMaxValues(0,0)
        layout.addWidget(self.slider)
        layout.addWidget(self.spinBox)
        return layout

if __name__=='__main__':
        app=QApplication(sys.argv)
        window=Form()
        window.show()
        app.exec()