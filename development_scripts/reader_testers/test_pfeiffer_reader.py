"""For use in development of the pfeiffer reader. Requires access to sample data."""

from pathlib import Path
from matplotlib import pyplot as plt

from ixdat import Measurement

path_to_file = (
    Path.home()
    / ("Dropbox/ixdat_resources/test_data/pfeiffer")
    / "MID_air, Position 1, RGA PrismaPro 200 44526001, 003-02-2021 17'41'12 - Bin.dat"
)

meas = Measurement.read(path_to_file, reader="pfeiffer")

meas.plot_measurement()
