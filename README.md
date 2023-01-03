# uxn-player
An animation player for the [Uxn](https://100r.co/site/uxn.html) virtual machine.

![cat](https://user-images.githubusercontent.com/100698182/210180843-be2c0a9c-25ff-416a-9e0d-dd4c745609ea.gif)


It displays 1 bpp animations stored with a custom made file format. Audio isn't supported.

This project started as an exercise for learning [Uxntal](https://wiki.xxiivv.com/site/uxntal.html) and is still a work in progress.

## File format

Clips used by uxn-player follow the custom `1ba` file format (for **1-b**it **a**nimation), described in [ENCODING.md](ENCODING.md).

## Requirements
- Python 3 with the [Pillow](https://pypi.org/project/Pillow/) module
- [uxn](https://git.sr.ht/~rabbits/uxn/) assembler and emulator

## Build
```
uxnasm player.tal player.rom
```

## Usage
### Encoding GIF files
Use `encode-gif.py` to generate the encoded file:

```
python encode-gif.py src-file encoded-file
```
The encoder converts color GIFs into grayscale, and uses [ordered dithering](https://en.wikipedia.org/wiki/Ordered_dithering) with a 2x2 Bayer matrix to turn them into 1 bpp images. Custom threshold values for dithering can be specified with the `-t/--thresholds` option.
For example, the command bellow uses the following threshold matrix:
 ```math
{\left\lbrack \matrix{80 & 100 \cr 150 & 60} \right\rbrack}
```
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
- [x] Use transparency optimization to reduce file size
- [x] Adjust playback speed (currently set to 30 fps)
- [ ] Rewrite encoder in uxntal
- [ ] Add support for 2 bpp frames

## Licensing

The code for this project is licensed under the terms of the GNU GPLv3 license.
