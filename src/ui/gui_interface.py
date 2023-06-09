import customtkinter

from .tabs.about_tab import AboutTab
from .tabs.main_tab import MainTab

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")


class App(customtkinter.CTk):
    _window_width: int = 1400
    _window_height: int = 700

    _tabview_container: customtkinter.CTkTabview

    def __init__(self):
        super().__init__()

        self._setup_window()
        self._populate_tabview()

    def _setup_window(self) -> None:
        """
        Sets up the window.
        :return:
        """
        self.title("MultiProcess Image Processing")
        x_offset: int = int((self.winfo_screenwidth() / 2) - (self._window_width / 2))
        y_offset: int = int((self.winfo_screenheight() / 2) - (self._window_height / 2))
        self.geometry("{}x{}+{}+{}".format(self._window_width, self._window_height, x_offset, y_offset))
        self.configure(fg_color=("gray86", "gray17"))
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def _populate_tabview(self) -> None:
        """
        Populates the tabview.
        :return:
        """
        self._tabview_container = customtkinter.CTkTabview(master=self, width=self._window_width,
                                                           height=self._window_height)
        self._tabview_container.grid(row=0, column=0, sticky="nsew")
        MainTab(self._tabview_container).populate()
        self._tabview_container.add("Benchmark")
        AboutTab(self._tabview_container).populate()