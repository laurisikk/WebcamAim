# -*- coding: utf-8 -*-

import cv2
import math
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QSpinBox, QPushButton, QGraphicsView, QGraphicsScene, QButtonGroup, QVBoxLayout, QHBoxLayout, QGraphicsItem, QGridLayout, QLineEdit, QSlider
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPainter, QImage, QPen, QBrush, QFont, QPolygonF
from PyQt5.QtCore import Qt, QLine, pyqtSignal, QThread, pyqtSlot, QRectF

feedCh=0
gridView=False
BEView=False
BEx=0
BEy=0
BEd=20
imageWidth=None
imageHeight=None
lineWidth=1
lineColorR=0
lineColorG=255
lineColorB=0
lineCount=3
	
#video channel number ==0 
def testChannels():
	global feedCh
	global imageWidth
	global imageHeight
	global BEx
	global BEy
	for i in range(0,1):
		testCap=cv2.VideoCapture(i)
		test,frame=testCap.read()
		#print("Testing channel ", i, ": result: ", str(test))
		if test == True:
			feedCh=i
			rgbImage=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
			imageHeight,imageWidth =rgbImage.shape[:2]
			BEx=imageWidth/2
			BEy=imageHeight/2
			
			
		
#video capture thread
class Thread(QThread):
	def __init__(self,parent):
		QThread.__init__(self,parent)
		self.running=False
	global feedCh
	changePixmap=pyqtSignal(QImage)
	def stop(self):
		self.running=False
		print("Video feed thread recieved stop signal from window")
		self.cap.release()

	def run(self):
		self.running=True
		self.cap = cv2.VideoCapture(feedCh)
		while self.running==True:
			ret, frame = self.cap.read()
			if ret:
				rgbImage=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
				height,width =rgbImage.shape[:2]
				convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
				p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
				self.changePixmap.emit(p)
class grid(QGraphicsItem):
	def __init__(self):
		super(grid,self).__init__()
		global imageWidth
		global imageHeight
		global lineCount
		global lineColorR
		global lineColorG
		global lineColorB
		global lineWidth
	def boundingRect(self):
		return QRectF(0,0,imageWidth,imageHeight)
	def paint(self,painter,option,widget):
		pen=QPen(Qt.SolidLine)
		pen.setColor(QColor(lineColorR,lineColorG,lineColorB))
		pen.setWidth(lineWidth)
		painter.setPen(pen)
		for i in range(1,1+lineCount):
			painter.drawLine(QLine(int(i*imageWidth/(lineCount+1)),0,int(i*imageWidth/(lineCount+1)),imageHeight))
			painter.drawLine(QLine(0,int(i*imageHeight/(lineCount+1)),imageWidth,int(i*imageHeight/(lineCount+1))))
		self.update()

class bullsEye(QGraphicsItem):
	def __init__(self):
		super(bullsEye,self).__init__()
		global imageWidth
		global imageHeight
		global BEx
		global BEy
		global BEd
		global lineColorR
		global lineColorG
		global lineColorB
		global lineWidth
		self.line1=QLine(BEx,BEy-BEd/2,BEx,BEy+BEd/2)
		self.line2=QLine(BEx-BEd/2,BEy,BEx+BEd/2,BEy)		
	def boundingRect(self):
		return QRectF(0,0,imageWidth,imageHeight)
	def paint(self,painter,option,widget):
		pen=QPen(Qt.SolidLine)
		pen.setColor(QColor(lineColorR,lineColorG,lineColorB))
		pen.setWidth(lineWidth)
		painter.setPen(pen)
		painter.drawEllipse(BEx-BEd/2,BEy-BEd/2,BEd,BEd)
		painter.drawLine(self.line1)
		painter.drawLine(self.line2)
		self.update()




class DrawingArea(QGraphicsScene):
	def __init__(self):
		global imageWidth
		global imageHeight
		super(DrawingArea,self).__init__()
		self.setSceneRect(0,0,imageWidth,imageHeight)
		
	



#class for the main application window
class MainWindow(QWidget):
	def __init__(self):
		super(MainWindow,self).__init__()
		self.InitUI()
	@pyqtSlot(QImage)
	def setImage(self, image):
		self.canvas.clear()
		self.canvas.addPixmap(QPixmap.fromImage(image))
		if gridView==True:
			self.grid=grid()
			self.canvas.addItem(self.grid)
		if BEView==True:
			self.bullsEye=bullsEye()
			self.canvas.addItem(self.bullsEye)
			


	def InitUI(self):
		global imageWidth
		global imageHeight
		global feedCh
		global lineColorR
		global lineColorG
		global lineColorB
		global lineCount
		global BEd
		#test channels for live feed, get size of image
		testChannels()
		self.resize(1200, 700)
		#create horizontal layout, add graphicsview and graphicsscene
		self.HLayout=QHBoxLayout()
		self.GraphicsView = QGraphicsView()
		self.HLayout.addWidget(self.GraphicsView)
		self.canvas=DrawingArea()
		self.GraphicsView.setScene(self.canvas)
		self.setLayout(self.HLayout)


		#create button list
		self.buttonList=QVBoxLayout()
		self.HLayout.addLayout(self.buttonList)
		self.channelText=QLabel()
		self.channelText.setText("Video feed channel: "+str(feedCh))
		self.buttonList.addWidget(self.channelText)
		
		#grid toggle
		self.button1=QPushButton("Grid")
		self.button1.setCheckable(True)
		self.button1.clicked.connect(self.toggleBTN1)
		self.buttonList.addWidget(self.button1)	

		#bullseye toggle
		self.button2=QPushButton("Bullseye")
		self.button2.setCheckable(True)
		self.button2.clicked.connect(self.toggleBTN2)
		self.buttonList.addWidget(self.button2)
		
		#no of lines selection
		self.lineCountLayout=QHBoxLayout()
		self.buttonList.addLayout(self.lineCountLayout)
		self.lineCountText=QLabel()
		self.lineCountText.setText("Number of lines:")
		self.lineCountLayout.addWidget(self.lineCountText)
		self.lineCountSB=QSpinBox()
		self.lineCountLayout.addWidget(self.lineCountSB)
		self.lineCountSB.setValue(lineCount)
		self.lineCountSB.valueChanged.connect(self.lineCountValueChange)
		
		#line width selection
		self.lineWidthLayout=QHBoxLayout()
		self.buttonList.addLayout(self.lineWidthLayout)
		self.lineWidthText=QLabel()
		self.lineWidthText.setText("Line width:")
		self.lineWidthLayout.addWidget(self.lineWidthText)
		self.lineWidthSB=QSpinBox()
		self.lineWidthLayout.addWidget(self.lineWidthSB)
		self.lineWidthSB.setValue(lineWidth)
		self.lineWidthSB.valueChanged.connect(self.lineWidthValueChange)
		
		#bullseye radius selection
		self.BERadiusLayout=QHBoxLayout()
		self.buttonList.addLayout(self.BERadiusLayout)
		self.BERadiusText=QLabel()
		self.BERadiusText.setText("Bullseye radius:")
		self.BERadiusLayout.addWidget(self.BERadiusText)
		self.BERadiusSB=QSpinBox()
		self.BERadiusLayout.addWidget(self.BERadiusSB)
		self.BERadiusSB.setValue(BEd)
		self.BERadiusSB.valueChanged.connect(self.BERadiusValueChange)
		
		#bullseye coordinates
		self.BECoordsText=QLabel()
		self.BECoordsText.setText("BullsEye coordinates")
		self.buttonList.addWidget(self.BECoordsText)
		self.BECoordXLayout=QHBoxLayout()
		self.buttonList.addLayout(self.BECoordXLayout)
		self.BECoordXText=QLabel()
		self.BECoordXText.setText("X:")
		self.BECoordXLayout.addWidget(self.BECoordXText)
		self.BECoordX=QSpinBox()
		self.BECoordX.setRange(0,imageWidth)
		self.BECoordX.setValue(imageWidth/2)
		self.BECoordXLayout.addWidget(self.BECoordX)
		self.BECoordX.valueChanged.connect(self.BECoordXValueChange)
		
		self.BECoordYLayout=QHBoxLayout()
		self.buttonList.addLayout(self.BECoordYLayout)
		self.BECoordYText=QLabel()
		self.BECoordYText.setText("Y:")
		self.BECoordYLayout.addWidget(self.BECoordYText)
		self.BECoordY=QSpinBox()
		self.BECoordY.setRange(0,imageHeight)
		self.BECoordY.setValue(imageHeight/2)
		self.BECoordYLayout.addWidget(self.BECoordY)
		self.BECoordY.valueChanged.connect(self.BECoordYValueChange)
		
		#line color sliders
		self.LineColorText=QLabel()
		self.LineColorText.setText("Line Color")
		self.buttonList.addWidget(self.LineColorText)
		
		self.ColorLayout=QHBoxLayout()
		self.buttonList.addLayout(self.ColorLayout)
		self.RColorLayout=QVBoxLayout()
		self.ColorLayout.addLayout(self.RColorLayout)
		self.RColorText=QLabel()
		self.RColorText.setText("R")
		self.RColorLayout.addWidget(self.RColorText)
		self.RSlider=QSlider()
		self.RSlider.setRange(0,255)
		self.RSlider.setValue(lineColorR)
		self.RColorLayout.addWidget(self.RSlider)
		self.RSlider.valueChanged.connect(self.RSliderValueChange)
		
		self.GColorLayout=QVBoxLayout()
		self.ColorLayout.addLayout(self.GColorLayout)
		self.GColorText=QLabel()
		self.GColorText.setText("G")
		self.GColorLayout.addWidget(self.GColorText)
		self.GSlider=QSlider()
		self.GSlider.setRange(0,255)
		self.GSlider.setValue(lineColorG)
		self.GColorLayout.addWidget(self.GSlider)
		self.GSlider.valueChanged.connect(self.GSliderValueChange)
		
		self.BColorLayout=QVBoxLayout()
		self.ColorLayout.addLayout(self.BColorLayout)
		self.BColorText=QLabel()
		self.BColorText.setText("B")
		self.BColorLayout.addWidget(self.BColorText)
		self.BSlider=QSlider()
		self.BSlider.setRange(0,255)
		self.BSlider.setValue(lineColorB)
		self.BColorLayout.addWidget(self.BSlider)
		self.BSlider.valueChanged.connect(self.BSliderValueChange)
		
		self.buttonList.addStretch(1)
		self.exitButton=QPushButton("EXIT")
		self.exitButton.clicked.connect(self.close)
		self.buttonList.addWidget(self.exitButton)
		
		th=Thread(self)
		th.changePixmap.connect(self.setImage)
		app.aboutToQuit.connect(th.stop)
		th.start()


	def RSliderValueChange(self):
		global lineColorR
		lineColorR=self.RSlider.value()
	def GSliderValueChange(self):
		global lineColorG
		lineColorG=self.GSlider.value()
	def BSliderValueChange(self):
		global lineColorB
		lineColorB=self.BSlider.value()
	def BERadiusValueChange(self):
		global BEd
		BEd=self.BERadiusSB.value()
	def BECoordXValueChange(self):
		global BEx
		BEx=self.BECoordX.value()
	def BECoordYValueChange(self):
		global BEy
		BEy=self.BECoordY.value()
	def lineCountValueChange(self):
		global lineCount
		lineCount=self.lineCountSB.value()	
	def lineWidthValueChange(self):
		global lineWidth
		lineWidth=self.lineWidthSB.value()
	def toggleBTN1(self,pressed):
		source=self.sender()
		global gridView
		if pressed:
			gridView=True
		else:
			gridView=False
	def toggleBTN2(self,pressed):
		source=self.sender()
		global BEView
		if pressed:
			BEView=True
		else:
			BEView=False
				

#initialize main app window if program is called
if __name__ == "__main__":
	import sys
	app = QApplication(sys.argv)
	AppWindow=MainWindow()
	AppWindow.show()
	sys.exit(app.exec_())



