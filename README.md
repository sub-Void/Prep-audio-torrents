# Prep-audio-torrents
A python script that transcodes a FLAC audio directory into MP3 (V0 and 320kbps) variants, and generate the .torrent files for all three. 

**Requires**: ffmpeg, libmp3lame, mktorrent

**Example Usage**: <br>
prep-audio-torrents.py --flacfolder "Artist - Album (Year) [FLAC]" --urlannounce "https://my.tracker.me/xyz/announce" --source "XYZ"
