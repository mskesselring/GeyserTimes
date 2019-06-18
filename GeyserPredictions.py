import requests
import json
import datetime
from tkinter import *
import tkinter.ttk
from tkinter import messagebox

DEBUG = bool(0)
url = {
    "base": "https://www.geysertimes.org/api/v5",
    "geysers": "https://www.geysertimes.org/api/v5/geysers",
    "predictions": "https://www.geysertimes.org/api/v5/predictions_latest",
    "entries": "https://www.geysertimes.org/api/v5/entries_latest"
}
format_string = "%h %d %I:%M %p"
update_format = "%h %d %I:%M:%S %p"
center_format = None
attribution = "Contains information from GeyserTimes, which is made " \
              "available here under the Open Database License (ODbL). " \
              "https://Geysertimes.org " \
              "https://opendatacommons.org/licenses/odbl/"
freq = int(1000 * 60 * 5)  # ms/s * s/min * min
root = None
geyser_root = None
geyser_labels = []
open_labels = []
close_labels = []
probability_labels = []
titles = []
updated_label = None
row_offset = 3
cols = None
attributeFont = ("Calibri", "10")
boldFont = ("Calibri", "12", "bold")
myFont = ("Calibri", "12")
geysers = {}
geyser_listbox = None
geyser_scroll = None
entries = {}
entry_string = ""


def resize(event):
    geyser_scroll.pack(side=RIGHT, fill=Y)
    geyser_listbox.pack(side=LEFT, fill=BOTH, expand=YES)


def refresh():
    global entries
    if not DEBUG:
        r = requests.get(url["entries"] + "/" + entry_string)
        r = r.json()
        data = r["entries"]
        with open("entries.json", "w") as json_file:
            json.dump(data, json_file)
    else:
        with open("entries.json") as json_file:
            data = json.load(json_file)
    for e in data:
        entries[e["geyserID"]] = e
    geyser_root.after(freq, refresh)


def get_recent(event):
    name = geyser_listbox.get(geyser_listbox.curselection())
    geyser_id = geysers[name]["id"]
    if geyser_id in entries:
        recent = entries[geyser_id]
        time = datetime.datetime.fromtimestamp(int(recent["time"]))
        time_str = time.strftime(format_string)
        if bool(int(recent["maj"])):
            event_type = "Major"
        else:
            event_type = "Minor"
        message = "Last Eruption: %s, Eruption Type: %s" % (
            time_str, event_type)
        messagebox.showinfo(name, message)
        # print(name, time_str, event_type)
    else:
        tkinter.messagebox.showerror(name,
                                     "No entries found for " + name)


def update():
    global geyser_labels, open_labels, close_labels, probability_labels, \
        updated_label

    # Print time to console
    print(datetime.datetime.now())
    last_update = "Last Update: " + datetime.datetime.now().strftime(
        update_format)
    updated_label = Label(root, text=last_update, font=myFont)
    updated_label.grid(row=row_offset - 2, column=0, columnspan=cols)

    # Get available predictions
    if not DEBUG:
        r = requests.get(url["predictions"])
        r = r.json()
        predictions = r["predictions"]
        with open("data.json", "w") as json_file:
            json.dump(predictions, json_file)
    else:
        with open("data.json") as json_file:
            predictions = json.load(json_file)

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
    row_num = row_offset
    for i in range(len(predictions)):
        p = predictions[i]
        name = p["geyserName"]
        window_open = datetime.datetime.fromtimestamp(int(p["windowOpen"]))
        window_close = datetime.datetime.fromtimestamp(int((p["windowClose"])))
        probability = p["probability"]

        geyser_labels.append(Label(root, text=name, font=myFont))
        open_labels.append(
            Label(root, text=window_open.strftime(format_string),
                  font=myFont))
        close_labels.append(
            Label(root, text=window_close.strftime(format_string),
                  font=myFont))
        probability_labels.append(Label(root, text=probability, font=myFont))

        tkinter.ttk.Separator(root, orient=HORIZONTAL).grid(column=0,
                                                            row=row_num,
                                                            columnspan=cols,
                                                            sticky="ew")
        row_num += 1
        geyser_labels[i].grid(row=row_num, column=0)
        open_labels[i].grid(row=row_num, column=1)
        close_labels[i].grid(row=row_num, column=2)
        probability_labels[i].grid(row=row_num, column=3)
        row_num += 1

    # Refresh after (freq) miliseconds
    root.after(freq, update)


def main():
    # Get list of geysers
    global geysers
    if not DEBUG:
        r = requests.get(url["geysers"])
        r = r.json()
        geyser_list = r["geysers"]
        with open("geyserList.json", "w") as json_file:
            json.dump(geyser_list, json_file)
    else:
        with open("geyserList.json", "r") as json_file:
            geyser_list = json.load(json_file)

    geyser_list.sort(key=lambda x: x["name"])
    tmp = []
    for g in geyser_list:
        if "Uncommon" not in g["groupName"]:
            geysers[g["name"]] = g
            tmp.append(g["id"])
    tmp.sort(key=lambda x: int(x))
    global entry_string
    entry_string = ";".join(tmp)
    # Set up root windows
    global root, geyser_root, geyser_listbox, geyser_scroll
    geyser_root = Tk()
    geyser_root.title("Recent Eruptions")
    root = Tk()
    root.title("Geyser Eruption Prediction")

    # Set up prediction gui
    titles.append(Label(root, text="Geyser", font=boldFont))
    titles.append(Label(root, text="Window Open", font=boldFont))
    titles.append(Label(root, text="Window Close", font=boldFont))
    titles.append(Label(root, text="Probability", font=boldFont))

    global cols
    cols = len(titles)
    for i in range(0, len(titles)):
        t_width = titles[i].winfo_reqwidth()
        titles[i].grid(row=row_offset - 1, column=i, padx=t_width * 0.1)
    root.update()
    width = root.winfo_width()

    attribute_label = Label(root, text=attribution, font=attributeFont,
                            wraplength=width, justify=CENTER)
    attribute_label.grid(row=0, column=0, columnspan=cols)

    root.after(0, update)

    # Set up recent eruption gui
    geyser_scroll = Scrollbar(master=geyser_root)
    geyser_scroll.pack(side=RIGHT, fill=Y)
    geyser_listbox = Listbox(master=geyser_root,
                             yscrollcommand=geyser_scroll.set, font=myFont)

    for g in geysers.values():
        geyser_listbox.insert(END, g["name"])
    geyser_listbox.pack(side=LEFT, fill=BOTH, expand=YES)
    geyser_scroll.config(command=geyser_listbox.yview)
    geyser_listbox.bind('<<ListboxSelect>>', get_recent)
    geyser_root.bind("<Configure>", resize)
    geyser_root.after(0, refresh())

    mainloop()


if __name__ == "__main__":
    sys.exit(main())
