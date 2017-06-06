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

2. Perform rhythm analysis and extract beat locations from the audio.

3. Generate a set of random video segments from the video files, with durations corresponding to the durations of beat intervals. 

4. Discard and replace segments with scene changes, detectable text (e.g. credits), or low contrast (i.e. solid colors, very dark scenes).

5. Combine the segments in order, overlay the audio, and output the resulting music video.

6. Save a reusable spec file detailing the structure of the music video. 

## Requirements

1. A Python 3.6+ virtual environment. Using [Miniconda](http://conda.pydata.org/miniconda.html) is recommended.

2. The pip dependencies listed in mugen's [conda environment](environment.yml). 

**Optional:** 

- Install [tesseract](https://github.com/tesseract-ocr/tesseract) >= 3.04 and `pip install tesserocr>=2.2.1` for text detection features.

Mugen has not been tested on Linux or Windows, but should work on these systems provided the dependencies are compiled and installed properly.

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

**Warning: Recreate is still in the works, and is currently unavailable**

### Help Menu

```
python cli.py --help
python cli.py create --help
python cli.py recreate --help
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

**Allow clips with cuts and repeat clips**

```
python cli.py create --exclude-video-filters not_has_cut not_is_repeat
```

**Use only clips that have text**

```
python cli.py create --video-filters has_text
```

**Slow down scene changes for weak beats at the beginning and end**

```
python cli.py create --beats-mode weak_beats --group-events-by-type --group-speeds 1/2 1 1/4
```

**Control the speed of scene changes at specific sections**

```
python cli.py create --group-events-by-slices (0,23) (23,32) (32,95) (160,225) (289,321) (321,415) --target-groups primary --group-speeds 1/2 0 1/4 1/2 1/2 1/4
```

### Preview events in a song
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

### Recreate a music video (currently unavailable)
---

```
python cli.py recreate --spec-source vaporwave_timescapes_spec.json
```

## Python Examples

### Create a Preview
---

```
>>> from mugen import MusicVideoGenerator
>>>
>>> generator = MusicVideoGenerator("Pogo - Forget.mp3")
>>> beats = generator.audio.beats()
>>> beats.speed_multiply(1/2)
>>> generator.preview_events(beats, "forget.mkv")
```

### Create a Music Video
---
```
>>> from mugen import MusicVideoGenerator
>>> generator = MusicVideoGenerator("in love with a ghost - flowers feat. nori.mp3", ["wolf children ame & yuki.mkv"])

>>> beats = generator.audio.beats()
>>> beat_groups = beats.group_by_slices([(0, 23), (23, 32), (32, 95), (160, 225), (289,331), (331, 415)])
>>> beat_groups.primary_groups.speed_multiply([1/2, 0, 1/4, 1/2, 1/2, 1/4])
>>> beats = beat_groups.flatten()

>>> music_video = generator.generate_from_audio_events(beats)
>>> music_video.write_to_video_file("flowers.mkv")
```






