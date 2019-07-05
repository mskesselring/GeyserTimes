from tkinter import *
from prediction import Predictions
from history import History

DEBUG = bool(0)
url = {
    "base"       : "https://www.geysertimes.org/api/v5",
    "geysers"    : "https://www.geysertimes.org/api/v5/geysers",
    "predictions": "https://www.geysertimes.org/api/v5/predictions_latest",
    "entries"    : "https://www.geysertimes.org/api/v5/entries_latest"
}
format_string = "%h %d %I:%M %p"
update_format = "%h %d %I:%M:%S %p"
center_format = None
freq = int(1000 * 60 * 5)  # ms/s * s/min * min
prediction_window = None
history_window = None
attributeFont = ("Calibri", "10")
boldFont = ("Calibri", "12", "bold")
myFont = ("Calibri", "12")


def main():
    """
    Set up GUIs
    @return: None
    """
    # Create GUI windows
    global prediction_window, history_window
    history_window = History(freq=freq, DEBUG=DEBUG, url=url, myFont=myFont,
                             format_string=format_string)
    prediction_window = Predictions(freq=freq, boldFont=boldFont, myFont=myFont,
                                    attributeFont=attributeFont, DEBUG=DEBUG,
                                    update_format=update_format, url=url,
                                    format_string=format_string)
    mainloop()


if __name__ == "__main__":
    sys.exit(main())
