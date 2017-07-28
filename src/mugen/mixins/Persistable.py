from dill import dill
from typing import Optional as Opt

from mugen.utility import temp_file_enabled

PICKLE_EXTENSION = '.pickle'


class Persistable:
    """
    Mixin for persisting objects
    """

    @temp_file_enabled('output_path', PICKLE_EXTENSION)
    def save(self, output_path: Opt[str] = None):
        with open(output_path, "wb") as output_file:
            dill.dump(self, output_file)

        return output_path

    @classmethod
    def load(cls, input_path: str):
        with open(input_path, "rb") as input_file:
            persistable = dill.load(input_file)

        return persistable
