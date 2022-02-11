```

 _ __ ___  _   _  __ _  ___ _ __
| '_ ` _ \| | | |/ _` |/ _ \ '_ \
| | | | | | |_| | (_| |  __/ | | |
|_| |_| |_|\__,_|\__, |\___|_| |_|
                  |___/
```

[![tests](https://img.shields.io/github/workflow/status/scherroman/mugen/Test?label=tests&logo=github)](https://github.com/scherroman/mugen/actions/workflows/test.yml)
[![coverage](https://img.shields.io/codecov/c/github/scherroman/mugen?label=coverage&logo=codecov)](https://codecov.io/gh/scherroman/mugen)
[![license](https://img.shields.io/github/license/scherroman/mugen?color=blue)](https://github.com/scherroman/mugen/blob/master/LICENSE)
[![Ko-Fi](https://img.shields.io/badge/buy%20me%20a%20coffee-F16061?logo=ko-fi&logoColor=white)](https://ko-fi.com/scherroman)

A music video generator based on rhythm

Use it to brainstorm AMVs, montages, and more! [Check it out](https://youtu.be/ZlTR6XULe5M).

Built with [moviepy](https://github.com/Zulko/moviepy) programmatic video editing and [librosa](https://github.com/librosa/librosa) audio analysis.

## Basic Strategy

1. Provide an audio file and a set of video files

2. Perform rhythm analysis to identify beat locations

3. Generate a set of random video segments syced to the beat

4. Discard segments with scene changes, detectable text (e.g. credits), or low contrast (i.e. solid colors, very dark scenes)

5. Combine the segments in order, overlay the audio, and output the resulting music video

## Installation

Mugen is supported across Linux, macOS, and Windows.

**1. Install [Miniconda](http://conda.pydata.org/miniconda.html)**

Miniconda helps create an isolated virtual environment and install the project's dependencies across platforms.

**2. Download this repository**

```
git clone https://github.com/scherroman/mugen
```

**3. Create the project's virtual environment**

```
conda env create --file mugen/environment.yml
```

**4. Activate the virtual environment**

```
source activate mugen
```

## Usage

### Help Menu

---

```
mugen --help
mugen create --help
mugen preview --help
```

Use the above commands at any time to clarify the examples below and view the full list of available options.

By default output files are sent to the desktop. This can be changed with the `-od --output-directory` option.

### Create a music video

---

```
mugen create --audio-source MACINTOSH_PLUS_420.mp3 --video-sources TimeScapes.mkv
```

**Use a series 60% of the time and a movie 40% of the time**

```
mugen create --video-sources Neon_Genesis_Evangelion/ The_End_of_Evangelion.mkv --video-source-weights .6 .4
```

**Slow down scene changes to every other beat**

```
mugen create --events-speed 1/2
```

**Slow down scene changes for leading and trailing weak beats**

```
mugen create --beats-mode weak_beats --group-events-by-type --group-speeds 1/2 1 1/4
```

**Control the speed of scene changes for specific sections**

```
mugen create --group-events-by-slices (0,23) (23,32) (32,95) (160,225) (289,321) (321,415) --group-speeds 1/2 0 1/4 1/2 1/2 1/4
```

**Allow clips with cuts and repeat clips**

```
mugen create --exclude-video-filters not_has_cut not_is_repeat
```

**Use only clips that have text**

```
mugen create --video-filters has_text
```

### Preview a music video

---

Create a quick preview of your music video by marking cut locations with beeps and flashes.

```
mugen preview --audio-source Spazzkid_Goodbye.mp3
```

**Input event locations manually**

```
mugen preview --event-locations 2 4 6 10 11 12
```

**This gets interesting!**

```
mugen preview --audio-events-mode onsets --events-speed 1/2 --events-speed-offset 1
```

## Python Usage

### Preview a music video

---

```
from mugen import MusicVideoGenerator

generator = MusicVideoGenerator("Pogo - Forget.mp3")
beats = generator.audio.beats()
beats.speed_multiply(1/2)

generator.preview_events(beats, "forget-preview.mkv")
```

### Create a music video

---

```
from mugen import MusicVideoGenerator

generator = MusicVideoGenerator("in love with a ghost - flowers.mp3", ["wolf children.mkv"])
beats = generator.audio.beats()
beat_groups = beats.group_by_slices([(0, 23), (23, 32), (32, 95), (160, 225), (289,331), (331, 415)])
beat_groups.selected_groups.speed_multiply([1/2, 0, 1/4, 1/2, 1/2, 1/4])
beats = beat_groups.flatten()

music_video = generator.generate_from_events(beats)
music_video.write_to_video_file("flowers.mkv")
music_video.save("flowers.pickle")
```

### Replace a segment in a music video

---

```
from mugen import VideoSource, SourceSampler, MusicVideo

music_video = MusicVideo.load("flowers.pickle")
wolf_children = VideoSource("wolf children.mkv", weight=.2)
spirited_away = VideoSource("spirited away.mkv", weight=.8)
sampler = SourceSampler([wolf_children, spirited_away])
music_video.segments[1] = sampler.sample(music_video.segments[1].duration)

music_video.write_to_video_file("flowers.mkv")
```

### Preview a segment in a music video

---

```
from mugen import MusicVideo

music_video = MusicVideo.load("flowers.pickle")

''' Basic Previews (pretty iffy) '''

# Use a lower fps to reduce lag in playback
music_video.segments[1].preview(fps=10)

# Preview a frame at a specific time (seconds)
music_video.segments[1].show(.5)

''' Jupyter Notebook Previews (much better) '''

music_video.segments[1].ipython_display(autoplay=1, loop=1, width=400)

# Preview a frame at a specific time (seconds)
music_video.segments[1].ipython_display(t=.5, width=400)
```

## Notes

### Subtitles

---

The music videos generated by `create` include subtitles which display segment numbers, locations, and intervals. Likewise the previews generated by `preview` include subtitles which display detected event types, numbers, and locations.

## Troubleshooting

### Progress is stuck

---

The most common reason progress gets stuck is that mugen is trying but can't find any more segments from your video source(s) that pass the default video filters listed under `mugen create --help`. The `not_is_repeat` and `not_has_cut` filters in particular could be causing this if your video source is especially short and/or with little to no time between scene changes. The first one throws out segments that have already been used, and the latter throws out segments where there are scene changes detected. Try using one or more videos that are longer than your music, or otherwise disable the filters with `--exclude-video-filters not_has_cut not_is_repeat`.
