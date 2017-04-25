```
                                   
 _ __ ___  _   _  __ _  ___ _ __  
| '_ ` _ \| | | |/ _` |/ _ \ '_ \ 
| | | | | | |_| | (_| |  __/ | | |
|_| |_| |_|\__,_|\__, |\___|_| |_|
                  |___/            
```

A music video generator based on beat patterns

Use it to brainstorm AMVs, montages, what have you. [Check it out](https://youtu.be/ZlTR6XULe5M).

Built with [moviepy](https://github.com/Zulko/moviepy) Python video editing, and [librosa](https://github.com/librosa/librosa) audio analysis.

## Strategy

1 - Provide an audio file and a set of video files.

2 - Perform rhythm analysis and extract beat intervals from the audio.

3 - Generate a set of random video segments from the video files, with durations corresponding to the durations of the beat intervals. Discard and replace repeat segments, as well as segments with scene changes, low contrast (solid colors, very dark scenes), or detectable text (e.g. credits).

4 - Combine all the segments in order, overlay the audio, and output the resulting music video.

5 - Save a reusable spec file detailing the structure of the music video. 

## Requirements

- Python 3.6+ virtual environment

- pip package dependencies listed in the conda [environment](environment.yml) for this repository. I recommend using [miniconda](http://conda.pydata.org/miniconda.html) as shown in the installation walkthrough below.

- Optional: Install [tesseract](https://github.com/tesseract-ocr/tesseract) >= 3.04 and `pip install tesserocr>=2.1.3` for text detection features.

Recommended install order: tesseract -> conda virtual environment 

Below, an installation walthrough is provided for Mac OS X to give you a better idea of the installation process. This project has not been tested on Windows or Linux, but it should work on these systems provided the dependencies are compiled and installed properly.

## Installation Walkthrough (Mac OS X)

**1 - [Install Homebrew](http://brew.sh/) (General purpose package manager for mac)**

**2 - [Install Miniconda 3.5](http://conda.pydata.org/miniconda.html) (Python virtual environment and package manager)**

**4 - [Install tesseract](https://github.com/tesseract-ocr/tesseract) via Homebrew**

`brew install tesseract --with-all-languages`

**5 - Create mugen virtual environment**

`conda env create -f environment.yml`

**6 - Activate mugen environment**

`source activate mugen`

## Examples

###Help Menu

```
python cli.py --help
python cli.py create --help
python cli.py recreate --help
python cli.py preview --help
```

###Create a music video

`python cli.py create`

`python cli.py create --audio-source ~/Documents/mp3s/MACINTOSH\ PLUS\ -\ リサフランク420\ -\ 現代のコンピュー.mp3 --video-source /Volumes/Media_Drive/Movies/Timescapes/TimeScapes.2012.1080p.mkv /Volumes/Media_Drive/Series/FLCL/`

###Recreate a music video

`python cli.py recreate`

`python cli.py recreate --spec-source ~/Documents/music_video_specs/vaporwave_timescapes_spec.json`

**Slow down scene changes to every other beat**

`python cli.py create --speed-multiplier 1/2`

###Preview event locations in a song

`python cli.py preview --audio-source ~/Documents/mp3s/Spazzkid\ -\ Goodbye.mp3`

**Input event locations manually**

`python cli.py preview --event-locations 2 4 6 10 11 12`

**This gets interesting!**

`python cli.py preview --method onsets --speed-multiplier 1/2 --speed-multiplier-offset 1`




