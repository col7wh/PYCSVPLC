import time
import pandas as pd
import os
import numpy as np
import openpyxl
from openpyxl import Workbook
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import io
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt
from fastapi import FastAPI, Response, BackgroundTasks


class FileHandler(FileSystemEventHandler):
    def __init__(self, csv_folder):
        self.csv_folder = csv_folder

    def on_created(self, event):
        if event.is_directory:
            return
        elif event.src_path.endswith('.csv'):
            csv_file = event.src_path
            print('Find! '+event.src_path)
            time.sleep(2)
            self.process_csv(csv_file)

    def process_csv(self, csv_file):
        # Start of simpl
        # Чтение данных из файла CSV
        dataframe = pd.read_csv(csv_file, sep=';', header=0, encoding='windows-1251', parse_dates=True)
        data = dataframe.sort_values('Дата и время')

        # Создание графика
        datetime_list = data['Дата и время']

        x, y1, y2, y3 = [], [], [], []  # Новый список для хранения времени
        date_variable = None  # Переменная для хранения даты

        for dt in datetime_list:
            date, dtime = dt.split(' ')  # Разделение каждого элемента списка на дату и время
            if date_variable is None:  # Сохранение первой даты в переменную
                date_variable = date
            x.append(dtime)  # Добавление времени в новый список

        for t1 in data['Температура 1']:
            y1.append(float(t1.replace(',', '.')))  # Добавление времени в новый список

        for t2 in data['Температура 2']:
            y2.append(float(t2.replace(',', '.')))  # Добавление времени в новый список

        for pr in data['Давление']:
            y3.append(float(pr.replace(',', '.')))  # Добавление времени в новый список
        maxtpm = int(round(max(max(y1, y2))) / 10 + 2) * 10

        # Plot Line1 (Left Y Axis)
        fig, ax1 = plt.subplots(1, 1, figsize=(20, 10), dpi=80)
        ax1.plot(x, y1, color='tab:red')
        ax1.plot(x, y2, color='tab:orange')

        # Decorations
        # ax1 (left Y axis)
        ax1.set_xlabel('Дата и время', fontsize=20)
        ax1.tick_params(axis='x', rotation=0, labelsize=12)
        ax1.set_ylabel('Температура', color='tab:red', fontsize=20)
        ax1.set_yticks(np.arange(0, maxtpm + 1, maxtpm / 10))
        # ax1.set_yticklabels(np.arange(0, 110, 10), rotation=0)
        ax1.tick_params(axis='y', rotation=0, labelcolor='tab:red')
        ax1.grid(alpha=.4)
        # ax1.autoscale(axis="y")

        # Plot Line2 (Right Y Axis)
        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
        ax2.plot(x, y3, color='tab:blue')
        # ax2 (right Y axis)
        ax2.set_ylabel("Давление", color='tab:blue', fontsize=20)
        ax2.tick_params(axis='y', labelcolor='tab:blue')
        if len(x)>12:
            ax2.set_xticks(np.arange(0, len(x), int(len(x) / 12)))
            ax2.set_xticklabels(x[::int(len(x) / 12)], rotation=0, fontdict={'fontsize': 10})
        else:
            ax2.set_xticks(np.arange(0, len(x)))
            ax2.set_xticklabels(x, rotation=0, fontdict={'fontsize': 10})
        ax2.set_title("График " + date_variable, fontsize=22)
        fig.tight_layout()

        # plt.show()

        # excel_file = os.path.join(self.csv_folder, fname+'.xlsx')
        # writer = pd.ExcelWriter(excel_file, engine='openpyxl')
        # data.to_excel(writer, sheet_name='Graph', index=False)
        # writer.close()

        # end of simple
        png_folder = 'C:/PNG/'
        file_name = csv_file.split(csv_folder, 1)[1]
        fname = file_name[:-4]
        # print(f"{file_name} was just Created")
        #print((png_folder+fname+'.png'))
        plt.savefig(os.path.join(csv_folder,'\\','PNG', fname+'.png'))
        #plt.savefig(png_folder+fname+'.png')
        plt.close()


csv_folder = 'C:/FTP/'
app = FastAPI()
event_handler = FileHandler(csv_folder)
observer = Observer()
observer.schedule(event_handler, csv_folder, recursive=True)
observer.start()
print('v12.12.2023 Run. Find csv an save plot. ')

try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    observer.stop()
observer.join()
