from PIL import Image
import numpy as np
from .convolution import generate_gauss_kernel, convolve_native, convolution_kernels

np.seterr(divide='ignore', invalid='ignore', over='ignore')
name: str = "Canny Edge Detection"


def _non_maximal_supress(gradient_magnitude: np.ndarray, gradient_direction: np.ndarray) -> np.ndarray:
    """
    Suppresses the non-maximal values in the given gradient magnitude array.
    :param gradient_magnitude: The gradient magnitude array.
    :param gradient_direction: The gradient direction array.
    :return: The suppressed gradient magnitude array.
    """
    suppressed_magnitude = np.zeros_like(gradient_magnitude)
    angles = np.rad2deg(gradient_direction)
    angles[angles < 0] += 180
    for i in range(1, gradient_magnitude.shape[0] - 1):
        for j in range(1, gradient_magnitude.shape[1] - 1):
            direction = angles[i, j]
            if (0 <= direction < 22.5) or (157.5 <= direction <= 180):  # 0 degrees
                neighbors = [gradient_magnitude[i, j - 1], gradient_magnitude[i, j + 1]]
            elif 22.5 <= direction < 67.5:  # 45 degrees
                neighbors = [gradient_magnitude[i - 1, j - 1], gradient_magnitude[i + 1, j + 1]]
            elif 67.5 <= direction < 112.5:  # 90 degrees
                neighbors = [gradient_magnitude[i - 1, j], gradient_magnitude[i + 1, j]]
            else:  # 135 degrees
                neighbors = [gradient_magnitude[i - 1, j + 1], gradient_magnitude[i + 1, j - 1]]
            if gradient_magnitude[i, j] >= max(neighbors):
                suppressed_magnitude[i, j] = gradient_magnitude[i, j]
    return suppressed_magnitude


def _double_threshold(image_array: np.ndarray, low_threshold: int, high_threshold: int) -> np.ndarray:
    """
    Filters the given image array with the given thresholds.
    :param image_array: The image array.
    :param low_threshold:
    :param high_threshold:
    :return: The filtered image array.
    """
    edge_map = np.zeros_like(image_array)
    edge_map[(image_array >= high_threshold)] = 255
    edge_map[(image_array >= low_threshold) & (image_array < high_threshold)] = 127
    return edge_map


def _link_edges(image_array: np.ndarray) -> np.ndarray:
    """
    Links the edges of the given image array
    :param image_array: The image array.
    :return: Tge image array with the edges linked.
    """
    for i in range(1, image_array.shape[0] - 1):
        for j in range(1, image_array.shape[1] - 1):
            if image_array[i, j] == 127:
                if np.max(image_array[i - 1:i + 2, j - 1:j + 2]) == 255:
                    image_array[i, j] = 255
                else:
                    image_array[i, j] = 0
    return image_array


def canny_edge_detector(target_image: Image.Image, gauss_size: int, sigma: int, low_threshold: int,
                        high_threshold: int) -> Image.Image:
    """
    Applies the canny edge detection algorithm to the given image.
    :param target_image: The image to apply the canny algorithm to.
    :param gauss_size: The size of the gaussian kernel.
    :param sigma: The sigma value for the gaussian kernel.
    :param low_threshold: The low threshold for the double thresholding.
    :param high_threshold: The high threshold for the double thresholding.
    :return: The image with the canny algorithm applied.
    """
    target_image = target_image.convert("L")
    # Phase 1 Smoothing applying gaussian kernel
    gauss_kernel = generate_gauss_kernel(gauss_size, sigma)
    gauss_image = convolve_native(target_image, gauss_kernel)
    # Phase 2 Finding the gradients
    sobel_x_array = np.array(convolve_native(gauss_image, convolution_kernels["edge_detection (sobel-x)"], True))
    sobel_y_array = np.array(convolve_native(gauss_image, convolution_kernels["edge_detection (sobel-y)"], True))
    gradient_magnitude = np.hypot(sobel_x_array, sobel_y_array)
    gradient_direction = np.arctan2(sobel_y_array, sobel_x_array)
    # Phase 3 Non-maximal supression
    supressed = _non_maximal_supress(gradient_magnitude, gradient_direction)
    # Phase 4 Double thresholding
    thresholded = _double_threshold(supressed, low_threshold, high_threshold)
    # Phase 5 Edge tracking by linking edges
    result_array = _link_edges(thresholded)
    return Image.fromarray(result_array.astype(np.uint8))
