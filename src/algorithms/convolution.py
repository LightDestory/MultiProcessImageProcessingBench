from PIL import Image
from scipy.signal import convolve2d
import numpy as np

name_native: str = "Convolution (Native)"
name_lib: str = "Convolution (SciPy)"

convolution_kernels: dict[str, list[list[float]]] = {
    "identity": [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
    "edge_detection (high-pass)": [[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]],
    "edge_detection (sobel-x)": [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
    "edge_detection (sobel-y)": [[-1, -2, -1], [0, 0, 0], [1, 2, 1]],
    "edge_detection (prewitt-x)": [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]],
    "edge_detection (prewitt-y)": [[-1, -1, -1], [0, 0, 0], [1, 1, 1]],
    "edge_detection (laplacian)": [[0, -1, 0], [-1, 4, -1], [0, -1, 0]],
    "sharpen": [[0, -1, 0], [-1, 5, -1], [0, -1, 0]],
    "blur (low-pass)": [[1 / 9, 1 / 9, 1 / 9], [1 / 9, 1 / 9, 1 / 9], [1 / 9, 1 / 9, 1 / 9]],
    "blur (gaussian 3x3)": [[1 / 16, 2 / 16, 1 / 16], [2 / 16, 4 / 16, 2 / 16], [1 / 16, 2 / 16, 1 / 16]],
    "blur (gaussian 5x5)": [
        [1 / 256, 4 / 256, 6 / 256, 4 / 256, 1 / 256],
        [4 / 256, 16 / 256, 24 / 256, 16 / 256, 4 / 256],
        [6 / 256, 24 / 256, 36 / 256, 24 / 256, 6 / 256],
        [4 / 256, 16 / 256, 24 / 256, 16 / 256, 4 / 256],
        [1 / 256, 4 / 256, 6 / 256, 4 / 256, 1 / 256]
    ]
}


def convolve_native(target_image: Image.Image, kernel_name: str, gray_scale: bool = False) -> Image.Image:
    """
    Convolves the target image with the given kernel.
    :param target_image: The image to convolve.
    :param kernel_name: The name of the kernel to convolve with.
    :param gray_scale: Whether to convert the image to grayscale before convolving.
    :return: The convolved image.
    """
    img_type: str = "L" if gray_scale else "RGB"
    kernel: list[list[float]] = convolution_kernels[kernel_name]
    image_width, image_height = target_image.size
    kernel_size: int = len(kernel)
    padding: int = int(kernel_size / 2)
    result_image: Image.Image = Image.new(img_type, (image_width, image_height))
    target_image = target_image.convert(img_type)
    target_pixels = target_image.load()
    result_pixels = result_image.load()
    for y in range(image_height):
        for x in range(image_width):
            x_start: int = x - padding
            x_end: int = x + padding + 1
            y_start: int = y - padding
            y_end: int = y + padding + 1
            conv_pixel: list[float, float, float] | float = 0.0 if gray_scale else [0, 0, 0]
            iterator: int = 0
            for ky in range(y_start, y_end):
                for kx in range(x_start, x_end):
                    px = max(0, min(kx, image_width - 1))
                    py = max(0, min(ky, image_height - 1))
                    pixel = target_pixels[px, py]
                    kernel_value = kernel[int(iterator / kernel_size)][iterator % kernel_size]
                    if gray_scale:
                        conv_pixel += pixel * kernel_value
                    else:
                        conv_pixel[0] += pixel[0] * kernel_value
                        conv_pixel[1] += pixel[1] * kernel_value
                        conv_pixel[2] += pixel[2] * kernel_value
                    iterator += 1
            normalized: tuple[int, int, int] | int
            if gray_scale:
                normalized: int = max(0, min(255, int(conv_pixel)))
            else:
                normalized: tuple[int, int, int] = (
                    max(0, min(255, int(conv_pixel[0]))),
                    max(0, min(255, int(conv_pixel[1]))),
                    max(0, min(255, int(conv_pixel[2])))
                )
            result_pixels[x, y] = normalized
    return result_image


def convolve_lib(target_image: Image.Image, kernel_name: str, gray_scale: bool = False) -> Image.Image:
    """
    Convolves using the scipy library the target image with the given kernel.
    :param target_image: The image to convolve.
    :param kernel_name: The name of kernel to convolve with.
    :param gray_scale: Whether to convert the image to grayscale before convolving.
    :return: The convolved image.
    """
    if gray_scale:
        target_image = target_image.convert("L")
    image_array = np.array(target_image)
    output_array = np.zeros_like(image_array, dtype=np.float32)
    if gray_scale:
        output_array = convolve2d(image_array, convolution_kernels[kernel_name], mode='same', boundary='symm')
    else:
        for channel in range(3):
            channel_array = image_array[:, :, channel]
            output_array[:, :, channel] = convolve2d(channel_array,
                                                     convolution_kernels[kernel_name], mode='same', boundary='symm')
    output_array = np.clip(output_array, 0, 255)
    return Image.fromarray(output_array.astype(np.uint8))
