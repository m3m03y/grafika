import sys
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
import matplotlib

matplotlib.use('Qt5Agg')

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from scipy.special import comb

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

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
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.points = []

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
        # self.setCentralWidget(self.drawCurve())
        # self.show()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)
        self.layout = QGridLayout()
        self.bezier_curve = MplCanvas(self, width=10, height=10, dpi=100)
        self.initToolbox()
        self.plotWidget = QWidget()
        self.plot_layout = QHBoxLayout()
        self.plot_layout.addWidget(self.bezier_curve)
        self.plotWidget.setLayout(self.plot_layout)
        self.layout.addWidget(self.plotWidget,0,0,1,5)
        self.layout.addWidget(self.toolbox,0,6,1,1)
        widget = QWidget()
        widget.setLayout(self.layout)
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
        self.table.setModel(self.model)
        self.toolbox_layout.addWidget(QLabel("Degree: "))
        self.toolbox_layout.addWidget(self.curveDegreeInput)
        self.toolbox_layout.addWidget(self.table)

        submitBtn = QPushButton("Submit")
        submitBtn.clicked.connect(self.__onSubmitClicked)
        self.toolbox_layout.addWidget(submitBtn)
        self.toolbox.setLayout(self.toolbox_layout)

    def __readTableInput(self):
        table_data = []
        model = self.table.model()
        if (model.columnCount() != 2):
            print("Invalid column number")

        for row in range(model.rowCount()):
            table_data.append([])
            for column in range(model.columnCount()):
                index = model.index(row, column)
                try:
                    val = str(model.data(index)).replace(',','.')
                    table_data[row].append(float(val))
                except TypeError: 
                    # self.__showErrorMessage("Mask values must be numbers", "Invalid value")
                    return None
        return table_data

    def __onSubmitClicked(self):
        self.points = self.__readTableInput()
        # self.points = [(0, 0), (5, 5), (5, 0), (2.5, -2.5)]

        print(self.points)
        self.drawCurve()

    def __updateToolbox(self):
        size = self.curveDegreeInput.value()
        self.model = QStandardItemModel(size,2,self)
        self.table.setModel(self.model)
        self.update()

    def drawCurve(self):
        self.bezier_curve = MplCanvas(self, width=10, height=10, dpi=100)

        degree = len(self.points) - 1
        bc = BezierCurve()
        to_plot_x, to_plot_y = bc.bezier_curve_points_to_draw(self.points)

        x = [i[0] for i in self.points]
        y = [i[1] for i in self.points]

        self.bezier_curve.axes.plot(
            to_plot_x,
            to_plot_y,
            color="blue",
            label="Curve of Degree " + str(degree),
        )
        
        self.bezier_curve.axes.scatter(x, y, color="red", label="Control Points")

        self.plot_layout.itemAt(0).widget().deleteLater()
        self.plot_layout.addWidget(self.bezier_curve)
        self.plotWidget.update()
        self.update()

if __name__=='__main__':
        app=QApplication(sys.argv)
        window=MainWindow()
        # window.show()
        app.exec_()
