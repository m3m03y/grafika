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

class FileReader:
    def __init__(self, parent):
        self.mode = ""
        self.width = 0
        self.height = 0
        self.maxColorVal = 0
        self.parent = parent

    def saveFile(self, compression):
        res = self.openFile()
        if (not res): return

        saveFilePath, _ = QFileDialog.getSaveFileName(self.parent, "Save Image", "",
            "*")
 
        if saveFilePath == "":
            return        
        
        if not saveFilePath.__contains__('.jpeg'): saveFilePath += '.jpeg'

        self.img.save(saveFilePath, "JPEG", quality = compression)
        
    def openFile(self):
        self.start = datetime.now()
        filePath, _ = QFileDialog.getOpenFileName(self.parent, 'Open File', "",
            "Images (*.ppm *.jpeg *.jpg)")
 
        if filePath == "":
            return False
        
        ext = self.__getExtension(filePath)
        if (ext == ".ppm"):
            self.__getPPMImage(filePath)
        elif (ext == ".jpeg") | (ext == ".jpg"):
            self.__getJPEGImage(filePath)
        else:
            self.__showErrorMessage("Only ppm and jpeg supported!","Invalid file extensions!")   
            return    
        if (platform.system() == "Linux") & str(platform.uname()).__contains__("manjaro"):
            self.__displayOnManjaro()
        else: self.img.show()
        end = datetime.now()   
        time = end - self.start
        print('Duration {} File {}'.format(time,filePath))
        return True

    def __getExtension(self,path):
        return pathlib.Path(path).suffix
    
    def __getPPMImage(self,filePath):
        colors = []
        file = open(filePath,'rb') 
        while True:
            line = file.readline()
            if not line:
                break
            try:
                line = ''.join(map(chr, line))
            except:
                print('skip')
            if (str(line).startswith("#")):
                continue
            elif (len(line.split()) < 1):
                continue
            elif (str(line).startswith("P")):
                if (line.__contains__("P3")):
                    self.mode = "P3"
                elif(line.__contains__("P6")):
                    self.mode = "P6"
                else:
                    self.__showErrorMessage("Only PPM P3 and PPM P6 supported!","Invalid PPM mode!")          
                    return
            elif (self.mode != "") & (self.width == 0):
                if (str(line).__contains__("#")):
                    line = line.split("#")[0]
                params = line.split()
                if (len(params) == 1):
                    self.width =  int(params[0])
                elif (len(params) == 2):
                    self.width =  int(params[0])
                    self.height = int(params[1])
                elif (len(params) == 3):
                    self.width =  int(params[0])
                    self.height = int(params[1])
                    self.maxColorVal = int(params[2])
                elif (len(params) > 3):
                    self.width =  int(params[0])
                    self.height = int(params[1])
                    self.maxColorVal = int(params[2])
                    colors = params[3:len(params) + 1]
                else:
                    self.__showErrorMessage("Something gone wrong, should be size values or max color value!","File corrupted!")          
                    return
            elif (self.mode != "") & (self.width != 0) & (self.height == 0):
                if (str(line).__contains__("#")):
                    line = str(line).split("#")[0]
                params = line.split()
                if (len(params) == 1):
                    self.height = int(params[0])
                elif (len(params) == 2):
                    self.height = int(params[0])
                    self.maxColorVal = int(params[1])
                elif (len(params) > 2):
                    self.height = int(params[0])
                    self.maxColorVal = int(params[1])
                    colors = params[2:len(params) + 1]
                else:     
                    self.__showErrorMessage("Something gone wrong, should be size values or max color value!","File corrupted!")          
                    return
            elif (self.mode != "") & (self.width != 0) & (self.height != 0):
                if (str(line).__contains__("#")):
                    line = line.split("#")[0]
                params = line.split()
                if (len(params) == 1):
                    self.maxColorVal = int(params[0])
                elif (len(params) > 1):
                    self.maxColorVal = int(params[0])
                    colors = params[2:len(params) + 1]
                else:
                    self.__showErrorMessage("Something gone wrong, should be max color value!","File corrupted!")
                    return
            if (self.mode != "") & (self.width != 0) & (self.height != 0) & (self.maxColorVal != 0):
                break
        print("Mode: " + str(self.mode) + " Width: " + str(self.width) + " Height: " + str(self.height) + " Max Color Value: " + str(self.maxColorVal))
        self.scale = 255 / self.maxColorVal
        if (self.mode == "P3"):
            self.__processP3(colors,file)
        elif (self.mode == "P6"):
            self.__processP6(colors,file)
        else:
            self.__showErrorMessage("Only PPM P3 and PPM P6 supported!","File corrupted!")

    def __displayOnManjaro(self):
        tmpstmp = datetime.now()
        tempFileName = "/tmp/temporary_{}.PNG".format(tmpstmp)
        self.img.save(tempFileName,"PNG")
        webbrowser.open(tempFileName)

    def __getJPEGImage(self,file):
        self.img = Image.open(file)

    def __scaleColor(self,color):
        return int(self.scale * color)

    def __processP3(self,lines,file):
        self.img  = Image.new( mode = "RGB", size = (self.width, self.height))
        fileInput = ' '.join(lines) + ' ' + str(file.read().decode())
        if (str(fileInput).__contains__("#")):
            fileInput = (re.sub(r'#.*\n',' ', fileInput))
        values = list(map(int,fileInput.split()))
        file.close()
        # self.__printSubTime()
        self.__colorImage(values)
        # self.__printSubTime()

    def __processP6(self,lines,file):
        self.img  = Image.new( mode = "RGB", size = (self.width, self.height) )
        # self.__printSubTime()
        values = list(lines) + list(file.read())
        file.close()
        # self.__printSubTime()
        self.__colorImage(values)
        # self.__printSubTime()
    
    def __colorImage(self,values):
        pixels = self.img.load()
        i,j,startIdx,endIdx = 0,0,0,3
        while (startIdx < len(values)):
            color = values[startIdx:endIdx]
            startIdx += 3
            endIdx += 3
            if (self.maxColorVal != 255):
                color[0] = self.__scaleColor(color[0])
                color[1] = self.__scaleColor(color[1])
                color[2] = self.__scaleColor(color[2])
            pixels[j,i] = (color[0],color[1],color[2])
            if (j == (self.img.size[0] - 1)):
                j = 0
                if (i < self.img.size[1]):
                    i += 1
                else:
                    self.__showErrorMessage("Invalid colors value!","File corrupted!")
                    return
            else: j += 1

    def __showErrorMessage(self, msg, title):
        QMessageBox.critical(
            self.parent,
            title,
            msg,
            buttons=QMessageBox.Ignore,
            defaultButton=QMessageBox.Ignore,
        )
    
    def __printSubTime(self):
        sub = datetime.now()
        subTime = sub - self.start
        print('Subtime {}.'.format(subTime))
    
    def pixels(self):
        return self.img.load()

class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        openBtn = QPushButton("Open file")
        openBtn.clicked.connect(self.open)

        self.layout = QFormLayout()
        self.layout.addWidget(openBtn)
        self.image_label = QLabel(" ")
        self.layout.addWidget(self.image_label)
        self.setLayout(self.layout)

    def open(self):
        filePath, _ = QFileDialog.getOpenFileName(self, 'Open File', "",
            "Images (*.ppm *.jpeg *.jpg)")
 
        if filePath == "":
            return False

        img = QImage(filePath)
        self.image_label.setPixmap(QPixmap.fromImage(img))
        self.update()

if __name__=='__main__':
        app=QApplication(sys.argv)
        window=Form()
        window.show()
        app.exec()