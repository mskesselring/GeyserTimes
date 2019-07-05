from tkinter import *
import requests
import json
import datetime
from tkinter import messagebox
import tkinter.ttk


class History:

    def __init__(self, freq, DEBUG, url, myFont, format_string):
        self.freq = freq
        self.myFont = myFont
        self.DEBUG = DEBUG
        self.url = url
        self.geysers = {}
        self.entries = {}
        self.format_string = format_string
        self.openWindows = {}
        self.recent = {}

        # Get list of geysers
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
        groups = set()
        for g in geyser_list:
            groups.add(g["groupName"])
            if ("Uncommon" not in g["groupName"]) and (
                    "Other" not in g["groupName"]):
                self.geysers[g["name"]] = g
                tmp.append(g["id"])
        tmp.sort(key=lambda x: int(x))
        self.entry_string = ";".join(tmp)
        # Print list of geyser groups
        # for i in groups:
        #     print(i)

        # Create GUI
        self.root = Tk()
        self.root.title("Recent Eruptions")
        self.geyser_scroll = Scrollbar(master=self.root)
        self.geyser_scroll.pack(side=RIGHT, fill=Y)
        self.geyser_listbox = Listbox(master=self.root,
                                      yscrollcommand=self.geyser_scroll.set,
                                      font=self.myFont)

        for g in self.geysers.values():
            self.geyser_listbox.insert(END, g["name"])
        self.geyser_listbox.pack(side=LEFT, fill=BOTH, expand=YES)
        self.geyser_scroll.config(command=self.geyser_listbox.yview)
        self.geyser_listbox.bind('<<ListboxSelect>>', self.get_recent)
        self.root.bind("<Configure>", self.resize)
        self.root.after(0, self.refresh())

    def resize(self, e=None):
        """
        Resize listbox and scrollbar on window resize
        @param e: Event
        @return: None
        """
        if self.DEBUG:
            print(e)
        self.geyser_scroll.pack(side=RIGHT, fill=Y)
        self.geyser_listbox.pack(side=LEFT, fill=BOTH, expand=YES)

    def refresh(self):
        """
        Get most recent eruption for all geysers
        @return: None
        """
        if not self.DEBUG:
            r = requests.get(self.url["entries"] + "/" + self.entry_string)
            r = r.json()
            data = r["entries"]
            with open("entries.json", "w") as json_file:
                json.dump(data, json_file)
        else:
            with open("entries.json") as json_file:
                data = json.load(json_file)
        for e in data:
            self.entries[e["geyserID"]] = e
        self.root.after(self.freq, self.refresh)

    def get_recent(self, e=None):
        """
        Display most recent eruption for selected geyser
        @param e: Event
        @return: None
        """
        if self.DEBUG:
            print(e)
        name = self.geyser_listbox.get(self.geyser_listbox.curselection())
        geyser_id = self.geysers[name]["id"]
        if geyser_id in self.entries:
            recent = self.entries[geyser_id]
            time = datetime.datetime.fromtimestamp(int(recent["time"]))
            time_str = time.strftime(self.format_string)
            if bool(int(recent["maj"])):
                event_type = "Major"
            else:
                event_type = "Minor"
            message = "Last Eruption: %s, Eruption Type: %s" % (
                time_str, event_type)
            if name not in self.openWindows.keys():
                self.openWindows[name] = Tk()
                self.openWindows[name].title(name)
                self.recent[name] = Label(self.openWindows[name], text=message,
                                          font=self.myFont)
                self.recent[name].pack()
                self.openWindows[name].protocol("WM_DELETE_WINDOW", lambda
                    obj=name: self.on_closing(obj))
            else:
                self.recent[name].text = message
                self.recent[name].pack()
                self.openWindows[name].lift()
        else:
            tkinter.messagebox.showerror(name,
                                         "No entries found for" + name)

    def on_closing(self, obj):
        caller = self.openWindows[obj]
        caller.destroy()
        if obj in self.openWindows.keys():
            del self.openWindows[obj]
