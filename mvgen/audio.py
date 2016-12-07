import logging
import essentia
import essentia.standard

# Project modules
import settings as s

# Extracts beat locations and intervals from an audio file
def get_beat_stats(audio_file):
	print("Processing audio beat patterns...")

	# Load audio
	try:
		loader = essentia.standard.MonoLoader(filename = audio_file)
	except Exception as e:
		print(e)
		sys.exit(1)
	
	# Get beat stats from audio
	audio = loader()
	rhythm_loader = essentia.standard.RhythmExtractor2013()
	rhythm = rhythm_loader(audio)
	beat_stats = {'bpm':rhythm[0], 
				  'beat_locations':rhythm[1], 
				  'bpm_estimates':rhythm[3], 
				  'beat_intervals':rhythm[4]}

	logging.debug("\n")
	logging.debug("Beats per minute: {}".format(beat_stats['bpm']))
	logging.debug("Beat locations: {}".format(beat_stats['beat_locations'].tolist()))
	logging.debug("Beat intervals: {}".format(beat_stats['beat_intervals'].tolist()))
	logging.debug("BPM estimates: {}".format(beat_stats['bpm_estimates'].tolist()))
	logging.debug("\n")

	return beat_stats

# Group together beat intervals based on speed_multiplier by
# -> splitting individual beat intervals for speedup
# -> combining adjacent beat intervals for slowdown
# -> using original beat interval for normal speed
def get_beat_interval_groups(beat_intervals, speed_multiplier, speed_multiplier_offset):
	beat_interval_groups = [] 
	beat_intervals = beat_intervals.tolist()
	
	total_beat_intervals_covered = 0
	for index, beat_interval in enumerate(beat_intervals):
		if index < total_beat_intervals_covered:
			continue

		beat_interval_group, num_beat_intervals_covered = get_beat_interval_group(beat_intervals, index, speed_multiplier, speed_multiplier_offset)
		beat_interval_groups.append(beat_interval_group)
		total_beat_intervals_covered += num_beat_intervals_covered

	logging.debug("\nbeat_interval_groups: {}\n".format(beat_interval_groups))

	return beat_interval_groups

### HELPER FUNCTIONS ###

def get_beat_interval_group(beat_intervals, index, speed_multiplier, speed_multiplier_offset):
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