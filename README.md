```
                                   
 _ __ ___  _   _  __ _  ___ _ __  
| '_ ` _ \| | | |/ _` |/ _ \ '_ \ 
| | | | | | |_| | (_| |  __/ | | |
|_| |_| |_|\__,_|\__, |\___|_| |_|
                  |___/            
```

A music video generator based on rhythm

Use it to brainstorm AMVs, montages, and more! [Check it out](https://youtu.be/lHgFYo37CaU).

Built with [moviepy](https://github.com/Zulko/moviepy) Python video editing, and [librosa](https://github.com/librosa/librosa) audio analysis.

## Basic Strategy

1. Provide an audio file and a set of video files.

2. Perform rhythm analysis to identify beat locations.

3. Generate a set of random video segments syced to the beat.

4. Discard segments with scene changes, detectable text (e.g. credits), or low contrast (i.e. solid colors, very dark scenes).

5. Combine the segments in order, overlay the audio, and output the resulting music video.

## Requirements

1. A Python 3.6+ virtual environment. Using [Miniconda](http://conda.pydata.org/miniconda.html) is recommended.

2. The pip dependencies listed in mugen's [conda environment](environment.yml). 

**Optional:** 

- Install [tesseract](https://github.com/tesseract-ocr/tesseract) >= 3.04 and `pip install tesserocr>=2.2.1` for text detection features.

Mugen has not been tested on Linux or Windows, but should work on these systems provided the dependencies are compiled and installed properly.

## Quick Install

**1. [Install Miniconda 3.6](http://conda.pydata.org/miniconda.html) (Python virtual environment and package manager)**

**2. Create mugen virtual environment**

`conda env create -f environment.yml`

**3. Activate mugen environment**

`source activate mugen`

## Full Install  (Mac OS X)

**1. [Install Homebrew](http://brew.sh/) (General purpose package manager for mac)**

**2. [Install Miniconda 3.6](http://conda.pydata.org/miniconda.html) (Python virtual environment and package manager)**

**4. [Install tesseract](https://github.com/tesseract-ocr/tesseract) via Homebrew**

`brew install tesseract --with-all-languages`

**5. Create mugen virtual environment**

`conda env create -f environment_full.yml`

**6. Activate mugen environment**

`source activate mugen`

## Examples

**Navigate to the command line interface**

`
cd src/bin/
`

### Help Menu
---

```
python cli.py --help
python cli.py create --help
python cli.py preview --help
```

### Create a music video
---

```
python cli.py create --audio-source MACINTOSH_PLUS_420.mp3 --video-sources TimeScapes.mkv
```

**Use a series 60% of the time and a movie 40% of the time**

```
python cli.py create --video-sources Neon_Genesis_Evangelion/ The_End_of_Evangelion.mkv --video-source-weights .6 .4
```

**Slow down scene changes to every other beat**

```
python cli.py create --events-speed 1/2
```

**Slow down scene changes for leading and trailing weak beats**

```
python cli.py create --beats-mode weak_beats --group-events-by-type --group-speeds 1/2 1 1/4
```

**Control the speed of scene changes for specific sections**

```
python cli.py create --group-events-by-slices (0,23) (23,32) (32,95) (160,225) (289,321) (321,415) --group-speeds 1/2 0 1/4 1/2 1/2 1/4
```

**Allow clips with cuts and repeat clips**

```
python cli.py create --exclude-video-filters not_has_cut not_is_repeat
```

**Use only clips that have text**

```
python cli.py create --video-filters has_text
```

### Preview a music video
---

```
python cli.py preview --audio-source Spazzkid_Goodbye.mp3
```

**Input event locations manually**

```
python cli.py preview --event-locations 2 4 6 10 11 12
```

**This gets interesting!**

```
python cli.py preview --audio-events-mode onsets --events-speed 1/2 --events-speed-offset 1
```

## Python Examples

### Import mugen
---

```
>>> import sys
>>> sys.path.append("/Users/myuser/Documents/repos/mugen/src")
>>> import mugen
```

### Preview a music video
---

```
>>> from mugen import MusicVideoGenerator
>>>
>>> generator = MusicVideoGenerator("Pogo - Forget.mp3")
>>>
>>> beats = generator.audio.beats()
>>> beats.speed_multiply(1/2)
>>>
>>> generator.preview_events(beats, "forget-preview.mkv")
```

### Create a music video
---

```
>>> from mugen import MusicVideoGenerator
>>>
>>> generator = MusicVideoGenerator("in love with a ghost - flowers.mp3", ["wolf children.mkv"])
>>>
>>> beats = generator.audio.beats()
>>> beat_groups = beats.group_by_slices([(0, 23), (23, 32), (32, 95), (160, 225), (289,331), (331, 415)])
>>> beat_groups.selected_groups.speed_multiply([1/2, 0, 1/4, 1/2, 1/2, 1/4])
>>> beats = beat_groups.flatten()
>>>
>>> music_video = generator.generate_from_events(beats)
>>> music_video.write_to_video_file("flowers.mkv")
>>> music_video.save("flowers.pickle")
```

### Replace a segment in a music video
---

```
>>> from mugen import VideoSource, SourceSampler, MusicVideo
>>>
>>> music_video = MusicVideo.load("flowers.pickle")
>>> wolf_children = VideoSource("wolf children.mkv", weight=.2)
>>> spirited_away = VideoSource("spirited away.mkv", weight=.8)
>>> sampler = SourceSampler([wolf_children, spirited_away])
>>> music_video.segments[1] = sampler.sample(music_video.segments[1].duration)
>>>
>>> music_video.write_to_video_file("flowers.mkv")
```

### Preview a segment in a music video
---

```
>>> from mugen import MusicVideo
>>>
>>> music_video = MusicVideo.load("flowers.pickle")
>>>
>>> ''' Basic Previews (pretty iffy) '''
>>>
>>> # Use a lower fps to reduce lag in playback
>>> music_video.segments[1].preview(fps=10)
>>>
>>> # Preview a frame at a specific time (seconds)
>>> music_video.segments[1].show(.5)
>>>
>>> ''' Jupyter Notebook Previews (much better) '''
>>> 
>>> music_video.segments[1].ipython_display(autoplay=1, loop=1, width=400)
>>>
>>> # Preview a frame at a specific time (seconds)
>>> music_video.segments[1].ipython_display(t=.5, width=400)
```
