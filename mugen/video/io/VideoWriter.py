import os
from typing import List, Optional, Union

from moviepy.editor import VideoClip
from tqdm import tqdm

from mugen.utilities.logger import logger
from mugen.utilities.system import use_temporary_file_fallback


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

    crf
        Constant rate factor (quality) for the music video (0 - 51).

    audio_codec
        Audio codec to use if no audio_file is provided.

    audio_bitrate
        Audio bitrate (kbps) to use if no audio_file is provided.

    ffmpeg_parameters
        Any additional ffmpeg parameters you would like to pass as a list of terms,
        like ['-option1', 'value1', '-option2', 'value2']
    """

    codec: str
    crf: int
    preset: str
    audio_codec: str
    audio_bitrate: int
    ffmpeg_parameters: list

    DEFAULT_VIDEO_CODEC = "libx264"
    DEFAULT_VIDEO_CRF = 18
    DEFAULT_VIDEO_PRESET = "medium"
    DEFAULT_VIDEO_EXTENSION = ".mkv"
    DEFAULT_AUDIO_CODEC = "libmp3lame"
    DEFAULT_AUDIO_BITRATE = 320

    def __init__(self):
        self.codec = self.DEFAULT_VIDEO_CODEC
        self.crf = self.DEFAULT_VIDEO_CRF
        self.preset = self.DEFAULT_VIDEO_PRESET
        self.audio_codec = self.DEFAULT_AUDIO_CODEC
        self.audio_bitrate = self.DEFAULT_AUDIO_BITRATE
        self.ffmpeg_parameters = []

    def write_video_clips_to_directory(
        self,
        video_clips: List[VideoClip],
        directory: str,
        *,
        file_extension: str = DEFAULT_VIDEO_EXTENSION,
        show_progress: bool = True
    ):
        """
        Writes a list of video segments to files in the specified directory
        """
        for index, segment in enumerate(tqdm(video_clips, disable=not show_progress)):
            output_path = os.path.join(directory, str(index) + file_extension)
            self.write_video_clip_to_file(segment, output_path, show_progress=False)

    @use_temporary_file_fallback("output_path", DEFAULT_VIDEO_EXTENSION)
    def write_video_clip_to_file(
        self,
        video_clip: VideoClip,
        output_path: Optional[str] = None,
        *,
        audio: Union[str, bool] = True,
        show_progress: bool = True
    ):
        """
        Writes a video clip to file in the specified directory

        Parameters
        ----------
        video_clip

        output_path

        audio
            Audio for the video clip. Can be True to enable, False to disable, or an external audio file.

        show_progress
            Whether to output progress information to stdout
        """
        ffmpeg_parameters = ["-crf", str(self.crf)] + self.ffmpeg_parameters
        audio_bitrate = str(self.audio_bitrate) + "k"

        video_clip.write_videofile(
            output_path,
            audio=audio,
            preset=self.preset,
            codec=self.codec,
            audio_codec=self.audio_codec,
            audio_bitrate=audio_bitrate,
            ffmpeg_params=ffmpeg_parameters,
            verbose=False,
            logger=logger if show_progress else None,
        )

        return output_path
