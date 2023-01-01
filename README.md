# uxn-player
(WIP) An animation player for the [Uxn](https://100r.co/site/uxn.html) virtual machine.

It displays 1 bpp animations at 30 fps, and uses a custom made file format. Audio isn't supported.
This project started as an exercise for learning [Uxntal](https://wiki.xxiivv.com/site/uxntal.html) and is still a work in progress.

## File format
The file format used for storing an animation is pretty bare-bones:
- A 6 bytes long header storing:
    - Screen width (2 bytes)
    - Screen height (2 bytes)
    - Number of bytes per frame (2 bytes)
    The three values are stored MSB first.

- The animation frames, [ICN-encoded](https://wiki.xxiivv.com/site/icn_format.html) and concatenated together.

Currently the frames are stored uncompressed, therefore the encoded files can get pretty large (more than 3MB for a 6 seconds clip at 600x338 pixel).

## Requirements
- Python 3 with the [Pillow](https://pypi.org/project/Pillow/) module
- [uxn](https://git.sr.ht/~rabbits/uxn/) assembler and emulator

## Build
```
uxnasm player.tal player.rom
```

## Usage
### Encoding GIF files
Use *encode.py* to generate the encoded file:

```
python encode-gif.py src-file dst-file
```
The encoder converts color GIFs into grayscale, and uses [ordered dithering](https://en.wikipedia.org/wiki/Ordered_dithering) with a 2x2 Bayer matrix to turn them into 1 bpp images. Custom threshold values for dithering can be specified with the `-t/--thresholds` option.
For example, the following command uses the matrix:

 `[80 100; 150 100]`

```
python encode-gif.py -t 60 80 100 150 src-file encoded-file
```

### Playback
To play the animation, pass it as an argument to `player.rom`. Window size is set dynamically:

```
uxnemu player.rom encoded-file
```
Use <kbd>Space</kbd> to pause the video.

## TODO
- [ ] Use transparency optimization to reduce file size
- [ ] Adjust playback speed (currently set to 30 fps)
- [ ] Rewrite encoder in uxntal
- [ ] Add support for 2 bpp frames

## Licensing

The code for this project is licensed under the terms of the GNU GPLv3 license.
