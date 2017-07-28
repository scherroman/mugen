import moviepy.editor as moviepy


class CompositeVideoClip(moviepy.CompositeVideoClip):
    """
    A wrapper around moviepy's CompositeVideoClip, fixing issues with fps calculation
    """
    def __init__(self, clips, *args, **kwargs):
        super().__init__(clips, *args, **kwargs)

        fpss = [c.fps for c in clips if hasattr(c, 'fps') and c.fps is not None]
        if len(fpss) == 0:
            self.fps = None
        else:
            self.fps = max(fpss)
