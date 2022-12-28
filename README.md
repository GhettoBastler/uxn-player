# uxn-player
A video player prototype for the [Uxn](https://100r.co/site/uxn.html) virtual machine.

![bunny](https://user-images.githubusercontent.com/100698182/209220053-95d4a295-7417-4049-b5f8-624548ad66bc.gif)

*Original video: [Big Buck Bunny - Blender Fundation (CC-BY-3.0)](https://www.youtube.com/watch?v=YE7VzlLtp-4)*

This project was written as an exercise for learning [Uxntal](https://wiki.xxiivv.com/site/uxntal.html). The encoding scheme is pretty bare: each frame is converted to 1-bit using [ordered dithering](https://en.wikipedia.org/wiki/Ordered_dithering) (with custom threshold values), before being [ICN-encoded](https://wiki.xxiivv.com/site/icn_format.html) and concatenated together. A 6-bytes header stores the width, height and number of bytes per frame (three 2-bytes shorts, MSB first).

As this is pretty experimental, there's a lot of room for improvement: the playback speed is set at 30 fps, the frames aren't compressed therefore the resulting file can get pretty large (more than 3MB for a 6 seconds clip at 600x338 pixel), and there is no audio.

**WIP: new encoder written in uxntal**

Not yet functionnal. The encoder generates a single ICN image from a PGM file.

## Requirements
- [FFmpeg](https://ffmpeg.org/) (for extracting the frames of the video to encode)
- [uxn](https://git.sr.ht/~rabbits/uxn/) assembler and emulator

## Build
```
uxnasm player.tal player.rom
uxnasm encoder.tal encoder.rom
```

## Usage
### Extracting the frames
```
mkdir frames
ffmpeg -i [src-video] -ss [start-time] -t [duration] -f image2 -vf "format=gray scale=[width]:-2" frames/%03d.pgm
```

### Encoding the frames
```
uxncli encoder.rom [pgm-file]
```
This generates a 1-bit image in a file named *out.icn*.

**TODO:** Process a list of pgm files and concatenate them into a single file.

## Licensing

The code for this project is licensed under the terms of the GNU GPLv3 license.
