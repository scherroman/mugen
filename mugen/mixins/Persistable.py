from typing import Optional

import dill

from mugen.utilities.system import use_temporary_file_fallback

PICKLE_EXTENSION = ".pickle"


class Persistable:
    """
    Mixin for persisting objects
    """

    @use_temporary_file_fallback("output_path", PICKLE_EXTENSION)
    def save(self, output_path: Optional[str] = None):
        with open(output_path, "wb") as output_file:
            dill.dump(self, output_file)

        return output_path

    @classmethod
    def load(cls, input_path: str):
        with open(input_path, "rb") as input_file:
            persistable = dill.load(input_file)

        return persistable
