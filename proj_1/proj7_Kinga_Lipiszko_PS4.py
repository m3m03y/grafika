import sys
# from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
import matplotlib

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
CANVAS_WIDTH = 10
CANVAS_HEIGHT = 10

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
            "Clear" : "Clear"
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
            self.parent.showErrorMessage("Points coordinates must be numbers", "Invalid value")
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
                try:
                    val = str(model.data(index)).replace(',','.')
                    table_data[row].append(float(val))
                except TypeError: 
                    return None
                except ValueError:
                    return None
        return table_data

class MoveInput(QWidget):
    def __init__(self):
        super(MoveInput, self).__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, toolboxColor)
        self.setPalette(palette)
        
        self.layout = QVBoxLayout()
        self.test = QLabel("Move")
        self.layout.addWidget(self.test)
        self.setLayout(self.layout)

class RotateInput(QWidget):
    def __init__(self):
        super(RotateInput, self).__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, toolboxColor)
        self.setPalette(palette)
        
        self.layout = QVBoxLayout()
        self.test = QLabel("Rotate")
        self.layout.addWidget(self.test)
        self.setLayout(self.layout)
        
class ScaleInput(QWidget):
    def __init__(self):
        super(ScaleInput, self).__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, toolboxColor)
        self.setPalette(palette)
        
        self.layout = QVBoxLayout()
        self.test = QLabel("Scale")
        self.layout.addWidget(self.test)
        self.setLayout(self.layout)

# class Painter(QWidget):
#     def __init__(self):
#         super(Painter, self).__init__()

#         self.image = QImage(self.size(), QImage.Format_RGB32)
        
#     def paintEvent(self, event):
#         painter = QPainter(self)
#         painter.setPen(QPen(Qt.red,  10, Qt.SolidLine))
#         painter.drawLine(QPoint(200,200),QPoint(300,300))

#     def mouseMoveEvent(self, e):
#         ...

#     def mousePressEvent(self, e):
#         print("pressed")

#     def mouseReleaseEvent(self, e):
#         ...
    
#     def mouseDoubleClickEvent(self, e):
#         ...

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, setPoints, parent=None, width=5, height=4, dpi=100):
        self.points = []
        self.parent = parent
        self.createMode = False
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig.canvas.callbacks.connect('button_press_event', self.__on_click)
        self.fig.canvas.callbacks.connect('motion_notify_event', self.__move_obj)
        self.setPointsAction = setPoints
        super(MplCanvas, self).__init__(self.fig)

    def __move_obj(self, event):
        ...

    def __on_click(self,event):
        if (event.button is MouseButton.LEFT) and self.createMode:
            self.points.append([event.xdata, event.ydata])
            self.drawFigure()
            if (self.points != None):
                self.setPointsAction(self.points)

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

    def setMode(self, mode):
        self.createMode = mode
        
    def setPoints(self,points):
        self.points = points
        self.drawFigure()
        
    def clear(self):
        self.drawFigure()
        
    def drawFigure(self):
        self.axes.clear()

        self.axes.set_xlim(0,CANVAS_WIDTH)
        self.axes.set_ylim(0,CANVAS_HEIGHT)
        
        if (self.points == None) or (len(self.points) <= 0):
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
        
        self.painter = MplCanvas(self.__setPoints, self, width=10, height=10, dpi=100)
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
        self.painter.setMode(False)
        if (self.sender().text() == "Create"):
            self.painter.setMode(True)
            self.table = CreateInput(self.__setPoints,self)
            self.toolbox_layout.addWidget(self.table)
            self.mode = 0
        elif (self.sender().text() == "Move"):
            self.toolbox_layout.addWidget(MoveInput())
            self.mode = 1
        elif (self.sender().text() == "Rotate"):
            self.toolbox_layout.addWidget(RotateInput())
            self.mode = 2
        elif (self.sender().text() == "Scale"):
            self.toolbox_layout.addWidget(ScaleInput())
            self.mode = 3
        elif (self.sender().text() == "Clear"):
            self.__setPoints([])
            self.mode = 4
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
    
    def __setPoints(self, points):
        self.painter.setPoints(points)
        if (self.table != None):
            self.table.setPoints(points)
    

if __name__=='__main__':
        app=QApplication(sys.argv)
        window=MainWindow()
        app.exec_()
