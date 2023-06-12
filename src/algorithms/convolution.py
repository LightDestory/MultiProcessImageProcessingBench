from PIL import Image

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
    "blur (low-pass)": [[1/9, 1/9, 1/9], [1/9, 1/9, 1/9], [1/9, 1/9, 1/9]],
    "blur (gaussian 3x3)": [[1/16, 2/16, 1/16], [2/16, 4/16, 2/16], [1/16, 2/16, 1/16]],
    "blur (gaussian 5x5)": [
        [1/256, 4/256, 6/256, 4/256, 1/256],
        [4/256, 16/256, 24/256, 16/256, 4/256],
        [6/256, 24/256, 36/256, 24/256, 6/256],
        [4/256, 16/256, 24/256, 16/256, 4/256],
        [1/256, 4/256, 6/256, 4/256, 1/256]
    ]
}


def convolve(target_image: Image.Image, kernel: list[list[float]]) -> Image.Image:
    """
    Convolve the target image with the given kernel.
    :param target_image: The target image to be convolved.
    :param kernel: The kernel to be used for convolution.
    :return: The convolved image.
    """
    width, height = target_image.size
    kernel_width = len(kernel[0])
    kernel_height = len(kernel)
    border_x = kernel_width // 2
    border_y = kernel_height // 2
    result = Image.new("RGB", (width, height))

    # Aggiungi il padding all'immagine
    padded_image = Image.new("RGB", (width + 2 * border_x, height + 2 * border_y))
    padded_image.paste(target_image, (border_x, border_y))

    # Applica la convoluzione
    for y in range(height):
        for x in range(width):
            # Calcola il valore del pixel convoluto per ogni canale di colore (R, G, B)
            convolved_pixel = [0, 0, 0, 0]
            for ky in range(kernel_height):
                for kx in range(kernel_width):
                    pixel = padded_image.getpixel((x + kx, y + ky))
                    kernel_value = kernel[ky][kx]
                    for i in range(3):  # 3 canali di colore (R, G, B)
                        convolved_pixel[i] += pixel[i] * kernel_value

            # Normalizza i valori dei pixel convoluti e assegna il risultato all'immagine di output
            for i in range(3):  # 3 canali di colore (R, G, B)
                convolved_pixel[i] = max(0, min(255, int(convolved_pixel[i])))

            result.putpixel((x, y), tuple(convolved_pixel))

    return result
