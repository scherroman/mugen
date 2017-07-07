import pytest

from mugen.video.cuts import Cut, CutList, EndCut


@pytest.fixture
def cuts() -> CutList:
    return CutList([6, 12, 18, 24, Cut(30)])


def test_video_cut_list__ensure_end_cut(cuts):
    cuts.ensure_end_cut(40)
    assert cuts == CutList([6, 12, 18, 24, 30, EndCut(40)])
