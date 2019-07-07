import datetime
import json
import requests
from tkinter import *
import tkinter.ttk


class Predictions:
    attribution = "Contains information from GeyserTimes, which is made "\
                  "available here under the Open Database License (ODbL). "\
                  "https://Geysertimes.org "\
                  "https://opendatacommons.org/licenses/odbl/"
    open_labels = []
    close_labels = []
    probability_labels = []
    titles = []
    updated_label = None
    row_offset = 3

    def __init__(self, freq, boldFont, myFont, attributeFont, DEBUG,
                 update_format, url, format_string):
        self.freq = freq
        self.boldFont = boldFont
        self.myFont = myFont
        self.attributeFont = attributeFont
        self.DEBUG = DEBUG
        self.update_format = update_format
        self.url = url
        self.format_string = format_string
        # Set up root
        self.root = Tk()
        self.root.title("Geyser Eruption Prediction")
        # Create titles
        self.titles.append(Label(self.root, text="Geyser", font=boldFont))
        self.titles.append(Label(self.root, text="Window Open", font=boldFont))
        self.titles.append(Label(self.root, text="Window Close", font=boldFont))
        self.titles.append(Label(self.root, text="Probability", font=boldFont))

        # Populate GUI
        self.cols = len(self.titles)
        for i in range(0, len(self.titles)):
            t_width = self.titles[i].winfo_reqwidth()
            self.titles[i].grid(row=self.row_offset - 1, column=i,
                                padx=t_width * 0.1)
        self.root.update()
        width = self.root.winfo_width()
        attribute_label = Label(self.root, text=self.attribution,
                                font=attributeFont, wraplength=width,
                                justify=CENTER)
        attribute_label.grid(row=0, column=0, columnspan=self.cols)
        self.root.after(0, self.update)

    def update(self):
        # Print time to console
        print(datetime.datetime.now())
        last_update = "Last Update: " + datetime.datetime.now().strftime(
                self.update_format)
        updated_label = Label(self.root, text=last_update, font=self.myFont)
        updated_label.grid(row=self.row_offset - 2, column=0,
                           columnspan=self.cols)

        # Get available predictions
        if not self.DEBUG:
            r = requests.get(self.url["predictions"])
            r = r.json()
            predictions = r["predictions"]
            with open("data.json", "w") as json_file:
                json.dump(predictions, json_file)
        else:
            try:
                with open("data.json") as json_file:
                    predictions = json.load(json_file)
            except:
                predictions = {}

        # Remove duplicate predictions, keep higher probability
        temp = {}
        for p in predictions:
            if p["geyserName"] in temp.keys():
                # Check for higher prediction
                if temp[p["geyserName"]]["probability"] < p["probability"]:
                    temp[p["geyserName"]] = p
            else:
                temp[p["geyserName"]] = p
        # Convert back to list
        predictions = list(temp.values())
        # Sort predictions by geyser name
        predictions.sort(key=lambda x: x["geyserName"])

        geyser_labels = []
        open_labels = []
        close_labels = []
        probability_labels = []

        # Display predictions
        row_num = self.row_offset
        for i in range(len(predictions)):
            p = predictions[i]
            name = p["geyserName"]
            window_open = datetime.datetime.fromtimestamp(int(p["windowOpen"]))
            window_close = datetime.datetime.fromtimestamp(
                    int((p["windowClose"])))
            probability = p["probability"]

            geyser_labels.append(Label(self.root, text=name, font=self.myFont))
            open_labels.append(
                    Label(self.root,
                          text=window_open.strftime(self.format_string),
                          font=self.myFont))
            close_labels.append(
                    Label(self.root,
                          text=window_close.strftime(self.format_string),
                          font=self.myFont))
            probability_labels.append(
                    Label(self.root, text=probability, font=self.myFont))

            tkinter.ttk.Separator(
                    self.root, orient=HORIZONTAL).grid(column=0,
                                                       row=row_num,
                                                       columnspan=self.cols,
                                                       sticky="ew")
            row_num += 1
            geyser_labels[i].grid(row=row_num, column=0)
            open_labels[i].grid(row=row_num, column=1)
            close_labels[i].grid(row=row_num, column=2)
            probability_labels[i].grid(row=row_num, column=3)
            row_num += 1

        # Refresh after (freq) miliseconds
        self.root.after(self.freq, self.update)
