from PIL import Image

name: str = "Morphological Ops"


structural_elements: dict[str, list[list[int]]] = {
    "square": [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ],
    "cross": [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0]
    ],
    "line": [
        [0, 0, 0],
        [1, 1, 1],
        [0, 0, 0]
    ],
    "circle": [
        [0, 1, 1, 1, 0],
        [1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1],
        [0, 1, 1, 1, 0]
    ]

}

morphological_sub_types: list[str] = ["erosion", "dilation"]


def morphological_operate(target_image: Image.Image, sub_type: str, structural_element: list[list[int]]) -> Image.Image:
    """
    Applies the morphological operator to an RGB image.
    :param target_image: The image to apply the operator to.
    :param sub_type: The morphological operator to apply.
    :param structural_element: The structural element to use.
    :return: The filtered image.
    """
    if sub_type == "erosion":
        return _erosion(target_image, structural_element)
    else:
        return _dilation(target_image, structural_element)


def _erosion(target_image: Image.Image, structural_element: list[list[int]]) -> Image.Image:
    """
    Applies the erosion operator to an RGB image.
    :param target_image: The image to apply the operator to.
    :param structural_element: The structural element to use.
    :return: The eroded image.
    """
    width, height = target_image.size
    kernel_size: int = len(structural_element)
    target_image = target_image.convert("RGB")
    target_pixels = target_image.load()
    result_image = Image.new("RGB", (width, height))
    result_pixels = result_image.load()
    for y in range(height):
        for x in range(width):
            pixel_chs: list[int] = [255, 255, 255]
            for ky in range(kernel_size):
                for kx in range(kernel_size):
                    px = x + kx - int(kernel_size / 2)
                    py = y + ky - int(kernel_size / 2)
                    if 0 <= px < width and 0 <= py < height:
                        pixel_r, pixel_g, pixel_b = target_pixels[px, py]
                        kernel_value = structural_element[ky][kx]
                        pixel_chs[0] = min(pixel_chs[0], pixel_r - kernel_value)
                        pixel_chs[1] = min(pixel_chs[1], pixel_g - kernel_value)
                        pixel_chs[2] = min(pixel_chs[2], pixel_b - kernel_value)
            result_pixels[x, y] = (pixel_chs[0], pixel_chs[1], pixel_chs[2])
    return result_image


def _dilation(target_image: Image.Image, structural_element: list[list[int]]) -> Image.Image:
    """
    Applies the dilation operator to an RGB image.
    :param target_image: The image to apply the operator to.
    :param structural_element: The structural element to use.
    :return: The dilated image.
    """
    width, height = target_image.size
    kernel_size: int = len(structural_element)
    target_image = target_image.convert("RGB")
    target_pixels = target_image.load()
    result_image = Image.new("RGB", (width, height))
    result_pixels = result_image.load()
    for y in range(height):
        for x in range(width):
            pixel_chs: list[int] = [0, 0, 0]
            for ky in range(kernel_size):
                for kx in range(kernel_size):
                    px = x + kx - int(kernel_size / 2)
                    py = y + ky - int(kernel_size / 2)
                    if 0 <= px < width and 0 <= py < height:
                        pixel_r, pixel_g, pixel_b = target_pixels[px, py]
                        kernel_value = structural_element[ky][kx]
                        pixel_chs[0] = max(pixel_chs[0], pixel_r + kernel_value)
                        pixel_chs[1] = max(pixel_chs[1], pixel_g + kernel_value)
                        pixel_chs[2] = max(pixel_chs[2], pixel_b + kernel_value)
            result_pixels[x, y] = (pixel_chs[0], pixel_chs[1], pixel_chs[2])
    return result_image
