"""numpy-only perceptual hash (same algorithm as imagehash.phash, hash_size=8)."""
import io
import numpy as np
from PIL import Image, ImageOps

_N = 32
_LANCZOS = getattr(Image, "Resampling", Image).LANCZOS


def _dct_matrix(n=_N):
    k = np.arange(n).reshape(-1, 1)
    i = np.arange(n).reshape(1, -1)
    return 2.0 * np.cos(np.pi * (2 * i + 1) * k / (2.0 * n))  # unnormalised DCT-II (matches scipy.fftpack.dct)


_C = _dct_matrix()


def load_pil(img):
    """Accept PIL image or bytes; return an upright image (EXIF applied)."""
    if isinstance(img, (bytes, bytearray, memoryview)):
        img = Image.open(io.BytesIO(bytes(img)))
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass
    return img


def to_gray(img):
    """-> PIL 'L' image; transparency is flattened onto white."""
    img = load_pil(img)
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        rgba = img.convert("RGBA")
        bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        img = Image.alpha_composite(bg, rgba)
    return img.convert("L")


def phash(img):
    g = to_gray(img).resize((_N, _N), _LANCZOS)
    x = np.asarray(g, dtype=np.float64)
    d = _C @ x @ _C.T
    low = d[:8, :8]
    bits = (low > np.median(low)).flatten()
    return "%016x" % int("".join("1" if b else "0" for b in bits), 2)


def hamming(a_hex, b_hex):
    return bin(int(a_hex, 16) ^ int(b_hex, 16)).count("1")
