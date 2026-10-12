import pandas as pd
from src.data.download import synthetic
from src.data.pipeline import validate
from src.ml.train import choose_threshold


def test_synthetic_schema_and_labels():
    frame = synthetic(1000)
    assert len(frame) == 1000
    assert set(frame["Class"]) == {0, 1}


def test_rejection_and_schema():
    frame = synthetic(200)
    frame.loc[0, "Amount"] = -1
    good, bad = validate(frame)
    assert len(good) == 199
    assert len(bad) == 1


def test_threshold_is_valid():
    assert 0 < choose_threshold([0, 1, 0, 1], [0.1, 0.8, 0.2, 0.9]) < 1
