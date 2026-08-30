import tkinter as tk
from matplotlib import pyplot as plt
from PIL import Image

def save_images_as_grid(images: list[Image.Image], columns: int, output_path: str) -> None:
    image_dimensions = (488, 680)
    dpi = tk.Tk().winfo_fpixels('1i')  # Get the screen DPI
    rows = (len(images) + columns - 1) // columns

    fig, axes = plt.subplots(rows, columns, figsize=(columns*image_dimensions[0]/dpi, rows*image_dimensions[1]/dpi), dpi=dpi)
    axes = axes.flatten()

    for ax, img in zip(axes, images):
        ax.imshow(img)
        ax.axis('off')

    plt.tight_layout(h_pad=1, w_pad=1)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()