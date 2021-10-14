import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PIL import Image

class FileReader:
    def saveFile(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
            "*")
 
        if filePath == "":
            return        
        
    def openFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, 'Open File', "",
            "PPM(*.ppm) ")
 
        if filePath == "":
            return         
        
        file = open(filePath,'r')
        lines = file.readlines()

        for line in lines:
            if (line[0] != "#"):
                print(line)
        
class Toolbar(QToolBar):
    def __init__(self, btnClick):
        super(Toolbar, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, Qt.black)
        self.setPalette(palette)
        self.buttons = {
            "Save" : "Save image",
            "Open" : "Open image"
        }
        self.createToolbar(btnClick)

    def createToolbar(self, btnClick):
        for btn in self.buttons:
            button = QToolButton()
            button.setText(btn)
            button.setStatusTip(self.buttons[btn])
            button.setAutoExclusive(True)
            button.clicked.connect(btnClick)
            self.addWidget(button)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, Qt.white)
        self.setPalette(palette)

        self.title='Kinga Lipiszko PS4'
        self.left=10
        self.top=10
        self.width=1280
        self.height=720
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)
        self.layout = QGridLayout()

        self.addToolBar(Toolbar(self.onMyToolBarButtonClick))
        self.setStatusBar(QStatusBar(self))
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

    def onMyToolBarButtonClick(self, s):
        if (self.sender().text() == "Save"):
            FileReader.saveFile(self)
        if (self.sender().text() == "Open"):
            FileReader.openFile(self)

if __name__=='__main__':
        app=QApplication(sys.argv)
        window=MainWindow()
        window.show()
        app.exec()