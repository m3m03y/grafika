import sys
from typing import Any
# from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
import matplotlib
import math
import json
import numpy as np
matplotlib.use('Qt5Agg')

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from scipy.special import comb

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from matplotlib.backend_bases import MouseButton

toolboxColor = QColor("gray")
MIN_VAL = -10
MAX_VAL = 10
class Toolbar(QToolBar):
    def __init__(self, btnClick):
        super(Toolbar, self).__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, Qt.gray)
        self.setPalette(palette)
        self.buttons = {
            "Create" : "Create figure",
            "Move" : "Move figure",
            "Rotate" : "Rotate figure",
            "Scale" : "Scale figure",
            "Clear" : "Clear",
            "Save" : "Save figure",
            "Open" : "Open figure"
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

class CreateInput(QWidget):
    def __init__(self, addPoint, parent = None):
        super(CreateInput, self).__init__()
        self.row_size = 1
        self.points = []
        self.parent = parent
        if (parent == None): self.parent = self
        
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, toolboxColor)
        self.setPalette(palette)
            
        self.addPointAction = addPoint
        self.layout = QVBoxLayout()
        self.table = QTableView()
        self.model = QStandardItemModel(self.row_size,2,self)
        self.model.setHorizontalHeaderLabels(['x', 'y'])
        self.model.dataChanged.connect(self.__update)
        self.table.setModel(self.model)
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
    
    def __update(self):
        self.points = self.readTable()
        if (self.points == None):
            return
        self.__updateModel()
        self.addPointAction(self.points)
        
    def __updateModel(self):
        self.row_size = 0
        self.model = QStandardItemModel(0,2,self)
        for i in range(len(self.points)):
            self.model.insertRow(i)
            self.row_size += 1
            for j in range(len(self.points[i])):
                val = self.points[i][j]
                self.model.setData(self.model.index(i,j), float(val))
        self.model.insertRow(self.row_size)
        self.model.dataChanged.connect(self.__update)
        self.table.setModel(self.model)

    def setPoints(self,points):
        self.points = points
        self.__updateModel()
        
    def readTable(self):
        table_data = []
        model = self.table.model()
        if (model.columnCount() != 2):
            print("Invalid column number")
            return

        for row in range(model.rowCount()):
            table_data.append([])
            for column in range(model.columnCount()):
                index = model.index(row, column)
                val = model.data(index)
                try:
                    str(val).replace(',','.')
                    table_data[row].append(float(val))
                except TypeError: 
                    if (val != None): 
                        self.parent.showErrorMessage("Points coordinates must be numbers", "Invalid value")
                    return None
                    table_data[row].append(float(0.0))
                except ValueError:
                    if (val != None): 
                        self.parent.showErrorMessage("Points coordinates must be numbers", "Invalid value")
                    return None
        return table_data

class MoveInput(QWidget):
    def __init__(self, updatePoints, parent = Any):
        super(MoveInput, self).__init__()
        self.updatePointsAction = updatePoints
        self.parent = parent
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, toolboxColor)
        self.setPalette(palette)
        
        self.layout = QFormLayout()
        self.header = QLabel("Vector")
        self.layout.addRow(self.header)
        self.xIn = self.__initInput("X: ")
        self.yIn = self.__initInput("Y: ")
        self.layout.addRow(self.xIn[0],self.xIn[1])
        self.layout.addRow(self.yIn[0],self.yIn[1])
        submitBtn = QPushButton("Submit")
        submitBtn.clicked.connect(self.__onSubmitClicked)        
        self.layout.addRow(submitBtn)
        self.setLayout(self.layout)
        
    def __initInput(self,name):
        label = QLabel(name)
        value = QDoubleSpinBox()
        value.setDecimals(3)
        value.setMaximum(MAX_VAL)            
        value.setMinimum(MIN_VAL)            
        value.setSingleStep(1.0)
        return (label,value)

    def __onSubmitClicked(self):
        x = self.xIn[1].value()
        y = self.yIn[1].value()
        self.updatePointsAction([x,y])
        self.parent.savePoints()
    
    def setVector(self,pos):
        self.xIn[1].setValue(pos[0])
        self.yIn[1].setValue(pos[1])
        self.update()

class RotateInput(QWidget):
    def __init__(self, updatePoints, parent = Any):
        super(RotateInput, self).__init__()
        self.updatePointsAction = updatePoints
        self.parent = parent
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, toolboxColor)
        self.setPalette(palette)
        
        self.layout = QFormLayout()
        self.header = QLabel("Vector")
        self.layout.addRow(self.header)
        self.xIn = self.__initInput("X: ")
        self.yIn = self.__initInput("Y: ")
        self.layout.addRow(self.xIn[0],self.xIn[1])
        self.layout.addRow(self.yIn[0],self.yIn[1])
        self.angle_label = QLabel("Angle: ")
        self.layout.addRow(self.angle_label,self.__initAngleInput())
        submitBtn = QPushButton("Submit")
        submitBtn.clicked.connect(self.__onSubmitClicked)        
        self.layout.addRow(submitBtn)
        self.setLayout(self.layout)
    
    def setAngle(self,pos,angle):
        self.angle_input.setValue(self.__toDegrees(angle))
        self.xIn[1].setValue(pos[0])
        self.yIn[1].setValue(pos[1])
        self.update()
        
    def __initAngleInput(self):
        self.angle_input = QSpinBox()
        self.angle_input.setMaximum(360)            
        self.angle_input.setMinimum(-360)            
        self.angle_input.setSingleStep(1)
        return self.angle_input
        
    def __initInput(self,name):
        label = QLabel(name)
        value = QDoubleSpinBox()
        value.setDecimals(3)
        value.setMaximum(MAX_VAL)            
        value.setMinimum(MIN_VAL)            
        value.setSingleStep(1.0)
        return (label,value)

    def __onSubmitClicked(self):
        x = self.xIn[1].value()
        y = self.yIn[1].value()
        angle = self.angle_input.value()
        angle = self.__toRadians(angle)
        self.updatePointsAction([x,y],angle)
        self.parent.setWaypoint([x,y])
        self.parent.savePoints()
        
    def __toRadians(self,angle):
        return angle*math.pi/180
    
    def __toDegrees(self,angle):
        return angle * 180 / math.pi
    
class ScaleInput(QWidget):
    def __init__(self, updatePoints, parent = Any):
        super(ScaleInput, self).__init__()
        self.updatePointsAction = updatePoints
        self.parent = parent
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, toolboxColor)
        self.setPalette(palette)
        
        self.layout = QFormLayout()
        self.header = QLabel("Vector")
        self.layout.addRow(self.header)
        self.xIn = self.__initInput("X: ",MIN_VAL,MAX_VAL)
        self.yIn = self.__initInput("Y: ",MIN_VAL,MAX_VAL)
        self.layout.addRow(self.xIn[0],self.xIn[1])
        self.layout.addRow(self.yIn[0],self.yIn[1])
        self.scaleXIn = self.__initInput("Scale X: ",0,10)
        self.scaleYIn = self.__initInput("Scale Y: ",0,10)
        self.layout.addRow(self.scaleXIn[0],self.scaleXIn[1])
        self.layout.addRow(self.scaleYIn[0],self.scaleYIn[1])
        submitBtn = QPushButton("Submit")
        submitBtn.clicked.connect(self.__onSubmitClicked)        
        self.layout.addRow(submitBtn)
        self.setLayout(self.layout)
    
    def setScale(self,pos,scale):
        self.xIn[1].setValue(pos[0])
        self.yIn[1].setValue(pos[1])        
        self.scaleXIn[1].setValue(scale[0])
        self.scaleYIn[1].setValue(scale[1])
        self.update()
        
    def __initInput(self,name, minVal, maxVal):
        label = QLabel(name)
        value = QDoubleSpinBox()
        value.setDecimals(3)
        value.setMaximum(maxVal)            
        value.setMinimum(minVal)            
        value.setSingleStep(1.0)
        return (label,value)

    def __onSubmitClicked(self):
        x = self.xIn[1].value()
        y = self.yIn[1].value()
        scaleX = self.scaleXIn[1].value()
        scaleY = self.scaleYIn[1].value()
        self.updatePointsAction([x,y],[scaleX,scaleY])
        self.parent.setWaypoint([x,y])
        self.parent.savePoints()
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, setPoints, translatePoints, rotatePoints, scalePoints, parent=None, width=5, height=4, dpi=100):
        self.points = []
        self.parent = parent
        self.mode = -1
        self.selectedIdx = -1
        self.original_position = None
        self.waypoint = [0,0]
        
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig.canvas.callbacks.connect('button_press_event', self.__on_click)
        self.fig.canvas.callbacks.connect('button_release_event', self.__on_release)
        self.fig.canvas.callbacks.connect('motion_notify_event', self.__move_obj)
        self.setPointsAction = setPoints
        self.translatePointsAction = translatePoints
        self.rotatePointsAction = rotatePoints
        self.scalePointsAction = scalePoints
        super(MplCanvas, self).__init__(self.fig)

    def __move_obj(self, event):
        if (self.mode >= 1) and (self.selectedIdx >= 0):
            try:
                difX = event.xdata - self.original_position[0]
                difY = event.ydata - self.original_position[1]
                if (self.mode == 1):
                    self.translatePointsAction([difX,difY])        
                elif (self.mode == 2):
                    angle = self.__calculateAngleBetweenPoints([event.xdata,event.ydata],self.original_position)
                    self.parent.setAngle([difX,difY],angle)
                    self.rotatePointsAction(self.waypoint,angle)
                elif (self.mode == 3):
                    scale = self.__calculateScale([event.xdata,event.ydata],self.original_position,self.waypoint);
                    self.scalePointsAction(self.waypoint,scale)
            except TypeError:
                return
            
    def __on_click(self,event):
        if (event.button is MouseButton.LEFT) and self.mode == 0:
            self.points.append([event.xdata, event.ydata])
            self.drawFigure()
            if (self.points != None):
                self.setPointsAction(self.points)
        elif (event.button is MouseButton.LEFT) and self.mode >= 1:
            self.__checkIfOnFigure([event.xdata, event.ydata])        
        elif (event.button is MouseButton.RIGHT) and (self.mode >= 2):
            self.waypoint = [event.xdata, event.ydata]
            self.drawFigure()

    def __on_release(self,event):
        if (event.button is MouseButton.LEFT) and self.mode >= 1:
            self.selectedIdx = -1
            self.original_position = None
            self.parent.savePoints()
            self.drawFigure()
            
    def __checkIfOnFigure(self,pos):
        for i in range(len(self.points)):
            p = self.points[i]
            if (abs(p[0] - pos[0]) <= 0.1) and (abs(p[1]-pos[1])<= 0.1):
                self.selectedIdx = i
                self.original_position = self.points[i]
                self.drawFigure()
                return True
        return False
        
    def __calculateFigure(self):
        x_arr = []
        y_arr = []
        if (self.points == None) or (len(self.points) == 0): return None
        for i in self.points:
            x_arr.append(i[0])
            y_arr.append(i[1])
        x_arr.append(self.points[0][0])
        y_arr.append(self.points[0][1])
        return (x_arr,y_arr)

    def __calculateAngleBetweenPoints(self, pointA, pointB):
        ang1 = np.arctan2(*pointA[::-1])
        ang2 = np.arctan2(*pointB[::-1])
        angle = (ang1 - ang2) % (2 * np.pi)
        return angle
    
    def __calculateScale(self,pointA,pointB, center):
        if (pointB[0] == center[0]):
            xscale = 1
        else: xscale = (pointA[0] - center[0]) / (pointB[0] - center[0]) #TODO: do ABSOLUTE value needed?
        if (pointB[1] == center[1]):
            yscale = 1
        else: yscale = (pointA[1] - center[1]) / (pointB[1] - center[1])
        return (xscale, yscale)
                
    def setWaypoint(self,waypoint):
        self.waypoint = waypoint
        self.drawFigure()
        
    def setMode(self, mode):
        self.mode = mode
        
    def setPoints(self,points):
        self.points = points
        self.drawFigure()
        
    def drawFigure(self):
        self.axes.clear()

        self.axes.set_xlim(MIN_VAL,MAX_VAL)
        self.axes.set_ylim(MIN_VAL,MAX_VAL)
        
        if (self.points == None) or (len(self.points) <= 0):
            self.fig.canvas.draw()
            return
        
        to_plot_x, to_plot_y = self.__calculateFigure()

        x = [i[0] for i in self.points]
        y = [i[1] for i in self.points]
            
        self.axes.plot(
            to_plot_x,
            to_plot_y,
            color="blue",
            label="Figure",
        )
        
        self.axes.scatter(x, y, color="red", label="Vertex")
        if (self.selectedIdx >= 0):
            self.axes.scatter(self.points[self.selectedIdx][0], self.points[self.selectedIdx][1], color="green", label="Selected")
        if (self.mode == 2) or (self.mode == 3):
            self.axes.scatter(self.waypoint[0], self.waypoint[1], color="cyan", label="Waypoint")
        self.fig.canvas.draw()

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.points = []
        self.setAutoFillBackground(True)
        self.mode = -1
        self.table = None
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
        self.addToolBar(Toolbar(self.__changeMode))
        
        self.painter = MplCanvas(self.__setPoints, self.__translatePoints, self.__rotatePoints, self.__scalePoints, self, width=10, height=10, dpi=100)
        self.painter.drawFigure()
        
        self.toolbox = QWidget()
        self.toolbox_layout = QVBoxLayout()
        self.toolbox.setLayout(self.toolbox_layout)
        
        self.layout.addWidget(self.painter,0,0,1,5)
        self.layout.addWidget(self.toolbox,0,6,1,1)
        
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        self.show()

    def __changeMode(self, s):
        self.__clearToolbox()
        self.painter.setMode(-1)
        if (self.mode <= 0):
            self.original = [i for i in self.points]
            
        if (self.sender().text() == "Create"):
            self.mode = 0
            self.painter.setMode(0)
            self.table = CreateInput(self.__setPoints,self)
            self.__setPoints(self.points)
            self.toolbox_layout.addWidget(self.table)
        elif (self.sender().text() == "Move"):
            self.mode = 1
            self.painter.setMode(1)
            self.move_input = MoveInput(self.__translatePoints,self)
            self.toolbox_layout.addWidget(self.move_input)
        elif (self.sender().text() == "Rotate"):
            self.mode = 2
            self.painter.setMode(2)
            self.rotate_input = RotateInput(self.__rotatePoints,self)
            self.toolbox_layout.addWidget(self.rotate_input)
        elif (self.sender().text() == "Scale"):
            self.mode = 3
            self.painter.setMode(3)
            self.scale_input = ScaleInput(self.__scalePoints,self)
            self.toolbox_layout.addWidget(self.scale_input)
        elif (self.sender().text() == "Clear"):
            self.__setPoints([])
            self.mode = -1        
        elif (self.sender().text() == "Save"):
            self.__saveFile()
            self.mode = -2        
        elif (self.sender().text() == "Open"):
            self.__openFile()
            self.__setPoints(self.points)
            self.mode = -3
        print('Set to {} mode'.format(self.mode))

        self.toolbox.update()
        self.update()
    
    def __clearToolbox(self):
        if (self.toolbox_layout.count() > 0):
            self.toolbox_layout.itemAt(0).widget().deleteLater()

    def showErrorMessage(self, msg, title):
        QMessageBox.critical(
            self,
            title,
            msg,
            buttons=QMessageBox.Ignore,
            defaultButton=QMessageBox.Ignore,
        )
    
    def setWaypoint(self,waypoint):
        self.painter.setWaypoint(waypoint)    
        
    def setAngle(self,vector,angle):
        self.rotate_input.setAngle(vector,angle)
    
    def savePoints(self):
        self.original = [i for i in self.points]

    def setVector(self,vector):
        self.move_input.setVector(vector)
    
    def setScale(self,vector,scale):
        self.scale_input.setScale(vector,scale)
        
    def __setPoints(self, points):
        self.points = points
        self.painter.setPoints(points)
        if (self.mode == 0):
            self.table.setPoints(points)
    
    def __translatePoints(self,vector):
        self.setVector(vector)
        newPoints = []
        for i in self.original:
            newPoints.append([i[0] + vector[0], i[1] + vector[1]])
        self.__setPoints(newPoints)      
    
    def __rotatePoints(self,vector, angle):
        newPoints = []
        for i in self.original:
            x, y = i
            xr, yr = vector
            x_new = xr + (x-xr)*math.cos(angle)-(y-yr)*math.sin(angle)
            y_new = yr + (x-xr)*math.sin(angle)+(y-yr)*math.cos(angle)
            newPoints.append([x_new,y_new])
        self.__setPoints(newPoints)    
    
    def __scalePoints(self,vector, scale):
        self.setScale(vector,scale)
        newPoints = []
        for i in self.original:
            x, y = i
            xf, yf = vector
            x_new = xf + (x-xf)*scale[0]
            y_new = yf + (y-yf)*scale[1]
            newPoints.append([x_new,y_new])
        self.__setPoints(newPoints)    
        
    def __saveFile(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
            "JSON(*.json) ")
 
        if filePath == "":
            return        
        
        if not filePath.__contains__('.json'): filePath += '.json'
        jsonString = json.dumps(self.points)

        file = open(filePath, 'w')
        file.write(jsonString)
        file.close()

    def __openFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, 'Open File', "",
            "JSON(*.json) ")
 
        if filePath == "":
            return         
        
        file = open(filePath,'r')
        self.points = []
        data = json.load(file)
        for obj in data:
            self.points.append(obj)
        self.painter.update()
        
if __name__=='__main__':
        app=QApplication(sys.argv)
        window=MainWindow()
        app.exec_()
