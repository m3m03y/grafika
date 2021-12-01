import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import numpy as np
from PySide6.QtCharts import * 
import math

MODES = [
    "Dilation",                 #0
    "Erosion",                  #1
    "Opening",                  #2
    "Closing",                  #3
    "Hit-or-miss",              #4
    "Thickening",               #5
    "Thinning"                  #6
    ]

MIN_VAL = 0
MAX_VAL = 255
MAX_COLOR_VALUE = 255

class ImageConverter:
    def __init__(self):
        ...

    def setOriginal(self,image):
        self.original = QPixmap.fromImage(image).toImage()
        self.bin_image = self.__binarization(QPixmap.fromImage(image).toImage())
        self.temp = self.__binarization(QPixmap.fromImage(image).toImage())

    def __processImageFiltering(self, func, image, kernel, miss = None):
        if (kernel is not None):
            kernel_range = math.floor(len(kernel) / 2)
        else: kernel_range = 1
        for y in range (self.bin_image.height()):
            for x in range (self.bin_image.width()):
                pix = self.bin_image.pixel(x,y)
                r,g,b = qRed(pix), qGreen(pix), qBlue(pix)
                if (x > (kernel_range - 1)) and (x < (self.bin_image.width() - kernel_range)) and (y > (kernel_range - 1)) and (y < (self.bin_image.height() - kernel_range)):
                    if (miss == None): r, g, b = func([x,y], kernel)
                    else: r, g, b = func([x,y], kernel,miss)
                image.setPixelColor(x,y, QColor(r,g,b))
        return image

    def __binarization(self, image, treshhold = MAX_COLOR_VALUE/2):
        for y in range (image.height()):
            for x in range (image.width()):
                pix = image.pixel(x,y)
                r,g,b = qRed(pix), qGreen(pix), qBlue(pix)
                avg = round((r + g + b) / 3)
                if (avg > treshhold):
                    r,g,b = [255,255,255]
                else:
                    r,g,b = [0,0,0]
                image.setPixelColor(x,y, QColor(r,g,b))
        return image  
    
    def __addTwoImages(self,image1, image2):
        image = QPixmap.fromImage(image1).toImage()
        for y in range (image1.height()):
            for x in range (image1.width()):
                pix1 = image1.pixel(x,y)
                r1 = qRed(pix1)
                pix2 = image2.pixel(x,y)
                r2 = qRed(pix2)
                r = max(min(r1,r2),0)
                image.setPixelColor(x,y, QColor(r,r,r))
        return image  

    def __sumTwoImages(self,image1, image2):
        image = QPixmap.fromImage(image1).toImage()
        for y in range (image1.height()):
            for x in range (image1.width()):
                pix1 = image1.pixel(x,y)
                r1 = qRed(pix1)
                pix2 = image2.pixel(x,y)
                r2 = qRed(pix2)
                r = max(max(r1,r2),0)
                image.setPixelColor(x,y, QColor(r,r,r))
        return image  

    def __subtractTwoImages(self,image1,image2):
        return self.__addTwoImages(image1, self.__reverse(image2))
 
    def __reverse(self, image):
        for y in range (image.height()):
            for x in range (image.width()):
                pix = image.pixel(x,y)
                r,g,b = qRed(pix), qGreen(pix), qBlue(pix)
                if (r == 0):
                    r,g,b = [255,255,255]
                else:
                    r,g,b = [0,0,0]
                image.setPixelColor(x,y, QColor(r,g,b))
        return image  
    
    def __rotate(self, matrix):
        temp_matrix = []
        column = len(matrix)-1
        for column in range(len(matrix)):
            temp = []
            for row in range(len(matrix)-1,-1,-1):
                temp.append(matrix[row][column])
            temp_matrix.append(temp)
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                matrix[i][j] = temp_matrix[i][j]
        return matrix
  
    def __dilation(self, pos, kernel):
        kernel_range = math.floor(len(kernel) / 2)
        for x in range(pos[0] - kernel_range, pos[0] + (kernel_range + 1)): 
            for y in range(pos[1] - kernel_range, pos[1] + (kernel_range + 1)):
                idxX = x - (pos[0] - kernel_range)
                idxY = y - (pos[1] - kernel_range)
                kernelVal = kernel[idxX][idxY]
                pix = self.bin_image.pixel(x,y)
                r,g,b = qRed(pix), qGreen(pix), qBlue(pix)
                if (kernelVal == r):
                    return [255,255,255]
        return [0,0,0]

    def __erosion(self,pos,kernel):
        kernel_range = math.floor(len(kernel) / 2)
        for x in range(pos[0] - kernel_range, pos[0] + (kernel_range + 1)): 
            for y in range(pos[1] - kernel_range, pos[1] + (kernel_range + 1)):
                idxX = x - (pos[0] - kernel_range)
                idxY = y - (pos[1] - kernel_range)
                kernelVal = kernel[idxX][idxY]
                pix = self.bin_image.pixel(x,y)
                r,g,b = qRed(pix), qGreen(pix), qBlue(pix)
                if ((kernelVal != r) and (kernelVal != -255)):
                    return [0,0,0]
        return [255,255,255]    
    
    def __hit_or_miss(self,pos,kernel,miss):
        kernel_range = math.floor(len(kernel) / 2)
        for x in range(pos[0] - kernel_range, pos[0] + (kernel_range + 1)): 
            for y in range(pos[1] - kernel_range, pos[1] + (kernel_range + 1)):
                idxX = x - (pos[0] - kernel_range)
                idxY = y - (pos[1] - kernel_range)
                kernelVal = kernel[idxX][idxY]
                missVal = miss[idxX][idxY]
                pix = self.bin_image.pixel(x,y)
                r,g,b = qRed(pix), qGreen(pix), qBlue(pix)
                if not(((kernelVal == -255) and (missVal != r)) or ((kernelVal == r) and (missVal != r)) or ((kernelVal == r) and (missVal == -255))):
                    return [0,0,0]
        return [255,255,255]
    
    def printPixels(self,image):
        print('------------')
        for y in range (image.height()):
            row = []
            for x in range (image.width()):
                pix1 = image.pixel(x,y)
                r = qRed(pix1)
                row.append(r)
            print(' '.join([str(i) for i in row]))
                

    def dilation(self,kernel):
        return self.__processImageFiltering(self.__dilation,QPixmap.fromImage(self.bin_image).toImage(),kernel)   

    def erosion(self,kernel):
        return self.__processImageFiltering(self.__erosion,QPixmap.fromImage(self.bin_image).toImage(),kernel)

    def opening(self,kernel):
        self.bin_image = self.__processImageFiltering(self.__erosion,QPixmap.fromImage(self.bin_image).toImage(),kernel)
        image = self.__processImageFiltering(self.__dilation,QPixmap.fromImage(self.bin_image).toImage(),kernel)
        self.bin_image = QPixmap.fromImage(self.temp).toImage()
        return image

    def closing(self,kernel):
        self.bin_image = self.__processImageFiltering(self.__dilation,QPixmap.fromImage(self.bin_image).toImage(),kernel)
        image = self.__processImageFiltering(self.__erosion,QPixmap.fromImage(self.bin_image).toImage(),kernel)
        self.bin_image = QPixmap.fromImage(self.temp).toImage()
        return image

    def hit_or_miss(self,kernel,miss):
        return self.hit_or_miss_from_erosion(kernel,miss)
        # return self.__processImageFiltering(self.__hit_or_miss,QPixmap.fromImage(self.bin_image).toImage(),kernel,miss) 
       
    def hit_or_miss_from_erosion(self,kernel,miss):
        image1 = self.__processImageFiltering(self.__erosion,QPixmap.fromImage(self.bin_image).toImage(),kernel)
        self.bin_image = self.__reverse(QPixmap.fromImage(self.bin_image).toImage())
        image2 = self.__processImageFiltering(self.__erosion,QPixmap.fromImage(self.bin_image).toImage(),miss)
        self.bin_image = QPixmap.fromImage(self.temp).toImage()
        return self.__addTwoImages(image1,image2)
    
    def thickening(self,kernel,miss):
        for i in range(40):
            image1 = self.__processImageFiltering(self.__erosion,QPixmap.fromImage(self.bin_image).toImage(),kernel)
            self.bin_image = self.__sumTwoImages(self.bin_image, image1)
            self.bin_image = self.__reverse(QPixmap.fromImage(self.bin_image).toImage())
            image2 = self.__processImageFiltering(self.__erosion,QPixmap.fromImage(self.bin_image).toImage(),miss)
            self.bin_image = self.__reverse(QPixmap.fromImage(self.bin_image).toImage())
            self.bin_image = self.__sumTwoImages(self.bin_image, image2)
            kernel = self.__rotate(kernel)
            miss = self.__rotate(miss)
        image = QPixmap.fromImage(self.bin_image).toImage()
        self.bin_image = QPixmap.fromImage(self.temp).toImage()
        return image   

    def thinning(self,kernel,miss):
        for i in range(40):
            image1 = self.__processImageFiltering(self.__erosion,QPixmap.fromImage(self.bin_image).toImage(),kernel)
            self.bin_image = self.__subtractTwoImages(self.bin_image, image1)
            self.bin_image = self.__reverse(QPixmap.fromImage(self.bin_image).toImage())
            image2 = self.__processImageFiltering(self.__erosion,QPixmap.fromImage(self.bin_image).toImage(),miss)
            self.bin_image = self.__reverse(QPixmap.fromImage(self.bin_image).toImage())
            self.bin_image = self.__subtractTwoImages(self.bin_image, image2)
            kernel = self.__rotate(kernel)
            miss = self.__rotate(miss)
        image = QPixmap.fromImage(self.bin_image).toImage()
        self.bin_image = QPixmap.fromImage(self.temp).toImage()
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
        self.kernelRow = QHBoxLayout()
        self.layout.addRow(self.kernelRow)
        self.table = QTableView()
        self.layout.addRow(self.table)        
        self.miss = QTableView()
        self.layout.addRow(self.miss)
        self.__initKernelInput()
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
        self.original_to_show = self.__fixScale(QPixmap.fromImage(self.original).toImage())
        self.converter.setOriginal(QPixmap.fromImage(self.original).toImage())
        self.image_original_label.setPixmap(QPixmap.fromImage(self.original_to_show))

        self.update()

    def __showImage(self):
        self.img = self.__fixScale(self.img)
        self.image_label.setPixmap(QPixmap.fromImage(self.img))
        self.update()

    def __fixScale(self, image):
        if (image.height() > 600):
            image = image.scaledToHeight(600)
        elif (image.height() < 200):
            image = image.scaledToHeight(200)
        if (image.width() > 800):
            image = image.scaledToWidth(800)        
        elif (image.width() < 200):
            image = image.scaledToWidth(200)
        return image

    def __readKernelInput(self, table):
        kernel = []
        model = table.model()
        for row in range(model.rowCount()):
            kernel.append([])
            for column in range(model.columnCount()):
                index = model.index(row, column)
                try:
                    val = model.data(index)
                    if (float(val) == 0):
                        kernel[row].append(float(0))                    
                    elif (float(val) == 1):
                        kernel[row].append(float(255))
                    elif (float(val) == -1):
                        kernel[row].append(float(-255))
                    else:
                        return None
                except TypeError: 
                    return None
        return kernel

    def __sizeChanged(self):
        size = self.kernelSizeInput.value()
        self.model = QStandardItemModel(size,size,self)
        for i in range(size):
            for j in range(size):
                self.model.setData(self.model.index(i,j), float(1.0))
        self.table.setModel(self.model)
        self.model_miss = QStandardItemModel(size,size,self)
        for i in range(size):
            for j in range(size):
                self.model_miss.setData(self.model_miss.index(i,j), float(0.0))
        self.miss.setModel(self.model_miss)
        self.update()

    def __initKernelInput(self):
        self.kernelSize = QLabel("Kernel size: ")
        self.kernelSizeInput = QSpinBox()
        self.kernelSizeInput.setMinimum(3)
        self.kernelSizeInput.setMaximum(51)
        self.kernelSizeInput.setSingleStep(2)
        self.kernelSizeInput.valueChanged.connect(self.__sizeChanged)
        self.kernelRow.addWidget(self.kernelSize)
        self.kernelRow.addWidget(self.kernelSizeInput)
        self.__sizeChanged()
        self.update()

    def __processImage(self):
        self.successLabel.setText(" ")
        self.update()
        if (self.img == None):
            self.__showErrorMessage("No image selected", "Invalid image")
            return
        pos = self.menu.currentIndex()
        print('Mode: {}'.format(pos))

        if self.kernelSizeInput.value() % 2 == 0:
            self.__showErrorMessage("Mask size must be odd", "Invalid value")
            return
        kernel = self.__readKernelInput(self.table)
        if (kernel is None): 
            self.__showErrorMessage("Invalid kernel, values must be 0 or 1", "Invalid value")
            return
        print('Kernel: {}'.format(kernel))

        if (int(pos) == 0):
            self.img = self.converter.dilation(kernel)
        elif (int(pos) == 1):
            self.img = self.converter.erosion(kernel)
        elif (int(pos) == 2):
            self.img = self.converter.opening(kernel)
        elif (int(pos) == 3):
            self.img = self.converter.closing(kernel)
        elif (int(pos) >= 4):
            miss = self.__readKernelInput(self.miss)
            if (miss is None): 
                self.__showErrorMessage("Invalid miss values, values must be 0 or 1", "Invalid value")
                return
            print('Miss: {}'.format(miss))
            if (int(pos) == 4):
                self.img = self.converter.hit_or_miss(kernel,miss)            
            elif (int(pos) == 5):
                self.img = self.converter.thickening(kernel,miss)            
            elif (int(pos) == 6):
                self.img = self.converter.thinning(kernel,miss)
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