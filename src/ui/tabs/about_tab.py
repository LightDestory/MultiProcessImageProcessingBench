import customtkinter


class AboutTab:
    _reference: customtkinter.CTkFrame
    _description_frame: customtkinter.CTkFrame
    _about_label_title: customtkinter.CTkLabel
    _about_label: customtkinter.CTkLabel
    _options_frame: customtkinter.CTkFrame
    _options_frame_title: customtkinter.CTkLabel
    _about_label_text: str = """
MultiProcess Image Processing is a tool designed for benchmarking parallelizable image processing algorithms using Python and the multiprocessing module. This tool enables users to assess the performance and efficiency of different image processing techniques when executed in parallel on multiple cores.

The tool provides a user-friendly interface that allows users to input their image, select a processing algorithm and specify the desired number of processes to be utilized. It then automatically divides the image data into manageable chunks and assigns them to separate processes for parallel execution.

This tool was developed as part of a final project for the course "Multimedia" at the University of Study of Catania, Department of Mathematics and Computer Science. 
"""
    _appearance_mode_label: customtkinter.CTkLabel
    _scaling_menu_label: customtkinter.CTkLabel
    _appearance_mode_menu: customtkinter.CTkOptionMenu
    _scaling_menu: customtkinter.CTkOptionMenu

    def __init__(self, container: customtkinter.CTkTabview):
        """
        Initializes the About tab.
        :param container:
        """
        self._reference = container.add("About")
        self._reference.columnconfigure(0, weight=1)

    def populate(self):
        """
        Populates the About tab by adding and griding widgets.
        :return:
        """
        # Description frame
        self._description_frame = customtkinter.CTkFrame(self._reference)
        self._description_frame.grid(row=0, column=0, sticky="nsew", pady=(20, 20), padx=(80, 80))
        self._description_frame.columnconfigure(0, weight=1)
        self._description_frame.rowconfigure((0, 1), weight=1)

        self._about_label_title = customtkinter.CTkLabel(self._description_frame, text="Description",
                                                         font=customtkinter.CTkFont(size=22, weight="bold"))
        self._about_label_title.grid(row=0, pady=(20, 0), sticky="new")
        self._about_label = customtkinter.CTkLabel(self._description_frame, text=self._about_label_text, justify="left",
                                                   font=customtkinter.CTkFont(size=18), wraplength=1000)
        self._about_label.grid(row=1, sticky="new")

        # Options frame
        self._options_frame = customtkinter.CTkFrame(self._reference)
        self._options_frame.grid(row=1, column=0, sticky="nsew", pady=(20, 20), padx=(80, 80), ipady=20)
        self._options_frame.columnconfigure((0, 1), weight=1)
        self._options_frame_title = customtkinter.CTkLabel(master=self._options_frame, text="Settings:",
                                                           font=customtkinter.CTkFont(size=22, weight="bold"))
        self._options_frame_title.grid(row=0, column=0, columnspan=2, pady=(20, 0), sticky="ewn")

        self._appearance_mode_label = customtkinter.CTkLabel(master=self._options_frame, text="Appearance Mode:",
                                                             font=customtkinter.CTkFont(size=18), justify="left")
        self._appearance_mode_label.grid(row=1, column=0, sticky="w", padx=(20, 0), pady=(20, 0))
        self._appearance_mode_menu = customtkinter.CTkOptionMenu(self._options_frame,
                                                                 values=["Light", "Dark", "System"],
                                                                 command=self.change_appearance_mode_event)
        self._appearance_mode_menu.grid(row=1, column=1, sticky="e", padx=(0, 20), pady=(20, 0))

        self._scaling_menu_label = customtkinter.CTkLabel(master=self._options_frame, text="Scaling:",
                                                          font=customtkinter.CTkFont(size=18), justify="left")
        self._scaling_menu_label.grid(row=2, column=0, sticky="w", padx=(20, 0), pady=(20, 0))
        self._scaling_menu = customtkinter.CTkOptionMenu(self._options_frame,
                                                         values=["80%", "90%", "100%", "110%"],
                                                         command=self.change_scaling_event)
        self._scaling_menu.grid(row=2, column=1, sticky="e", padx=(0, 20), pady=(20, 0))

        # Default values
        self._appearance_mode_menu.set("System")
        self._scaling_menu.set("100%")

    def change_appearance_mode_event(self, new_appearance_mode: str) -> None:
        """
        Changes the appearance mode of the GUI.
        :param new_appearance_mode: The selected appearance mode.
        :return:
        """
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str) -> None:
        """
        Changes the scaling of the GUI.
        :param new_scaling: A percentage value.
        :return:
        """
        customtkinter.set_widget_scaling(int(new_scaling.replace("%", "")) / 100)
