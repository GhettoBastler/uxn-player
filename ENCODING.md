# File format

Description of the file format used to store the animation:

- A 4 bytes long header storing:
    - Screen width - 2 bytes
    - Screen height - 2 bytes
  
- Then comes all the frames concatenated together. For each frame:
    - Duration for which to display the frame (number of milliseconds * 0.06) - 2 bytes
    - Number of skip/draw blocks - 2 bytes
    - Blocks of data, all concatenated together:
        - flag - 1 byte: 00 means we skip, any other value means we draw
        - length: 2 bytes
        - The next bytes depend on the flag value:
            - if the flag was 00, the next skip/draw marker comes right after
            - else, length-byte long bytestring for the [ICN-encoded](https://wiki.xxiivv.com/site/icn_format.html) data

All values are stored MSB first
