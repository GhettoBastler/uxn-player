# uxn-player
An animation player for the [Uxn](https://100r.co/site/uxn.html) virtual machine.

![cat](https://user-images.githubusercontent.com/100698182/210180843-be2c0a9c-25ff-416a-9e0d-dd4c745609ea.gif)


It displays 1 bpp animations stored with a custom made file format. Audio isn't supported.

This project started as an exercise for learning [Uxntal](https://wiki.xxiivv.com/site/uxntal.html) and is still a work in progress.

## File format
The file format used for storing an animation is pretty bare-bones:
- A 6 bytes long header storing:
    - Screen width - 2 bytes
    - Screen height - 2 bytes
    - Number of bytes per frame - 2 bytes
  
    The three values are stored MSB first.

- The animation frames:
    - Duration for which to display the frame (number of milliseconds * 0.06) - 2 bytes
    - [ICN-encoded](https://wiki.xxiivv.com/site/icn_format.html) frame data
    
    Frames are concatenated in the order they are displayed in.

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
- [ ] Use transparency optimization to reduce file size
- [x] Adjust playback speed (currently set to 30 fps)
- [ ] Rewrite encoder in uxntal
- [ ] Add support for 2 bpp frames

## Licensing

The code for this project is licensed under the terms of the GNU GPLv3 license.
