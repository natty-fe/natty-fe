from PIL import Image, ImageOps, ImageEnhance, ImageFilter

RAMP = "@%#*+=-:. "

def image_to_ascii(path, cols=64, char_aspect=2.0, crop_box=None, blur=1.0, contrast=1.35):
    """
    Convert an image to ASCII art text lines.
    crop_box: optional (left, top, right, bottom) in original pixel coords,
    used to zoom in on a face/shoulders region instead of the whole photo.
    """
    img = Image.open(path).convert("L")
    if crop_box:
        img = img.crop(crop_box)
    else:
        w, h = img.size
        target_ratio = 0.85
        if w / h > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            img = img.crop((left, 0, left + new_w, h))

    img = img.filter(ImageFilter.GaussianBlur(radius=blur))
    img = ImageOps.autocontrast(img, cutoff=2)
    img = ImageEnhance.Contrast(img).enhance(contrast)

    w, h = img.size
    rows = int(cols * (h / w) / char_aspect)
    img = img.resize((cols, rows))
    pixels = list(img.getdata())
    ramp_len = len(RAMP)
    lines = []
    for r in range(rows):
        row_pixels = pixels[r*cols:(r+1)*cols]
        line = "".join(RAMP[min(p * ramp_len // 256, ramp_len - 1)] for p in row_pixels)
        lines.append(line)
    return lines
