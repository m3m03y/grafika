import sys
import matplotlib

matplotlib.use('Qt5Agg')

from PySide2.QtWidgets import QMainWindow, QApplication
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
        super(MainWindow, self).__init__(*args, **kwargs)


        self.setCentralWidget(self.drawCurve())
        self.show()

    def drawCurve(self):
        points = [(0, 0), (5, 5), (5, 0), (2.5, -2.5)]
        bc = BezierCurve()
        to_plot_x, to_plot_y = bc.bezier_curve_points_to_draw(points)

        x = [i[0] for i in points]
        y = [i[1] for i in points]

        sc = MplCanvas(self, width=10, height=10, dpi=100)

        sc.axes.plot(
            to_plot_x,
            to_plot_y,
            color="blue",
            label="Curve of Degree " + str(len(points) - 1),
        )
        
        sc.axes.scatter(x, y, color="red", label="Control Points")

        return sc
app = QApplication(sys.argv)
w = MainWindow()
app.exec_()