from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys
import math
from dataclasses import dataclass
objects = []

@dataclass
class Point:
    x: float
    y: float

@dataclass
class Shape:
    A: QPoint

@dataclass
class Line(Shape):
    B: QPoint
    color: QColor = Qt.red

@dataclass
class Rectangle(Shape):
    B: QPoint
    color: QColor = Qt.green

@dataclass
class Circle(Shape):
    radius: float
    color: QColor = Qt.blue

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
    def __init__(self, color, type, p):
        super(Toolbox, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)
        self.mode = 0
        self.inputs = []
        self.painter = p
        if (type == 0):
            self.mode = 0
            self.lineInput()
        elif (type == 1):
            self.mode = 1
            self.rectangleInput()
        elif (type == 2):
            self.mode = 2
            self.circleInput()

        # inputAX.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

    def lineInput(self):
        self.layout = QFormLayout(self)
        self.label = QLabel(self)
        self.label.setText("Line")
        self.layout.addRow(self.label)

        self.createPoint("Point A:")
        self.createPoint("Point B:")

        submitBtn = QPushButton("Submit")
        submitBtn.clicked.connect(self.onSubmitBtnClicked)
        self.layout.addRow(submitBtn)

    def rectangleInput(self):
        self.layout = QFormLayout(self)
        self.label = QLabel(self)
        self.label.setText("Rectangle")
        self.layout.addRow(self.label)

        self.createPoint("Point A:")
        self.createPoint("Point B:")
        # self.createPoint("Point C:")
        # self.createPoint("Point D:")

        submitBtn = QPushButton("Submit")
        submitBtn.clicked.connect(self.onSubmitBtnClicked)
        self.layout.addRow(submitBtn)

    def circleInput(self):
        self.layout = QFormLayout(self)
        self.label = QLabel(self)
        self.label.setText("Circle")
        self.layout.addRow(self.label)

        self.createPoint("Center:")
        self.createPositionInput("Radius:")
        submitBtn = QPushButton("Submit")
        submitBtn.clicked.connect(self.onSubmitBtnClicked)
        self.layout.addRow(submitBtn)

    def createPoint(self, name):
        pointLabel = QLabel(self)
        pointLabel.setText(name)
        self.layout.addRow(pointLabel)
        self.createPositionInput("X:")
        self.createPositionInput("Y:")

    def createPositionInput(self, name):
        coordLabel = QLabel(self)
        coordLabel.setText(name)
        inputSpinBox = QDoubleSpinBox(self)
        inputSpinBox.setMinimum(0.0);
        inputSpinBox.setMaximum(1280.0);
        inputSpinBox.setSingleStep(0.5)
        self.inputs.append(inputSpinBox)
        self.layout.addRow(coordLabel,inputSpinBox)

    def onSubmitBtnClicked(self, s):
        if (self.mode == 0):
            A = QPoint(float(self.inputs[0].text().replace(",",".")),float(self.inputs[1].text().replace(",",".")))
            B = QPoint(float(self.inputs[2].text().replace(",",".")),float(self.inputs[3].text().replace(",",".")))
            shape = Line(A,B)
        elif (self.mode == 1):
            A = QPoint(float(self.inputs[0].text().replace(",",".")),float(self.inputs[1].text().replace(",",".")))
            B = QPoint(float(self.inputs[2].text().replace(",",".")),float(self.inputs[3].text().replace(",",".")))
            shape = Rectangle(A,B)
        elif (self.mode == 2):
            A = QPoint(float(self.inputs[0].text().replace(",",".")),float(self.inputs[1].text().replace(",",".")))
            shape = Circle(A,float(self.inputs[2].text().replace(",",".")))
        self.updateDraw(shape)

    def updateDraw(self,shape):
        print(shape)
        objects.append(shape)
        self.painter.update()

class Painter(QWidget):
    def __init__(self, color):
        super(Painter, self).__init__()

        self.mode = 0
        self.isDrawing = False
        self.lastPos = QPoint()

        self.lineStart = QPoint()
        self.lineEnd = QPoint()
        self.image = QImage(self.size(), QImage.Format_RGB32)
        
        self.points = QPolygon()


    def paintEvent(self, event):
        painter = QPainter(self)
        
        for obj in objects:
            painter.setPen(QPen(obj.color,  8, Qt.SolidLine))
            if (isinstance(obj,Line)):
                painter.drawLine(obj.A, obj.B)
            if (isinstance(obj,Rectangle)):
                painter.drawRect(QRect(obj.A, obj.B))
            if (isinstance(obj,Circle)):
                painter.drawEllipse(obj.A,obj.radius,obj.radius)

        if not self.lineStart.isNull() and not self.lineEnd.isNull():
            painter.setPen(QPen(Qt.black,  8, Qt.SolidLine))
            if (self.mode == 0):
                painter.drawLine(self.lineStart, self.lineEnd)
            elif (self.mode == 1):
                painter.drawRect(QRect(self.lineStart, self.lineEnd))
            elif (self.mode == 2):
                radius = math.sqrt(abs(self.lineStart.x() - self.lineEnd.x())**2 + abs(self.lineStart.y() - self.lineEnd.y())**2)
                painter.drawEllipse(self.lineStart,radius,radius)

    def mouseMoveEvent(self, e):
        if self.isDrawing :
            self.lineEnd = e.pos()
            self.points << e.pos()
            self.update()


    def mousePressEvent(self, e):
        if self.mode == 3:
            print("is moving!!!")
        elif self.mode == 4:
            print("is resizing!!!")
        elif e.button() == Qt.LeftButton:
            self.isDrawing = True;
            self.lastPos = e.pos()
            self.lineStart = e.pos()
            self.lineEnd = e.pos()
            print("is drawing!!!")

    def mouseReleaseEvent(self, e):
        if self.isDrawing:
            if (self.mode == 0):
                A = self.lineStart
                B = self.lineEnd
                line = Line(A,B)
                objects.append(line)
            elif (self.mode == 1):
                A = self.lineStart
                B = self.lineEnd
                rectangle = Rectangle(A,B)
                objects.append(rectangle)
            elif (self.mode == 2):
                A = self.lineStart
                radius = math.sqrt(abs(self.lineStart.x() - self.lineEnd.x())**2 + abs(self.lineStart.y() - self.lineEnd.y())**2)
                circle = Circle(A,radius)
                objects.append(circle)

        self.isDrawing = False;
        self.lineStart = QPoint()
        self.lineEnd = QPoint()
        self.update()

    def setMode(self,mode):
        self.lineStart = QPoint()
        self.lineEnd = QPoint()
        print("Draw mode changed from " + str(self.mode) + " to " + str(mode))
        self.mode = mode

    # def mouseDoubleClickEvent(self, e):
    #     print("mouseDoubleClickEvent")

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
        self.painter = Painter('white')
        self.layout.addWidget(self.painter,0,0,1,5)
        self.toolbox = Toolbox('lightgray',3,self.painter);
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
            self.painter.setMode(0)
            self.toolbox = Toolbox('lightgray',0,self.painter);
        elif (self.sender().text() == "Rectangle"):
            self.painter.setMode(1)
            self.toolbox = Toolbox('lightgray',1,self.painter);
        elif (self.sender().text() == "Circle"):
            self.painter.setMode(2)
            self.toolbox = Toolbox('lightgray',2,self.painter);
        elif (self.sender().text() == "Move"):
            self.painter.setMode(3)
            self.toolbox = Toolbox('lightgray',2,self.painter);
        elif (self.sender().text() == "Edit"):
            self.painter.setMode(4)
            self.toolbox = Toolbox('lightgray',2,self.painter);
        self.layout.addWidget(self.toolbox,0,6,1,1)

        print("click", self.sender().text())
        
if __name__=='__main__':
        app=QApplication(sys.argv)
        painter=MainWindow()
        painter.show()
        app.exec()