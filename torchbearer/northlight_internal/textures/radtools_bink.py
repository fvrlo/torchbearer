import enum

from mulch import StreamObject, StreamFields

"""
Sources:
> https://wiki.multimedia.cx/index.php/Bink_Container
> https://multimedia.cx/bink-format.txt

Bink files are multimedia files used in a variety of video games, both on personal computers platforms and video game consoles.
The files act as containers for data compressed with the proprietary Bink video, Bink video 2 and audio codecs.
Bink multimedia files are known to bear the .bik, .bk2 or .bik2 extension.

This description is known to be incomplete.

All multi-byte numbers are stored in little endian format.

Bink files commence with a 44-byte header which is laid out as follows. Audio information follows the main header. If there are zero audio tracks, then the headers are omitted.

>   bytes 0-2     file signature ('BIK', or 'KB2' for Bink Video 2)
>   byte 3        Bink Video codec revision (0x62, 0x64, 0x66, 0x67, 0x68, 0x69; b,d,f,g,h,i respectively)
>                 Bink Video 2 codec revision ('a', 'd', 'f', 'g', 'h', 'i')
>   bytes 4-7     file size not including the first 8 bytes
>   bytes 8-11    number of frames
>   bytes 12-15   largest frame size in bytes
>   bytes 16-19   number of frames again?
>   bytes 20-23   video width (less than or equal to 32767)
>   bytes 24-27   video height (less than or equal to 32767)
>   bytes 28-31   video frames per second dividend
>   bytes 32-35   video frames per second divider
>   bytes 36-39   video flags
>                    bit 17: grayscale
>                    bit 20: has alpha plane
>                    bits 28-31: width and height scaling
>                      1 = 2x height doubled
>                      2 = 2x height interlaced
>                      3 = 2x width doubled
>                      4 = 2x width and height-doubled
>                      5 = 2x width and height-interlaced
>   bytes 40-43   number of audio tracks (less than or equal to 256)
>
>   for each audio track
>      two bytes   unknown
>      two bytes   audio channels (1 or 2). Not authoritative, see flags below.
>
>   for each audio track
>      two bytes   audio sample rate (Hz)
>      two bytes   flags
>                    bit 15: unknown (observed in some samples)
>                    bit 14: unknown (observed in some samples)
>                    bit 13: stereo flag
>                    bit 12: Bink Audio algorithm
>                      1 = use Bink Audio DCT
>                      0 = use Bink Audio FFT
>
>   for each audio track
>      four bytes  audio track ID


Bink Video revisions f and g contain video planes in YVU order, while the planes are ordered YUV in other (later) revisions.
Revision b is found in Heroes of Might and Magic 3, but is not supported by any of the tools published by RAD Game Tools.

Bink Video 2 revision a is found in Gears of War 3 (Xbox 360).
Revision d is found in WWE `13 (Xbox 360).
Neither are currently supported by the tools published by RAD Game Tools.

The audio track flags are similar to those defined for the Smacker AudioRate flags.

Following the header is a frame index table.
The number of entries in the table is equal to the number of frames specified in the header plus one.
Each entry consists of a 32-bit absolute offset for that frame.
There is no length information provided in the table, so the length of a sample is implicitly the difference between frame offsets, and the size of the file (for the very last frame).
If bit 0 of an entry is set, that frame is a keyframe; this bit should be masked off to find the actual offset of the frame data in the file.
The final frame offset is equal to the size of the entire file (likely included to simplify calculation of the length of the final frame).

Each frame contains (optional) audio and video data. Bytes 12-15 (largest frame size) probably exist to provide the playback application with the largest single buffer it will have to allocate. The layout of each frame is as follows:
>   for each audio track
		> four bytes        length of audio packet (bytes) plus four bytes.
		>                   A value of zero indicates no audio is present for this track.
		> four bytes        number of samples in packet
		> variable length   Bink Audio packet
>   variable length         Bink Video packet
"""

class BinkMagic(enum.Enum):
	v1rB = b'BIKb'    # Bink Video rev. B
	v1rD = b'BIKd'    # Bink Video rev. D
	v1rF = b'BIKf'    # Bink Video rev. F
	v1rG = b'BIKg'    # Bink Video rev. G
	v1rH = b'BIKh'    # Bink Video rev. H
	v1rI = b'BIKi'    # Bink Video rev. I
	v2rA = b'KB2a'    # Bink Video 2 rev. A
	v2rD = b'KB2d'    # Bink Video 2 rev. D
	v2rF = b'KB2f'    # Bink Video 2 rev. F
	v2rG = b'KB2g'    # Bink Video 2 rev. G
	v2rH = b'KB2h'    # Bink Video 2 rev. H
	v2rI = b'KB2i'    # Bink Video 2 rev. I


class BINK_Header(StreamObject):
	signature:              BinkMagic   = StreamFields.call(lambda x: BinkMagic(x.string(4)))   # file signature ('BIK', or 'KB2' for Bink Video 2) + codec revision (letter)
	file_size_following:    int         = StreamFields.int()    # file size not including the first 8 bytes
	frames:                 int         = StreamFields.int()    # number of frames
	largest_frame_size:     int         = StreamFields.int()    # largest frame size in bytes
	frames_again_maybe:     int         = StreamFields.int()    # number of frames again?
	video_width:            int         = StreamFields.int()    # video width (less than or equal to 32767)
	video_height:           int         = StreamFields.int()    # video height (less than or equal to 32767)
	fps_dividend:           int         = StreamFields.int()    # video frames per second dividend
	fps_divider:            int         = StreamFields.int()    # video frames per second divider
	flags:                  bytes       = StreamFields.bytes(4) # video flags
	audio_tracks:           int         = StreamFields.int()    # number of audio tracks (less than or equal to 256)