from PIL import Image

name: str = "Morphological Ops"
_default_kernel = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]

morphological_sub_types: list[str] = ["erosion", "dilation"]


def erosion(target_image: Image.Image, kernel: list[list[int]] = _default_kernel) -> Image.Image:
    """
    Applies the erosion operator to an RGB image.
    :param target_image: The image to apply the operator to.
    :param kernel: The kernel to use.
    :return: The eroded image.
    """
    width, height = target_image.size
    result = Image.new("RGB", (width, height))
    kernel_size: int = len(kernel)
    target_image = target_image.convert("RGB")
    target_image.load()
    result.load()
    for y in range(height):
        for x in range(width):
            min_r, min_g, min_b = 255, 255, 255
            for ky in range(kernel_size):
                for kx in range(kernel_size):
                    px = x + kx - kernel_size // 2
                    py = y + ky - kernel_size // 2
                    if 0 <= px < width and 0 <= py < height:
                        pixel_r, pixel_g, pixel_b = target_image.getpixel((px, py))
                        kernel_value = kernel[ky][kx]
                        min_r = min(min_r, pixel_r - kernel_value)
                        min_g = min(min_g, pixel_g - kernel_value)
                        min_b = min(min_b, pixel_b - kernel_value)
            result.putpixel((x, y), (min_r, min_g, min_b))
    return result


def dilation(target_image: Image.Image, kernel: list[list[int]] = _default_kernel) -> Image.Image:
    """
    Applies the dilation operator to an RGB image.
    :param target_image: The image to apply the operator to.
    :param kernel: The kernel to use.
    :return: The dilated image.
    """
    width, height = target_image.size
    result = Image.new("RGB", (width, height))
    kernel_size: int = len(kernel)
    target_image = target_image.convert("RGB")
    target_image.load()
    result.load()
    for y in range(height):
        for x in range(width):
            max_r, max_g, max_b = 0, 0, 0
            for ky in range(kernel_size):
                for kx in range(kernel_size):
                    px = x + kx - kernel_size // 2
                    py = y + ky - kernel_size // 2
                    if 0 <= px < width and 0 <= py < height:
                        pixel_r, pixel_g, pixel_b = target_image.getpixel((px, py))
                        kernel_value = kernel[ky][kx]
                        max_r = max(max_r, pixel_r + kernel_value)
                        max_g = max(max_g, pixel_g + kernel_value)
                        max_b = max(max_b, pixel_b + kernel_value)
            result.putpixel((x, y), (max_r, max_g, max_b))
    return result
