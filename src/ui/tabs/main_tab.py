import customtkinter
import multiprocessing
import math
from PIL import Image, ImageDraw, ImageChops
from CTkMessagebox import CTkMessagebox
from customtkinter import filedialog

from src.shared import shared


class MainTab:
    _reference: customtkinter.CTkFrame
    _load_image_btn: customtkinter.CTkButton
    _image_viewer: customtkinter.CTkLabel
    _image_thumbnail: customtkinter.CTkImage
    _image_selector_title: customtkinter.CTkLabel
    _image_selector_frame: customtkinter.CTkFrame
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
    _preview_image_divider_implementation: callable
    _image_divider_implementation: callable
    _image_options_label: customtkinter.CTkLabel
    _image_divider_switch: customtkinter.CTkSwitch
    _square_division_warning_label: customtkinter.CTkLabel

    def __init__(self, container: customtkinter.CTkTabview):
        """
        Initializes the Main tab.
        :param container:
        """
        shared.available_cpu_core = multiprocessing.cpu_count()
        self._reference = container.add("Main")
        self._reference.columnconfigure(0, weight=1)
        self._preview_image_divider_implementation = self._preview_line_image_sub_divider
        self._image_divider_implementation = self._line_image_sub_divider

    def populate(self):
        """
        Populates the Main tab by adding and griding widgets.
        :return:
        """
        # Image frame
        self._image_selector_frame = customtkinter.CTkFrame(self._reference)
        self._image_selector_frame.grid(row=0, column=0, sticky="nsew", pady=(20, 20), padx=(80, 80))
        self._image_selector_frame.columnconfigure((0, 1, 2), weight=1)
        self._image_selector_frame.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), weight=1)

        self._image_selector_title = customtkinter.CTkLabel(self._image_selector_frame, text="Select an Image:",
                                                            font=customtkinter.CTkFont(size=22, weight="bold"))
        self._image_selector_title.grid(row=0, column=0, pady=(20, 0), sticky="nw", padx=(20, 0))
        self._load_image_btn = customtkinter.CTkButton(self._image_selector_frame, text="Load Image from disk",
                                                       command=self._import_image)
        self._load_image_btn.grid(row=0, column=1, sticky="ewn", pady=(20, 0))

        self._image_thumbnail = customtkinter.CTkImage(light_image=Image.new("RGB", (512, 512), color="#dbdbdb"),
                                                       dark_image=Image.new("RGB", (512, 512), color="#2b2b2b"),
                                                       size=(512, 512))
        self._image_viewer = customtkinter.CTkLabel(self._image_selector_frame, text="", image=self._image_thumbnail)
        self._image_viewer.grid(row=0, rowspan=12, column=2, sticky="ne", pady=(20, 20), padx=(0, 20))

        self._image_path_label = customtkinter.CTkLabel(self._image_selector_frame, text="Filename:",
                                                        font=customtkinter.CTkFont(size=18))
        self._image_path_label.grid(row=1, column=0, sticky="nw", pady=(20, 0), padx=(20, 0))

        self._image_path = customtkinter.CTkLabel(self._image_selector_frame, text="",
                                                  font=customtkinter.CTkFont(size=18, slant="italic"))
        self._image_path.grid(row=1, column=1, sticky="nw", pady=(20, 0), padx=(20, 0))

        self._image_size_label = customtkinter.CTkLabel(self._image_selector_frame, text="File size:",
                                                        font=customtkinter.CTkFont(size=18))
        self._image_size_label.grid(row=2, column=0, sticky="nw", pady=(20, 0), padx=(20, 0))

        self._image_size = customtkinter.CTkLabel(self._image_selector_frame, text="",
                                                  font=customtkinter.CTkFont(size=18, slant="italic"))
        self._image_size.grid(row=2, column=1, sticky="nw", pady=(20, 0), padx=(20, 0))

        self._benchmark_selector_title = customtkinter.CTkLabel(self._image_selector_frame,
                                                                text="MultiProcess Options:",
                                                                font=customtkinter.CTkFont(size=22, weight="bold"))
        self._benchmark_selector_title.grid(row=3, column=0, pady=(20, 0), sticky="nw", padx=(20, 0))

        self._cpu_core_label = customtkinter.CTkLabel(self._image_selector_frame,
                                                      text=f"Worker Cores ({shared.available_cpu_core} CPU cores available):",
                                                      font=customtkinter.CTkFont(size=18))
        self._cpu_core_label.grid(row=4, column=0, sticky="nw", pady=(20, 0), padx=(20, 0))

        self._cpu_core_text = customtkinter.CTkLabel(self._image_selector_frame, text="1",
                                                     font=customtkinter.CTkFont(size=18, slant="italic"))
        self._cpu_core_text.grid(row=4, column=1, sticky="new", pady=(20, 0), padx=(20, 0))

        self._slider_cpu_workers_frame = customtkinter.CTkFrame(self._image_selector_frame, fg_color="transparent")
        self._slider_cpu_workers_frame.grid(row=5, column=1, sticky="nsew")
        self._slider_cpu_workers_frame.grid_columnconfigure(0, weight=1)

        self._cpu_core_progress_bar = customtkinter.CTkProgressBar(self._slider_cpu_workers_frame)
        self._cpu_core_progress_bar.grid(row=0, column=0, sticky="enw")

        self._cpu_core_slider = customtkinter.CTkSlider(self._slider_cpu_workers_frame, from_=1, to=16,
                                                        number_of_steps=shared.available_cpu_core - 1,
                                                        command=self._on_cpu_core_slider_change)
        self._cpu_core_slider.grid(row=1, column=0, sticky="enw", pady=(20, 0))

        self._bench_all_checkbox = customtkinter.CTkCheckBox(self._image_selector_frame,
                                                             font=customtkinter.CTkFont(size=18),
                                                             text="Bench all available cores sets",
                                                             command=self._on_bench_all_checkbox_change)
        self._bench_all_checkbox.grid(row=5, column=0, padx=(30, 0), pady=(15, 0), sticky="wne")

        self._image_options_label = customtkinter.CTkLabel(self._image_selector_frame, text="Image Processing Options:",
                                                           font=customtkinter.CTkFont(size=22, weight="bold"))
        self._image_options_label.grid(row=6, column=0, sticky="nw", pady=(20, 0), padx=(20, 0))

        self._image_divider_switch = customtkinter.CTkSwitch(self._image_selector_frame,
                                                             text="Divide image using lines",
                                                             command=self._on_divider_switch_change,
                                                             font=customtkinter.CTkFont(size=18))
        self._image_divider_switch.grid(row=7, column=0, padx=(30, 0), pady=(5, 0), sticky="wne")

        self._square_division_warning_label = customtkinter.CTkLabel(self._image_selector_frame,
                                                                     text="Workers must be a square number",
                                                                     font=customtkinter.CTkFont(size=18),
                                                                     text_color="red")

        # Default values
        self._cpu_core_slider.set(1)
        self._cpu_core_progress_bar.set(0)

    def _import_image(self) -> None:
        filepath: str = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        title_text: str = "Importing Image"
        if not filepath:
            CTkMessagebox(title=title_text, message="Image loading cancelled.", icon="warning")
            return
        temp_image: Image.Image = Image.open(filepath)
        width, height = temp_image.size
        if width != height:
            new_size = 2 ** (int(math.log2(max(width, height))) + 1)
            resize_question = CTkMessagebox(title=title_text,
                                            message=f"The image MUST be a square. Resize it to {new_size}x{new_size}?\nDeclining will cancel the import.",
                                            icon="question", option_1="No", option_2="Yes")
            if resize_question.get() == "Yes":
                temp_image = temp_image.resize((new_size, new_size))
            else:
                CTkMessagebox(title=title_text, message="Image loading cancelled.", icon="warning")
                return
        shared.target_image = temp_image
        self._image_path.configure(text=f"{filepath.split('/')[-1]} ")
        self._image_size.configure(text=f"{shared.target_image.size[0]}x{shared.target_image.size[1]} ")
        self._update_image_preview()

    def _update_image_preview(self) -> None:
        if shared.target_image is None:
            return
        self._image_thumbnail = customtkinter.CTkImage(light_image=self._preview_image_divider_implementation(),
                                                       size=(512, 512))
        self._image_viewer.configure(image=self._image_thumbnail)

    def _on_cpu_core_slider_change(self, value: float) -> None:
        int_value = int(value)
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
        shared.bench_all_configurations = bool(self._bench_all_checkbox.get())
        if shared.bench_all_configurations:
            self._cpu_core_text.configure(text=f"∞ ")
            self._cpu_core_slider.configure(state="disabled")
            self._cpu_core_slider.configure(button_color="red")
            self._cpu_core_progress_bar.configure(progress_color="red")
        else:
            self._cpu_core_slider.configure(state="normal")
            self._cpu_core_text.configure(text=f"{int(self._cpu_core_slider.get())} ")
            self._cpu_core_slider.configure(button_color=("#2CC985", "#2FA572"))
            self._cpu_core_progress_bar.configure(progress_color=("#2CC985", "#2FA572"))

    def _on_divider_switch_change(self) -> None:
        is_square_dividing = bool(self._image_divider_switch.get())
        if is_square_dividing:
            self._image_divider_switch.configure(text="Divide image using squares")
            self._preview_image_divider_implementation = self._preview_square_image_sub_divider
            self._image_divider_implementation = self._square_image_sub_divider
            self._square_division_warning_label.grid(row=7, column=1, columnspan=2, sticky="wn")

        else:
            self._image_divider_switch.configure(text="Divide image using lines")
            self._preview_image_divider_implementation = self._preview_line_image_sub_divider
            self._image_divider_implementation = self._line_image_sub_divider
            self._square_division_warning_label.grid_forget()
        self._update_image_preview()

    def _preview_line_image_sub_divider(self) -> Image.Image:
        tmp_image: Image.Image = shared.target_image.copy().resize((512, 512))
        if shared.target_cpu_core_set == 1:
            return tmp_image
        line_width = 512 // shared.target_cpu_core_set
        draw = ImageDraw.Draw(tmp_image)
        for i in range(1, shared.target_cpu_core_set):
            left = i * line_width
            draw.line((left, 0, left, 512), fill=(255, 0, 0), width=2)
        return tmp_image

    def _line_image_sub_divider(self) -> list[Image.Image]:
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
        tmp_image: Image.Image = shared.target_image.copy().resize((512, 512))
        if (shared.target_cpu_core_set ** 0.5).is_integer() is False:
            return tmp_image
        draw = ImageDraw.Draw(tmp_image)
        square_size = int(512 / (shared.target_cpu_core_set ** 0.5))
        for row in range(int(shared.target_cpu_core_set ** 0.5)):
            for column in range(int(shared.target_cpu_core_set ** 0.5)):
                x_start: int = column * square_size
                y_start: int = row * square_size
                x_end: int = x_start + square_size
                y_end: int = y_start + square_size
                draw.rectangle((x_start, y_start, x_end, y_end), outline=(255, 0, 0), width=2)
        return tmp_image

    def _square_image_sub_divider(self) -> list[Image.Image]:
        tmp_image: Image.Image = shared.target_image.copy().resize((512, 512))
        if (shared.target_cpu_core_set ** 0.5).is_integer() is False:
            return [tmp_image]
        square_size = 512 // shared.target_cpu_core_set
        sub_images: list[Image.Image] = []
        for row in range(int(shared.target_cpu_core_set ** 0.5)):
            for column in range(int(shared.target_cpu_core_set ** 0.5)):
                x_start: int = column * square_size
                y_start: int = row * square_size
                x_end: int = x_start + square_size
                y_end: int = y_start + square_size
                sub_images.append(tmp_image.crop((x_start, y_start, x_end, y_end)))
        return sub_images
