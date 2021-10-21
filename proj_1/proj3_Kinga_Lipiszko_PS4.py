import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from datetime import datetime
maxColorVal = 255

def convertRGBtoCMYK(R,G,B):
    R = R/maxColorVal
    G = G/maxColorVal
    B = B/maxColorVal
    b = min(1-R,1-G,1-B)
    c = (1-R-b)/(1-b)
    m = (1-G-b)/(1-b)
    y = (1-B-b)/(1-b)
    return [c,m,y,b]

def convertCMYKtoRGB(C,M,Y,B):
    r = 1 - min(1,C*(1-B)+B)
    g = 1 - min(1,M*(1-B)+B)
    b = 1 - min(1,Y*(1-B)+B)
    r = maxColorVal * r
    g = maxColorVal * g
    b = maxColorVal * b
    return [r,g,b]
    
class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        layout = QFormLayout()
        self.mode = ""
        # rgbRow = QHBoxLayout()
        # rgbLabel = QLabel(self)

        # rgbLabel.setText("RGB: ")
        # R = QDoubleSpinBox(self)
        # G = QDoubleSpinBox(self)
        # B = QDoubleSpinBox(self)
        
        # rgbRow.addWidget(rgbLabel)
        # rgbRow.addWidget(R)
        # rgbRow.addWidget(G)
        # rgbRow.addWidget(B)

        # cmykRow = QHBoxLayout()
        # cmykLabel = QLabel(self)

        # cmykLabel.setText("CMYK: ")
        # C = QDoubleSpinBox(self)
        # M = QDoubleSpinBox(self)
        # Y = QDoubleSpinBox(self)
        # K = QDoubleSpinBox(self)
        
        # cmykRow.addWidget(cmykLabel)
        # cmykRow.addWidget(C)
        # cmykRow.addWidget(M)
        # cmykRow.addWidget(Y)
        # cmykRow.addWidget(K)

        # layout.addRow(rgbRow)
        # layout.addRow(cmykRow)

        self.colorBox = QWidget()
        self.colorBox.setAutoFillBackground(True)
        self.palette = self.palette()
        self.palette.setColor(QPalette.Window, QColor(0,0,0))
        self.colorBox.setPalette(self.palette)
        self.colorBox.setMinimumHeight(20)

        self.rgbInArr = []
        self.cmykInArr = []
        rgb = self.__createColorInput(['R','G','B'], "RGB",self.rgbInArr, self.__showRGB)
        cmyk = self.__createColorInput(['C','M','Y','K'], "CMYK", self.cmykInArr, self.__showCMYK)

        layout.addRow(rgb)
        layout.addRow(cmyk)
        layout.addRow(self.colorBox)
        self.setLayout(layout)

    def __createColorInput(self, colors, mode, arr, clickAction):
        row = QHBoxLayout()
        label = QLabel(self)

        label.setText(mode)
        row.addWidget(label)
        for color in colors:
            if (mode == "RGB"):
                colorInput = QSpinBox(self)
            else: 
                colorInput = QDoubleSpinBox(self)
                colorInput.setDecimals(3)
            colorInput.setSingleStep(1.0)
            colorInput.setMinimum(0.0)
            if (mode == "RGB"):
                colorInput.setMaximum(255)
            else: 
                colorInput.setMaximum(1.0)            
            colorInput.valueChanged.connect(clickAction)
            row.addWidget(colorInput)
            arr.append(colorInput)

        return row

    def __showRGB(self):
        if (self.mode == "CMYK"):
            return
        self.mode = "RGB"
        R = self.rgbInArr[0].value()
        G = self.rgbInArr[1].value()
        B = self.rgbInArr[2].value()

        CMYK = convertRGBtoCMYK(R,G,B)

        for i in range(len(self.cmykInArr)):
            self.cmykInArr[i].setValue(CMYK[i])
        
        self.__updateColorBox([R,G,B])
        self.mode = ""

    def __showCMYK(self):
        if (self.mode == "RGB"): return
        self.mode = "CMYK"
        C = self.cmykInArr[0].value()
        M = self.cmykInArr[1].value()
        Y = self.cmykInArr[2].value()
        B = self.cmykInArr[3].value()

        RGB = convertCMYKtoRGB(C,M,Y,B)

        for i in range(len(self.rgbInArr)):
            self.rgbInArr[i].setValue(RGB[i])

        self.__updateColorBox(RGB)
        self.mode = ""
  
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