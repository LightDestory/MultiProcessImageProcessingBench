from PIL.Image import Image
target_image: Image | None = None
resized_target_image: Image | None = None
target_sub_images: list[Image] = []
available_cpu_core: int = -1
target_cpu_core_set: int = 1
bench_all_configurations: bool = False
