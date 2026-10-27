"""Image evidence crops, persisted under local uploads only."""
import uuid
import math
from pathlib import Path
from PIL import Image
from core import config

def _rect(box):
    try:
        if len(box) == 4 and all(isinstance(value, (int, float)) for value in box):
            rect = tuple(box)
        else:
            if len(box) != 4 or any(len(point) != 2 for point in box):
                raise ValueError("Use a four-point evidence box")
            rect = (min(p[0] for p in box), min(p[1] for p in box), max(p[0] for p in box), max(p[1] for p in box))
        if not all(math.isfinite(value) for value in rect) or rect[2] <= rect[0] or rect[3] <= rect[1]:
            raise ValueError("The evidence box has no visible area")
        return rect
    except (TypeError, IndexError) as exc:
        raise ValueError("The evidence box is not valid") from exc

def batch_line_crop(image, line_box, output=None, *, _image=None):
    from core.pack_tools import validate_image
    path = Path(output) if output else config.DATA_DIR / "crops" / f"{uuid.uuid4().hex}.png"
    source = _image if _image is not None else validate_image(image)
    x1, y1, x2, y2 = _rect(line_box)
    if x2 <= 0 or y2 <= 0 or x1 >= source.width or y1 >= source.height:
        raise ValueError("The evidence box lies outside the photo")
    pad = max(4, (y2 - y1) * .25)
    path.parent.mkdir(parents=True, exist_ok=True)
    source.crop((max(0, x1-pad), max(0, y1-pad), min(source.width, x2+pad), min(source.height, y2+pad))).save(path)
    return path

def char_boxes(line_box, line_text, batch_span, word_boxes=None):
    x1, y1, x2, y2 = _rect(line_box)
    start, end = batch_span
    length = max(1, len(line_text))
    advance = (x2-x1) / length
    return [[[x1+i*advance, y1], [x1+(i+1)*advance, y1], [x1+(i+1)*advance, y2], [x1+i*advance, y2]]
            for i in range(max(0, start), min(length, end))]

def glyph_crops(image, boxes, directory=None):
    from core.pack_tools import validate_image
    directory = Path(directory) if directory else config.DATA_DIR / "crops"
    prefix = uuid.uuid4().hex
    source = validate_image(image)
    return [batch_line_crop(image, box, directory / f"{prefix}-{index}.png", _image=source) for index, box in enumerate(boxes[:30])]
