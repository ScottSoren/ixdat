import numpy as np
from .ec import ECMeasurement
from ..data_series import ValueSeries


class CyclicVoltammagram(ECMeasurement):
    """Class for cyclic voltammatry measurements.

    Onto ECMeasurement, this adds:
    - a property `cycle` which is a ValueSeries on the same TimeSeries as potential,
        which counts cycles. "cycle" becomes the Measurement's `sel_str`. Indexing with
        integer or iterable selects according to `cycle`.
    - functions for quantitatively comparing cycles (like a stripping cycle, base cycle)
    - the default plot() is plot_vs_potential()
    """

    selector_name = "cycle"
    """Name of the default selector"""

    def __init__(self, *args, **kwargs):
        """Only reason to have an __init__ here is to set the default plot()"""
        super().__init__(*args, **kwargs)
        self.plot = self.plotter.plot_vs_potential  # gets the right docstrings! :D

        self.start_potential = None  # see `redefine_cycle`
        self.redox = None  # see `redefine_cycle`

    def __getitem__(self, key):
        """Given int list or slice key, return a CyclicVoltammagram with those cycles"""
        if isinstance(key, slice):
            start, stop, step = key.start, key.stop, key.step
            if step is None:
                step = 1
            key = list(range(start, stop, step))
        if isinstance(key, (int, list)):
            if type(key) is list and not all([type(i) is int for i in key]):
                print("can't get an item of type list unless all elements are int")
                print(f"you tried to get key = {key}.")
                raise AttributeError
            return self.select(key)
        return super().__getitem__(key)

    def redefine_cycle(self, start_potential=None, redox=None, N_points=5):
        """Build `cycle` which iterates when passing through start_potential

        Args:
            start_potential (float): The potential in [V] at which the cycle counter will
                iterate. If start_potential is not given, the cycle is just the
                `selector` inherited from ECMeasurement shifted to start at 0.
            redox (bool): True (or 1) for anodic, False (or 0) for cathodic. The
                direction in which the potential is scanning through start_potential to
                trigger an iteration of `cycle`.
            N_points (int): The number of consecutive points for which the potential
                needs to be above (redox=True) or below (redox=False) the
                start_potential for the new cycle to register.
        """
        self.start_potential = start_potential
        self.redox = redox
        if start_potential is None:
            old_cycle_series = self["cycle_number"]
            new_cycle_series = ValueSeries(
                name="cycle",
                unit_name=old_cycle_series.unit_name,
                data=old_cycle_series.data - min(old_cycle_series.data),
                tseries=old_cycle_series.tseries,
            )
        else:
            cycle_vec = np.zeros(self.t.shape)
            c = 0
            n = 0
            N = len(self.t)
            v = self.v
            if not redox:
                # easiest way to reverse directions is to use the same > < operators
                # but negate the arguments
                start_potential = -start_potential
                v = -v
            while n < N:
                # mask on remaining potential, True wherever behind the start potential:
                mask_behind = v[n:] < start_potential
                if True not in mask_behind:
                    # if the potenential doesn't go behind start potential again, then
                    # there are no more cycles
                    break
                else:
                    # the potential has to get behind the start potential for at least
                    # N_points data points before a new cycle can start.
                    n += np.argmax(mask_behind) + N_points

                # a mask on remaining potential, True wherever ahead of start potential:
                mask_in_front = v[n:] > start_potential
                if True not in mask_in_front:  # again, no more cycles.
                    break
                else:
                    # We've already been behind for N_points, so as soon as the
                    # potential gets ahead of the start_potential, a new cycle begins!
                    n += np.argmax(mask_in_front)
                c += 1
                cycle_vec[n:] = c  # and subsequent points increase in cycle number
                n += N_points  # have to be above start_potential for N_points
                # datapoints before getting behind it for this to count as a cycle.
            new_cycle_series = ValueSeries(
                name="cycle",
                unit_name="",
                data=cycle_vec,
                tseries=self.potential.tseries,
            )
        self.replace_series("cycle", new_cycle_series)
