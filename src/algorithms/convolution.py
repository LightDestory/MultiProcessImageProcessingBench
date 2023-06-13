from PIL import Image

name: str = "Convolution"

convolution_kernels: dict[str, list[list[float]]] = {
    "identity": [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
    "edge_detection (high-pass)": [[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]],
    "edge_detection (sobel-x)": [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
    "edge_detection (sobel-y)": [[-1, -2, -1], [0, 0, 0], [1, 2, 1]],
    "edge_detection (prewitt-x)": [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]],
    "edge_detection (prewitt-y)": [[-1, -1, -1], [0, 0, 0], [1, 1, 1]],
    "edge_detection (roberts-x)": [[1, 0], [0, -1]],
    "edge_detection (roberts-y)": [[0, 1], [-0, 0]],
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


def convolve(target_image: Image.Image, kernel: list[list[float]]) -> Image.Image:
    image_width, image_height = target_image.size
    kernel_size: int = len(kernel)
    padding: int = kernel_size // 2
    result_image: Image.Image = Image.new("RGB", (image_width, image_height))
    target_image = target_image.convert("RGB")
    target_pixels = target_image.load()
    result_pixels = result_image.load()
    for y in range(image_height):
        for x in range(image_width):
            x_start: int = x - padding
            x_end: int = x + padding + 1
            y_start: int = y - padding
            y_end: int = y + padding + 1
            iterator: int = 0
            conv_pixel: list[float, float, float] = [0, 0, 0]
            for ky in range(y_start, y_end):
                for kx in range(x_start, x_end):
                    px = max(0, min(kx, image_width - 1))
                    py = max(0, min(ky, image_height - 1))
                    pixel = target_pixels[px, py]
                    kernel_value = kernel[iterator // kernel_size][iterator % kernel_size]
                    conv_pixel[0] += pixel[0] * kernel_value
                    conv_pixel[1] += pixel[1] * kernel_value
                    conv_pixel[2] += pixel[2] * kernel_value
                    iterator += 1
            result_pixels[x, y] = (
                max(0, min(255, int(conv_pixel[0]))),
                max(0, min(255, int(conv_pixel[1]))),
                max(0, min(255, int(conv_pixel[2])))
            )
    return result_image
