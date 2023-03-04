# Converts a FLAC folder into high quality MP3 encodes, updates the playlists, and creates torrent files for all three.
# VBR: V0 + CBR: 320kbps
# Requires: ffmpeg, libmp3lame, mktorrent

import os
import os.path
import sys
import argparse
import fnmatch
import shutil
import errno


# ~~ functions ~~
def find_files(base, pattern):
	"""Return list of files matching pattern in base folder"""
	return [
		n for n in fnmatch.filter(os.listdir(base), pattern)
		if os.path.isfile(os.path.join(base, n))
	]


def copy_folder(src, dst):
	"""Copies a folder if the destination doesn't already exist."""
	try:
		shutil.copytree(src, dst)
	except OSError as exc:  # python >2.5
		if exc.errno in (errno.ENOTDIR, errno.EINVAL):
			shutil.copy(src, dst)
		else:
			raise


def playlist_to_mp3(ppath):
	"""Opens a file and replaces any instances of .flac with .mp3"""
	playlist = open(ppath, 'r')
	lines = playlist.readlines()
	playlist.close
	playlist = open(ppath, 'w')
	for line in lines:
		line = line.replace('.flac', '.mp3')
		playlist.write(line)
	playlist.close()


# ~~ script ~~

# ----- Load arguments
parser = argparse.ArgumentParser()
parser.add_argument('--flacfolder', help='The prepared FLAC folder')
parser.add_argument('--urlannounce', help='The tracker announce URL')
parser.add_argument('--source', help='Optional source tag for the torrent')
args = parser.parse_args()

flac_path = os.path.abspath(args.flacfolder)
directory = os.path.dirname(flac_path)
folder_name = os.path.basename(flac_path)
announce = args.urlannounce
source_tag = args.source

# ----- Ensure the folder exists and contains FLAC files
if not os.path.exists(flac_path):
	sys.exit("Path not found.")
print("Path found!")

if not find_files(flac_path, '*.flac'):
	sys.exit("No FLAC files found in that directory.")
print("FLAC file(s) found!")

# ----- Clone it into a new [MP3 V0] folder
vbr_folder_name = folder_name.replace('[FLAC]', '[MP3 V0]')
vbr_path = directory + '/' + vbr_folder_name
copy_folder(flac_path, vbr_path)
print(f"VBR Path : {vbr_path}")

# ----- Clone it into a new [MP3 320] folder
cbr_folder_name = folder_name.replace('[FLAC]', '[MP3 320]')
cbr_path = directory + '/' + cbr_folder_name
copy_folder(flac_path, cbr_path)
print(f"CBR Path : {cbr_path}")

# ----- VBR - V0 Conversion
os.chdir(vbr_path)
os.system(
	'for file in *.flac; do ffmpeg -i "$file" -codec:a libmp3lame -q:a 0 "${file%%flac}mp3" ; rm "$file" ; done'
)
os.system('for file in *.log; do rm "$file" ; done')
if playlist := find_files(vbr_path, '*.m3u8')[0]:
	playlist_to_mp3(playlist)

# ----- CBR - 320  Conversion
os.chdir(cbr_path)
os.system(
	'for file in *.flac; do ffmpeg -i "$file" -codec:a libmp3lame -b:a 320k "${file%%flac}mp3" ; rm "$file" ; done'
)
os.system('for file in *.log; do rm "$file" ; done')
if playlist := find_files(cbr_path, '*.m3u8')[0]:
	playlist_to_mp3(playlist)

# ----- Return to parent folder and generate .torrent files
os.chdir(directory)
if source_tag:
	source_tag = '-s ' + source_tag

mk_flac = f'mktorrent -l 17 -p {source_tag} -a {announce} "{flac_path}" -o "{folder_name}.torrent"'
mk_vbr = f'mktorrent -l 17 -p {source_tag} -a {announce} "{vbr_path}" -o "{vbr_folder_name}.torrent"'
mk_cbr = f'mktorrent -l 17 -p {source_tag} -a {announce} "{cbr_path}" -o "{cbr_folder_name}.torrent"'

os.system(mk_flac)
os.system(mk_vbr)
os.system(mk_cbr)
