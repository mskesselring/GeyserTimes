import requests
import json
import datetime
from tkinter import *
import tkinter.ttk

url = {
    "base": "https://www.geysertimes.org/api/v5",
    "geysers": "https://www.geysertimes.org/api/v5/geysers",
    "predictions": "https://www.geysertimes.org/api/v5/predictions_latest"
}
format_string = "%h %d %I:%M %p"
update_format  = "%h %d %I:%M:%S %p"
center_format = None
attribution = "Contains information from GeyserTimes, which is made available here under the Open Database"
attribution2 = "License (ODbL). https://Geysertimes.org https://opendatacommons.org/licenses/odbl/"
freq = int(1000*60*5)  # ms/s * s/min * min
root = None
geyser_labels = []
open_labels = []
# center_labels = []
close_labels = []
probability_labels = []
titles = []
updated_label = None
row_offset = 4
cols = None
attributeFont = ("Calibri", "10")
boldFont = ("Calibri", "12", "bold")
myFont = ("Calibri", "12")


def update():
    global geyser_labels, open_labels, close_labels, probability_labels, updated_label
    # global center_labels

    # Print time to console
    print(datetime.datetime.now())
    last_update = "Last Update: " + datetime.datetime.now().strftime(update_format)
    updated_label = Label(root, text=last_update, font=myFont)
    updated_label.grid(row=2, column=0, columnspan=cols)

    # Get available predictions
    r = requests.get(url["predictions"])
    r = r.json()
    predictions = r["predictions"]
    # with open("data.txt") as json_file:
    #     predictions = json.load(json_file)

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
    # center_labels = []
    close_labels = []
    probability_labels = []

    # Display predictions
    row_num = row_offset
    for i in range(len(predictions)):
        p = predictions[i]
        name = p["geyserName"]
        window_open = datetime.datetime.fromtimestamp(int(p["windowOpen"]))
        # center = datetime.datetime.fromtimestamp(int(p["prediction"]))
        window_close = datetime.datetime.fromtimestamp(int((p["windowClose"])))
        probability = p["probability"]

        geyser_labels.append(Label(root, text=name, font=myFont))
        open_labels.append(Label(root, text=window_open.strftime(format_string), font=myFont))
        # center_labels.append(Label(root, text=center.strftime(format_string), font=myFont))
        close_labels.append(Label(root, text=window_close.strftime(format_string), font=myFont))
        probability_labels.append(Label(root, text=probability, font=myFont))

        tkinter.ttk.Separator(root, orient=HORIZONTAL).grid(column=0, row=row_num, columnspan=cols, sticky="ew")
        row_num += 1
        geyser_labels[i].grid(row=row_num, column=0)
        open_labels[i].grid(row=row_num, column=1)
        # center_labels[i].grid(row=row_offset+i, column=2)
        close_labels[i].grid(row=row_num, column=2)
        probability_labels[i].grid(row=row_num, column=3)
        row_num += 1

        # print("%14s:  %s   %s   %s" % (name,
        #                                window_open.strftime(format_string),
        #                                center.strftime(format_string),
        #                                window_close.strftime(format_string)
        #                                )
        #       )
    # Refresh after (freq) miliseconds
    root.after(freq, update)


def main():
    # Set up gui
    global root
    root = Tk()
    root.title("Geyser Times API")

    titles.append(Label(root, text="Geyser", font=boldFont))
    titles.append(Label(root, text="Window Open", font=boldFont))
    titles.append(Label(root, text="Window Close", font=boldFont))
    titles.append(Label(root, text="Probability", font=boldFont))

    global cols
    cols = len(titles)

    attribute_label = Label(root, text=attribution, font=attributeFont)
    attribute_label.grid(row=0, column=0, columnspan=cols)
    attribute2_label = Label(root, text=attribution2, font=attributeFont)
    attribute2_label.grid(row=1, column=0, columnspan=cols)

    for i in range(0, len(titles)):
        titles[i].grid(row=3, column=i)
    root.after(0, update)
    root.mainloop()


if __name__ == "__main__":
    sys.exit(main())
