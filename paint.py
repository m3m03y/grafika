from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys
from dataclasses import dataclass

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

@dataclass
class Rectangle(Shape):
    B: QPoint

@dataclass
class Circle(Shape):
    radius: float
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
        elif (type == 2):
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
        self.layout.addRow(coordLabel,inputSpinBox)

    def onSubmitBtnClicked(self, s):
        test = self.layout.findChildren(QDoubleSpinBox)
        for t in test:
            print(t.text())
        print("SUBMIT CLICKED:" )

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

        self.objects = []

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.blue,  8, Qt.SolidLine))
        
        for obj in self.objects:
            print(obj)
            if (isinstance(obj,Line)):
                painter.drawLine(obj.A, obj.B)
            if (isinstance(obj,Rectangle)):
                painter.drawRect(QRect(obj.A, obj.B))
            if (isinstance(obj,Circle)):
                print("This is circle")

        if not self.lineStart.isNull() and not self.lineEnd.isNull():
            if (self.mode == 0):
                painter.drawLine(self.lineStart, self.lineEnd)
            elif (self.mode == 1):
                painter.drawRect(QRect(self.lineStart, self.lineEnd))
            elif (self.mode == 2):
                painter.drawEllipse(QRect(self.lineStart, self.lineEnd))

    def mouseMoveEvent(self, e):
        if self.isDrawing :
            self.lineEnd = e.pos()
            self.points << e.pos()
            self.update()


    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.isDrawing = True;
            self.lastPos = e.pos()
            self.lineStart = e.pos()
            self.lineEnd = e.pos()

    def mouseReleaseEvent(self, e):
        if self.isDrawing:
            if (self.mode == 0):
                A = self.lineStart
                B = self.lineEnd
                line = Line(A,B)
                self.objects.append(line)
            elif (self.mode == 1):
                A = self.lineStart
                B = self.lineEnd
                rectangle = Rectangle(A,B)
                self.objects.append(rectangle)
            elif (self.mode == 2):
                painter.drawEllipse(QRect(self.lineStart, self.lineEnd))
            print(self.objects)

        self.isDrawing = False;
        self.lineEnd = e.pos()

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
        self.toolbox = Toolbox('lightgray',3);
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
            self.toolbox = Toolbox('lightgray',0);
        elif (self.sender().text() == "Rectangle"):
            self.painter.setMode(1)
            self.toolbox = Toolbox('lightgray',1);
        elif (self.sender().text() == "Circle"):
            self.painter.setMode(2)
            self.toolbox = Toolbox('lightgray',2);
        self.layout.addWidget(self.toolbox,0,6,1,1)

        print("click", self.sender().text())

if __name__=='__main__':
        app=QApplication(sys.argv)
        painter=MainWindow()
        painter.show()
        app.exec()