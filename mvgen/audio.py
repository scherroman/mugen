import sys
import logging
import pprint
import essentia
import essentia.standard
import subprocess as sp

# Project modules
import settings as s
import utility as util

def get_beat_stats(audio_file):
    """
    Extracts beat locations and intervals from an audio file
    """
    print("Processing audio beat patterns...")

    # Load audio
    try:
        loader = essentia.standard.MonoLoader(filename = audio_file)
    except Exception as e:
        print("Error reading audio file '{}'. Cannot continue. Error: {}".format(audio_file, e))
        sys.exit(1)
    
    # Get beat stats from audio
    audio = loader()
    rhythm_loader = essentia.standard.RhythmExtractor2013()
    rhythm = rhythm_loader(audio)
    beat_stats = {'bpm':rhythm[0], 'beat_locations':rhythm[1], 'bpm_estimates':rhythm[3], 
                  'beat_intervals':rhythm[4]}

    logging.debug("\n")
    logging.debug("Beats per minute: {}".format(pprint.pformat(beat_stats['bpm'])))
    logging.debug("Beat locations: {}".format(pprint.pformat(beat_stats['beat_locations'].tolist())))
    logging.debug("Beat intervals: {}".format(pprint.pformat(beat_stats['beat_intervals'].tolist())))
    logging.debug("BPM estimates: {}".format(pprint.pformat(beat_stats['bpm_estimates'].tolist())))
    logging.debug("\n")

    return beat_stats

def get_beat_interval_groups(beat_intervals, speed_multiplier, speed_multiplier_offset):
    """
    Group together beat intervals based on speed_multiplier by
    -> splitting individual beat intervals for speedup
    -> combining adjacent beat intervals for slowdown
    -> using original beat interval for normal speed
    """
    beat_interval_groups = [] 
    beat_intervals = beat_intervals.tolist()
    
    total_beat_intervals_covered = 0
    for index, beat_interval in enumerate(beat_intervals):
        if index < total_beat_intervals_covered:
            continue

        beat_interval_group, num_beat_intervals_covered = get_beat_interval_group(beat_interval, index, beat_intervals, 
                                                                                  speed_multiplier, speed_multiplier_offset)
        beat_interval_groups.append(beat_interval_group)
        total_beat_intervals_covered += num_beat_intervals_covered

    logging.debug("\nbeat_interval_groups: {}\n".format(pprint.pformat(beat_interval_groups)))

    return beat_interval_groups

### HELPER FUNCTIONS ###

def get_beat_interval_group(beat_interval, index, beat_intervals, 
                            speed_multiplier, speed_multiplier_offset):
    """
    Assign beat intervals to groups based on speed_multiplier
    """
    beat_interval_group = None
    num_beat_intervals_covered = 0

    # Combine adjacent beat intervals
    if speed_multiplier < 1:
        desired_num_intervals = speed_multiplier.denominator
        # Apply offset to first group
        if index == 0 and speed_multiplier_offset:
            desired_num_intervals -= speed_multiplier_offset

        remaining_intervals = len(beat_intervals) - index
        if remaining_intervals < desired_num_intervals:
            desired_num_intervals = remaining_intervals

        interval_combo = sum(beat_intervals[index:index + desired_num_intervals])
        interval_combo_numbers = range(index, index + desired_num_intervals)
        beat_interval_group = {'intervals':[interval_combo], 'beat_interval_numbers':interval_combo_numbers}

        num_beat_intervals_covered = desired_num_intervals
    # Split up the beat interval
    elif speed_multiplier > 1:
        speedup_factor = speed_multiplier.numerator
        interval_fragment = beat_interval/speedup_factor
        interval_fragments = [interval_fragment] * speedup_factor
        beat_interval_group = {'intervals':interval_fragments, 'beat_interval_numbers':index}
        num_beat_intervals_covered = 1
    # Use the original beat interval
    else:
        beat_interval_group = {'intervals':[beat_interval], 'beat_interval_numbers':index}
        num_beat_intervals_covered = 1

    return beat_interval_group, num_beat_intervals_covered

def get_temp_offset_audio_file(audio_file, offset):
    """
    Create a temporary new audio file with the given offset to use for the music video
    """
    print("Creating temporary audio file with specified offset {}...".format(offset))
    offset_audio_path = None

    # Get path to temporary offset audio file
    util.ensure_dir(s.TEMP_PATH_BASE)
    temp_offset_audio_path = util.get_temp_audio_file_path(audio_file)

    cmd = [
            util.get_ffmpeg_binary(),
            '-i', audio_file,
            '-ss', str(offset),
            '-acodec', 'copy',
            temp_offset_audio_path
          ]

    # Generate new temporary audio file with offset
    p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
    p_out, p_err = p.communicate()
    
    if p.returncode != 0:
        raise IOError("Failed to create temporary audio file with specified offset {}. ffmpeg returned error code: {}\n\nOutput from ffmpeg:\n\n{}".format(offset, p.returncode, p_err))
    
    return temp_offset_audio_path


