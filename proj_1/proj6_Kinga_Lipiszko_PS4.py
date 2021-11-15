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

selectedIdx = [None]
isEditMode = [False]
class Toolbar(QToolBar):
    def __init__(self, btnClick):
        super(Toolbar, self).__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, Qt.gray)
        self.setPalette(palette)
        self.buttons = {
            "Mouse" : "Create with mouse",
            "Table" : "Create in table",
            "Edit mouse" : "Edit with mouse",
            "Edit table" : "Edit in table",
            "Clear" : "Clear plot"
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


class BezierCurve:
    def __calculate_value(self,t, idx):
        return comb(self.curve_degree, idx) * ((1-t)** (self.curve_degree - idx)) * (t** idx)

    def __bezier_curve(self,t):
        x = 0
        y = 0
        for i in range(len(self.points)):
            x += self.__calculate_value(t,i) * self.points[i][0]
            y += self.__calculate_value(t,i) * self.points[i][1]
        return (x,y)

    def bezier_curve_points_to_draw(self,points):
        self.points = points
        self.curve_degree = len(points) - 1
        step = 0.01
        x_arr = []
        y_arr = []
        t = 0
        while t <= 1:
            val = self.__bezier_curve(t)
            x_arr.append(val[0])
            y_arr.append(val[1])
            t += step
        return (x_arr,y_arr)
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.parent = parent
        self.axes = self.fig.add_subplot(111)
        self.fig.canvas.callbacks.connect('button_press_event', self.on_click)
        self.fig.canvas.callbacks.connect('button_move_event', self.move_obj)
        super(MplCanvas, self).__init__(self.fig)

    def __findIndex(self,pos):
        points = self.parent.points
        for i in range(len(points)):
            print(points)
            if (abs(points[i][0] - pos[0])<=0.1) and (abs(points[i][1] - pos[1])<=0.1):
                print(i)
                return i
        return 0
    
    def move_obj(self, event):
        print("Move over diagram")
        if (isEditMode[0]):
            self.parent.updatePoint(selectedIdx[0],event.xdata, event.ydata)

    def on_click(self,event):
        if event.button is MouseButton.LEFT:
            # print (event.xdata, event.ydata)    
            if (isEditMode[0]):
                if (selectedIdx[0] == None):
                    selectedIdx[0] = self.__findIndex([event.xdata, event.ydata])
                    self.parent.drawCurve()
                else: self.parent.updatePoint(selectedIdx[0],event.xdata, event.ydata)
            else:   self.parent.addPoint(event.xdata, event.ydata)
        elif event.button is MouseButton.RIGHT:
            if (isEditMode[0]):
                selectedIdx[0] = None
                self.parent.drawCurve()

    def clearCurve(self):
        self.drawCurve(None)
        
    def drawCurve(self, points):
        degree = len(points) - 1
        bc = BezierCurve()            
        to_plot_x, to_plot_y = bc.bezier_curve_points_to_draw(points)
        self.axes.set_xlim(0,10)
        self.axes.set_ylim(0,10)
        if (points == None) or (len(points) <= 0):
            return
        x = [i[0] for i in points]
        y = [i[1] for i in points]
            
        self.axes.plot(
            to_plot_x,
            to_plot_y,
            color="blue",
            label="Curve of Degree " + str(degree),
        )
        
        self.axes.scatter(x, y, color="red", label="Control Points")
        if (selectedIdx[0] != None) and (selectedIdx[0] < len(points)):
            self.axes.scatter(points[selectedIdx[0]][0], points[selectedIdx[0]][1], color="green", label="Edited Points")
        

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.points = []
        self.isEditMode = False
        self.setAutoFillBackground(True)
        self.mode = -1
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
        self.bezier_curve = MplCanvas(self, width=10, height=10, dpi=100)
        self.addToolBar(Toolbar(self.onMyToolBarButtonClick))
        self.initToolbox()
        self.plotWidget = QWidget()
        self.plot_layout = QHBoxLayout()
        self.plot_layout.addWidget(self.bezier_curve)
        self.plotWidget.setLayout(self.plot_layout)
        self.layout.addWidget(self.plotWidget,0,0,1,5)
        self.layout.addWidget(self.toolbox,0,6,1,1)
        widget = QWidget()
        widget.setLayout(self.layout)
        self.drawCurve()
        self.setCentralWidget(widget)
        self.show()

    def initToolbox(self):
        self.toolbox = QWidget()
        self.toolbox_layout = QVBoxLayout()
        self.curveDegreeInput = QSpinBox()
        self.curveDegreeInput.setMinimum(1)
        self.curveDegreeInput.setMaximum(50)
        self.curveDegreeInput.valueChanged.connect(self.__updateToolbox)
        self.table = QTableView()
        self.model = QStandardItemModel(1,2,self)
        self.model.dataChanged.connect(self.__tableValueChanged)
        self.table.setModel(self.model)
        self.toolbox_layout.addWidget(QLabel("Degree: "))
        self.toolbox_layout.addWidget(self.curveDegreeInput)
        self.toolbox_layout.addWidget(self.table)

        submitBtn = QPushButton("Submit")
        submitBtn.clicked.connect(self.__onSubmitClicked)        
        self.toolbox_layout.addWidget(submitBtn)
        self.toolbox.setLayout(self.toolbox_layout)

    def onMyToolBarButtonClick(self, s):
        isEditMode[0] = False
        selectedIdx[0] = None
        if (self.sender().text() == "Mouse"):
            self.__clearCurve()
            self.__resetTable()
            self.points = []
            self.mode = 0
        elif (self.sender().text() == "Table"):
            self.__clearCurve()
            self.points = []
            self.mode = 1
        elif (self.sender().text() == "Edit mouse"):
            isEditMode[0] = True
            self.__resetTable()
            self.mode = 2
        elif (self.sender().text() == "Edit table"):
            self.mode = 3
        elif (self.sender().text() == "Clear"):
            self.mode = 4
            self.__resetTable()
            self.__clearCurve()


    def __readTableInput(self):
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
    
    def __tableValueChanged(self):
        if (self.mode == 3):
            print("Data set changed!")
            self.__updatePlot()

    def __showErrorMessage(self, msg, title):
        QMessageBox.critical(
            self,
            title,
            msg,
            buttons=QMessageBox.Ignore,
            defaultButton=QMessageBox.Ignore,
        )

    def __onSubmitClicked(self):
        if (self.mode == 1):
            self.__updatePlot()

    def __clearCurve(self):
        self.points = []
        self.bezier_curve = MplCanvas(self, width=10, height=10, dpi=100)
        self.drawCurve()
        self.clearAndUpdatePlot()

    def __updatePlot(self):
        self.points = self.__readTableInput()
        if (self.points == None):
            self.__showErrorMessage("Points coordinates must be numbers", "Invalid value")
            return
        print('Points: {}'.format(self.points))
        self.drawCurve()

    def __updateTable(self):
        size = self.curveDegreeInput.value()
        self.model = QStandardItemModel(size,2,self)
        for i in range(len(self.points)):
            self.model.insertRow(i)
            for j in range(len(self.points[i])):
                val = self.points[i][j]
                self.model.setData(self.model.index(i,j), float(val))
        self.model.removeRow(self.model.rowCount() -1)
        self.model.dataChanged.connect(self.__tableValueChanged)
        self.table.setModel(self.model)
        self.update()
        
    def __updateToolbox(self):
        self.isEditMode = False
        size = self.curveDegreeInput.value()
        self.model = QStandardItemModel(size,2,self)
        self.model.dataChanged.connect(self.__tableValueChanged)
        self.table.setModel(self.model)
        self.update()

    def __resetTable(self):
        self.curveDegreeInput.setValue(1)
        self.model = QStandardItemModel(1,2,self)
        self.model.dataChanged.connect(self.__tableValueChanged)
        self.table.setModel(self.model)
        self.update()

    def drawCurve(self):
        self.bezier_curve = MplCanvas(self, width=10, height=10, dpi=100)
        self.bezier_curve.drawCurve(self.points)
        self.clearAndUpdatePlot()
    
    def clearAndUpdatePlot(self):
        self.plot_layout.itemAt(0).widget().deleteLater()
        self.plot_layout.addWidget(self.bezier_curve)
        self.plotWidget.update()
        self.update()    
        
    def addPoint(self,x,y):
        if (self.mode == 0):
            self.points.append([x,y])
            self.bezier_curve = MplCanvas(self, width=10, height=10, dpi=100)
            self.bezier_curve.drawCurve(self.points)
            self.clearAndUpdatePlot()
            self.__updateTable()
            
    def updatePoint(self,idx,x,y):
        if (self.mode == 2):
            self.points[idx][0] = x 
            self.points[idx][1] = y
            self.bezier_curve = MplCanvas(self, width=10, height=10, dpi=100)
            self.bezier_curve.drawCurve(self.points)
            self.clearAndUpdatePlot()
            self.__updateTable()

if __name__=='__main__':
        app=QApplication(sys.argv)
        window=MainWindow()
        app.exec_()
