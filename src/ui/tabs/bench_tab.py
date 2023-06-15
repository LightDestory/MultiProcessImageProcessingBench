import _tkinter
import customtkinter
import io
import matplotlib.pyplot as plt
from PIL import Image

from src.ui.components.image_viewer_top_level import ImageViewerTopLevel


class BenchTab:
    _reference: customtkinter.CTkFrame
    _main_container: customtkinter.CTkScrollableFrame
    _result_title: customtkinter.CTkLabel
    _result_image_thumbnail: customtkinter.CTkImage
    _result_image_viewer: customtkinter.CTkLabel
    _result_image_viewer_text: str = "Result Image"
    _result_bench_plot_thumbnail: customtkinter.CTkImage
    _result_bench_plot_viewer: customtkinter.CTkLabel
    _result_bench_plot_viewer_text: str = "Performance Plot"
    _top_level_image_viewer: ImageViewerTopLevel | None = None
    _timestamp_title: customtkinter.CTkLabel
    _timestamp_label_frame: customtkinter.CTkFrame
    _timestamp_text: customtkinter.CTkLabel
    _result_image: Image.Image | None = None
    _plot_image: Image.Image | None = None

    def __init__(self, container: customtkinter.CTkTabview):
        """
        Initializes the Main tab.
        :param container:
        """
        self._reference = container.add("Benchmark")
        self._reference.columnconfigure(0, weight=1)

    def populate(self) -> None:
        """
        Populates the Bench tab by adding and griding widgets.
        :return:
        """
        # Bench frame
        self._main_container = customtkinter.CTkScrollableFrame(self._reference, height=550)
        self._main_container.grid(row=0, column=0, sticky="nsew", pady=(20, 20), padx=(80, 80))
        self._main_container.columnconfigure((0, 1, 2), weight=1)
        # Result Image viewer
        self._result_image_thumbnail = customtkinter.CTkImage(light_image=Image.new("RGB", (512, 512), color="#dbdbdb"),
                                                              dark_image=Image.new("RGB", (512, 512), color="#2b2b2b"),
                                                              size=(512, 512))
        self._result_image_viewer = customtkinter.CTkLabel(self._main_container, text=self._result_image_viewer_text,
                                                           image=self._result_image_thumbnail, compound="bottom",
                                                           font=customtkinter.CTkFont(size=18, weight="bold"))
        self._result_image_viewer.grid(row=0, column=0, sticky="nw", pady=(10, 10), padx=(20, 0))
        self._result_image_viewer.bind("<Button-1>", self._on_preview_image_click)
        # Benchmark plot viewer
        self._result_bench_plot_thumbnail = customtkinter.CTkImage(
            light_image=Image.new("RGB", (512, 512), color="#dbdbdb"),
            dark_image=Image.new("RGB", (512, 512), color="#2b2b2b"),
            size=(512, 512))
        self._result_bench_plot_viewer = customtkinter.CTkLabel(self._main_container,
                                                                text=self._result_bench_plot_viewer_text,
                                                                image=self._result_bench_plot_thumbnail,
                                                                compound="bottom",
                                                                font=customtkinter.CTkFont(size=18, weight="bold"))
        self._result_bench_plot_viewer.grid(row=0, column=2, sticky="ne", pady=(10, 10), padx=(0, 20))
        self._result_bench_plot_viewer.bind("<Button-1>", self._on_preview_image_click)
        self._timestamp_title = customtkinter.CTkLabel(self._main_container, text="Execution Times",
                                                       font=customtkinter.CTkFont(size=22, weight="bold"))
        self._timestamp_title.grid(row=1, column=0, columnspan=3, pady=(20, 20), sticky="new")
        self._timestamp_label_frame = customtkinter.CTkFrame(self._main_container)
        self._timestamp_label_frame.columnconfigure(0, weight=1)
        self._timestamp_label_frame.grid(row=2, column=0, columnspan=3, sticky="nsew")
        self._timestamp_text = customtkinter.CTkLabel(self._timestamp_label_frame, text="",
                                                      font=customtkinter.CTkFont(size=20))
        self._timestamp_text.grid(row=0, column=0, sticky="nsew", pady=(20, 0))

    def _refresh_top_level_image_viewer(self, element: str) -> None:
        """
        Refreshes the top level image viewer.
        :return:
        """
        if self._top_level_image_viewer is None or not self._top_level_image_viewer.winfo_exists():
            return
        if element == self._result_image_viewer_text:
            self._top_level_image_viewer.set_image(self._result_image)
        else:
            self._top_level_image_viewer.set_image(self._plot_image)

    def set_result_image(self, image: Image.Image) -> None:
        """
        Displays the result image in the tab.
        :param image: The merged image.
        :return:
        """
        self._result_image = image.copy()
        self._result_image_thumbnail = customtkinter.CTkImage(light_image=self._result_image.copy().resize((512, 512)),
                                                              size=(512, 512))
        self._result_image_viewer.configure(image=self._result_image_thumbnail)
        self._refresh_top_level_image_viewer(self._result_image_viewer_text)

    def _on_preview_image_click(self, event) -> None:
        """
        Called when the preview image is clicked. Opens the image in the image viewer.
        :return:
        """
        if event.widget.cget("text") == self._result_image_viewer_text:
            if self._result_image is None:
                return
        else:
            if self._plot_image is None:
                return
        if self._top_level_image_viewer is None or not self._top_level_image_viewer.winfo_exists():
            self._top_level_image_viewer = ImageViewerTopLevel()
            self._top_level_image_viewer.title("Image Viewer - BenchTab")
        else:
            self._top_level_image_viewer.focus()
        self._refresh_top_level_image_viewer(event.widget.cget("text"))

    def set_timestamps(self, timestamps: dict[str, float]) -> None:
        """
        Displays plot and timestamps
        :param timestamps: The timestamps.
        :return:
        """
        self._set_plot_image(timestamps)
        results: str = ""
        for key, value in timestamps.items():
            results += f"{key}: {value:.2f}s\n"
        self._timestamp_text.configure(text=results)

    def _set_plot_image(self, timestamps: dict[str, float]) -> None:
        """
        Creates the plot image.
        :return:
        """
        y_elements: list[str] = list(timestamps.keys())
        x_elements: list[float] = list(timestamps.values())
        plt.clf()
        plt.barh(y_elements, x_elements, height=0.8, color="#2CC985")
        plt.ylabel("CPU set")
        plt.xlabel("Time (s)")
        plt.title("Execution Time Comparison")
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        im = Image.open(img_buf)
        self._plot_image = im.copy().resize((512, 512))
        img_buf.close()
        self._result_bench_plot_thumbnail = customtkinter.CTkImage(light_image=self._plot_image,
                                                                   size=(512, 512))
        self._result_bench_plot_viewer.configure(image=self._result_bench_plot_thumbnail)
