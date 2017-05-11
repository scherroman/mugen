from typing import List, Optional as Opt


class Taggable:
    """
    Mixin for tagging objects with arbitrary information
    """
    tags: List[str]

    def __init__(self, *args, tags: Opt[List[str]] = None, **kwargs):
        self.tags = tags or []
