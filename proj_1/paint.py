from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys
import math
from dataclasses import dataclass
import json

objects = []
selectedIndex = []
brushSize = 8
toolboxColor = QColor("gray")
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
    isSelected: bool = False
    color: QColor = Qt.red

@dataclass
class Rectangle(Shape):
    B: QPoint
    isSelected: bool = False
    color: QColor = Qt.green

@dataclass
class Circle(Shape):
    radius: float
    isSelected: bool = False
    color: QColor = Qt.blue

class Toolbar(QToolBar):
    def __init__(self, btnClick):
        super(Toolbar, self).__init__()

        self.buttons = {
            "Line" : "Create line",
            "Rectangle" : "Create rectangle",
            "Circle" : "Create circle",
            "Move" : "Move shape",
            "Edit" : "Edit shape - resize or reshape",
            "Clear" : "Clear all shapes",
            "Save" : "Save current workspace",
            "Open" : "Open saved workspace"
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
    def __init__(self, mode, p, isEditMode):
        super(Toolbox, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, toolboxColor)
        self.setPalette(palette)
        self.mode = mode
        self.inputs = []
        self.painter = p
        self.editMode = isEditMode

        if (mode == 0):
            self.lineInput()
        elif (mode == 1):
            self.rectangleInput()
        elif (mode == 2):
            self.circleInput()

    def lineInput(self):
        self.layout = QFormLayout(self)
        self.label = QLabel(self)
        self.label.setText("Line")
        self.layout.addRow(self.label)
        
        if (self.editMode):
            obj = objects[selectedIndex[0]]
            self.createPoint("Point A:", obj.A.x(), obj.A.y())
            self.createPoint("Point B:", obj.B.x(), obj.B.y())
        else:
            self.createPoint("Point A:", 0,0)
            self.createPoint("Point B:", 0,0)

        submitBtn = QPushButton("Submit")
        submitBtn.clicked.connect(self.onSubmitBtnClicked)
        self.layout.addRow(submitBtn)
        if (self.editMode):
            cancelBtn = QPushButton("Cancel")
            cancelBtn.clicked.connect(self.onCancelBtnClicked)
            self.layout.addRow(cancelBtn)

    def rectangleInput(self):
        self.layout = QFormLayout(self)
        self.label = QLabel(self)
        self.label.setText("Rectangle")
        self.layout.addRow(self.label)

        if (self.editMode):
            obj = objects[selectedIndex[0]]
            self.createPoint("Point A:", obj.A.x(), obj.A.y())
            self.createPoint("Point B:", obj.B.x(), obj.B.y())
        else:
            self.createPoint("Point A:", 0,0)
            self.createPoint("Point B:", 0,0)

        submitBtn = QPushButton("Submit")
        submitBtn.clicked.connect(self.onSubmitBtnClicked)
        self.layout.addRow(submitBtn)
        if (self.editMode):
            cancelBtn = QPushButton("Cancel")
            cancelBtn.clicked.connect(self.onCancelBtnClicked)
            self.layout.addRow(cancelBtn)

    def circleInput(self):
        self.layout = QFormLayout(self)
        self.label = QLabel(self)
        self.label.setText("Circle")
        self.layout.addRow(self.label)

        if (self.editMode):
            obj = objects[selectedIndex[0]]
            self.createPoint("Center:", obj.A.x(), obj.A.y())
            self.createPositionInput("Radius:", obj.radius)            
        else:
            self.createPoint("Center:", 0,0)
            self.createPositionInput("Radius:", 0)    

        submitBtn = QPushButton("Submit")
        submitBtn.clicked.connect(self.onSubmitBtnClicked)
        self.layout.addRow(submitBtn)
        if (self.editMode):
            cancelBtn = QPushButton("Cancel")
            cancelBtn.clicked.connect(self.onCancelBtnClicked)
            self.layout.addRow(cancelBtn)


    def createPoint(self, name, posX, posY):
        pointLabel = QLabel(self)
        pointLabel.setText(name)
        self.layout.addRow(pointLabel)
        self.createPositionInput("X:", posX)
        self.createPositionInput("Y:", posY)

    def createPositionInput(self, name, default):
        coordLabel = QLabel(self)
        coordLabel.setText(name)
        inputSpinBox = QDoubleSpinBox(self)
        inputSpinBox.setMinimum(0.0);
        inputSpinBox.setMaximum(1280.0);
        inputSpinBox.setSingleStep(0.5)
        inputSpinBox.setValue(default)
        self.inputs.append(inputSpinBox)
        self.layout.addRow(coordLabel,inputSpinBox)

    def clearToolbox(self):
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)
        self.editMode = False
        objects[selectedIndex[0]].isSelected = False
        selectedIndex[0] = -1
        self.painter.update()

    def onCancelBtnClicked(self, s):
        self.clearToolbox()

    def onSubmitBtnClicked(self, s):

        if (self.mode == 0):
            A = QPoint(float(self.inputs[0].text().replace(",",".")),float(self.inputs[1].text().replace(",",".")))
            B = QPoint(float(self.inputs[2].text().replace(",",".")),float(self.inputs[3].text().replace(",",".")))
            if (A == B):
                button = QMessageBox.critical(
                        self,
                        "Invalid input!",
                        "Points must not be on the same place",
                        buttons=QMessageBox.Ignore,
                        defaultButton=QMessageBox.Ignore,
                    )
                return
            shape = Line(A,B)
        elif (self.mode == 1):
            A = QPoint(float(self.inputs[0].text().replace(",",".")),float(self.inputs[1].text().replace(",",".")))
            B = QPoint(float(self.inputs[2].text().replace(",",".")),float(self.inputs[3].text().replace(",",".")))
            if (A == B):
                button = QMessageBox.critical(
                    self,
                    "Invalid input!",
                    "Points must not be on the same place",
                    buttons=QMessageBox.Ignore,
                    defaultButton=QMessageBox.Ignore,
                )
                return
            shape = Rectangle(A,B)
        elif (self.mode == 2):
            A = QPoint(float(self.inputs[0].text().replace(",",".")),float(self.inputs[1].text().replace(",",".")))
            radius = float(self.inputs[2].text().replace(",","."))
            if (radius == 0):
                button = QMessageBox.critical(
                    self,
                    "Invalid input!",
                    "Radius cannot equals 0",
                    buttons=QMessageBox.Ignore,
                    defaultButton=QMessageBox.Ignore,
                )
                return
            shape = Circle(A,radius)
        if (self.editMode) :
            objects[selectedIndex[0]] = shape
            selectedIndex[0] = -1
            self.painter.update()
            self.clearToolbox()
        else:
            self.updateDraw(shape)

    def updateDraw(self,shape):
        objects.append(shape)
        self.painter.update()

class Painter(QWidget):
    def __init__(self, color, editFunc):
        super(Painter, self).__init__()

        self.mode = -1
        self.isDrawing = False
        self.lastPos = QPoint()

        self.lineStart = QPoint()
        self.lineEnd = QPoint()
        self.image = QImage(self.size(), QImage.Format_RGB32)
        selectedIndex.append(-1)
        self.editFunc = editFunc
        self.editMode = False
        
    def paintEvent(self, event):
        painter = QPainter(self)
        for obj in objects:
            if obj.isSelected: painter.setPen(QPen(obj.color,  brushSize, Qt.DashLine))
            else: painter.setPen(QPen(obj.color,  brushSize, Qt.SolidLine))
            if (isinstance(obj,Line)):
                painter.drawLine(obj.A, obj.B)
            if (isinstance(obj,Rectangle)):
                painter.drawRect(QRect(obj.A, obj.B))
            if (isinstance(obj,Circle)):
                painter.drawEllipse(obj.A,obj.radius,obj.radius)

        if not self.lineStart.isNull() and not self.lineEnd.isNull():
            painter.setPen(QPen(Qt.black,  brushSize, Qt.SolidLine))
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
            self.update()
        elif (self.mode == 3) & (selectedIndex[0] >= 0) & (not self.editMode):
            if (isinstance(objects[selectedIndex[0]],Line)):
                self.moveLine(e.pos())
            elif (isinstance(objects[selectedIndex[0]],Circle)):
                self.moveCircle(e.pos())
            elif (isinstance(objects[selectedIndex[0]],Rectangle)):
                self.moveLine(e.pos())
            self.lastPos = e.pos()
            self.update()
        elif (self.mode == 4) & (selectedIndex[0] >= 0) & (not self.editMode):
            if (isinstance(objects[selectedIndex[0]],Line)):
                self.resizeLine(e.pos())
            elif (isinstance(objects[selectedIndex[0]],Circle)):
                self.resizeCircle(e.pos())
            elif (isinstance(objects[selectedIndex[0]],Rectangle)):
                self.resizeLine(e.pos())
            self.lastPos = e.pos()
            self.update()

    def mousePressEvent(self, e):
        if (selectedIndex[0] < 0) :
            self.editMode = False
        if (self.mode == 3) & (not self.editMode):
            self.findObject(e.pos())
            self.lastPos = e.pos()
        elif (self.mode == 4) & (e.button() == Qt.LeftButton) & (not self.editMode):
            self.findObject(e.pos())
        elif e.button() == Qt.LeftButton:
            self.isDrawing = True;
            self.lineStart = e.pos()
            self.lineEnd = e.pos()

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

        elif ((self.mode == 3) | (self.mode == 4)) & (selectedIndex[0] >= 0) & (not self.editMode):
            objects[selectedIndex[0]].isSelected = False
            selectedIndex[0] = -1
        self.resetPoints()
        self.update()
    
    def mouseDoubleClickEvent(self, e):
        if (selectedIndex[0] < 0) :
            self.editMode = False
        if (self.mode == 4) & (not self.editMode):
            self.findObject(e.pos())
            self.editMode = True
            self.editFunc(self.editMode)

    def resizeLine(self,pos):
        objects[selectedIndex[0]].B = pos

    def resizeCircle(self, pos):
        obj = objects[selectedIndex[0]]
        objects[selectedIndex[0]].radius = math.sqrt(abs(obj.A.x() - pos.x())**2 + abs(obj.A.y() - pos.y())**2)

    def moveCircle(self,pos):
        A = QPoint(objects[selectedIndex[0]].A.x() + (pos.x() - self.lastPos.x()),objects[selectedIndex[0]].A.y() + (pos.y() - self.lastPos.y()))
        objects[selectedIndex[0]].A = A

    def moveLine(self,pos):
        A = QPoint(objects[selectedIndex[0]].A.x() + (pos.x() - self.lastPos.x()),objects[selectedIndex[0]].A.y() + (pos.y() - self.lastPos.y()))
        B = QPoint(objects[selectedIndex[0]].B.x() + (pos.x() - self.lastPos.x()),objects[selectedIndex[0]].B.y() + (pos.y() - self.lastPos.y()))
        objects[selectedIndex[0]].A = A
        objects[selectedIndex[0]].B = B

    def resetPoints(self):
        self.lineStart = QPoint()
        self.lineEnd = QPoint()

    def setMode(self,mode):
        self.resetPoints()
        print("Draw mode changed from " + str(self.mode) + " to " + str(mode))
        self.mode = mode
        if self.editMode:
            self.editMode = False
            if (selectedIndex[0] > 0) : objects[selectedIndex[0]].isSelected = False
            selectedIndex[0] = -1

    def findObject(self,pos):
        for i in range(len(objects)):
            obj = objects[i]
            if (isinstance(obj,Line)):
                if (self.checkIsOnLine(obj,pos)):
                    obj.isSelected = True
                    selectedIndex[0] = i
                    self.update()
                    break
            if (isinstance(obj,Rectangle)):
                if (self.checkIsOnRectangle(obj,pos)):
                    obj.isSelected = True
                    selectedIndex[0] = i
                    self.update()
                    break
            if (isinstance(obj,Circle)):
                if (self.checkIsOnCircle(obj,pos)):
                    obj.isSelected = True
                    selectedIndex[0] = i
                    self.update()
                    break
    
    def checkIsOnRectangle(self,obj,pos):
        width = obj.A.x() - obj.B.x()
        height = obj.A.y() - obj.B.y() 
        A = obj.A
        B = QPoint(obj.A.x() + width, obj.A.y())
        C = obj.B
        D = QPoint(obj.A.x(), obj.A.y() + height)
        a = Line(A,B)
        b = Line(B,C)
        c = Line(C,D)
        d = Line(D,A)
        res1 = self.checkIsOnLine(a,pos)
        res2 = self.checkIsOnLine(b,pos)
        res3 = self.checkIsOnLine(c,pos)
        res4 = self.checkIsOnLine(d,pos)
        return res1 | res2 | res3 | res4
    
    def checkIsOnCircle(self,obj,pos):
        radius =  math.sqrt(abs(obj.A.x() - pos.x())**2 + abs(obj.A.y() - pos.y())**2)
        return abs(round(radius) - round(obj.radius)) < 8

    def checkIsOnLine(self, obj, pos):
        if ((pos.x() > obj.A.x()) & (pos.x() > obj.B.x())) or ((pos.x() < obj.A.x()) & (pos.x() < obj.B.x())) : return False;
        if ((pos.y() > obj.A.y()) & (pos.y() > obj.B.y())) or ((pos.y() < obj.A.y()) & (pos.y() < obj.B.y())) : return False;
        ABx = abs(obj.A.x() - obj.B.x())
        ABy = abs(obj.A.y() - obj.B.y())
        ACx = abs(obj.A.x() - pos.x())
        ACy = abs(obj.A.y() - pos.y())
        BCx = abs(obj.B.x() - pos.x())
        BCy = abs(obj.B.y() - pos.y())
        if (ABx == 0) & (ACx == 0) & (BCx == 0): return True
        if (ABy == 0) & (ACy == 0) & (BCy == 0): return True
        if (ABy != 0) :ab = round(abs(obj.A.x() - obj.B.x()) / abs(obj.A.y() - obj.B.y()))
        else : ab = 0
        if (ACy != 0) :ac = round(abs(obj.A.x() - pos.x()) / abs(obj.A.y() - pos.y()))
        else : ac = 0
        if (BCy != 0) :bc = round(abs(pos.x() - obj.B.x()) / abs(pos.y() - obj.B.y()))
        else : bc = 0
        print(str(ab) + " " + str(ac) + " "+ str(bc))
        return (abs(ab - ac) < 8) & (abs(ab - bc) < 8) & (abs(ac - bc) < 8)
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
        self.painter = Painter('white', self.editShape)
        self.layout.addWidget(self.painter,0,0,1,5)
        self.toolbox = Toolbox(3,self.painter, False);
        self.layout.addWidget(self.toolbox,0,6,1,1)

        self.addToolBar(Toolbar(self.onMyToolBarButtonClick))
        self.setStatusBar(QStatusBar(self))
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.label = QLabel("Click in this window")
        self.label.move(320, 20)

    def editShape(self, isEditMode):
        obj = objects[selectedIndex[0]]
        self.layout.removeWidget(self.toolbox)
        if (isinstance(obj,Line)):
            self.setToolBox(0,isEditMode)
        elif (isinstance(obj,Rectangle)):
            self.setToolBox(1,isEditMode)
        elif (isinstance(obj,Circle)):
            self.setToolBox(2,isEditMode)

    def onMyToolBarButtonClick(self, s):
        self.layout.removeWidget(self.toolbox)
        if (self.sender().text() == "Line"):
            self.setToolBoxWithPainter(0)
        elif (self.sender().text() == "Rectangle"):
            self.setToolBoxWithPainter(1)
        elif (self.sender().text() == "Circle"):
            self.setToolBoxWithPainter(2)
        elif (self.sender().text() == "Move"):
            self.setToolBoxWithPainter(-1)
            self.painter.setMode(3)
        elif (self.sender().text() == "Edit"):
            self.setToolBoxWithPainter(-1)
            self.painter.setMode(4)
        elif (self.sender().text() == "Clear"):
            self.setToolBoxWithPainter(-1)
            self.clearScreen()
        elif (self.sender().text() == "Save"):
            self.setToolBoxWithPainter(-1)
            self.saveFile()
        elif (self.sender().text() == "Open"):
            self.setToolBoxWithPainter(-1)
            self.openFile()

    def setToolBox(self,mode,isEditMode):
        self.toolbox = Toolbox(mode,self.painter,isEditMode);
        self.layout.addWidget(self.toolbox,0,6,1,1)

    def setToolBoxWithPainter(self,mode):
        self.painter.setMode(mode)
        self.toolbox = Toolbox(mode,self.painter,False);
        self.layout.addWidget(self.toolbox,0,6,1,1)

    def clearScreen(self):
        objects.clear()
        selectedIndex[0] = -1
        self.painter.update()

    def saveFile(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
            "JSON(*.json) ")
 
        if filePath == "":
            return        

    def openFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, 'Open File', "",
            "JSON(*.json) ")
 
        if filePath == "":
            return         
        
if __name__=='__main__':
        app=QApplication(sys.argv)
        painter=MainWindow()
        painter.show()
        app.exec()