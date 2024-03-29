import pprint
import threading
import time
import sys
import customtkinter
import multiprocessing
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from multiprocessing import Pool
from multiprocessing.pool import Pool as PoolType
from CTkMessagebox import CTkMessagebox
from customtkinter import filedialog

CURRENT_POSITION = Path(__file__).parent
sys.path.append(f"{CURRENT_POSITION}/../../../")
from src.algorithms import morphological_operators, convolution, noise_reduction, canny
from ..components.image_viewer_top_level import ImageViewerTopLevel
from .bench_tab import BenchTab


def generic_benchmark(target_image: Image.Image, selected_algorithm_type: str,
                      selected_algorithm_sub_type: str) -> Image.Image:
    if selected_algorithm_type == convolution.name_native:
        return convolution.convolve_native(target_image,
                                           convolution.convolution_kernels[selected_algorithm_sub_type],
                                           "edge_detection" in selected_algorithm_sub_type)
    elif selected_algorithm_type == convolution.name_lib:
        return convolution.convolve_lib(target_image, convolution.convolution_kernels[selected_algorithm_sub_type],
                                        "edge_detection" in selected_algorithm_sub_type)
    else:
        raise ValueError(f"Invalid algorithm type: {selected_algorithm_type}")


def one_parameter_benchmark(target_image: Image.Image, algorithm: str, parameter) -> Image.Image:
    if algorithm == noise_reduction.noise_reduction_sub_types[0]:
        return noise_reduction.mean_filter(target_image, parameter)
    elif algorithm == convolution.name_native:
        return convolution.convolve_native(target_image, parameter)
    elif algorithm == convolution.name_lib:
        return convolution.convolve_lib(target_image, parameter)


def two_parameter_benchmark(target_image: Image.Image, algorithm: str, parameter_1, parameter_2) -> Image.Image:
    if algorithm == morphological_operators.name:
        return morphological_operators.morphological_operate(target_image, parameter_1, parameter_2)


def three_parameters_benchmark(target_image: Image.Image,
                               algorithm: str, parameter_1, parameter_2,
                               parameter_3) -> Image.Image:
    if algorithm == noise_reduction.noise_reduction_sub_types[1]:
        return noise_reduction.bilateral_filter(target_image, parameter_1, parameter_2, parameter_3)


def four_parameters_benchmark(target_image: Image.Image,
                              algorithm: str, parameter_1, parameter_2,
                              parameter_3, parameter_4) -> Image.Image:
    if algorithm == canny.name:
        return canny.canny_edge_detector(target_image, parameter_1, parameter_2, parameter_3, parameter_4)


class MainTab:
    # tkinter widgets
    _reference: customtkinter.CTkFrame
    _benchmark_tab: BenchTab
    _main_container: customtkinter.CTkFrame
    _load_image_btn: customtkinter.CTkButton
    _image_viewer: customtkinter.CTkLabel
    _image_thumbnail: customtkinter.CTkImage
    _image_selector_title: customtkinter.CTkLabel
    _image_path_label: customtkinter.CTkLabel
    _image_path: customtkinter.CTkLabel
    _image_size_label: customtkinter.CTkLabel
    _image_size: customtkinter.CTkLabel
    _benchmark_selector_title: customtkinter.CTkLabel
    _cpu_core_text: customtkinter.CTkLabel
    _cpu_core_label: customtkinter.CTkLabel
    _cpu_core_slider_workers_frame: customtkinter.CTkFrame
    _cpu_core_progress_bar: customtkinter.CTkProgressBar
    _cpu_core_slider: customtkinter.CTkSlider
    _bench_all_checkbox: customtkinter.CTkCheckBox
    _image_options_label: customtkinter.CTkLabel
    _image_divider_switch: customtkinter.CTkSwitch
    _square_division_warning_label: customtkinter.CTkLabel
    _bench_start_btn: customtkinter.CTkButton
    _bench_interrupt_btn: customtkinter.CTkButton
    _bench_progress_bar: customtkinter.CTkProgressBar
    _algorithm_label: customtkinter.CTkLabel
    _algorithm_type_menu: customtkinter.CTkOptionMenu
    _algorithm_sub_type_menu: customtkinter.CTkOptionMenu
    _status_text: customtkinter.CTkLabel
    _status_label: customtkinter.CTkLabel
    # Image Viewer Widget
    _top_level_image_viewer: ImageViewerTopLevel | None = None
    # Function references
    _preview_image_divider_implementation: callable
    _image_divider_implementation: callable
    _image_merger_implementation: callable
    # Implemented algorithms (Name, HasSubTypes)
    _implemented_algorithms: dict[str, bool] = {
        convolution.name_native: True,
        convolution.name_lib: True,
        morphological_operators.name: True,
        noise_reduction.name: True,
        canny.name: False
    }
    # Algorithm states
    _selected_algorithm_type: str = ""
    _selected_algorithm_sub_type: str = ""
    _selected_algorithm_params: dict[str, dict] = {}
    _specialized_runners: dict[str, callable] = {
        convolution.parameterized_kernel_list[0]: one_parameter_benchmark,
        noise_reduction.noise_reduction_sub_types[0]: one_parameter_benchmark,
        noise_reduction.noise_reduction_sub_types[1]: three_parameters_benchmark,
        canny.name: four_parameters_benchmark,
        morphological_operators.morphological_sub_types[0]: two_parameter_benchmark,
        morphological_operators.morphological_sub_types[1]: two_parameter_benchmark
    }
    # Logic states
    _available_cpu_core: int = multiprocessing.cpu_count()
    _target_cpu_core_set: int = 1
    _target_image: Image.Image | None = None
    _resized_target_image: Image.Image | None = None
    _bench_all_configurations: bool = False
    _is_square_dividing: bool = False
    _bench_interrupt_signal: bool = False
    _latest_bench_pool: PoolType | None = None

    def __init__(self, container: customtkinter.CTkTabview):
        """
        Initializes the Main tab.
        :param container: Container to add the Main tab to.
        """
        self._reference = container.add("Main")
        self._reference.columnconfigure(0, weight=1)
        self._preview_image_divider_implementation = self._preview_line_image_sub_divider
        self._image_divider_implementation = self._line_image_sub_divider
        self._image_merger_implementation = self._merge_image_lines

    def link_bench_tab(self, bench_tab: BenchTab) -> None:
        """
        Links the Bench tab to the Main tab.
        :param bench_tab: Bench tab to link.
        :return:
        """
        self._benchmark_tab = bench_tab

    def populate(self) -> None:
        """
        Populates the Main tab by adding and griding widgets.
        :return:
        """
        # Main frame
        self._main_container = customtkinter.CTkFrame(self._reference)
        self._main_container.grid(row=0, column=0, sticky="nsew", pady=(20, 20), padx=(80, 80))
        self._main_container.columnconfigure((0, 1, 2), weight=1)
        self._main_container.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), weight=1)
        # Image Selection title
        self._image_selector_title = customtkinter.CTkLabel(self._main_container, text="Select an Image:",
                                                            font=customtkinter.CTkFont(size=22, weight="bold"))
        self._image_selector_title.grid(row=0, column=0, pady=(10, 0), sticky="nw", padx=(20, 0))
        # Load image button
        self._load_image_btn = customtkinter.CTkButton(self._main_container, text="Load Image from disk",
                                                       command=self._import_image)
        self._load_image_btn.grid(row=0, column=1, sticky="ewn", pady=(10, 0))
        # Image viewer
        self._image_thumbnail = customtkinter.CTkImage(light_image=Image.new("RGB", (512, 512), color="#dbdbdb"),
                                                       dark_image=Image.new("RGB", (512, 512), color="#2b2b2b"),
                                                       size=(512, 512))
        self._image_viewer = customtkinter.CTkLabel(self._main_container, text="", image=self._image_thumbnail)
        self._image_viewer.grid(row=0, rowspan=12, column=2, sticky="ne", pady=(10, 10), padx=(0, 20))
        self._image_viewer.bind("<Button-1>", self._on_preview_image_click)
        # Image path label
        self._image_path_label = customtkinter.CTkLabel(self._main_container, text="Filename:",
                                                        font=customtkinter.CTkFont(size=18))
        self._image_path_label.grid(row=1, column=0, sticky="nw", padx=(20, 0))
        # Image path
        self._image_path = customtkinter.CTkLabel(self._main_container, text="",
                                                  font=customtkinter.CTkFont(size=18, slant="italic"))
        self._image_path.grid(row=1, column=1, sticky="nw", padx=(20, 0))
        # Image size label
        self._image_size_label = customtkinter.CTkLabel(self._main_container, text="File size:",
                                                        font=customtkinter.CTkFont(size=18))
        self._image_size_label.grid(row=2, column=0, sticky="nw", padx=(20, 0))
        # Image size
        self._image_size = customtkinter.CTkLabel(self._main_container, text="",
                                                  font=customtkinter.CTkFont(size=18, slant="italic"))
        self._image_size.grid(row=2, column=1, sticky="nw", padx=(20, 0))
        # MultiProcess Options title
        self._benchmark_selector_title = customtkinter.CTkLabel(self._main_container,
                                                                text="MultiProcess Options:",
                                                                font=customtkinter.CTkFont(size=22, weight="bold"))
        self._benchmark_selector_title.grid(row=3, column=0, sticky="nw", padx=(20, 0))
        # CPU core label
        self._cpu_core_label = customtkinter.CTkLabel(self._main_container,
                                                      text=f"Worker Cores ({self._available_cpu_core} CPU cores available):",
                                                      font=customtkinter.CTkFont(size=18))
        self._cpu_core_label.grid(row=4, column=0, sticky="nw", padx=(20, 0))
        # CPU core text
        self._cpu_core_text = customtkinter.CTkLabel(self._main_container, text="1",
                                                     font=customtkinter.CTkFont(size=18, slant="italic"))
        self._cpu_core_text.grid(row=4, column=1, sticky="new", padx=(20, 0))
        # CPU core slider frame
        self._cpu_core_slider_workers_frame = customtkinter.CTkFrame(self._main_container, fg_color="transparent")
        self._cpu_core_slider_workers_frame.grid(row=5, column=1, sticky="nsew")
        self._cpu_core_slider_workers_frame.grid_columnconfigure(0, weight=1)
        # CPU core progress bar
        self._cpu_core_progress_bar = customtkinter.CTkProgressBar(self._cpu_core_slider_workers_frame)
        self._cpu_core_progress_bar.grid(row=0, column=0, sticky="enw")
        # CPU core slider
        self._cpu_core_slider = customtkinter.CTkSlider(self._cpu_core_slider_workers_frame, from_=1, to=16,
                                                        number_of_steps=self._available_cpu_core - 1,
                                                        command=self._on_cpu_core_slider_change)
        self._cpu_core_slider.grid(row=1, column=0, sticky="enw", pady=(10, 0))
        # Bench all checkbox
        self._bench_all_checkbox = customtkinter.CTkCheckBox(self._main_container,
                                                             font=customtkinter.CTkFont(size=18),
                                                             text="Bench all available cores sets",
                                                             command=self._on_bench_all_checkbox_change)
        self._bench_all_checkbox.grid(row=5, column=0, padx=(30, 0), sticky="wne")
        # Image Processing Options title
        self._image_options_label = customtkinter.CTkLabel(self._main_container, text="Image Processing Options:",
                                                           font=customtkinter.CTkFont(size=22, weight="bold"))
        self._image_options_label.grid(row=6, column=0, sticky="nw", padx=(20, 0))
        # Image divider switch
        self._image_divider_switch = customtkinter.CTkSwitch(self._main_container,
                                                             text="Divide image using lines",
                                                             command=self._on_divider_switch_change,
                                                             font=customtkinter.CTkFont(size=18))
        self._image_divider_switch.grid(row=7, column=0, padx=(30, 0), pady=(5, 0), sticky="wne")
        # Image divider label
        self._square_division_warning_label = customtkinter.CTkLabel(self._main_container,
                                                                     text="Workers must be a square number",
                                                                     font=customtkinter.CTkFont(size=18),
                                                                     text_color="red")
        # Algorithm label
        self._algorithm_label = customtkinter.CTkLabel(self._main_container, text=f"Algorithm to use:",
                                                       font=customtkinter.CTkFont(size=18))
        self._algorithm_label.grid(row=8, column=0, sticky="nw", padx=(20, 0))
        # Algorithm type menu
        self._algorithm_type_menu = customtkinter.CTkOptionMenu(self._main_container, width=230,
                                                                values=list(self._implemented_algorithms.keys()),
                                                                command=self._on_algorithm_type_menu_change)
        self._algorithm_type_menu.grid(row=9, column=0, sticky="nw", padx=(60, 0))
        # Algorithm sub_type menu
        self._algorithm_sub_type_menu = customtkinter.CTkOptionMenu(self._main_container, dynamic_resizing=False,
                                                                    width=200,
                                                                    command=self._on_algorithm_sub_type_menu_change)

        # Status label
        self._status_label = customtkinter.CTkLabel(self._main_container, text="Status:",
                                                    font=customtkinter.CTkFont(size=18, weight="bold"))
        self._status_label.grid(row=10, column=0, sticky="nw", padx=(20, 0))

        # Start benchmark button
        self._bench_start_btn = customtkinter.CTkButton(self._main_container, text="Start Benchmark", width=200,
                                                        command=self._on_start_bench_btn)
        self._bench_start_btn.grid(row=11, column=0, padx=(0, 50), sticky="en", pady=(10, 10))
        # Start Interrupt button
        self._bench_interrupt_btn = customtkinter.CTkButton(self._main_container, text="Stop Benchmark", width=200,
                                                            command=self._on_interrupt_bench_btn, state="disabled",
                                                            fg_color="#c40000", hover_color="#780000")
        self._bench_interrupt_btn.grid(row=11, column=1, sticky="wn", pady=(10, 10))
        # Benchmark progress bar
        self._bench_progress_bar = customtkinter.CTkProgressBar(self._main_container, mode="indeterminate",
                                                                indeterminate_speed=0.5, width=512)
        # Status text
        self._status_text = customtkinter.CTkLabel(self._main_container, text="Waiting for benchmark to start...",
                                                   font=customtkinter.CTkFont(size=18))
        self._status_text.grid(row=12, column=0, columnspan=3, sticky="nw", padx=(20, 0), pady=(0, 20))

        # Default values
        self._cpu_core_slider.set(1)
        self._cpu_core_progress_bar.set(0)
        self._bench_progress_bar.start()
        self._on_algorithm_type_menu_change(self._algorithm_type_menu.get())

    def _import_image(self) -> None:
        """
        Import an image to be processed. If the image is not a square, ask the user if they want to resize it.
        :return:
        """
        filepath: str = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        title_text: str = "Importing Image"
        if not filepath:
            CTkMessagebox(title=title_text, message="Image loading cancelled.", icon="warning")
            return
        temp_image: Image.Image = Image.open(filepath)
        width, height = temp_image.size
        if width != height:
            new_size: int = 2 ** (int(math.log2(max(width, height))) + 1)
            resize_question: CTkMessagebox = CTkMessagebox(title=title_text,
                                                           message=f"The image MUST be a square. Resize it to {new_size}x{new_size}?\nDeclining will cancel the import.",
                                                           icon="question", option_1="No", option_2="Yes")
            if resize_question.get() == "Yes":
                temp_image = temp_image.resize((new_size, new_size))
            else:
                CTkMessagebox(title=title_text, message="Image loading cancelled.", icon="warning")
                return
        self._target_image = temp_image
        self._resized_target_image = self._target_image.copy().resize((512, 512))
        self._image_path.configure(text=f"{filepath.split('/')[-1]} ")
        self._image_size.configure(text=f"{self._target_image.size[0]}x{self._target_image.size[0]} ")
        self._update_image_preview()
        self._refresh_top_level()

    def _update_image_preview(self) -> None:
        """
        Update the image preview.
        :return:
        """
        if self._target_image is None:
            return
        self._image_thumbnail = customtkinter.CTkImage(light_image=self._preview_image_divider_implementation(),
                                                       size=(512, 512))
        self._image_viewer.configure(image=self._image_thumbnail)

    def _preview_line_image_sub_divider(self) -> Image.Image:
        """
        Preview the image divider using lines.
        :return: A preview of the image divider using lines.
        """
        tmp_image: Image.Image = self._resized_target_image.copy()
        if self._target_cpu_core_set == 1:
            return tmp_image
        line_width = 512 // self._target_cpu_core_set
        draw = ImageDraw.Draw(tmp_image)
        for i in range(1, self._target_cpu_core_set):
            left = i * line_width
            draw.line((left, 0, left, 512), fill=(255, 0, 0), width=2)
        return tmp_image

    def _line_image_sub_divider(self) -> list[Image.Image]:
        """
        Divide the image using lines.
        :return: A list of the lines that the image is divided into.
        """
        tmp_image: Image.Image = self._target_image.copy()
        if self._target_cpu_core_set == 1:
            return [tmp_image]
        sub_images: list[Image.Image] = []
        line_width = tmp_image.width // self._target_cpu_core_set
        for i in range(self._target_cpu_core_set):
            left = i * line_width
            right = left + line_width
            sub_images.append(tmp_image.crop((left, 0, right, tmp_image.height)))
        return sub_images

    def _merge_image_lines(self, lines: list[Image.Image]) -> Image.Image:
        """
        Merge the lines of an image into one image.
        :param lines: The lines to merge.
        :return: The merged image.
        """
        if len(lines) == 1:
            return lines[0]
        tmp_image = Image.new("RGBA", self._target_image.size)
        line_width = tmp_image.width // self._target_cpu_core_set
        for i in range(self._target_cpu_core_set):
            left = i * line_width
            right = left + line_width
            tmp_image.paste(lines[i], (left, 0, right, tmp_image.height))
        return tmp_image

    def _preview_square_image_sub_divider(self) -> Image.Image:
        """
        Preview the image divider using squares.
        :return: The preview of the image divider using squares.
        """
        tmp_image: Image.Image = self._resized_target_image.copy()
        draw = ImageDraw.Draw(tmp_image)
        if self._is_square_doable() is False:
            draw.text((100, 225), "ERROR:\nThe number of CPU cores must \nbe a square number.", fill=(255, 0, 0),
                      stroke_fill=(0, 0, 0), stroke_width=3, font=ImageFont.truetype("arial.ttf", 22))
        else:
            num_parts: int = int(self._target_cpu_core_set ** 0.5)
            square_size: int = 512 // num_parts
            for row in range(num_parts):
                for column in range(num_parts):
                    x_start: int = column * square_size
                    y_start: int = row * square_size
                    x_end: int = x_start + square_size
                    y_end: int = y_start + square_size
                    draw.rectangle((x_start, y_start, x_end, y_end), outline=(255, 0, 0), width=2)
        return tmp_image

    def _square_image_sub_divider(self) -> list[Image.Image]:
        """
        Divide the image using squares.
        :return: A list of the squares that the image is divided into.
        """
        tmp_image: Image.Image = self._target_image.copy()
        if self._target_cpu_core_set == 1:
            return [tmp_image]
        else:
            num_parts: int = int(self._target_cpu_core_set ** 0.5)
            square_size: int = tmp_image.width // num_parts
            sub_images: list[Image.Image] = []
            for row in range(num_parts):
                for column in range(num_parts):
                    x_start: int = column * square_size
                    y_start: int = row * square_size
                    x_end: int = x_start + square_size
                    y_end: int = y_start + square_size
                    sub_images.append(tmp_image.crop((x_start, y_start, x_end, y_end)))
        return sub_images

    def _merge_image_squares(self, squares: list[Image.Image]) -> Image.Image:
        """
        Merge the squares of an image into one image.
        :param squares: The squares to merge.
        :return: The merged image.
        """
        if len(squares) == 1:
            return squares[0]
        tmp_image = Image.new("RGBA", self._target_image.size)
        square_size: int = squares[0].width
        iterator: int = int(len(squares) ** 0.5)
        for row in range(iterator):
            for column in range(iterator):
                x_start: int = column * square_size
                y_start: int = row * square_size
                x_end: int = x_start + square_size
                y_end: int = y_start + square_size
                tmp_image.paste(squares[row * iterator + column], (x_start, y_start, x_end, y_end))
        return tmp_image

    def _refresh_top_level(self) -> None:
        """
        Refresh the top level window.
        :return:
        """
        if self._top_level_image_viewer is None or not self._top_level_image_viewer.winfo_exists():
            return
        self._top_level_image_viewer.set_image(self._target_image)

    def _on_preview_image_click(self, _) -> None:
        """
        Called when the preview image is clicked. Opens the image in the image viewer.
        :return:
        """
        if self._target_image is None:
            return
        if self._top_level_image_viewer is None or not self._top_level_image_viewer.winfo_exists():
            self._top_level_image_viewer = ImageViewerTopLevel()
            self._top_level_image_viewer.title("Image Viewer - MainTab")
        else:
            self._top_level_image_viewer.focus()
        self._refresh_top_level()

    def _on_cpu_core_slider_change(self, value: float) -> None:
        """
        Called when the CPU core slider is changed. Updates the CPU core text, progress bar and refreshes the preview.
        :param value: The current value of the slider.
        :return:
        """
        int_value: int = int(value)
        if int_value == self._target_cpu_core_set:
            return
        self._target_cpu_core_set = int_value
        if int_value == 1:
            self._cpu_core_progress_bar.set(0)
        else:
            self._cpu_core_progress_bar.set((int_value / self._available_cpu_core))
        self._cpu_core_text.configure(text=f"{int(value)} ")
        self._update_image_preview()

    def _on_bench_all_checkbox_change(self) -> None:
        """
        Called when the bench all checkbox is changed.
        :return:
        """
        self._bench_all_configurations = bool(self._bench_all_checkbox.get())
        if self._bench_all_configurations:
            self._cpu_core_text.configure(text=f"∞ ")
            self._cpu_core_slider.configure(state="disabled")
            self._cpu_core_slider.configure(button_color="red")
            self._cpu_core_progress_bar.configure(progress_color="red")
            self._target_cpu_core_set = 1
        else:
            self._target_cpu_core_set = int(self._cpu_core_slider.get())
            self._cpu_core_slider.configure(state="normal")
            self._cpu_core_text.configure(text=f"{self._target_cpu_core_set} ")
            self._cpu_core_slider.configure(button_color=("#2CC985", "#2FA572"))
            self._cpu_core_progress_bar.configure(progress_color=("#2CC985", "#2FA572"))
        self._update_image_preview()

    def _on_divider_switch_change(self) -> None:
        """
        Called when the image divider switch is changed. Updates the switch text, implementation references and
        refreshes the preview.
        :return:
        """
        self._is_square_dividing = bool(self._image_divider_switch.get())
        if self._is_square_dividing:
            self._image_divider_switch.configure(text="Divide image using squares")
            self._preview_image_divider_implementation = self._preview_square_image_sub_divider
            self._image_divider_implementation = self._square_image_sub_divider
            self._image_merger_implementation = self._merge_image_squares
            self._square_division_warning_label.grid(row=7, column=1, columnspan=2, sticky="wn")

        else:
            self._image_divider_switch.configure(text="Divide image using lines")
            self._preview_image_divider_implementation = self._preview_line_image_sub_divider
            self._image_divider_implementation = self._line_image_sub_divider
            self._image_merger_implementation = self._merge_image_lines
            self._square_division_warning_label.grid_forget()
        self._update_image_preview()

    def _toggle_controls(self) -> None:
        """
        Toggles the controls of the tab.
        :return:
        """
        toggled: str = "disabled" if self._load_image_btn.cget("state") == "normal" else "normal"
        self._bench_start_btn.configure(state=toggled)
        self._load_image_btn.configure(state=toggled)
        self._image_divider_switch.configure(state=toggled)
        self._bench_all_checkbox.configure(state=toggled)
        if not self._bench_all_configurations:
            self._cpu_core_slider.configure(state=toggled)
        self._algorithm_type_menu.configure(state=toggled)
        self._algorithm_sub_type_menu.configure(state=toggled)
        if toggled == "normal":
            self._bench_interrupt_btn.configure(state="disabled")
            self._bench_progress_bar.grid_forget()
        else:
            self._bench_interrupt_btn.configure(state="normal")
            self._bench_progress_bar.grid(row=12, column=2, sticky="e", padx=(0, 20))

    def _is_square_doable(self) -> bool:
        """
        Returns whether the square division is doable or not.
        :return: A boolean value indicating whether the square division is doable or not.
        """
        return (self._target_cpu_core_set ** 0.5).is_integer()

    def _on_algorithm_type_menu_change(self, value: str) -> None:
        """
        Called when the algorithm type menu is changed.
        :param value: The new value of the algorithm type menu.
        :return:
        """
        if value == self._selected_algorithm_type:
            return
        self._selected_algorithm_sub_type = ""
        self._selected_algorithm_type = value
        if self._implemented_algorithms[value]:
            self._configure_sub_type()
        else:
            self._algorithm_sub_type_menu.grid_forget()
            self._check_algorithm_params()

    def _configure_sub_type(self) -> None:
        """
        Configures the algorithm sub type menu.
        :return:
        """
        if self._selected_algorithm_type in [convolution.name_native, convolution.name_lib]:
            values = list(convolution.convolution_kernels.keys())
            for parameterized_kernel in convolution.parameterized_kernel_list:
                if parameterized_kernel not in values:
                    values.append(parameterized_kernel)
        elif self._selected_algorithm_type == morphological_operators.name:
            values = morphological_operators.morphological_sub_types
        elif self._selected_algorithm_type == noise_reduction.name:
            values = noise_reduction.noise_reduction_sub_types
        else:
            raise NotImplementedError(f"Algorithm type {self._selected_algorithm_type} has not sub types "
                                      f"implemented yet.")
        self._algorithm_sub_type_menu.configure(values=values)
        self._algorithm_sub_type_menu.grid(row=9, column=1, sticky="new", padx=(0, 20))
        self._algorithm_sub_type_menu.set(values[0])
        self._on_algorithm_sub_type_menu_change(values[0])

    def _on_algorithm_sub_type_menu_change(self, value: str) -> None:
        """
        Called when the algorithm sub type menu is changed. Updates the selected algorithm sub type.
        :param value: The new value of the algorithm sub type menu.
        :return:
        """
        if value == self._selected_algorithm_sub_type:
            return
        self._selected_algorithm_sub_type = value
        self._check_algorithm_params()

    def _check_algorithm_params(self) -> None:
        """
        Checks and updates the algorithm parameters.
        :return:
        """
        self._selected_algorithm_params = {}
        if self._selected_algorithm_type == canny.name:
            self._selected_algorithm_params = {
                "gauss_size": {"value": 3, "type": int},
                "sigma": {"value": 1, "type": float},
                "low_threshold": {"value": 20, "type": int},
                "high_threshold": {"value": 40, "type": int}
            }
        elif self._selected_algorithm_sub_type in morphological_operators.morphological_sub_types:
            self._selected_algorithm_params = {
                "structural_element": {"value": "square", "type": str,
                                       "choices": list(morphological_operators.structural_elements.keys())},
            }
        elif self._selected_algorithm_sub_type == noise_reduction.noise_reduction_sub_types[0]:
            self._selected_algorithm_params = {"kernel_size": {"value": 3, "type": int}}
        elif self._selected_algorithm_sub_type == noise_reduction.noise_reduction_sub_types[1]:
            self._selected_algorithm_params = {
                "diameter": {"value": 5, "type": int},
                "sigma_color": {"value": 10, "type": int},
                "sigma_space": {"value": 15, "type": int}
            }
        elif self._selected_algorithm_sub_type == convolution.parameterized_kernel_list[0]:
            self._selected_algorithm_params = {
                "kernel_size": {"value": 3, "type": int},
                "sigma": {"value": 1, "type": int}
            }
        if not self._selected_algorithm_params:
            return
        for param in self._selected_algorithm_params.keys():
            user_input_failed: bool = False
            text: str = f"Insert the value for '{param}' parameter.\nDefault value is {self._selected_algorithm_params[param]['value']}"
            if "choices" in self._selected_algorithm_params[param]:
                text += f"\nAvailable choices are: {self._selected_algorithm_params[param]['choices']}"
            user_input: str = customtkinter.CTkInputDialog(text=text,
                                                           title=f"Algorithms Parameters").get_input()
            param_type = self._selected_algorithm_params[param]["type"]
            if param_type == str:
                if user_input not in self._selected_algorithm_params[param]["choices"]:
                    user_input_failed = True
                else:
                    self._selected_algorithm_params[param]["value"] = user_input
            else:
                if not user_input.isdecimal() or int(user_input) <= 0:
                    user_input_failed = True
                else:
                    self._selected_algorithm_params[param]["value"] = param_type(user_input)
            if user_input_failed:
                CTkMessagebox(title="Invalid input",
                              message=f"The value {user_input} is not a valid parameter for '{param}'.\n"
                                      f"Fallback to default value: {self._selected_algorithm_params[param]['value']}",
                              icon="warning")
        if self._selected_algorithm_sub_type == convolution.parameterized_kernel_list[0]:
            convolution.convolution_kernels[self._selected_algorithm_sub_type] = convolution.generate_gauss_kernel(
                self._selected_algorithm_params["kernel_size"]["value"],
                self._selected_algorithm_params["sigma"]["value"]
            )

    def _get_bench_configuration_sets(self) -> list[int]:
        """
        Returns the set of configurations to be benchmarked.
        :return: The set of configurations to be benchmarked.
        """
        result: list[int] = [1]
        if not self._bench_all_configurations:
            result.append(self._target_cpu_core_set)
        else:
            if not self._is_square_dividing:
                result += range(2, self._available_cpu_core + 1)
            else:
                upper_bound: int = int(math.sqrt(self._available_cpu_core))
                result += [i * i for i in range(2, upper_bound + 1)]
        return sorted(set(result))

    def _on_start_bench_btn(self) -> None:
        """
        Called when the start benchmark button is pressed. Starts the benchmark.
        :return:
        """
        if self._target_image is None:
            CTkMessagebox(title="No image selected", message="Please select an image and then run the benchmark.",
                          icon="warning")
            return
        if self._is_square_dividing and not self._is_square_doable():
            CTkMessagebox(title="Invalid settings", message="To perform a square division the image must be square.",
                          icon="warning")
            return
        self._toggle_controls()
        t = threading.Thread(target=self._bench_dispatch)
        t.start()

    def _on_interrupt_bench_btn(self) -> None:
        """
        Called when the interrupt benchmark button is pressed. Stops the benchmark.
        :return:
        """
        if self._bench_interrupt_signal:
            return
        self._bench_interrupt_signal = True

    def _bench_dispatch(self) -> None:
        result_timestamps: dict[str, float] = {}
        bench_config_sets: list[int] = self._get_bench_configuration_sets()
        result_image: Image.Image | None = None
        algorithm: str = self._selected_algorithm_sub_type if self._selected_algorithm_sub_type else self._selected_algorithm_type
        if algorithm in self._specialized_runners:
            benchmark: callable = self._specialized_runners[algorithm]
        else:
            benchmark: callable = generic_benchmark
        msgbox_text: str = "Benchmark completed successfully.\nLook at benchmark tab for results.\n"
        msgbox_icon: str = "check"
        for index, cpu_set in enumerate(bench_config_sets):
            self._status_text.configure(text=f"Running benchmark with {cpu_set} CPU core(s)...")
            self._target_cpu_core_set = cpu_set
            self._latest_bench_pool = Pool(cpu_set)
            args = self._generate_pickle_args_package(algorithm)
            start_time = time.time()
            async_handler = self._latest_bench_pool.starmap_async(benchmark, args)
            self._latest_bench_pool.close()
            while True:
                if self._bench_interrupt_signal:
                    self._latest_bench_pool.terminate()
                    break
                elif async_handler.ready():
                    break
                else:
                    time.sleep(0.05)
            if self._bench_interrupt_signal:
                break
            end_time = time.time()
            result_timestamps["Serial" if cpu_set == 1 else f"P ({cpu_set})"] = end_time - start_time
            if index == len(bench_config_sets) - 1:
                result_image = self._image_merger_implementation([img for img in async_handler.get()])
        if self._bench_interrupt_signal:
            self._bench_interrupt_signal = False
            msgbox_text = "Benchmark interrupted."
            msgbox_icon = "warning"
        else:
            self._benchmark_tab.update_bench_view(result_image, result_timestamps)
        self._toggle_controls()
        CTkMessagebox(title="Benchmark", message=msgbox_text,
                      icon=msgbox_icon)
        self._status_text.configure(text=msgbox_text.split(".")[0])

    def _generate_pickle_args_package(self, algorithm: str) -> list[tuple]:
        """
        Generates the arguments package for the benchmark function.
        :param algorithm: The algorithm to be benchmarked.
        :return: The arguments package for the benchmark function.
        """
        sub_images: list[Image.Image] = self._image_divider_implementation()
        if algorithm not in self._specialized_runners:
            return [(sub_image, self._selected_algorithm_type, self._selected_algorithm_sub_type) for sub_image in
                    sub_images]
        elif algorithm == noise_reduction.noise_reduction_sub_types[0]:
            return [(sub_image, self._selected_algorithm_sub_type, self._selected_algorithm_params[
                "kernel_size"]["value"]) for sub_image in sub_images]
        elif algorithm == noise_reduction.noise_reduction_sub_types[1]:
            return [(sub_image, self._selected_algorithm_sub_type, self._selected_algorithm_params[
                "diameter"]["value"], self._selected_algorithm_params["sigma_color"]["value"],
                     self._selected_algorithm_params["sigma_space"]["value"]) for sub_image in sub_images]
        elif algorithm == canny.name:
            return [(sub_image, self._selected_algorithm_type, self._selected_algorithm_params[
                "gauss_size"]["value"], self._selected_algorithm_params["sigma"]["value"],
                     self._selected_algorithm_params["low_threshold"]["value"],
                     self._selected_algorithm_params["high_threshold"]["value"]) for sub_image in sub_images]
        elif algorithm == convolution.parameterized_kernel_list[0]:
            return [(sub_image, self._selected_algorithm_type,
                     convolution.convolution_kernels[self._selected_algorithm_sub_type])
                    for sub_image in sub_images]
        elif algorithm in morphological_operators.morphological_sub_types:
            return [(sub_image, self._selected_algorithm_type, self._selected_algorithm_sub_type,
                     morphological_operators.structural_elements[self._selected_algorithm_params["structural_element"]["value"]]) for sub_image in sub_images]
        else:
            raise NotImplementedError("This algorithm has not pickle arguments implemented yet.")
