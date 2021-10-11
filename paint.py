from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title='PaintPrime'
        self.left=10
        self.top=10
        self.width=1280
        self.height=720
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)

        self.pointALabel = QLabel(self)
        self.pointALabel.setText('A:')
        self.pointALabel.move(620, 20)

        self.aX = QLineEdit(self)
        self.aX.move(660, 20)
        self.aX.resize(50, 32)

        self.aY = QLineEdit(self)
        self.aY.move(720, 20)
        self.aY.resize(50, 32)

        pybutton = QPushButton('OK', self)
        pybutton.clicked.connect(self.clickMethod)
        pybutton.resize(200,32)
        pybutton.move(80, 60) 

        self.show()

    def clickMethod(self):
        painter = QPainter(self)       
        painter.setPen(QPen(Qt.white,  8, Qt.SolidLine))
        painter.drawLine(int(self.aX.text()),int(self.aY.text()),500,100)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.white,  8, Qt.SolidLine))
        painter.drawEllipse(40, 40, 400, 400)
        
        painter.setPen(QPen(Qt.red,  8, Qt.SolidLine))
        painter.drawLine(40,100,500,100)

        painter.setPen(QPen(Qt.green,  8, Qt.SolidLine))
        painter.drawRect(40, 40, 400, 200)

if __name__=='__main__':
        app=QApplication(sys.argv)
        ex=App()
        sys.exit(app.exec_())