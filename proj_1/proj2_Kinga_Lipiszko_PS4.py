import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from datetime import datetime
from PIL import Image
import pathlib
import numpy

class FileReader:
    def __init__(self, parent):
        self.mode = ""
        self.width = 0
        self.height = 0
        self.maxColorVal = 0
        self.parent = parent

    def saveFile(self):
        filePath, _ = QFileDialog.getSaveFileName(self.parent, "Save Image", "",
            "*")
 
        if filePath == "":
            return        
        
    def openFile(self):
        start = datetime.now()
        filePath, _ = QFileDialog.getOpenFileName(self.parent, 'Open File', "",
            "Images (*.ppm *.jpeg *.jpg)")
 
        if filePath == "":
            return         
        
        ext = self.__getExtension(filePath)

        file = open(filePath,'r')
        lines = file.readlines()
        sub = datetime.now()
        subTime = sub - start
        print('Duration {}.'.format(subTime))

        if (ext == ".ppm"):
            self.__getPPMImage(lines)
        elif (ext == ".jpeg") | (ext == ".jpg"):
            self.__getJPEGImage(lines)
        else:
            self.__showErrorMessage("Only ppm and jpeg supported!","Invalid file extensions!")       
        end = datetime.now()   
        time = end - start
        print("Duration: " + str(time) + " File: " + str(filePath))

    def __getExtension(self,path):
        return pathlib.Path(path).suffix
    
    def __getPPMImage(self,lines):
        colors = []
        startFrom = 0
        for line in lines:
            if (line.startswith("#")):
                print("Comment line: " + line)
                startFrom+=1
            elif (len(line.split()) < 1):
                startFrom+=1
                continue
            elif (self.mode == "") & (line.startswith("P")):
                if (line.__contains__("P3")):
                    self.mode = "P3"
                elif(line.__contains__("P6")):
                    self.mode = "P6"
                else:
                    self.__showErrorMessage("Only PPM P3 and PPM P6 supported!","Invalid PPM mode!")          
                    return
                startFrom+=1
            elif (self.mode != "") & (self.width == 0):
                if (line.__contains__("#")):
                    line = line.split("#")[0]
                params = line.split()
                if (len(params) == 1):
                    self.width =  params[0]
                elif (len(params) == 2):
                    self.width =  params[0]
                    self.height = params[1]
                elif (len(params) == 3):
                    self.width =  params[0]
                    self.height = params[1]
                    self.maxColorVal = params[2]
                elif (len(params) > 3):
                    self.width =  params[0]
                    self.height = params[1]
                    self.maxColorVal = params[2]
                    colors = params[3:len(params) + 1]
                else:
                    self.__showErrorMessage("Something gone wrong, should be size values or max color value!","File corrupted!")          
                    return
                startFrom+=1
            elif (self.mode != "") & (self.width != 0) & (self.height == 0):
                if (line.__contains__("#")):
                    line = line.split("#")[0]
                params = line.split()
                if (len(params) == 1):
                    self.height = params[0]
                elif (len(params) == 2):
                    self.height = params[0]
                    self.maxColorVal = params[1]
                elif (len(params) > 2):
                    self.height = params[0]
                    self.maxColorVal = params[1]
                    colors = params[2:len(params) + 1]
                else:     
                    self.__showErrorMessage("Something gone wrong, should be size values or max color value!","File corrupted!")          
                    return
                startFrom+=1
            elif (self.mode != "") & (self.width != 0) & (self.height != 0):
                if (line.__contains__("#")):
                    line = line.split("#")[0]
                params = line.split()
                if (len(params) == 1):
                    self.maxColorVal = params[0]
                elif (len(params) > 1):
                    self.maxColorVal = params[0]
                    colors = params[2:len(params) + 1]
                else:
                    self.__showErrorMessage("Something gone wrong, should be max color value!","File corrupted!")
                    return
                startFrom+=1
            if (self.mode != "") & (self.width != 0) & (self.height != 0) & (self.maxColorVal != 0):
                break

        colors [len(colors):] = lines[startFrom:]
        print("Mode: " + str(self.mode) + " Width: " + str(self.width) + " Height: " + str(self.height) + " Max Color Value: " + str(self.maxColorVal))
        if (self.mode == "P3"):
            self.__processP3(colors)
        elif (self.mode == "P6"):
            self.__processP6(colors)
        else:
            self.__showErrorMessage("Only PPM P3 and PPM P6 supported!","File corrupted!")

    def __getJPEGImage(self,lines):
        print("JPEG")

    def __scaleColor(self,color):
        scale = 255 / int(self.maxColorVal)
        return int(scale  * color)

    def __processP3(self,lines):
        print("Processing P3")
        pixelsCount = (int(self.width) * int(self.height))
        colors = numpy.zeros((pixelsCount,3))
        column = 0
        row = 0
        for line in lines:
            if (line.__contains__("#")):
                line = line.split("#")[0]
            values = line.split()
            for val in values:
                colors[row,column] = int(val)
                if (column == 2):
                    column = 0
                    row += 1
                else: column += 1
        # TODO: error printing
        img  = Image.new( mode = "RGB", size = (int(self.width), int(self.height)) )
        pixels = img.load()
        pixelIdx = 0
        for i in range (img.size[1]):
            for j in range(img.size[0]):
                R = self.__scaleColor(colors[pixelIdx][0])
                G = self.__scaleColor(colors[pixelIdx][1])
                B = self.__scaleColor(colors[pixelIdx][2])
                pixels[j,i] = (R,G,B)
                pixelIdx += 1
        img.show()

    def __processP6(self,colors):
        print("Processing P6")
    
    def __showErrorMessage(self, msg, title):
        QMessageBox.critical(
            self.parent,
            title,
            msg,
            buttons=QMessageBox.Ignore,
            defaultButton=QMessageBox.Ignore,
        )

class Form(QDialog):
    
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        openBtn = QPushButton("Open file")
        saveBtn = QPushButton("Save as JPEG")

        openBtn.clicked.connect(self.open)
        saveBtn.clicked.connect(self.save)

        layout = QVBoxLayout()
        layout.addWidget(openBtn)
        layout.addWidget(saveBtn)

        self.setLayout(layout)

    def open(self):
        reader = FileReader(self)
        reader.openFile()

    def save(self):
        reader = FileReader(self)
        reader.saveFile()

if __name__=='__main__':
        app=QApplication(sys.argv)
        window=Form()
        window.show()
        app.exec()