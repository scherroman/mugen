import moviepy.editor as moviepy

def get_video_file_clips(video_files):
    """
    Returns a list of videoFileClips from a list of video file names,
    excluding those that could not be properly read
    """
    # Remove improper video files
    video_file_clips = []
    for video_file in video_files:
        try:
            video_file_clip = moviepy.VideoFileClip(video_file).without_audio()
        except Exception as e:
            print("Error reading video file '{}'. Will be excluded from the music video. Error: {}".format(video_file, e))
            continue
        else:
            video_file_clip.src_file = video_file
            video_file_clips.append(video_file_clip)

    # If no video files to work with, exit
    if len(video_file_clips) == 0:
        print("No more video files left to work with. I can't continue :(")
        sys.exit(1)

    return video_file_clips