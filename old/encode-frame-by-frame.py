#! /usr/bin/env python

import argparse
from pathlib import Path
from PIL import Image


THRESHOLDS = [120, 140, 150, 170]
DITHER_MATRIX = [
    [THRESHOLDS[1], THRESHOLDS[2]] * 4,
    [THRESHOLDS[3], THRESHOLDS[0]] * 4,
] * 4


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


def encode_frame(img):
    """
    ICN encode an image. Returns two bytestrings:
    - image width (2 bytes), image height (2 bytes), number of bytes in the frame (2 bytes)
    - the ICN encoded image"""

    padded = pad_image(img.convert('L'))
    width, height = padded.size
    tile_count = get_tile_count(width, height)
    frame_length = tile_count * 8
    data = []

    print(f'{width}x{height} pixels ({tile_count} tiles)')

    for tile_idx in range(tile_count):
        for intile_row in range(8):
            bmp_row = get_bmp_row(tile_idx, intile_row, width)
            curr_total = 0
            for intile_col in range(8):
                bmp_col = get_bmp_col(tile_idx, intile_col, width)
                if padded.getpixel((bmp_col, bmp_row)) > DITHER_MATRIX[intile_row][intile_col]:
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


def encode_all_frames(input_path, output_path):
    """
    Encode every frame in a directory, and outputs to a file with the corresponding header"""

    global_header = None
    frame_list = sorted([f for f in Path(input_path).iterdir()])

    print(f'{len(frame_list)} files to encode')

    with open(output_path, 'wb') as outfile:

        for i, frame in enumerate(frame_list):
            #TODO: Check if it is a valid BMP file
            curr_data = b''
            img = Image.open(frame)
            print(f'[{i+1}/{len(frame_list)}] ', end='')
            header, data = encode_frame(img)
            if i == 0:
                # First frame
                global_header = header
                curr_data += global_header
            else:
                if header != global_header:
                    raise ValueError(f'Frame size is not consistent with the previous ones')

            curr_data += data
            outfile.write(curr_data)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('frame_dir', help='Directory containing the frames (BMP files)')
    parser.add_argument('output_file', help='Encoded file')
    return parser


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    encode_all_frames(args.frame_dir, args.output_file)
