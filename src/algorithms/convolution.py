from PIL import Image
from scipy.signal import convolve2d
import numpy as np


def generate_gauss_kernel(kernel_size: int, sigma: int) -> list[list[float]]:
    """
    Generates a Gaussian kernel of the given size and sigma.
    :param kernel_size: The size of the kernel.
    :param sigma: The sigma value.
    :return: The generated kernel.
    """
    kernel = np.fromfunction(lambda x, y: (1 / (2 * np.pi * sigma ** 2)) * np.exp(
        -((x - (kernel_size - 1) / 2) ** 2 + (y - (kernel_size - 1) / 2) ** 2) / (2 * sigma ** 2)),
                             (kernel_size, kernel_size))
    return (kernel / np.sum(kernel)).tolist()


name_native: str = "Convolution (Native)"
name_lib: str = "Convolution (SciPy)"

parameterized_kernel_list: list[str] = ["blur (gaussian Parametrized)"]

convolution_kernels: dict[str, list[list[float]]] = {
    "identity": [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
    "edge_detection (sobel-x)": [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
    "edge_detection (sobel-y)": [[-1, -2, -1], [0, 0, 0], [1, 2, 1]],
    "edge_detection (prewitt-x)": [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]],
    "edge_detection (prewitt-y)": [[-1, -1, -1], [0, 0, 0], [1, 1, 1]],
    "edge_detection (laplacian)": [[0, -1, 0], [-1, 4, -1], [0, -1, 0]],
    "sharpen": [[0, -1, 0], [-1, 5, -1], [0, -1, 0]],
    "sharpen (high-pass)": [[0, -1/4, 0], [-1/4, 2, -1/4], [0, -1/4, 0]],
    "blur (low-pass)": [[1 / 9, 1 / 9, 1 / 9], [1 / 9, 1 / 9, 1 / 9], [1 / 9, 1 / 9, 1 / 9]],
    "blur (gaussian Dim: 3x3 Sigma: 1)": generate_gauss_kernel(3, 1),
    "blur (gaussian Dim: 5x5 Sigma 1)": generate_gauss_kernel(5, 1)
}


def convolve_native(target_image: Image.Image, kernel: list[list[float]], gray_scale: bool = False) -> Image.Image:
    """
    Convolves the target image with the given kernel.
    :param target_image: The image to convolve.
    :param kernel: The kernel to convolve with.
    :param gray_scale: Whether to convert the image to grayscale before convolving.
    :return: The convolved image.
    """
    img_type: str = "L" if gray_scale else "RGB"
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


def convolve_lib(target_image: Image.Image, kernel: list[list[float]], gray_scale: bool = False) -> Image.Image:
    """
    Convolves using the scipy library the target image with the given kernel.
    :param target_image: The image to convolve.
    :param kernel: The kernel to convolve with.
    :param gray_scale: Whether to convert the image to grayscale before convolving.
    :return: The convolved image.
    """
    if gray_scale:
        target_image = target_image.convert("L")
    image_array = np.array(target_image)
    output_array = np.zeros_like(image_array, dtype=np.float32)
    if gray_scale:
        output_array = convolve2d(image_array, kernel, mode='same', boundary='symm')
    else:
        for channel in range(3):
            channel_array = image_array[:, :, channel]
            output_array[:, :, channel] = convolve2d(channel_array, kernel, mode='same', boundary='symm')
    output_array = np.clip(output_array, 0, 255)
    return Image.fromarray(output_array.astype(np.uint8))
