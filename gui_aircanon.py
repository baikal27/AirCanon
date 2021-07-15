import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QColor
import time
import RPi.GPIO as GPIO
import threading

form_class = uic.loadUiType("gui_aircanon.ui")[0]

class MyWindow(QMainWindow, form_class):
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		time = [str(i +1) for i in range(5)]
		self.cb_time.addItems(time)
		self.setup_gpio()
		self.lbl_ready.setText("Waiting")

		self.btn_fog.clicked.connect(self.do_fog)
		self.btn_trigger.clicked.connect(self.do_trigger)

		self.stop_thread = False
		self.thread_temp()

	def setup_gpio(self):
		self.temp_in = 5
		self.red_out = 13
		self.blue_out = 6
		self.trig_pin = 18
		self.fog_pin = 21

		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.temp_in, GPIO.IN)
		GPIO.setup(self.red_out, GPIO.OUT)
		GPIO.setup(self.blue_out, GPIO.OUT)
		GPIO.setup(self.trig_pin, GPIO.OUT)
		GPIO.setup(self.fog_pin, GPIO.OUT)

	def thread_temp(self):
		if self.stop_thread:
			self.display.append("Threading is stopped. Restart the system.")
		else:
			self.t = threading.Thread(target=self.check_temp)
			self.display.append("Start threading for checking Temperature")
			self.t.start()
			
	def check_temp(self):
		while True:
			if GPIO.input(self.temp_in) == True:
				GPIO.output(self.red_out, True)
				GPIO.output(self.blue_out, False)
				self.lbl_ready.setStyleSheet("background-color: #f44336") # red
				self.lbl_ready.setText("Waiting")
			else:
				GPIO.output(self.red_out, False)
				GPIO.output(self.blue_out, True)
				self.lbl_ready.setStyleSheet("background-color: rgb(76, 175, 80)") # green
				self.lbl_ready.setText("Ready")
			if self.stop_thread:
				break
			time.sleep(0.5)

	def do_fog(self):
		self.display.setTextColor(QColor(76, 175, 80)) # green
		fog_secs = self.cb_time.currentText()
		fog_secs = float(fog_secs)
		self.display.append("Fogging for {} sec(s)".format(fog_secs))
		GPIO.output(self.fog_pin, True)
		time.sleep(fog_secs)
		GPIO.output(self.fog_pin, False)
		self.display.setTextColor(QColor(0, 0, 0)) # black

	def do_trigger(self):
		self.display.setTextColor(QColor(255, 179, 0)) # 주황
		self.display.append("AirCanon is fired")
		GPIO.output(self.trig_pin, True)
		time.sleep(0.15)
		GPIO.output(self.trig_pin, False)
		self.display.setTextColor(QColor(0, 0, 0)) # black

	def closeEvent(self, event):
	   	ans = QMessageBox.question(self, 'System Close', 'Are You Sure to Close the System?',
	   	                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
	   	if ans == QMessageBox.Yes:
	   		self.stop_thread = True
	   		self.t.join()
	   		GPIO.cleanup()
	   		event.accept()
	   	else:
	   		event.ignore()

if __name__ == "__main__":
	app = QApplication(sys.argv)
	myWindow = MyWindow()
	myWindow.show()
	app.exec_()
