import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from datetime import datetime
import numpy as np
from vispy import app, gloo, scene
from vispy.util.transforms import perspective, translate, rotate
from vispy.color import Color

maxColorVal = 255

def convertRGBtoCMYK(RGB):
    R = RGB[0]/maxColorVal
    G = RGB[1]/maxColorVal
    B = RGB[2]/maxColorVal
    b = min(1-R,1-G,1-B)
    div = max((1-b), 0.000000001)
    c = (1-R-b)/ div
    m = (1-G-b)/ div
    y = (1-B-b)/ div
    return [c,m,y,b]

def convertCMYKtoRGB(CMYK):
    r = 1 - min(1,CMYK[0]*(1-CMYK[3])+CMYK[3])
    g = 1 - min(1,CMYK[1]*(1-CMYK[3])+CMYK[3])
    b = 1 - min(1,CMYK[2]*(1-CMYK[3])+CMYK[3])
    r = maxColorVal * r
    g = maxColorVal * g
    b = maxColorVal * b
    return [r,g,b]

def addColors(color1, color2):
    return [color1[0] + color2[0],color1[1] + color2[1],color1[2] + color2[2]]

def createRGBMatrix():
    vertex_order = [
        [0,14,19],      #Black
        [1,12,23],      #Blue
        [2,10,18],      #Green
        [3,8,22],       #Cyan
        [4,15,17],      #Red
        [5,13,21],      #Magenta
        [6,11,16],      #Yellow
        [7,9,20]        #White
    ]
    colors = [0,0,0] * len(vertex_order)
    for i in range (len(vertex_order)):
        color = list('{0:03b}'.format(vertex_order[i][0]))
        for j in range (len(vertex_order[i])):
            idx = vertex_order[i][j]
            colors[idx] = color

    return colors

class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        layout = QFormLayout()
        self.mode = ""

        self.colorBox = QWidget()
        self.colorBox.setAutoFillBackground(True)
        self.palette = self.palette()
        self.palette.setColor(QPalette.Window, QColor(0,0,0))
        self.colorBox.setPalette(self.palette)
        self.colorBox.setMinimumHeight(20)

        self.rgbInArr = []
        self.cmykInArr = []
        self.rgbSlidersArr = []
        self.cmykSlidersArr = []

        rgbInput = self.__createColorInput(['Red','Green','Blue'], "RGB",self.rgbInArr, self.__showRGB)
        rgbSlider = self.__createColorSlider(['R','G','B'], "RGB",self.rgbSlidersArr, self.__onRGBSlider)
        cmykInput = self.__createColorInput(['Cyan','Magenta','Yellow','K'], "CMYK", self.cmykInArr, self.__showCMYK)
        cmykSlider = self.__createColorSlider(['C','M','Y','K'], "CMYK", self.cmykSlidersArr, self.__onCMYKSlider)

        layout.addRow(rgbInput)
        layout.addRow(rgbSlider)
        layout.addRow(cmykInput)
        layout.addRow(cmykSlider)
        layout.addRow(self.colorBox)


        self.canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)

        view = self.canvas.central_widget.add_view()
        view.bgcolor = 'white'
        view.camera = 'turntable'
        view.padding = 100

        # colors = [(0,0,0,1),(1,0,0,1),(0,1,0,1),(0,0,0,1),(0,1,0,1),(1,1,0,1),(0,0,1,1),(1,0,1,1),(0,1,1,1),(1,1,1,1),(0,1,1,1),(1,1,1,1),(0,0,0,1),(1,0,0,1),(0,1,0,1),(0,0,0,1),(0,1,0,1),(1,1,0,1),(0,0,1,1),(1,0,1,1),(0,1,1,1),(1,1,1,1),(0,1,1,1),(1,1,1,1)]
        # colors = [
        # (1,0,0,1),(0,1,0,1), (0,0,1,1),
        # (1,0,0,1),(0,1,0,1), (0,0,1,1),
        # (0.5,0.5,0,1),(0.5,0,0.5,1), (0,0.5,0.5,1),
        # (0.5,0.5,0,1),(0.5,0,0.5,1), (0,0.5,0.5,1),
        # (0,0,0,1),(1,1,1,1), (0,0,0,1),
        # (0,0,0,1),(1,1,1,1), (0,0,0,1),
        # (1,0,0,1),(0,1,0,1), (0,0,1,1),
        # (1,0,0,1),(0,1,0,1), (0,0,1,1)
        # ]

#  [(0,0,0,1),(1,0,0,1),(0,1,0,1),(0,0,0,1),(0,1,0,1),(1,1,0,1),(0,0,1,1),(1,0,1,1),(0,1,1,1),(1,1,1,1),(0,1,1,1),(1,1,1,1)],
        colors = createRGBMatrix()
        cube = scene.visuals.Box(1, 1, 1, vertex_colors = colors,
                                parent=view.scene)

        self.canvas.create_native()
        self.canvas.native.setParent(self)


        layout.addRow(self.canvas.native)

        self.setLayout(layout)

    def __createColorSlider(self,colors,mode,arr,action):
        row = QHBoxLayout()
        for color in colors:
            if (mode == "RGB"):
                colorInput = QSlider(Qt.Horizontal)
                colorInput.setSingleStep(1.0)
                colorInput.setMaximum(255)
            else: 
                colorInput = QSlider(Qt.Horizontal)
                colorInput.setSingleStep(1)
                colorInput.setMaximum(100)
            colorInput.setMinimum(0.0)          
            colorInput.valueChanged.connect(action)
            row.addWidget(colorInput)
            arr.append(colorInput)

        return row

    def __createColorInput(self, colors, mode, arr, clickAction):
        row = QHBoxLayout()
        label = QLabel(self)

        label.setText(mode)
        row.addWidget(label)
        for color in colors:
            nameLabel = QLabel(self)
            nameLabel.setText('{} :'.format(color))
            row.addWidget(nameLabel)
            if (mode == "RGB"):
                colorInput = QSpinBox(self)
                colorInput.setMaximum(255)
                colorInput.setSingleStep(1.0)
            else: 
                colorInput = QDoubleSpinBox(self)
                colorInput.setDecimals(3)
                colorInput.setMaximum(1.0)            
                colorInput.setSingleStep(0.05)
            colorInput.setMinimum(0.0)
            colorInput.valueChanged.connect(clickAction)
            row.addWidget(colorInput)
            arr.append(colorInput)

        return row

    def __showRGB(self):
        if (self.mode == "CMYK"):
            return
        self.mode = "RGB"

        RGB = []

        for i in self.rgbInArr:
            RGB.append(i.value())

        CMYK = convertRGBtoCMYK(RGB)

        self.__setCMYKValues(CMYK)
        self.__updateColorBox(RGB)
        self.mode = ""

    def __showCMYK(self):
        if (self.mode == "RGB"): return
        self.mode = "CMYK"

        CMYK = []
        for i in self.cmykInArr:
            CMYK.append(i.value())

        RGB = convertCMYKtoRGB(CMYK)

        self.__setRGBValues(RGB)
        self.__updateColorBox(RGB)
        self.mode = ""
    
    def __onRGBSlider(self):
        if (self.mode == "CMYK"):
                return
        self.mode = "RGB"
        RGB = []

        for i in self.rgbSlidersArr:
            RGB.append(i.value())

        self.__setRGBValues(RGB)
        self.mode = ""

    def __onCMYKSlider(self):
        if (self.mode == "RGB"): return
        self.mode = "CMYK"

        CMYK = []

        for i in self.cmykSlidersArr:
            CMYK.append(i.value()/100)

        self.__setCMYKValues(CMYK)
        self.mode = ""

    def __setRGBValues(self,RGB):
        for i in range(len(self.rgbInArr)):
            self.rgbInArr[i].setValue(RGB[i])
        for i in range(len(self.rgbSlidersArr)):
            self.rgbSlidersArr[i].setValue(RGB[i])

    def __setCMYKValues(self,CMYK):
        for i in range(len(self.cmykInArr)):
            self.cmykInArr[i].setValue(CMYK[i])

        for i in range(len(self.cmykSlidersArr)):
            self.cmykSlidersArr[i].setValue(CMYK[i] * 100)

    def __updateColorBox(self,params):
        self.palette.setColor(QPalette.Window, QColor(params[0],params[1],params[2]))

        self.colorBox.setPalette(self.palette)
        self.colorBox.update()
        self.update()

if __name__=='__main__':
        converter=QApplication(sys.argv)

        window=Form()
        window.show()
        converter.exec()
