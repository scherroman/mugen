import os
from typing import Optional as Opt, List, Tuple, Union

from moviepy.editor import VideoClip
from tqdm import tqdm

DEFAULT_AUDIO_BITRATE = 320
DEFAULT_AUDIO_CODEC = 'mp3'

DEFAULT_VIDEO_PRESET = 'medium'
DEFAULT_VIDEO_CODEC = 'libx264'
DEFAULT_VIDEO_CRF = 18

DEFAULT_VIDEO_EXTENSION = '.mkv'


class VideoWriter:
    """
    Class for writing VideoClips and VideoSegments to file
    
    Parameters
    ----------   
    preset
        Sets the time that FFMPEG will spend optimizing compression while writing the video to file.
        Note that this does not impact the quality of the video, only the size of the video file. 
        So choose ultrafast when you are in a hurry and file size does not matter.
        Choices are: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo. 
          
    codec 
        Video codec to use when writing the music video to file. 
        Defaults to :data:`~mugen.video.constants.DEFAULT_VIDEO_CODEC`
        
    crf 
        Constant rate factor (quality) for the music video (0 - 51).
        Defaults to :data:`~mugen.video.constants.DEFAULT_VIDEO_CRF`
        
    audio_codec 
        Audio codec to use if no audio_file is provided.
        Defaults to :data:`~mugen.video.constants.DEFAULT_AUDIO_CODEC`
        
    audio_bitrate 
        Audio bitrate (kbps) to use if no audio_file is provided.
        Defaults to :data:`~mugen.video.constants.DEFAULT_AUDIO_BITRATE` (kbps)
        
    ffmpeg_params 
        Any additional ffmpeg parameters you would like to pass as a list of terms, 
        like ['-option1', 'value1', '-option2', 'value2']
    """
    preset: str = DEFAULT_VIDEO_PRESET
    codec: str = DEFAULT_VIDEO_CODEC
    crf: int = DEFAULT_VIDEO_CRF
    audio_codec: str = DEFAULT_AUDIO_CODEC
    audio_bitrate: int = DEFAULT_AUDIO_BITRATE
    ffmpeg_params: list

    def __init__(self, preset: Opt[str] = None, codec: Opt[str] = None, crf: Opt[int] = None,
                 audio_codec: Opt[str] = None, audio_bitrate: Opt[int] = None, ffmpeg_params: Opt[List[str]] = None):
        if preset is not None:
            self.preset = preset
        if codec is not None:
            self.codec = codec
        if crf is not None:
            self.crf = crf
        if audio_codec is not None:
            self.audio_codec = audio_codec
        if audio_bitrate is not None:
            self.audio_bitrate = audio_bitrate
        self.ffmpeg_params = ffmpeg_params or []

    def write_video_clips_to_directory(self, video_clips: List[VideoClip], directory: str, *,
                                       file_extension: Opt[str] = None, audio: Union[str, bool] = True):
        """
        Writes a list of video segments to files in the specified directory
        """
        if not file_extension:
            file_extension = DEFAULT_VIDEO_EXTENSION

        for index, segment in enumerate(tqdm(video_clips)):
            output_path = os.path.join(directory, str(index) + file_extension)
            self.write_video_clip_to_file(segment, output_path, audio=audio, verbose=False, progress_bar=False)

    def write_video_clip_to_file(self, video_clip: VideoClip, output_path: str, *, audio: Union[str, bool] = True,
                                 progress_bar=True, verbose=True):
        """
        Writes a video clip to file in the specified directory
        """
        # Prepend crf to ffmpeg_params
        ffmpeg_params = ['-crf', str(self.crf)] + self.ffmpeg_params
        audio_bitrate = str(self.audio_bitrate) + 'k'

        video_clip.write_videofile(output_path, audio=audio,
                                   preset=self.preset, codec=self.codec, audio_codec=self.audio_codec,
                                   audio_bitrate=audio_bitrate, ffmpeg_params=ffmpeg_params, verbose=verbose,
                                   progress_bar=progress_bar)
