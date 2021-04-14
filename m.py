# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwin.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


import PyQt5.QtGui
import PyQt5.QtWidgets
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyqtgraph as pg
import pyqtgraph.exporters
import soundfile as sf
from PyQt5 import QtGui, QtWidgets
from pyqtgraph import PlotWidget
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Image
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
import mainlayout
from spectrogram import Ui_OtherWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class Pin():
    def __init__(self):
        self.title = ''
        self.SignalPath = []
        self.GramPath = []
        self.pinElementTable = None

    def getPins(self, path):
        name = path.split("/")[-1]
        self.title = name
        self.SignalPath = [name + ".png"]
        self.GramPath = [name + "s" + ".png"]

    def genPinTable(self):
        pinElemTable = None
        pinElemWidth = 500
        pinElemHeight = 1000

        # 1) Build Structure

        titleTable = Table([[self.title]]
                           , pinElemWidth)

        S_picture = Image(self.SignalPath[0])
        S_picture.drawWidth = 200
        S_picture.drawHeight = 100

        G_picture = Image(self.GramPath[0])
        G_picture.drawWidth = 200
        G_picture.drawHeight = 100

        picSignal = Table([
            [S_picture]
        ], 250, 125)
        picGram = Table([
            [G_picture]
        ], 250, 125)

        PicTable = Table([
            [picSignal, picGram]
        ], [250, 250])

        self.pinElemTable = Table([
            [titleTable],
            [PicTable]
        ], pinElemWidth)

        # 2) Add Style
        # List available fonts
        '''
        from reportlab.pdfgen import canvas
        for font in canvas.Canvas('abc').getAvailableFonts(): 
            print(font)
        '''
        titleTableStyle = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('FONTNAME', (0, 0), (-1, -1),
             'Helvetica-Oblique'
             ),

            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ])
        titleTable.setStyle(titleTableStyle)

        picTableStyle = TableStyle([
            ('LEFTPADDING', (0, 0), (-1, -1), 15),

            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ])
        picSignal.setStyle(picTableStyle)
        picGram.setStyle(picTableStyle)

        pinElemTableStyle = TableStyle([
            ('BOX', (0, 0), (-1, -1), 3, colors.pink),

            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ])
        self.pinElemTable.setStyle(pinElemTableStyle)


class Window(QtWidgets.QMainWindow, mainlayout.Ui_MainWindow):
    signals_windows = {}  # store signals paths' and their object

    def __init__(self):
        super(Window, self).__init__()
        # Using functions in the inherited class
        self.setupUi(self)

        # set pg configuration
        pg.setConfigOptions(background='w')
        # anti aliasing to improve the appearance of a small image that's being scaled up
        pg.setConfigOptions(antialias=True)

        # set the title
        self.setWindowTitle("MainWindow")

        # variables declaration
        self.path = None
        self.original_data = None  # store original signal data
        self.sample_rate = None  # store sample rate from signal file
        self.fft = None
        self.frequencies = None
        self.magnitude_spectrum = None
        self.phase_spectrum = None
        self.modified_data = None
        self.spec_mag =None

        # plots
        self.original_waveform = None
        self.modified_waveform = None
        self.pallette = 'plasma'

        # self.signal = None  # have the created signal object
        self.pins = {}  # have signal path and created pin object
        self.signals_fft = {}
        self.selected_signal = None
        self.played = 0  # playing flag
        self.pause = 0  # pause flag

        # Actions
        self.actionOpen_signal.triggered.connect(self.open_sig)
        self.actionImport_signal_from_CSV_decimal_comma.triggered.connect(self.open_csv)
        # self.actionImport_signal_from_CSV_decimal_dot.triggered.connect(self.open_scv)
        self.actionZoom_In.triggered.connect(lambda: self.zoom(1))
        self.actionZoom_out.triggered.connect(lambda: self.zoom(0))
        self.actionPlay_signal_no_sound.triggered.connect(lambda: self.play_signal(3))
        # self.actionPlay_signal_no_sound.triggered.connect(lambda: self.play_signal(self.modified_data, self.modified_waveform, 3))
        self.actionStop_playing.triggered.connect(self.pause_signal)
        self.action_Signal_beginning.triggered.connect(lambda: self.signal_beginning(1))
        self.actionLeft.triggered.connect(lambda: self.signal_beginning(0))  ##scroll to left
        self.actionRight.triggered.connect(lambda: self.signal_end(0))  ##scroll to Right
        self.actionSignal_End.triggered.connect(lambda: self.signal_end(1))
        self.actionPlay_as_fast_as_possible.triggered.connect(self.play_fast)
        self.Export_pdf.triggered.connect(self.E_pdf)
        self.actionSpectrogram.triggered.connect(self.spec_showhide)
        self.actionTime_FFT.triggered.connect(self.inverse_fft)
        self.radioButton1.toggled.connect(self.color_pallette)
        self.radioButton2.toggled.connect(self.color_pallette)
        self.radioButton3.toggled.connect(self.color_pallette)
        self.radioButton4.toggled.connect(self.color_pallette)
        self.radioButton5.toggled.connect(self.color_pallette)

        self.specSlider1.valueChanged.connect(self.spec_range)
        self.specSlider2.valueChanged.connect(self.spec_range)

        self.eq_Slider_1.valueChanged.connect(self.slider_step)
        self.eq_Slider_2.valueChanged.connect(self.slider_step)
        self.eq_Slider_3.valueChanged.connect(self.slider_step)
        self.eq_Slider_4.valueChanged.connect(self.slider_step)
        self.eq_Slider_5.valueChanged.connect(self.slider_step)
        self.eq_Slider_6.valueChanged.connect(self.slider_step)
        self.eq_Slider_7.valueChanged.connect(self.slider_step)
        self.eq_Slider_8.valueChanged.connect(self.slider_step)
        self.eq_Slider_9.valueChanged.connect(self.slider_step)
        self.eq_Slider_10.valueChanged.connect(self.slider_step)


        self.showMaximized()
        self.show()

    def spec_showhide(self):
        if self.frame_3.isVisible():
            self.frame_3.setVisible(False)
        else:
            self.frame_3.setVisible(True)

    def spec_range(self):
        min_index = None
        max_index = None
        min_freq = self.specSlider1.value()
        max_freq = self.specSlider2.value()

        self.spec_min_freq.setText(str(min_freq))
        self.spec_max_freq.setText(str(max_freq))

        if min_freq < min(self.frequencies):
            min_index = 0

        if max_freq > max(self.frequencies):
            max_index = len(self.frequencies)

        if min_index != 0:
            min_index = int(np.where(self.frequencies == min_freq)[0])

        if max_index is None:
            max_index = int(np.where(self.frequencies == max_freq)[0])

        modified_fft = np.fft.rfft(self.modified_data)
        modified_fft = modified_fft[min_index:max_index+1]
        self.spec_mag = np.fft.irfft(modified_fft)
        self.open_window()


    def open_window(self):
        # color_cmap="plasma"
        # self.spectro_draw(self.color_cmap)
        self.spectro_draw(self.pallette)
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_OtherWindow()
        self.ui.setupUi(self.window)
        #self.window.show()

    # open for signals .wav , .edf

    def open_sig(self):
        #print("open_sig")
        self.path = PyQt5.QtWidgets.QFileDialog.getOpenFileName(None, 'Open', None, "WAV (*.wav)")[0]
        if self.path:
            if len(self.signals_windows) == 0:
                self.signals_windows[self.path] = self
            else:
                self.signals_windows[self.path] = OtherWindows()
                self.signals_windows[self.path].config(self.path)

            # load .wav data
            self.signals_windows[self.path].original_data, self.signals_windows[self.path].sample_rate = sf.read(self.path)
            self.signals_windows[self.path].modified_data = self.signals_windows[self.path].original_data
            self.signals_windows[self.path].spec_mag = self.signals_windows[self.path].modified_data

            # create signal object and plot
            self.signals_windows[self.path].create_signal()

    # open for signals .csv
    def open_csv(self):
        if len(self.signals) < 3:
            print("open_csv")
            path = PyQt5.QtWidgets.QFileDialog.getOpenFileName(None, 'Open', None, "CSV (*.csv)")[0]
            # if path:
            #     df = pd.read_csv(path, usecols=[0, 1])
            #     data = np.array(df.iloc[:, 1])
            #     # create signa object and plot
            #     self.create_signal(path, data)
    def generate_band(self):
        self.b1=[]
        self.b2=[]
        self.b3=[]
        self.b4=[]
        self.b5=[]
        self.b6=[]
        self.b7=[]
        self.b8=[]
        self.b9=[]
        self.b10=[]
        freqs=np.sort(self.frequencies)
        for freq in self.frequencies:
            if freqs[0] <= freq < (freqs[-1]/10):
                self.b1.append(freq)
            if (freqs[-1]/10) <= freq < (2*(freqs[-1]/10)):
                self.b2.append(freq)
            if (2*(freqs[-1]/10)) <= freq < (3*(freqs[-1]/10)):
                self.b3.append(freq)
            if (3*(freqs[-1]/10)) <= freq < (4*(freqs[-1]/10)):
                self.b4.append(freq)
            if (4*(freqs[-1]/10)) <= freq < (5*(freqs[-1]/10)):
                self.b5.append(freq)
            if (5*(freqs[-1]/10)) <= freq < (6*(freqs[-1]/10)):
                self.b6.append(freq)
            if (6*(freqs[-1]/10)) <= freq < (7*(freqs[-1]/10)):
                self.b7.append(freq)
            if (7*(freqs[-1]/10)) <= freq < (8*(freqs[-1]/10)):
                self.b8.append(freq)
            if (8*(freqs[-1]/10)) <= freq < (9*(freqs[-1]/10)):
                self.b9.append(freq)
            if (9*(freqs[-1]/10)) <= freq <= (freqs[-1]):
                self.b10.append(freq)
        # print(b10)
    
    def get_amplitude(self):
        b = len(self.b1)
        As=[]
        self.A1=list(self.magnitude_spectrum[:b])
        self.A2=list(self.magnitude_spectrum[b:2*b])
        self.A3=list(self.magnitude_spectrum[2*b:3*b])
        self.A4=list(self.magnitude_spectrum[3*b:4*b])
        self.A5=list(self.magnitude_spectrum[4*b:5*b])
        self.A6=list(self.magnitude_spectrum[5*b:6*b])
        self.A7=list(self.magnitude_spectrum[6*b:7*b])
        self.A8=list(self.magnitude_spectrum[7*b:8*b])
        self.A9=list(self.magnitude_spectrum[8*b:9*b])
        self.A10=list(self.magnitude_spectrum[9*b:(10*b+1)])
        As = self.A1+self.A2+self.A3+self.A4+self.A5+self.A6+self.A7+self.A7+self.A8+self.A9+self.A10

    # create Signal object and plot signal
    def create_signal(self):
        # create fft for signal
        self.signal_fft()
        self.original_waveform = self.plot(self.original_data)
        self.modified_waveform = self.plot(self.modified_data)
        self.verticalLayout_6.addWidget(self.original_waveform)
        self.verticalLayout_7.addWidget(self.modified_waveform)
        self.open_window()
        self.frame.show()
        # self.play_signal(self.modified_data, self.modified_waveform, 3)  # to be changed to step

        # print(self.fft)
        #equalizer
        self.generate_band()
        self.get_amplitude()
        #self.play_signal(3)  # to be changed to step



    # for plotting after reading signal
    def plot(self, data):
        data_plot = PlotWidget()
        x_range = [min(data), min(data) + 2000]
        x = np.arange(0, len(self.original_data), 1)
        data_plot.showGrid(x=True, y=True)
        data_plot.enableAutoRange(x=False, y=True)
        p = data_plot.plot(pen='b', width=0.1)
        p.setData(x, data)
        data_plot.getViewBox().setLimits(xMin=min(data))
        data_plot.setXRange(x_range[0], x_range[1])
        #print(data_plot)
        return data_plot

    # fft for signal
    def signal_fft(self):
        self.fft = np.fft.rfft(self.original_data)
        self.magnitude_spectrum = np.abs(self.fft)  # for calculating magnitude spectrum
        self.phase_spectrum = np.angle(self.fft)
        self.frequencies = np.fft.rfftfreq(len(self.original_data), d=1 / self.sample_rate)
        # print(len(self.frequencies))
        # print(len(self.magnitude_spectrum))


    # Zoom
    def zoom(self, mode):
        center_x = (self.original_waveform.getAxis("bottom").range[0] +
                    self.original_waveform.getAxis("bottom").range[1]) / 2
        center_y = 0
        print("zooooom")
        # zoom in
        if mode == 1:
            self.original_waveform.getViewBox().scaleBy(y=0.9, x=0.9, center=(center_x, center_y))
            self.modified_waveform.getViewBox().scaleBy(y=0.9, x=0.9, center=(center_x, center_y))
        # zoom out
        else:
            self.original_waveform.getViewBox().scaleBy(y=(1 / 0.9), x=(1 / 0.9), center=(center_x, center_y))
            self.modified_waveform.getViewBox().scaleBy(y=(1 / 0.9), x=(1 / 0.9), center=(center_x, center_y))

    # play function and play as fast as possible
    def play_signal(self, step):
        self.pause = 0
        self.played = 1
        sig_length = len(self.original_data)
        starting_x = self.original_waveform.getAxis("bottom").range
        x_end = starting_x[1]
        # check if signal reached the end
        if starting_x[1] < sig_length:
            i = 1
            # play signal
            while x_end < sig_length:
                # break if pause is pressed
                if self.pause == 1:
                    break
                self.original_waveform.setXRange(starting_x[0] + step * i,
                                                 starting_x[1] + step * i)
                self.modified_waveform.setXRange(starting_x[0] + step * i,
                                                 starting_x[1] + step * i)  #

                QtWidgets.QApplication.processEvents()
                # x_end= x_end + step
                x_end = self.original_waveform.getAxis("bottom").range[1]
                i += 1

    def play_fast(self):
        self.pause_signal()
        self.play_signal(40)

    # pause function
    def pause_signal(self):
        self.pause = 1
        self.played = 0

    # to signal beginning
    def signal_beginning(self, mode):
        self.pause_signal()
        # get original xrange
        x_range = [min(self.original_data), min(self.original_data) + 2000]
        if mode == 1:  # start of the signal
            self.original_waveform.setXRange(x_range[0], x_range[1])
            self.modified_waveform.setXRange(x_range[0], x_range[1])  #
        else:
            x_start = self.original_waveform.getAxis("bottom").range[0]
            x_end = self.original_waveform.getAxis("bottom").range[1]
            # print(x_start)
            # print(x_end)
            if (x_start - 10) < 0:
                self.signal_beginning(1)
            else:
                self.original_waveform.setXRange(x_start - 10, x_end - 20)
                self.modified_waveform.setXRange(x_start - 10, x_end - 20)  #

    # to signal end
    def signal_end(self, mode):
        self.pause_signal()
        # set xrange to be
        if mode == 1:
            x_end = len(self.original_data)
            self.original_waveform.setXRange(x_end - 2000, x_end)
            self.modified_waveform.setXRange(x_end - 2000, x_end)

        else:
            x_start = self.original_waveform.getAxis("bottom").range[0]
            x_end = self.original_waveform.getAxis("bottom").range[1]
            # print(x_start)
            # print(x_end)
            if (x_end + 10) > len(self.original_data):
                self.signal_end(1)
            else:
                self.original_waveform.setXRange(x_start + 20, x_end + 10)
                self.modified_waveform.setXRange(x_start + 20, x_end + 10)

    # delete closed signal
    def signal_closed(self, file_path):
        # print(len(self.signals))
        del self.signals[file_path]
        # print(len(self.signals))

        # save signal plots

    def save(self):
        for sig in self.signals:
            # signal im save
            plot_data = self.signals[sig].waveform
            QtGui.QApplication.processEvents()
            exporter = pg.exporters.ImageExporter(plot_data)
            exporter.parameters()['width'] = 500
            name = sig.split("/")[-1]
            exporter.export(name + ".png")
            fig = plt.figure()
            plt.subplot(212)
            data = self.signals[sig].data
            plt.specgram(data, Fs=1000)
            plt.xlabel('Time(sec)')
            plt.ylabel('Frequency(Hz)')
            fig.savefig(name + "s" + ".png")
            plt.close(fig)

    def E_pdf(self):
        self.save()
        for i in self.signals:
            self.pins[i] = Pin()
            self.pins[i].getPins(i)
        # print(self.pins)

        fileName = 'pdfTable.pdf'

        self.pdf = SimpleDocTemplate(fileName, pagesize=letter)

        # append table elements
        self.elems = []
        for pin in self.pins:
            self.pins[pin].genPinTable()  # generate element for each signal
            self.elems.append(self.pins[pin].pinElemTable)
        self.pdf.build(self.elems)
        print("Report is done")





    def spectro_draw(self,colorcmap):
        self.pallette = colorcmap
        # clearing old figure
        self.figure.clear()
        plt.specgram(self.spec_mag, Fs=self.sample_rate,cmap=colorcmap)
        plt.xlabel('Time(sec)')
        plt.ylabel('Frequency(Hz)')
        self.canvas.draw()

    def color_pallette(self):
        colors = ['plasma','Purples', 'Blues', 'Greens', 'Oranges','cool']
        if self.radioButton1.isChecked():
            self.spectro_draw(colors[1])
        elif self.radioButton2.isChecked():
            self.spectro_draw(colors[2])
        elif self.radioButton3.isChecked():
            self.spectro_draw(colors[3])
        elif self.radioButton4.isChecked():
            self.spectro_draw(colors[4])
        elif self.radioButton5.isChecked():
            self.spectro_draw(colors[5])
        else:
            self.spectro_draw(colors[0])

    def slider_step(self):
        current_val_1 = self.eq_Slider_1.value()
        current_val_2= self.eq_Slider_2.value()
        current_val_3 = self.eq_Slider_3.value()
        current_val_4 = self.eq_Slider_4.value()
        current_val_5 = self.eq_Slider_5.value()
        current_val_6 = self.eq_Slider_6.value()
        current_val_7= self.eq_Slider_7.value()
        current_val_8 = self.eq_Slider_8.value()
        current_val_9= self.eq_Slider_9.value()
        current_val_10= self.eq_Slider_10.value()
        
        self.gain1.setText(str(current_val_1))
        self.gain2.setText(str(current_val_2))
        self.gain3.setText(str(current_val_3))
        self.gain4.setText(str(current_val_4))
        self.gain5.setText(str(current_val_5))
        self.gain6.setText(str(current_val_6))
        self.gain7.setText(str(current_val_7))
        self.gain8.setText(str(current_val_8))
        self.gain9.setText(str(current_val_9))
        self.gain10.setText(str(current_val_10))

        new_band_1 = [a * current_val_1 for a in self.A1]
        new_band_2 = [a * current_val_2 for a in self.A2]
        #new_band_2 = [a * current_val_2 for a in self.signals[self.selected_signal].A2]
        new_band_3 = [a * current_val_3 for a in self.A3]
        new_band_4 = [a * current_val_4 for a in self.A4]
        new_band_5 = [a * current_val_5 for a in self.A5]
        new_band_6 = [a * current_val_6 for a in self.A6]
        new_band_7 = [a * current_val_7 for a in self.A7]
        new_band_8 = [a * current_val_8 for a in self.A8]
        new_band_9 = [a * current_val_9 for a in self.A9]
        new_band_10 = [a * current_val_10 for a in self.A10]
        
        self.new_amp = new_band_1 + new_band_2 + new_band_3 + new_band_4 + new_band_5+new_band_6+new_band_7+new_band_8 + new_band_9 + new_band_10
        self.inverse_fft()
        #print(new_band_1)
        #print(len(new_band_1))
        #print(self.new_amp[20]/self.magnitude_spectrum[20])
        # print(len(new_amp))

    def inverse_fft(self):
        fft = np.multiply(self.new_amp, np.exp(1j * self.phase_spectrum))
        self.modified_data = np.fft.irfft(fft)
        #clear widget
        self.verticalLayout_6.removeWidget(self.original_waveform)
        self.verticalLayout_7.removeWidget(self.modified_waveform)
        #update 
        self.create_signal()
        #print(self.modified_waveform)
        self.spec_range()
        self.open_window()




class OtherWindows(Window):
    def __init__(self):
        super().__init__()
        # # set the title
        # title = "win"
        # self.setWindowTitle(title)

    def config(self, path):
        self.signals_windows[path] = self


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui = Window()
    # ui.showMaximized()
    # ui.show()
    sys.exit(app.exec_())
