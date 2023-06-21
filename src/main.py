import multiprocessing
import sys, os
from ui.gui_interface import App

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        multiprocessing.freeze_support()
    app = App()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        app.destroy()
