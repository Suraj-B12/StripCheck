"""Make print-friendly (light) versions of the Phoenix screenshots."""
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent.parent
FIG = HERE / "figures"
TRACE = HERE.parent.parent / "docs" / "trace"


def light(img, scale=2, fill_white=False):
    """Invert luminance, keep hue (invert RGB then rotate hue by 180 degrees)."""
    img = img.convert("RGB")
    if fill_white:
        a = np.array(img)
        a[(a >= 245).all(axis=2)] = a[3, 3]
        img = Image.fromarray(a)
    img = img.resize((img.width * scale, img.height * scale), Image.LANCZOS)
    hsv = np.array(Image.fromarray(255 - np.array(img)).convert("HSV"))
    hsv[..., 0] = (hsv[..., 0].astype(int) + 128) % 256
    return Image.fromarray(hsv, "HSV").convert("RGB")


light(Image.open(TRACE / "01_phoenix_trace_list.png").crop((262, 312, 1130, 625))).save(FIG / "fig_phoenix_list_print.png")
light(Image.open(FIG / "fig_phoenix_tree.png"), fill_white=True).save(FIG / "fig_phoenix_tree_print.png")
light(Image.open(FIG / "fig_phoenix_io.png")).save(FIG / "fig_phoenix_io_print.png")
