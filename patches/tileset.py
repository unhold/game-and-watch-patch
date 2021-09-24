import numpy as np
import matplotlib

from PIL import Image
from math import ceil


_BLOCK_SIZE = 16
_BLOCK_PIXEL = _BLOCK_SIZE * _BLOCK_SIZE

PALETTE_OFFSETS = [
    0xb_ec68,
    0xb_eda8,
    0xb_eee8,
    0xb_f028,
    0xb_f168,
]


def bytes_to_tilemap(data, palette, bpp=8, width=256):
    """
    Parameters
    ----------

    Returns
    -------
    PIL.Image
        Rendered RGB image.
    """

    assert bpp in [4, 8]

    if bpp == 4:
        nibbles = bytearray()
        offset = 0x0
        for b in data:
            nibbles.append((b >> 4) | (offset << 4))
            nibbles.append((b & 0xf) | (offset << 4))
        data = bytes(nibbles)
        del nibbles

    # Assemble bytes into an index-image
    h, w = int(ceil(len(data) / width / _BLOCK_SIZE) * _BLOCK_SIZE), width
    canvas = np.zeros((h, w), dtype=np.uint8)
    i_sprite = 0
    for i in range(0, len(data), _BLOCK_PIXEL):
        sprite = data[i:i+_BLOCK_PIXEL]

        x = i_sprite * _BLOCK_SIZE % w
        y = _BLOCK_SIZE * (i_sprite * _BLOCK_SIZE // w)
        view = canvas[y:y+_BLOCK_SIZE, x:x+_BLOCK_SIZE]
        sprite_block = np.frombuffer(sprite, dtype=np.uint8).reshape(_BLOCK_SIZE, _BLOCK_SIZE)
        view[:] = sprite_block

        i_sprite += 1

    # Apply palette to index-image
    p = np.frombuffer(palette, dtype=np.uint8).reshape((80, 4))
    p = p.astype(np.float32)[:, :3] / 255
    p = np.fliplr(p)  # BGR->RGB
    cmap = matplotlib.colors.ListedColormap(p)
    color_canvas = np.round(255 * cmap(canvas)[..., :3])
    color_canvas = color_canvas.astype(np.uint8)

    im = Image.fromarray(color_canvas)

    return im


def tilemap_to_bytes(tilemap):
    raise NotImplementedError

