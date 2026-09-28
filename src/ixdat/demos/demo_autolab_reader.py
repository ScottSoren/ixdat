"""Demo of the autolab reader. Requires the demo data."""

from matplotlib import pyplot as plt

from ixdat import Measurement
from ixdat.demos import get_demo_data_dir


def load_single_file(data_dir=None):
    """Return an ECMeasurement read from a single autolab test file."""
    root = data_dir or get_demo_data_dir()
    return Measurement.read(root / "autolab/autolab_test_file.txt", reader="autolab")


EXAMPLES = {"single_file": load_single_file}


def main(show=True):
    results = {name: load() for name, load in EXAMPLES.items()}
    if show:
        results["single_file"].plot()
        plt.show()
    return results


if __name__ == "__main__":
    results = main()
