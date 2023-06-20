from PIL import Image
import numpy as np
import scipy.stats as st
from math import atan
from .convolution import convolution_kernels

np.seterr(divide='ignore', invalid='ignore', over='ignore')
name: str = "Canny Edge Detection"

canny_sub_types: list[str] = ["Canny 4 Parameters"]


def _generate_gauss_kernel(kernel_length: int, sigma: int) -> np.ndarray:
    """
    Generate a gauss kernel
    :param kernel_length: The kernel length
    :param sigma: The sigma value
    :return: The gauss kernel, an np.ndarray
    """
    interval: float = (2 * sigma + 1.) / kernel_length
    x = np.linspace(-sigma - interval / 2., sigma + interval / 2., kernel_length + 1)
    kern1d = np.diff(st.norm.cdf(x))
    kernel_raw = np.sqrt(np.outer(kern1d, kern1d))
    kernel = kernel_raw / kernel_raw.sum()
    return kernel


def _apply_kernel_to_array(image_array: np.ndarray, kernel: np.ndarray, kernel_size: int) -> np.ndarray:
    """
    Applies the given kernel to the given image array.
    :param image_array: An np.ndarray representing the image.
    :param kernel: The kernel to apply.
    :param kernel_size: The size of the kernel.
    :return: The image array with the kernel applied.
    """
    width: int = len(image_array[0])
    height: int = len(image_array)
    result = np.empty([height - 2 * kernel_size, width - 2 * kernel_size])
    for x in range(kernel_size, width - 2 * kernel_size):
        for y in range(kernel_size, height - 2 * kernel_size):
            window = image_array[y - kernel_size:y + kernel_size + 1, x - kernel_size:x + kernel_size + 1]
            acc: int = 0
            for kx in range(0, 2 * kernel_size + 1):
                for ky in range(0, 2 * kernel_size + 1):
                    acc += kernel[kx][ky] * window[kx][ky]
            result[y][x] = max(0, min(255, int(acc)))
    return result


def _calc_magnitude_and_degree(sobel_x: list[list[int]], sobel_y: list[list[int]]) -> (np.ndarray, np.ndarray):
    """
    Calculates the magnitude and degree of the given sobel x and sobel y arrays.
    :param sobel_x: The sobel x array.
    :param sobel_y: The sobel y array.
    :return: The magnitude and degree arrays in a tuple.
    """
    width: int = len(sobel_x[0])
    height: int = len(sobel_x)
    mag: np.ndarray = np.empty([height, width])
    degree: np.ndarray = np.empty([height, width])
    for x in range(0, width):
        for y in range(0, height):
            mag[y][x] = np.math.sqrt(sobel_x[y][x] * sobel_x[y][x] + sobel_y[y][x] * sobel_y[y][x])
            degree[y][x] = atan(sobel_y[y][x] / sobel_x[y][x])
    degree = (np.round(degree * (5.0 / np.pi)) + 5) % 5
    return mag, degree


def _non_maximal_supress(image_array: np.ndarray, grad_deg: np.ndarray) -> np.ndarray:
    """
    Performs non-maximal suppression on the given image array.
    :param image_array: The image array.
    :param grad_deg: The gradient degree array.
    :return: The image array with non-maximal suppression applied.
    """
    width: int = len(image_array[0])
    height: int = len(image_array)
    for x in range(0, width):
        for y in range(0, height):
            if x == 0 or y == height - 1 or y == 0 or x == width - 1:
                image_array[y][x] = 0
                continue
            direction: int = grad_deg[y][x] % 4
            if direction == 0:
                if image_array[y][x] <= image_array[y][x - 1] or image_array[y][x] <= image_array[y][x + 1]:
                    image_array[y][x] = 0
            if direction == 1:
                if image_array[y][x] <= image_array[y - 1][x + 1] or image_array[y][x] <= image_array[y + 1][x - 1]:
                    image_array[y][x] = 0
            if direction == 2:
                if image_array[y][x] <= image_array[y - 1][x] or image_array[y][x] <= image_array[y + 1][x]:
                    image_array[y][x] = 0
            if direction == 3:
                if image_array[y][x] <= image_array[y - 1][x - 1] or image_array[y][x] <= image_array[y + 1][x + 1]:
                    image_array[y][x] = 0
    return image_array


def _double_threshold(image_array: np.ndarray, low_threshold: int, high_threshold: int) -> np.ndarray:
    """
    Filters the given image array with the given thresholds.
    :param image_array: The image array.
    :param low_threshold:
    :param high_threshold:
    :return: The filtered image array.
    """
    image_array[np.where(image_array > high_threshold)] = 255
    image_array[np.where((image_array >= low_threshold) & (image_array <= high_threshold))] = 75
    image_array[np.where(image_array < low_threshold)] = 0
    return image_array


def _link_edges(image_array: np.ndarray) -> np.ndarray:
    """
    Links the edges of the given image array
    :param image_array: The image array.
    :return: Tge image array with the edges linked.
    """
    width: int = len(image_array[0])
    height: int = len(image_array)
    for i in range(0, height):
        for j in range(0, width):
            if image_array[i][j] == 75:
                if ((image_array[i + 1][j] == 255) or (image_array[i - 1][j] == 255) or (image_array[i][j + 1] == 255) or (
                        image_array[i][j - 1] == 255) or (image_array[i + 1][j + 1] == 255) or (image_array[i - 1][j - 1] == 255)):
                    image_array[i][j] = 255
                else:
                    image_array[i][j] = 0
    return image_array


def canny_edge_detector(target_image: Image.Image, gauss_size: int, sigma: int, low_threshold: int,
                        high_threshold: int):
    pixel = np.array(target_image.convert("L"))
    result_array = pixel.copy()
    # Phase 1 Smoothing applying gaussian kernel
    gauss_kernel = _generate_gauss_kernel(2 * gauss_size + 1, sigma)
    result_array = _apply_kernel_to_array(result_array, gauss_kernel, gauss_size)
    result_array = result_array.astype(np.uint8)
    # Phase 2 Finding the gradients
    sobel_x_image = _apply_kernel_to_array(result_array, np.array(convolution_kernels["edge_detection (sobel-x)"]), 1)
    sobel_y_image = _apply_kernel_to_array(result_array, np.array(convolution_kernels["edge_detection (sobel-y)"]), 1)
    grad_mag, grad_deg = _calc_magnitude_and_degree(sobel_x_image, sobel_y_image)
    # Phase 3 Non-maximal supression
    supressed = _non_maximal_supress(grad_mag, grad_deg)
    # Phase 4 Double thresholding
    thresholded = _double_threshold(supressed, low_threshold, high_threshold)
    # Phase 5 Edge tracking by linking edges
    result_array = _link_edges(thresholded)
    return Image.fromarray(result_array.astype(np.uint8))