from mugen.mixins.Persistable import Persistable


class CoolClass(Persistable):
    def __init__(self, coolness: int = 1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coolness = coolness


def test_save_load():
    cool = CoolClass(5)
    cool_file = cool.save()
    loaded_cool = CoolClass.load(cool_file)

    assert loaded_cool.coolness == cool.coolness
