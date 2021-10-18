import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
# from PIL import Image
import pathlib

class FileReader:
    def __init__(self):
        self.mode = ""
        self.width = 0
        self.height = 0
        self.maxColorVal = 0

    def saveFile(self, obj):
        filePath, _ = QFileDialog.getSaveFileName(obj, "Save Image", "",
            "*")
 
        if filePath == "":
            return        
        
    def openFile(self,obj):
        filePath, _ = QFileDialog.getOpenFileName(obj, 'Open File', "",
            "Images (*.ppm *.jpeg *.jpg)")
 
        if filePath == "":
            return         
        
        ext = self.__getExtension(filePath)

        file = open(filePath,'r')
        img = file.readlines()

        if (ext == ".ppm"):
            self.__getPPMImage(img)
        elif (ext == ".jpeg") | (ext == ".jpg"):
            self.__getJPEGImage(img)
        else:
            print('Invalid file extension!')
    
    def __getExtension(self,path):
        return pathlib.Path(path).suffix
    
    def __getPPMImage(self,lines):
        pixels = []
        startFrom = 0
        for line in lines:
            if (line.startswith("#")):
                print("Comment line: " + line)
                startFrom+=1
            elif (len(line.split()) < 1):
                continue
            elif (self.mode == "") & (line.startswith("P")):
                if (line.__contains__("P3")):
                    self.mode = "P3"
                elif(line.__contains__("P6")):
                    self.mode = "P6"
                else:
                    print("Invalid mode")
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
                    pixels = params.slice(3,len(params) + 1)
                    # pixels.append(params.slice(3,len(params) + 1))
                else:
                    print("Something gone wrong, should be size values or max color value!")
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
                    pixels = params.slice(2,len(params) + 1)
                    # pixels.append(params.slice(2,len(params) + 1))
                else:
                    print("Something gone wrong, should be size values or max color value!")
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
                    pixels = params.slice(1,len(params) + 1)
                    # pixels.append(params.slice(1,len(params) + 1))
                else:
                    print("Something gone wrong, should be max color value!")
                    return
                startFrom+=1
            if (self.mode != "") & (self.width != 0) & (self.height != 0) & (self.maxColorVal != 0):
                break

        print("Mode: " + str(self.mode) + " Width: " + str(self.width) + " Height: " + str(self.height) + " Max Color Value: " + str(self.maxColorVal))
        pixels [len(pixels):] = lines[startFrom:]
        print(pixels)

    def __getJPEGImage(self,lines):
        print("JPEG")

# class Toolbar(QToolBar):
#     def __init__(self, btnClick):
#         super(Toolbar, self).__init__()
#         self.setAutoFillBackground(True)

#         palette = self.palette()
#         palette.setColor(QPalette.Window, Qt.black)
#         self.setPalette(palette)
#         self.buttons = {
#             "Save" : "Save image",
#             "Open" : "Open image"
#         }
#         self.createToolbar(btnClick)

#     def createToolbar(self, btnClick):
#         for btn in self.buttons:
#             button = QToolButton()
#             button.setText(btn)
#             button.setStatusTip(self.buttons[btn])
#             button.setAutoExclusive(True)
#             button.clicked.connect(btnClick)
#             self.addWidget(button)

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setAutoFillBackground(True)

#         palette = self.palette()
#         palette.setColor(QPalette.Window, Qt.white)
#         self.setPalette(palette)

#         self.title='Kinga Lipiszko PS4'
#         self.left=10
#         self.top=10
#         self.width=1280
#         self.height=720
#         self.initUI()

#     def initUI(self):
#         self.setWindowTitle(self.title)
#         self.setGeometry(self.left,self.top,self.width,self.height)
#         self.layout = QGridLayout()

#         self.addToolBar(Toolbar(self.onMyToolBarButtonClick))
#         self.setStatusBar(QStatusBar(self))
#         widget = QWidget()
#         widget.setLayout(self.layout)
#         self.setCentralWidget(widget)

#     def onMyToolBarButtonClick(self, s):
#         if (self.sender().text() == "Save"):
#             FileReader.saveFile(self)
#         if (self.sender().text() == "Open"):
#             FileReader.openFile(self)

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
        reader = FileReader()
        reader.openFile(self)

    def save(self):
        reader = FileReader()
        reader.saveFile(self)

if __name__=='__main__':
        app=QApplication(sys.argv)
        window=Form()
        window.show()
        app.exec()