from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys
class Toolbar(QToolBar):
    def __init__(self, btnClick):
        super(Toolbar, self).__init__()

        self.buttons = {
            "Line" : "Create line",
            "Rectangle" : "Create rectangle",
            "Circle" : "Create circle",
            "Move" : "Move shape",
            "Edit" : "Edit shape - resize or reshape" 
        }
        self.createToolbar(btnClick)

    def createToolbar(self, btnClick):
        for btn in self.buttons:
            button = QToolButton()
            button.setText(btn)
            button.setStatusTip(self.buttons[btn])
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.clicked.connect(btnClick)
            self.addWidget(button)
class Toolbox(QWidget):
    def __init__(self, color, type):
        super(Toolbox, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

        if (type == 0):
            self.lineInput()
        elif (type == 1):
            self.rectangleInput()
        else :
            self.circleInput()

        # inputAX.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

    def lineInput(self):
        self.layout = QFormLayout(self)
        label = QLabel(self)
        label.setText("Line")
        self.layout.addRow(label)

        self.createPoint("Point A:")
        self.createPoint("Point B:")

        submitBtn = QPushButton("Submit")
        self.layout.addRow(submitBtn)

    def rectangleInput(self):
        self.layout = QFormLayout(self)
        label = QLabel(self)
        label.setText("Rectangle")
        self.layout.addRow(label)

        self.createPoint("Point A:")
        self.createPoint("Point B:")
        self.createPoint("Point C:")
        self.createPoint("Point D:")

        submitBtn = QPushButton("Submit")
        self.layout.addRow(submitBtn)

    def circleInput(self):
        self.layout = QFormLayout(self)
        label = QLabel(self)
        label.setText("Rectangle")
        self.layout.addRow(label)

        self.createPoint("Center:")
        self.createPositionInput("Radius:")
        submitBtn = QPushButton("Submit")
        self.layout.addRow(submitBtn)

    def createPoint(self, label):
        pointLabel = QLabel(self)
        pointLabel.setText(label)
        self.layout.addRow(pointLabel)
        self.createPositionInput("X:")
        self.createPositionInput("Y:")

    def createPositionInput(self, name):
        label = QLabel(self)
        label.setText(name)
        inputSpinBox = QDoubleSpinBox(self)
        inputSpinBox.setMinimum(0.0);
        inputSpinBox.setMaximum(1280.0);
        inputSpinBox.setSingleStep(0.5)
        self.layout.addRow(label,inputSpinBox)

class Painter(QWidget):
    def __init__(self, color):
        super(Painter, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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
        self.layout.addWidget(Painter('white'),0,0,1,5)
        self.toolbox = Toolbox('lightgray',1);
        self.layout.addWidget(self.toolbox,0,6,1,1)

        self.addToolBar(Toolbar(self.onMyToolBarButtonClick))
        self.setStatusBar(QStatusBar(self))
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.label = QLabel("Click in this window")
        self.label.move(320, 20)

    def onMyToolBarButtonClick(self, s):
        self.layout.removeWidget(self.toolbox)
        if (self.sender().text() == "Line"):
            self.toolbox = Toolbox('lightgray',0);
        elif (self.sender().text() == "Rectangle"):
            self.toolbox = Toolbox('lightgray',1);
        elif (self.sender().text() == "Circle"):
            self.toolbox = Toolbox('lightgray',2);
        self.layout.addWidget(self.toolbox,0,6,1,1)

        print("click", self.sender().text())

    def mouseMoveEvent(self, e):
        self.label.setText("mouseMoveEvent")

    def mousePressEvent(self, e):
        self.label.setText("mousePressEvent")

    def mouseReleaseEvent(self, e):
        self.label.setText("mouseReleaseEvent")

    def mouseDoubleClickEvent(self, e):
        self.label.setText("mouseDoubleClickEvent")

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
        painter=MainWindow()
        painter.show()
        app.exec()