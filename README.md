```

 _ __ ___  _   _  __ _  ___ _ __
| '_ ` _ \| | | |/ _` |/ _ \ '_ \
| | | | | | |_| | (_| |  __/ | | |
|_| |_| |_|\__,_|\__, |\___|_| |_|
                  |___/
```

[![tests](https://img.shields.io/github/actions/workflow/status/scherroman/mugen/test.yml?branch=master&label=tests&logo=github)](https://github.com/scherroman/mugen/actions/workflows/test.yml)
[![coverage](https://img.shields.io/codecov/c/github/scherroman/mugen?label=coverage&logo=codecov)](https://codecov.io/gh/scherroman/mugen)
[![Maintainability](https://api.codeclimate.com/v1/badges/76b9fd9b7ca0250ad526/maintainability)](https://codeclimate.com/github/scherroman/mugen/maintainability)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![license](https://img.shields.io/github/license/scherroman/mugen?color=blue)](https://github.com/scherroman/mugen/blob/master/LICENSE)
[![Ko-Fi](https://img.shields.io/badge/buy%20me%20a%20coffee-F16061?logo=ko-fi&logoColor=white)](https://ko-fi.com/scherroman)

A command-line music video generator based on rhythm

Use it to brainstorm AMVs, montages, and more! [Check it out](https://youtu.be/ZlTR6XULe5M).

Built with [moviepy](https://github.com/Zulko/moviepy) programmatic video editing and [librosa](https://github.com/librosa/librosa) audio analysis.

## Strategy

1. Provide an audio file and a set of video files

2. Perform rhythm analysis to identify beat locations

3. Generate a set of random video segments synced to the beat

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
conda activate mugen
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

### Preview a music video

---

Create a quick preview of how your music video will be cut to the music with beeps and flashes.

It's common for beat timing to be a little off or too fast, so to save time it's recommended to generate and tweak previews beforehand to make sure the timing feels right.

```
mugen preview --audio-source Spazzkid_Goodbye.mp3
```

**Slow down cuts to every other beat**

```
--events-speed 1/2
```

**Offset the grouping of beats when slowing down cuts**

```
--events-speed 1/4 --events-speed-offset 2
```

**Globally offset beat locations in seconds**

```
--events-offset 0.25
```

**Slow down cuts for leading and trailing weak beats**

```
--beats-mode weak_beats --group-events-by-type --group-speeds 1/2 1 1/4
```

**Control the speed of cuts for specific sections**

```
--group-events-by-slices (0,23) (23,32) (32,95) (160,225) (289,321) (321,415) --group-speeds 1/2 0 1/4 1/2 1/2 1/4
```

**Input event locations manually in seconds**

```
--event-locations 2 4 6 10.5 11 12
```

**Use onsets instead of beats**

```
--audio-events-mode onsets
```

### Create a music video

---

```
mugen create --audio-source MACINTOSH_PLUS_420.mp3 --video-sources TimeScapes.mkv
```

**Use a series 60% of the time and a movie 40% of the time**

```
--video-sources Neon_Genesis_Evangelion/ The_End_of_Evangelion.mkv --video-source-weights .6 .4
```

**Use all files and subdirectories under a directory**

```
--video-sources Miyazaki/*
```

**Use files that match a prefix**

```
--video-sources Higurashi/S01*
```

**Allow clips with cuts and repeat clips**

```
--exclude-video-filters not_has_cut not_is_repeat
```

**Use only clips that have text**

```
--video-filters has_text
```

**Save individual segments**

To save all the segments that make up the music video as separate files:

```
--save-segments
```

To save all the rejected segments that did not pass filters as separate files:

```
--save-rejected-segments
```

These will be saved as `.mp4` files in folders alongside the music video.

## Python Usage

### Preview a music video

---

```
from mugen import MusicVideoGenerator

generator = MusicVideoGenerator("Pogo - Forget.mp3")
beats = generator.audio.beats()
beats.speed_multiply(1/2)

preview = generator.preview_from_events(beats, "forget-preview.mkv")
preview.write_to_video_file("preview.mkv")
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

''' Basic Previews (less smooth) '''

# Use a lower fps to reduce lag in playback
music_video.segments[1].preview(fps=10)

# Preview a frame at a specific time (seconds)
music_video.segments[1].show(.5)

''' Jupyter Notebook Previews (smoother) '''

music_video.segments[1].ipython_display(autoplay=1, loop=1, width=400)

# Preview a frame at a specific time (seconds)
music_video.segments[1].ipython_display(t=.5, width=400)
```

## Notes

### Subtitles

The videos generated by `create` and `preview` include a subtitle track which display segment types, numbers, and locations.

### Text detection

Currently text detection uses the [Tesseract](https://github.com/tesseract-ocr/tesseract) optical character recognition engine and thus has been trained mainly on documents with standard type fonts. Credit sequences with nonstandard or skewed fonts will likely not be detected. It is also possible for Tesseract to occasionally falsely detect text in some images.

## Troubleshooting

### Progress is stuck

The most common reason progress gets stuck is that mugen is trying but can't find any more segments from your video source(s) that pass the default video filters listed under `mugen create --help`. The `not_is_repeat` and `not_has_cut` filters in particular could be causing this if your video source is especially short and/or with little to no time between scene changes. The first one throws out segments that have already been used, and the latter throws out segments where there are scene changes detected. Try using one or more videos that are longer than your music, or otherwise disable the filters with `--exclude-video-filters not_has_cut not_is_repeat`.

## Contributing

Thanks for considering contributing! To get started, see the [contributing documentation](documentation/CONTRIBUTING.md) for details on development setup and submitting pull requests.
