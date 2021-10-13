from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys
import math
from dataclasses import dataclass
import json
from array import array

objects = []
selectedIndex = []
isAPoint = [False]
brushSize = 8
toolboxColor = QColor("gray")

class Point:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def __str__(self):
         return "X:" + str(self.x) + " Y:" + str(self.y)

    def to_object(d):
        return Point(d['x'], d['y'])
    
    def to_dict(o):
        if isinstance(o, Point):
            dict = {
                "x": o.x,
                "y": o.y,
                "__class__": 'Point'
            }
            return dict
class Shape:
    def __init__(self, A):
        self.A = A
    def __str__(self):
        return str(self.A)
    def to_object(d):
        return Shape(Point.to_object(d['A']))
            
    def to_dict(o):
        if isinstance(o, Shape):
            dict = {
                "A": Point.to_dict(o.A),
                "__class__": 'Shape'
            }
            return dict 
class Line(Shape):
    def __init__(self, A, B, isSelected = False, color = Qt.red):
        super().__init__(A)
        self.B = B
        self.isSelected = isSelected
        self.color = color
    def __str__(self):
        return "A:" + str(self.A) + " B:" + str(self.B)
    def to_object(d):
        return Line(Point.to_object(d['A']), Point.to_object(d['B']))
    def to_dict(o):
        if isinstance(o, Line):
            dict = {
                "A": Point.to_dict(o.A),
                "B": Point.to_dict(o.B),
                "__class__": 'Line'
            }
            return dict 
class Rectangle(Shape):
    def __init__(self, A, B, isSelected = False, color = Qt.green):
        super().__init__(A)
        self.B = B
        self.isSelected = isSelected
        self.color = color
    def __str__(self):
        return "A:" + str(self.A) + " B:" + str(self.B)
    def to_object(d):
        return Rectangle(Point.to_object(d['A']), Point.to_object(d['B']))
    def to_dict(o):
        if isinstance(o, Rectangle):
            dict = {
                "A": Point.to_dict(o.A),
                "B": Point.to_dict(o.B),
                "__class__": 'Rectangle'
            }
            return dict 
class Circle(Shape):
    def __init__(self, A, radius, isSelected = False, color = Qt.blue):
        super().__init__(A)
        self.radius = radius
        self.isSelected = isSelected
        self.color = color
    def __str__(self):
        return "Center:" + str(self.A) + " radius:" + str(self.radius)
    def to_object(d):
        return Circle(Point.to_object(d['A']), d['radius'])
    def to_dict(o):
        if isinstance(o, Circle):
            dict = {
                "A": Point.to_dict(o.A),
                "radius": o.radius,
                "__class__": 'Circle'
            }
            return dict 
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
            self.createPoint("Point A:", obj.A.x, obj.A.y)
            self.createPoint("Point B:", obj.B.x, obj.B.y)
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
            self.createPoint("Point A:", obj.A.x, obj.A.y)
            self.createPoint("Point B:", obj.B.x, obj.B.y)
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
            self.createPoint("Center:", obj.A.x, obj.A.y)
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
            A = Point(float(self.inputs[0].text().replace(",",".")),float(self.inputs[1].text().replace(",",".")))
            B = Point(float(self.inputs[2].text().replace(",",".")),float(self.inputs[3].text().replace(",",".")))
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
            A = Point(float(self.inputs[0].text().replace(",",".")),float(self.inputs[1].text().replace(",",".")))
            B = Point(float(self.inputs[2].text().replace(",",".")),float(self.inputs[3].text().replace(",",".")))
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
            A = Point(float(self.inputs[0].text().replace(",",".")),float(self.inputs[1].text().replace(",",".")))
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
                painter.drawLine(QPoint(obj.A.x,obj.A.y), QPoint(obj.B.x,obj.B.y))
            if (isinstance(obj,Rectangle)):
                painter.drawRect(QRect(QPoint(obj.A.x,obj.A.y), QPoint(obj.B.x,obj.B.y)))
            if (isinstance(obj,Circle)):
                painter.drawEllipse(QPoint(obj.A.x,obj.A.y),obj.radius,obj.radius)

        if (not self.lineStart.isNull() and not self.lineEnd.isNull()) & self.isDrawing:
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
        elif (self.mode == 4) & (selectedIndex[0] >= 0) & (not self.editMode) :
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
        if (self.mode == 3) & (not self.editMode) & (e.button() == Qt.LeftButton):
            self.findObject(e.pos(), False)
            self.lastPos = e.pos()
        elif (self.mode == 4) & (e.button() == Qt.LeftButton) & (not self.editMode):
            self.findObject(e.pos(), True)
        elif e.button() == Qt.LeftButton:
            self.isDrawing = True;
            self.lineStart = e.pos()
            self.lineEnd = e.pos()
        if e.button() == Qt.RightButton:
            print(e.pos())
        if e.button() == Qt.MiddleButton:
            print(objects)

    def mouseReleaseEvent(self, e):
        if self.isDrawing & (e.button() == Qt.LeftButton):
            if (self.mode == 0):
                A = Point(self.lineStart.x(),self.lineStart.y())
                B = Point(self.lineEnd.x(),self.lineEnd.y())
                line = Line(A,B)
                if ((abs(A.x - B.x) <= brushSize/2) & (abs(A.y - B.y) <= brushSize/2)):
                    button = QMessageBox.critical(
                        self,
                        "Invalid input!",
                        "Points must not be on the same place",
                        buttons=QMessageBox.Ignore,
                        defaultButton=QMessageBox.Ignore,
                    )
                    return
                objects.append(line)
            elif (self.mode == 1) & (e.button() == Qt.LeftButton):
                A = Point(self.lineStart.x(),self.lineStart.y())
                B = Point(self.lineEnd.x(),self.lineEnd.y())
                rectangle = Rectangle(A,B)
                if ((abs(A.x - B.x) <= brushSize/2) & (abs(A.y - B.y) <= brushSize/2)):
                    button = QMessageBox.critical(
                        self,
                        "Invalid input!",
                        "Points must not be on the same place",
                        buttons=QMessageBox.Ignore,
                        defaultButton=QMessageBox.Ignore,
                    )
                    return
                objects.append(rectangle)
            elif (self.mode == 2) & (e.button() == Qt.LeftButton):
                A = Point(self.lineStart.x(),self.lineStart.y())
                radius = math.sqrt(abs(self.lineStart.x() - self.lineEnd.x())**2 + abs(self.lineStart.y() - self.lineEnd.y())**2)
                circle = Circle(A,radius)
                if (radius == 0):
                    button = QMessageBox.critical(
                        self,
                        "Invalid input!",
                        "Radius cannot equals 0",
                        buttons=QMessageBox.Ignore,
                        defaultButton=QMessageBox.Ignore,
                    )
                    return
                objects.append(circle)
            self.isDrawing = False;

        elif ((self.mode == 3) | (self.mode == 4)) & (selectedIndex[0] >= 0) & (not self.editMode) & (e.button() == Qt.LeftButton):
            objects[selectedIndex[0]].isSelected = False
            selectedIndex[0] = -1
        self.resetPoints()
        self.update()
        isAPoint[0] = False
    
    def mouseDoubleClickEvent(self, e):
        if (selectedIndex[0] < 0) & (e.button() == Qt.LeftButton):
            self.editMode = False
        if (self.mode == 4) & (not self.editMode) & (e.button() == Qt.LeftButton):
            res = self.findObject(e.pos(),False)
            if res:
                self.editMode = True
                self.editFunc(self.editMode)

    def resizeLine(self,pos):
        if isAPoint[0]: 
            objects[selectedIndex[0]].A = Point(pos.x(),pos.y())
        else : objects[selectedIndex[0]].B = Point(pos.x(),pos.y())

    def resizeCircle(self, pos):
        obj = objects[selectedIndex[0]]
        objects[selectedIndex[0]].radius = math.sqrt(abs(obj.A.x - pos.x())**2 + abs(obj.A.y - pos.y())**2)

    def moveCircle(self,pos):
        A = Point(objects[selectedIndex[0]].A.x + (pos.x() - self.lastPos.x()),objects[selectedIndex[0]].A.y + (pos.y() - self.lastPos.y()))
        objects[selectedIndex[0]].A = A

    def moveLine(self,pos):
        A = Point(objects[selectedIndex[0]].A.x + (pos.x() - self.lastPos.x()),objects[selectedIndex[0]].A.y + (pos.y() - self.lastPos.y()))
        B = Point(objects[selectedIndex[0]].B.x + (pos.x() - self.lastPos.x()),objects[selectedIndex[0]].B.y + (pos.y() - self.lastPos.y()))
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

    def findObject(self,pos, isEditMode):
        for i in range(len(objects)):
            obj = objects[i]
            res = False
            if (isinstance(obj,Line)):
                if (self.checkIsOnLine(obj,pos)):
                    res = True
            elif (isinstance(obj,Rectangle)):
                if (self.checkIsOnRectangle(obj,pos)):
                    res = True
            elif (isinstance(obj,Circle)):
                if (self.checkIsOnCircle(obj,pos)):
                    res = True
            if (res):
                if isEditMode & (not self.checkIsOnDistinctivePoint(obj,pos)): return False
                obj.isSelected = True
                selectedIndex[0] = i
                self.update()
                return True
        return False
    
    def checkIsOnDistinctivePoint(self,obj,pos):
        if (isinstance(obj,Line)):
            if (self.checkIsNearA(obj,pos)):
                isAPoint[0] = True
            else:
                isAPoint[0] = False
            return True
        elif (isinstance(obj,Rectangle)):
            if (self.checkIsOnPoint(obj.A,pos)):
                isAPoint[0] = True
                return True
            elif self.checkIsOnPoint(obj.B,pos):
                isAPoint[0] = False
                return True        
        elif (isinstance(obj,Circle)):
            return True
        return False

    def checkIsNearA(self, obj, pos):
        return self.distanceToPoint(obj.A, Point(pos.x(), pos.y())) < self.distanceToPoint(obj.B, Point(pos.x(), pos.y()))

    def distanceToPoint(self,pointA, pointB):
        return math.sqrt(abs(pointA.x - pointB.x)**2 + abs(pointA.y - pointB.y)**2)

    def checkIsOnPoint(self, point, pos):
        return (pos.x() >= (point.x - brushSize/2)) & (pos.x() <= (point.x + brushSize/2)) & (pos.y() >= (point.y - brushSize/2)) & (pos.y() <= (point.y + brushSize/2))
    
    def checkIsOnRectangle(self,obj,pos):
        minX = min(obj.A.x, obj.B.x)
        maxX = max(obj.A.x, obj.B.x)        
        minY = min(obj.A.y, obj.B.y)
        maxY = max(obj.A.y, obj.B.y)
        if not ((self.checkBetweenLines(minX - (brushSize/2), maxX + (brushSize/2), pos.x())) & (self.checkBetweenLines(minY - (brushSize/2), maxY + (brushSize/2), pos.y()))): return False
        return (abs(pos.x() - obj.A.x) <= brushSize/2) | (abs(pos.x() - obj.B.x) <= brushSize/2) | (abs(pos.y() - obj.A.y) < brushSize/2) | (abs(pos.y() - obj.B.y) < brushSize/2)
    
    def checkBetweenLines(self,line1,line2,current):
        return (current >= line1) & (current <= line2)

    def checkIsOnCircle(self,obj,pos):
        radius =  math.sqrt(abs(obj.A.x - pos.x())**2 + abs(obj.A.y - pos.y())**2)
        return abs(round(radius) - round(obj.radius)) < 8

    def checkIsOnLine(self, obj, pos):
        # FIRST: check if is between A and B
        minX = min(obj.A.x, obj.B.x)
        maxX = max(obj.A.x, obj.B.x)        
        minY = min(obj.A.y, obj.B.y)
        maxY = max(obj.A.y, obj.B.y)
        if not ((self.checkBetweenLines(minX - (brushSize/2), maxX + (brushSize/2), pos.x())) & (self.checkBetweenLines(minY - (brushSize/2), maxY + (brushSize/2), pos.y()))): return False
        print(obj,pos)

        # SECOND: count distance between points
        ABx = abs(obj.A.x - obj.B.x)
        ABy = abs(obj.A.y - obj.B.y)
        ACx = abs(obj.A.x - pos.x())
        ACy = abs(obj.A.y - pos.y())
        BCx = abs(obj.B.x - pos.x())
        BCy = abs(obj.B.y - pos.y())

        # THIRD: if A and B have the same X or Y then C also have to have the same coord +/- brushSize/2
        if (ABx == 0) : return (ACx < brushSize / 2) & (BCx < brushSize / 2)
        if (ABy == 0) : return (ACy < brushSize / 2) & (BCy < brushSize / 2)
        if (ACx == 0) | (ACy == 0) | (BCx == 0) | (BCy == 0) : return False

        ab = round(ABx / ABy)
        ac = round(ACx / ACy)
        bc = round(BCx / BCy)

        print(str(ab) + " " + str(ac) + " "+ str(bc))
        return (abs(ab - ac) == 0) & (abs(ab - bc) == 0) & (abs(ac - bc) == 0)
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
        
        if not filePath.__contains__('.json'): filePath += '.json'
        jsonString = json.dumps(objects, cls=ShapesEncoder)

        print(jsonString)
        file = open(filePath, 'w')
        file.write(jsonString)
        file.close()

    def openFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, 'Open File', "",
            "JSON(*.json) ")
 
        if filePath == "":
            return         
        
        file = open(filePath,'r')
        objects.clear()
        data = json.load(file)
        print(data)
        for obj in data:
            if obj['__class__'] == 'Line':
                objects.append(Line.to_object(obj))
            elif obj['__class__'] == 'Circle':
                objects.append(Circle.to_object(obj))
            elif obj['__class__'] == 'Rectangle':
                objects.append(Rectangle.to_object(obj))
        self.painter.update()


class ShapesEncoder(json.JSONEncoder):
     
    def default(self, obj):
        if isinstance(obj, Line):
            return Line.to_dict(obj)
        elif (isinstance(obj,Rectangle)):
            return Rectangle.to_dict(obj)
        elif (isinstance(obj,Circle)):
            return Circle.to_dict(obj)

if __name__=='__main__':
        app=QApplication(sys.argv)
        painter=MainWindow()
        painter.show()
        app.exec()