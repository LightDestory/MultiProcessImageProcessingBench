import customtkinter
from CTkMessagebox import CTkMessagebox
from PIL.Image import Image
from customtkinter import filedialog


class ImageViewerTopLevel(customtkinter.CTkToplevel):
    _window_width: int = 600
    _window_height: int = 600
    _image_thumbnail: customtkinter.CTkImage | None = None
    _image_viewer: customtkinter.CTkLabel
    _image: Image
    _save_file: customtkinter.CTkButton
    _open_file: customtkinter.CTkButton

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_window()

    def _setup_window(self) -> None:
        """
        Sets up the window.
        :return:
        """
        self.geometry("{}x{}".format(self._window_width, self._window_height))
        self.configure(fg_color=("gray86", "gray17"))
        self.resizable(False, False)
        self.columnconfigure((0, 1), weight=1)
        self._image_viewer = customtkinter.CTkLabel(self, text="")
        self._image_viewer.grid(row=0, column=0, columnspan=2, sticky="n", pady=(10, 10), padx=(20, 20))
        self._open_file = customtkinter.CTkButton(self, text="Open with System Image Viewer",
                                                  command=self._on_open_file_btn)
        self._open_file.grid(row=1, column=0, padx=(10, 10), sticky="ewn", pady=(10, 10))
        self._save_file = customtkinter.CTkButton(self, text="Save to file", command=self._on_save_file_btn)
        self._save_file.grid(row=1, column=1, padx=(10, 10), sticky="ewn", pady=(10, 10))

    def _on_open_file_btn(self) -> None:
        """
        Opens the image with the system image viewer.
        :return:
        """
        self._image.show()

    def _on_save_file_btn(self) -> None:
        """
        Saves the image to a file.
        :return:
        """
        file_handler = filedialog.asksaveasfile(mode='w', defaultextension=".png", filetypes=[('PNG', '*.png')])
        if file_handler is None:
            CTkMessagebox(title="Save Image", message="Image save cancelled.", icon="warning")
            return
        self._image.save(file_handler.name)
        file_handler.close()
        CTkMessagebox(title="Save Image", message="Image saved successfully.", icon="success")

    def set_image(self, image: Image) -> None:
        """
        Sets the image to be displayed.
        :param image: The image to be displayed.
        :return:
        """
        self._image = image
        self._image_thumbnail = customtkinter.CTkImage(light_image=self._image, size=(512, 512))
        self._image_viewer.configure(image=self._image_thumbnail)
