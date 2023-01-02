#!/usr/bin/env python

import argparse
from math import ceil
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


def encode_frame(img, dither_matrix, prev_data):
    """
    Encode a frame, skipping bytes that are the same as in previous frame.
    Returns three bytestrings:
    - the duration of the frame (= duration in ms * 0.06) (2 bytes)
    - transparency optimized data
    - the unencoded "raw" frame data (for encoding the next frame)"""

    duration = round(img.info['duration'] * 0.06)
    padded = pad_image(img.convert('L'))
    pwidth, pheight = padded.size
    tile_count = get_tile_count(pwidth, pheight)
    raw_data = b''

    for tile_idx in range(tile_count):
        for intile_row in range(8):
            bmp_row = get_bmp_row(tile_idx, intile_row, pwidth)
            curr_total = 0
            for intile_col in range(8):
                bmp_col = get_bmp_col(tile_idx, intile_col, pwidth)
                thresh_val = dither_matrix[intile_row][intile_col]
                if padded.getpixel((bmp_col, bmp_row)) > thresh_val:
                    output_val = 1
                else:
                    output_val = 0
                curr_total += output_val * 2**(7 - intile_col)
            raw_data += curr_total.to_bytes(1, 'big')

    optimized, n_blocks = transparency_optimize(raw_data, prev_data)
    res = (
        duration.to_bytes(2, 'big'),
        n_blocks.to_bytes(2, 'big'),
        optimized,
        raw_data,
    )
    return res


def transparency_optimize(curr_data, prev_data):
    """
    Returns the encoded data as a bytestream, as well as the number of blocks.
    If prev_data is None, write the entire frame data"""

    res = b''

    if prev_data is None:
        n_blocks = 1
        res += b'\x01' # Write flag
        res += len(curr_data).to_bytes(2, 'big') # length
        res += curr_data

    else:
        n_blocks = 0
        length = 0
        prev_state = None
        buffer = b''
        for i, b in enumerate(curr_data):
            curr_state = prev_data[i] == b # curr_state is True if we should skip this byte

            if prev_state is None: # Special case: first byte of the stream
                if curr_state:
                    res += b'\x00'
                else:
                    res += b'\x01'
                prev_state = curr_state

            if curr_state: # We should skip this byte
                to_store = b''
            else:
                to_store = b.to_bytes(1, 'big')

            if prev_state == curr_state:
                buffer += to_store
                length += 1
            else:
                n_blocks += 1
                res += length.to_bytes(2, 'big')
                res += buffer
                length = 1
                buffer = to_store
                if curr_state:
                    res += b'\x00'
                else:
                    res += b'\x01'
            prev_state = curr_state
        # Write remaining data
        n_blocks += 1
        res += length.to_bytes(2, 'big')
        res += buffer

    return res, n_blocks


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

    n_frames = gif.n_frames
    print(f'Source file contains {n_frames} frames.')

    width, height = gif.size
    print(f'Original size is {width}x{height}')

    pwidth = ceil(width/8)*8
    pheight = ceil(height/8)*8
    print(f'Encoded file will be {pwidth}x{pheight}.')
    
    header = pwidth.to_bytes(2, 'big') + pheight.to_bytes(2, 'big')

    i = 1
    prev_data = None
    with open(args.dst_file, 'wb') as f:
        f.write(header)
        for frame in ImageSequence.Iterator(gif):
            print(f'Encoding frame {i}/{n_frames}')
            bduration, bn_blocks, bopti, braw = encode_frame(frame, matrix, prev_data)
            f.write(bduration + bn_blocks + bopti)
            prev_data = braw
            i += 1


if __name__ == '__main__':
    main()
