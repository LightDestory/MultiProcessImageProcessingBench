from PIL import Image
import math

name: str = "Noise Reduction"

noise_reduction_sub_types: list[str] = ["mean filter", "bilateral filter"]


def mean_filter(target_image: Image.Image, filter_size: int) -> Image.Image:
    """
    Applies the mean filter to an RGB image.
    :param target_image: The image to apply the operator to.
    :param filter_size: The size of the filter. By default it is 3.
    :return: The filtered image.
    """
    width, height = target_image.size
    half_size: int = int(filter_size / 2)
    target_image = target_image.convert("RGB")
    target_pixels = target_image.load()
    result_image = Image.new("RGB", (width, height))
    result_pixels = result_image.load()
    for x in range(width):
        for y in range(height):
            pixel_ch: list[int] = [0, 0, 0]
            count: int = 0
            for i in range(-half_size, half_size + 1):
                for j in range(-half_size, half_size + 1):
                    nx = min(max(x + i, 0), width - 1)
                    ny = min(max(y + j, 0), height - 1)
                    pixel = target_pixels[nx, ny]
                    pixel_ch[0] += pixel[0]
                    pixel_ch[1] += pixel[1]
                    pixel_ch[2] += pixel[2]
                    count += 1
            result_pixels[x, y] = (int(pixel_ch[0] / count), int(pixel_ch[1] / count), int(pixel_ch[2] / count))
    return result_image


def bilateral_filter(target_image: Image.Image, diameter: int, sigma_color: int, sigma_space: int) -> Image.Image:
    """
    Applies the bilateral filter to an RGB image.
    :param target_image: The image to apply the operator to.
    :param diameter: The diameter of the neighborhood.
    :param sigma_color: The sigma color value. The greater the value, the colors farther to each other will start to get mixed
    :param sigma_space: The sigma space value. The greater its value, the further pixels will mix together, given that their colors lie within the sigmaColor range.
    :return: The filtered image.
    """
    def bilateral_filter_gaussian(dist: float, sigma_value: int) -> float:
        return (1 / (2 * math.pi * sigma_value ** 2)) * math.exp(-(dist ** 2) / (2 * sigma_value ** 2))
    width, height = target_image.size
    target_image = target_image.convert("RGB")
    target_pixels = target_image.load()
    result_image = Image.new("RGB", (width, height))
    result_pixels = result_image.load()
    for x in range(width):
        for y in range(height):
            r_acc, g_acc, b_acc = 0.0, 0.0, 0.0
            w_acc = 0.0
            for i in range(-diameter, diameter + 1):
                for j in range(-diameter, diameter + 1):
                    nx = min(max(x + i, 0), width - 1)
                    ny = min(max(y + j, 0), height - 1)
                    pixel = target_pixels[nx, ny]
                    spatial_dist = math.sqrt(i ** 2 + j ** 2)
                    range_dist = math.sqrt((pixel[0] - target_pixels[x, y][0]) ** 2 +
                                           (pixel[1] - target_pixels[x, y][1]) ** 2 +
                                           (pixel[2] - target_pixels[x, y][2]) ** 2)

                    weight = bilateral_filter_gaussian(spatial_dist, sigma_space) * bilateral_filter_gaussian(range_dist, sigma_color)
                    r_acc += pixel[0] * weight
                    g_acc += pixel[1] * weight
                    b_acc += pixel[2] * weight
                    w_acc += weight
            result_pixels[x, y] = (int(r_acc / w_acc), int(g_acc / w_acc), int(b_acc / w_acc))
    return result_image
