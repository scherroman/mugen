from typing import List, Optional


class Taggable:
    """
    Mixin for tagging objects with arbitrary information
    """

    tags: List[str]

    def __init__(self, *args, tags: Optional[List[str]] = None, **kwargs):
        super().__init__(*args, **kwargs)

        self.tags = tags or []
