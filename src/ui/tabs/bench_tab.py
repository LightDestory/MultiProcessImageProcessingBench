import customtkinter
import io
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


class BenchTab:
    _reference: customtkinter.CTkFrame
    _main_container: customtkinter.CTkFrame
    _result_title: customtkinter.CTkLabel
    _result_image_thumbnail: customtkinter.CTkImage
    _result_image_viewer: customtkinter.CTkLabel
    _result_bench_plot_thumbnail: customtkinter.CTkImage
    _result_bench_plot_viewer: customtkinter.CTkLabel

    _plot_image: Image.Image

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
        self._main_container = customtkinter.CTkFrame(self._reference)
        self._main_container.grid(row=0, column=0, sticky="nsew", pady=(20, 20), padx=(80, 80))
        self._main_container.columnconfigure((0, 1, 2), weight=1)
        # Result Image viewer
        self._result_image_thumbnail = customtkinter.CTkImage(light_image=Image.new("RGB", (512, 512), color="#dbdbdb"),
                                                              dark_image=Image.new("RGB", (512, 512), color="#2b2b2b"),
                                                              size=(512, 512))
        self._result_image_viewer = customtkinter.CTkLabel(self._main_container, text="",
                                                           image=self._result_image_thumbnail)
        self._result_image_viewer.grid(row=0, column=0, sticky="nw", pady=(10, 10), padx=(20, 0))
        # Benchmark plot viewer
        self._result_bench_plot_thumbnail = customtkinter.CTkImage(
            light_image=Image.new("RGB", (512, 512), color="#dbdbdb"),
            dark_image=Image.new("RGB", (512, 512), color="#2b2b2b"),
            size=(512, 512))
        self._result_bench_plot_viewer = customtkinter.CTkLabel(self._main_container, text="",
                                                                image=self._result_bench_plot_thumbnail)
        self._result_bench_plot_viewer.grid(row=0, column=2, sticky="ne", pady=(10, 10), padx=(0, 20))
        self.test_plot()

    def test_plot(self):
        np.random.seed(19680801)
        plt.rcdefaults()
        fig, ax = plt.subplots()
        # Example data
        people = ('Tom', 'Dick', 'Harry', 'Slim', 'Jim')
        y_pos = np.arange(len(people))
        performance = 3 + 10 * np.random.rand(len(people))
        ax.barh(y_pos, performance, align='center')
        ax.set_yticks(y_pos, labels=people)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xlabel('Performance')
        ax.set_title('How fast do you want to go today?')
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        im = Image.open(img_buf)

        self._plot_image = im.copy().resize((512, 512))
        img_buf.close()
        self._result_bench_plot_thumbnail = customtkinter.CTkImage(light_image=self._plot_image,
                                                                   size=(512, 512))
        self._result_bench_plot_viewer.configure(image=self._result_bench_plot_thumbnail)
