"""
Author: Claudia Bigoni
Date: 29.01.2021
Description: This file starts the application to manually choose the latency of a signal (in this case motor evoked
potentials). The application was created using PyQt5 and the layout is described in latency_gt_gui.ui.
MEP signals must be created as .pkl saved dataframes using create_dataframe.py.
"""
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, uic
import pyqtgraph as pg
import sys
import os
import datetime


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, data_dir, *args, **kwargs):
        """ Initialize the gui. This function will create a series of signal
        and slots for MainWindow
        Args:
            - MainWindow: Window where the gui will appear
        Returns:
            None
        Description: void
        """
        super(MainWindow, self).__init__(*args, **kwargs)
        # Load the UI Page
        uic.loadUi('latency_gt_gui.ui', self)

        self.data_dir = data_dir
        self.sub_id = ''
        self.trial = 0
        self.lat = 0

        self.df_all_meps = pd.DataFrame(columns=['sub_id', 'trial', 'mep'])
        self.df_row_idx = 0

        self.df_lat = pd.DataFrame(columns=['sub_id', 'trial', 'lat'])
        self.df_lat_row = 0

        # Connect signals and slots
        self.button_next.clicked.connect(self.next_file)
        self.button_save.clicked.connect(self.save_lat)
        self.button_save_df.clicked.connect(self.save_df)
        self.button_remove.clicked.connect(self.remove_trial)
        self.button_load_df_res.clicked.connect(self.load_df_res)
        self.button_load_meps.clicked.connect(self.load_all_meps_df)
        self.p = self.graphWidget.addPlot()
        self.graphWidget.scene().sigMouseClicked.connect(self.onClick)

        self.write_on_browser('INSTRUCTIONS:\n'
                              'Load the remaining MEP pkl file and the latencies ones by pressing on the '
                              'buttons "Load remaining MEPs" and "Load saved latencies" respectively.\nOnce these files'
                              ' have been loaded, MEPs from single pulse TMS of either healthy young participants or '
                              'stroke patients will appear on the black graph plot on the bottom left.\nWhen a new MEP '
                              'is plotted, you have 3 options:\n'
                              '1. Click with your cursor the point where you think the MEP begins. The point will be '
                              'represented as a red dot and the exact sample number will be reported on the very bottom'
                              ' left, underneath the plot. You can correct your choice as many times as you want by '
                              'clicking again on the plot. Once your are sure of your answer, press "Next". This will '
                              'plot on the graph a new MEP.\n'
                              '2. If you are uncertain of where the MEP begins, you can press the "Dont know" button.'
                              'You will be taken to the next MEP and that MEP will reappear later on.\n'
                              '3. If you think there is no MEP present on the plot (e.g. too much noise or too little '
                              'amplitude) press the "Not MEP: remove" button and the trial will be removed.\n'
                              '\n\n**** IMPORTANT!!!! ****\n\n'
                              'Click on "Update dataframes" when you want to save your progress. First you will be '
                              'asked to save the csv file with the latencies results; secondly the pkl file with the '
                              'remaining MEPs.')

    def write_on_browser(self, s):
        self.textEdit.append(
            f'{datetime.datetime.now().time()}\t-\t{s}')

    def plot_mep(self):
        self.p.clear()
        self.p.setLabel('bottom', 'Samples')
        self.p.setLabel('left', 'Voltage [mV]')
        self.p.plot(y=self.mep, pen=pg.mkPen('w', width=2))

    def onClick(self, event):
        items = self.graphWidget.scene().items(event.scenePos())
        mousePoint = self.p.vb.mapSceneToView(event._scenePos)
        print(mousePoint.x(), mousePoint.y())
        self.lat = int(mousePoint.x())
        self.p.plot([int(mousePoint.x())], [self.mep[int(mousePoint.x())]], symbol='o',
                    symbolPen=pg.mkPen(color=(255, 0, 0), width=0), symbolBrush=pg.mkBrush(255, 0, 0),
                    symbolSize=10)
        self.label_lat.setNum(self.lat)

    def next_file(self):
        """load next mep"""
        self.get_random_trial()
        self.plot_mep()

    def save_lat(self):
        """save in dataframe the ground truth latency"""
        self.df_lat.loc[self.df_lat_row] = pd.Series({
            'sub_id': self.sub_id, 'trial': self.trial, 'lat': self.lat
        })
        self.df_lat_row += 1
        self.write_on_browser('New latency saved in dataframe. Going to next trial.')
        self.df_all_meps = self.df_all_meps.drop(self.df_all_meps.index[self.trial_idx])
        self.next_file()

    def remove_trial(self):
        """No mep present, latency to NaN"""
        self.df_lat.loc[self.df_lat_row] = pd.Series({
            'sub_id': self.sub_id, 'trial': self.trial, 'lat': 'nan'
        })
        self.df_lat_row += 1
        self.write_on_browser('This trial will have a null latency. Going to next trial.')
        self.df_all_meps = self.df_all_meps.drop(self.df_all_meps.index[self.trial_idx])
        self.next_file()

    def save_df(self):
        """Save the dataframe with ground truth latency (csv) and updated dataframe with MEP to still evaluate (pkl)"""
        filename = self.file_save('Save latencies dataframe (csv)')
        self.df_lat.to_csv(filename)
        self.write_on_browser(f'Saved dataframe with ground truth latencies in {filename}')
        filename = self.file_save('Save dataframe (pkl) with missing MEPs.')
        self.df_all_meps.to_pickle(filename)
        self.write_on_browser(f'Saved dataframe with missing MEPs to evaluate in {filename}.')

    def file_save(self, capt):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(None, caption=capt,
                                                            directory=self.data_dir)
        return filename

    def get_random_trial(self):
        try:
            self.trial_idx = np.random.randint(0, len(self.df_all_meps.index), 1)[0]
            self.sub_id = self.df_all_meps.loc[self.df_all_meps.index[self.trial_idx]]['sub_id']
            self.mep = self.df_all_meps.loc[self.df_all_meps.index[self.trial_idx]]['mep'][0]
            self.trial = self.df_all_meps.loc[self.df_all_meps.index[self.trial_idx]]['trial']
        except Exception:
            self.save_df()

    def load_all_meps_df(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_dir = os.path.join(self.data_dir)
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, caption='Load dataframe with remaining MEPs', directory=file_dir, filter='(*.pkl)',
            options=options)
        self.df_all_meps = pd.read_pickle(filename)
        self.df_row_idx = 0
        self.write_on_browser('Loaded the dataframe with missing MEPs.')
        self.write_on_browser("Loading first MEP")
        self.next_file()

    def load_df_res(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_dir = os.path.join(self.data_dir)
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, caption='Load dataframe with initial results', directory=file_dir, filter='(*.csv)',
            options=options)
        self.df_lat = pd.read_csv(os.path.join(data_dir, filename))
        self.write_on_browser('Loaded the dataframe with some initial results.')
        self.df_lat_row = len(self.df_lat)

    def closeEvent(self, event):
        # save
        self.save_df()
        event.accept()  # let the window close


if __name__ == '__main__':
    data_dir = os.getcwd()
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow(data_dir)
    main.setWindowTitle('Latency ground truth')
    main.show()
    sys.exit(app.exec_())
