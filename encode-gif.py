#!/usr/bin/env python

import argparse
from PIL import Image, ImageSequence


def get_matrix(thresh_values):
    a, b, c, d = thresh_values
    matrix = [
        [b, c] * 4,
        [d, a] * 4,
    ] * 4
    return matrix


def get_bmp_col(tile_idx, intile_col, bmp_width):
    """
    Returns the column index of a pixel given its position within tile"""

    return ((tile_idx * 8) % bmp_width) + intile_col


def get_bmp_row(tile_idx, intile_row, bmp_width):
    """
    Returns the row index of a pixel given its position within a tile"""

    return (tile_idx // (bmp_width // 8)) * 8 + intile_row


def get_tile_count(width, height):
    """
    Returns the number of 8x8 pixel tiles for a given size"""

    if width % 8:
        raise ValueError(f'Image width is not a multiple of 8 ({width})')
    if height % 8:
        raise ValueError(f'Image height is not a multiple of 8 ({height})')
    return width * height // 64


def pad_image(img):
    """
    Pads an image so its width and height are multiples of 8"""
    width, height = img.size
    pad_width = -width % 8
    pad_height = -height % 8
    origin_x = pad_width // 2
    origin_y = pad_height // 2

    new_width = width + pad_width
    new_height = height + pad_height

    res = Image.new('L', (new_width, new_height), 0)
    res.paste(img, (origin_x, origin_y))

    return res


def encode_frame(img, dither_matrix):
    """
    ICN encode an image. Returns two bytestrings:
    - header:
        image width (2 bytes)
        image height (2 bytes)
        number of bytes in the frame (2 bytes)
    - the ICN encoded image"""

    padded = pad_image(img.convert('L'))
    width, height = padded.size
    tile_count = get_tile_count(width, height)
    frame_length = tile_count * 8
    data = []

    for tile_idx in range(tile_count):
        for intile_row in range(8):
            bmp_row = get_bmp_row(tile_idx, intile_row, width)
            curr_total = 0
            for intile_col in range(8):
                bmp_col = get_bmp_col(tile_idx, intile_col, width)
                thresh_val = dither_matrix[intile_row][intile_col]
                if padded.getpixel((bmp_col, bmp_row)) > thresh_val:
                    output_val = 1
                else:
                    output_val = 0
                curr_total += output_val * 2**(7 - intile_col)
            data.append(curr_total)

    header = b''
    header += width.to_bytes(2, 'big')
    header += height.to_bytes(2, 'big')
    header += frame_length.to_bytes(2, 'big')

    return (header, bytes(data))


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('src_file', help='The GIF file to encode')
    parser.add_argument('dst_file', help='The path for the destination file')
    parser.add_argument(
        '-t', '--thresholds',
        nargs=4,
        type=int,
        required=False,
        default=[0, 64, 127, 191],
        help='The four threshold values used for dithering')
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    gif = Image.open(args.src_file)
    if not gif.is_animated:
        raise ValueError('Not an animated GIF')

    matrix = get_matrix(args.thresholds)

    width, height = gif.size
    n_frames = gif.n_frames
    i = 1

    with open(args.dst_file, 'wb') as f:
        print(f'{width}x{height}, {n_frames} frames')
        first = True
        for frame in ImageSequence.Iterator(gif):
            print(f'Encoding frame {i}/{n_frames}')
            header, data = encode_frame(frame, matrix)
            if first:
                f.write(header)
                first = False
            f.write(data)
            i += 1


if __name__ == '__main__':
    main()
