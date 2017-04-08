from typing import List, Optional as Opt


class Taggable:
    """
    Mixin for tagging objects with arbitrary information
    """
    tags: List[str] = []

    def __init__(self, tags: Opt[List[str]] = None):
        if tags:
            self.tags = tags
