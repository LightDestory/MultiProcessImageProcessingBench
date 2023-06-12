import customtkinter
import multiprocessing
import math
from PIL import Image, ImageDraw, ImageFont
from CTkMessagebox import CTkMessagebox
from customtkinter import filedialog

from src.shared import shared
from src.ui.components.image_viewer_top_level import ImageViewerTopLevel
from src.ui.tabs.bench_tab import BenchTab


class MainTab:
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
    _slider_cpu_workers_frame: customtkinter.CTkFrame
    _cpu_core_progress_bar: customtkinter.CTkProgressBar
    _cpu_core_slider: customtkinter.CTkSlider
    _bench_all_checkbox: customtkinter.CTkCheckBox
    _image_options_label: customtkinter.CTkLabel
    _image_divider_switch: customtkinter.CTkSwitch
    _square_division_warning_label: customtkinter.CTkLabel
    _bench_start_btn: customtkinter.CTkButton
    _bench_progress_bar: customtkinter.CTkProgressBar
    _preview_image_divider_implementation: callable
    _image_divider_implementation: callable
    _image_merger_implementation: callable
    _top_level_image_viewer: ImageViewerTopLevel | None = None

    def __init__(self, container: customtkinter.CTkTabview):
        """
        Initializes the Main tab.
        :param container: Container to add the Main tab to.
        """
        shared.available_cpu_core = multiprocessing.cpu_count()
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
                                                      text=f"Worker Cores ({shared.available_cpu_core} CPU cores available):",
                                                      font=customtkinter.CTkFont(size=18))
        self._cpu_core_label.grid(row=4, column=0, sticky="nw", padx=(20, 0))
        # CPU core text
        self._cpu_core_text = customtkinter.CTkLabel(self._main_container, text="1",
                                                     font=customtkinter.CTkFont(size=18, slant="italic"))
        self._cpu_core_text.grid(row=4, column=1, sticky="new", padx=(20, 0))
        # CPU core slider frame
        self._slider_cpu_workers_frame = customtkinter.CTkFrame(self._main_container, fg_color="transparent")
        self._slider_cpu_workers_frame.grid(row=5, column=1, sticky="nsew")
        self._slider_cpu_workers_frame.grid_columnconfigure(0, weight=1)
        # CPU core progress bar
        self._cpu_core_progress_bar = customtkinter.CTkProgressBar(self._slider_cpu_workers_frame)
        self._cpu_core_progress_bar.grid(row=0, column=0, sticky="enw")
        # CPU core slider
        self._cpu_core_slider = customtkinter.CTkSlider(self._slider_cpu_workers_frame, from_=1, to=16,
                                                        number_of_steps=shared.available_cpu_core - 1,
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
        # Start benchmark button
        self._bench_start_btn = customtkinter.CTkButton(self._main_container, text="Start Benchmark",
                                                        command=self._on_start_bench_btn)
        self._bench_start_btn.grid(row=12, column=0, columnspan=2, padx=(50, 0), sticky="ewn", pady=(0, 10))
        # Benchmark progress bar
        self._bench_progress_bar = customtkinter.CTkProgressBar(self._main_container, mode="indeterminate",
                                                                indeterminate_speed=0.5, width=512)

        # Default values
        self._cpu_core_slider.set(1)
        self._cpu_core_progress_bar.set(0)
        self._bench_progress_bar.start()

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
        shared.target_image = temp_image
        shared.resized_target_image = shared.target_image.copy().resize((512, 512))
        self._image_path.configure(text=f"{filepath.split('/')[-1]} ")
        self._image_size.configure(text=f"{shared.target_image.size[0]}x{shared.target_image.size[0]} ")
        self._update_image_preview()
        self._refresh_top_level()

    def _update_image_preview(self) -> None:
        """
        Update the image preview.
        :return:
        """
        if shared.target_image is None:
            return
        self._image_thumbnail = customtkinter.CTkImage(light_image=self._preview_image_divider_implementation(),
                                                       size=(512, 512))
        self._image_viewer.configure(image=self._image_thumbnail)

    def _preview_line_image_sub_divider(self) -> Image.Image:
        """
        Preview the image divider using lines.
        :return: A preview of the image divider using lines.
        """
        tmp_image: Image.Image = shared.resized_target_image.copy()
        if shared.target_cpu_core_set == 1:
            return tmp_image
        line_width = 512 // shared.target_cpu_core_set
        draw = ImageDraw.Draw(tmp_image)
        for i in range(1, shared.target_cpu_core_set):
            left = i * line_width
            draw.line((left, 0, left, 512), fill=(255, 0, 0), width=2)
        return tmp_image

    def _line_image_sub_divider(self) -> list[Image.Image]:
        """
        Divide the image using lines.
        :return: A list of the lines that the image is divided into.
        """
        tmp_image: Image.Image = shared.target_image.copy()
        if shared.target_cpu_core_set == 1:
            return [tmp_image]
        sub_images: list[Image.Image] = []
        line_width = tmp_image.width // shared.target_cpu_core_set
        for i in range(shared.target_cpu_core_set):
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
        tmp_image = Image.new("RGBA", shared.target_image.size)
        line_width = tmp_image.width // shared.target_cpu_core_set
        for i in range(shared.target_cpu_core_set):
            left = i * line_width
            right = left + line_width
            tmp_image.paste(lines[i], (left, 0, right, tmp_image.height))
        return tmp_image

    def _preview_square_image_sub_divider(self) -> Image.Image:
        """
        Preview the image divider using squares.
        :return: The preview of the image divider using squares.
        """
        tmp_image: Image.Image = shared.resized_target_image.copy()
        draw = ImageDraw.Draw(tmp_image)
        if (shared.target_cpu_core_set ** 0.5).is_integer() is False:
            draw.text((100, 225), "ERROR:\nThe number of CPU cores must \nbe a square number.", fill=(255, 0, 0),
                      stroke_fill=(0, 0, 0), stroke_width=3, font=ImageFont.truetype("arial.ttf", 22))
        else:
            num_parts: int = int(shared.target_cpu_core_set ** 0.5)
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
        tmp_image: Image.Image = shared.target_image.copy()
        if shared.target_cpu_core_set == 1:
            return [tmp_image]
        else:
            num_parts: int = int(shared.target_cpu_core_set ** 0.5)
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
        tmp_image = Image.new("RGBA", shared.target_image.size)
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
        self._top_level_image_viewer.set_image(shared.target_image)

    def _on_preview_image_click(self, _) -> None:
        """
        Called when the preview image is clicked. Opens the image in the image viewer.
        :return:
        """
        if shared.target_image is None:
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
        if int_value == shared.target_cpu_core_set:
            return
        shared.target_cpu_core_set = int_value
        if int_value == 1:
            self._cpu_core_progress_bar.set(0)
        else:
            self._cpu_core_progress_bar.set((int_value / shared.available_cpu_core))
        self._cpu_core_text.configure(text=f"{int(value)} ")
        self._update_image_preview()

    def _on_bench_all_checkbox_change(self) -> None:
        """
        Called when the bench all checkbox is changed.
        :return:
        """
        shared.bench_all_configurations = bool(self._bench_all_checkbox.get())
        if shared.bench_all_configurations:
            self._cpu_core_text.configure(text=f"∞ ")
            self._cpu_core_slider.configure(state="disabled")
            self._cpu_core_slider.configure(button_color="red")
            self._cpu_core_progress_bar.configure(progress_color="red")
            shared.target_cpu_core_set = 1
        else:
            shared.target_cpu_core_set = int(self._cpu_core_slider.get())
            self._cpu_core_slider.configure(state="normal")
            self._cpu_core_text.configure(text=f"{shared.target_cpu_core_set} ")
            self._cpu_core_slider.configure(button_color=("#2CC985", "#2FA572"))
            self._cpu_core_progress_bar.configure(progress_color=("#2CC985", "#2FA572"))
        self._update_image_preview()

    def _on_divider_switch_change(self) -> None:
        """
        Called when the image divider switch is changed. Updates the switch text, implementation references and
        refreshes the preview.
        :return:
        """
        is_square_dividing = bool(self._image_divider_switch.get())
        if is_square_dividing:
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

    def _on_start_bench_btn(self) -> None:
        if shared.target_image is None:
            CTkMessagebox(title="No image selected", message="Please select an image and then run the benchmark.",
                          icon="warning")
            return
        if self._bench_progress_bar.winfo_viewable():
            self._bench_progress_bar.grid_forget()
        else:
            self._bench_progress_bar.grid(row=12, column=2, sticky="e", padx=(0, 20))
