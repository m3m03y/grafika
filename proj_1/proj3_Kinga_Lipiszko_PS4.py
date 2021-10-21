import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from datetime import datetime
maxColorVal = 255

def convertRGBtoCMYK(RGB):
    R = RGB[0]/maxColorVal
    G = RGB[1]/maxColorVal
    B = RGB[2]/maxColorVal
    b = min(1-R,1-G,1-B)
    c = (1-R-b)/(1-b)
    m = (1-G-b)/(1-b)
    y = (1-B-b)/(1-b)
    return [c,m,y,b]

def convertCMYKtoRGB(CMYK):
    r = 1 - min(1,CMYK[0]*(1-CMYK[3])+CMYK[3])
    g = 1 - min(1,CMYK[1]*(1-CMYK[3])+CMYK[3])
    b = 1 - min(1,CMYK[2]*(1-CMYK[3])+CMYK[3])
    r = maxColorVal * r
    g = maxColorVal * g
    b = maxColorVal * b
    return [r,g,b]
    
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

        rgbInput = self.__createColorInput(['R','G','B'], "RGB",self.rgbInArr, self.__showRGB)
        rgbSlider = self.__createColorSlider(['R','G','B'], "RGB",self.rgbSlidersArr, self.__onRGBSlider)
        cmykInput = self.__createColorInput(['C','M','Y','K'], "CMYK", self.cmykInArr, self.__showCMYK)
        cmykSlider = self.__createColorSlider(['C','M','Y','K'], "CMYK", self.cmykSlidersArr, self.__onCMYKSlider)

        layout.addRow(rgbInput)
        layout.addRow(rgbSlider)
        layout.addRow(cmykInput)
        layout.addRow(cmykSlider)
        layout.addRow(self.colorBox)
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

        self.__setRGBValues([R,G,B])
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

    def __setCMYKValues(self,CMYK):
        for i in range(len(self.cmykInArr)):
            self.cmykInArr[i].setValue(CMYK[i])

    def __updateColorBox(self,params):
        # if (len(params) <= 3):
        #     self.palette.setColor(QPalette.Window, QColor(params[0],params[1],params[2]))
        # else:
        #     self.palette.setColor(QPalette.Window, QColor.fromCmyk(params[0],params[1],params[2],params[3]))
        self.palette.setColor(QPalette.Window, QColor(params[0],params[1],params[2]))

        self.colorBox.setPalette(self.palette)
        self.colorBox.update()
        self.update()

if __name__=='__main__':
        app=QApplication(sys.argv)
        window=Form()
        window.show()
        app.exec()