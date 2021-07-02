import numpy as np
from .db import Saveable, PlaceHolderObject
from .data_series import DataSeries, TimeSeries, Field


class Spectrum(Saveable):
    """The Spectrum class.

    A spectrum is a data structure including one-dimensional arrays of x and y variables
    of equal length. Typically, information about the state of a sample can be obtained
    from a plot of y (e.g. adsorbance OR intensity OR counts) vs x (e.g energy OR
    wavelength OR angle OR mass-to-charge ratio). Even though in reality it takes time
    to require a spectrum, a spectrom is considered to represent one instance in time.

    In ixdat, the data of a spectrum is organized into a Field, where the y-data is
    considered to span a space defined by the x-data and the timestamp. If the x-data
    has shape (N, ), then the y-data has shape (N, 1) to span the x-axis and the
    single-point t axis.

    The Spectrum class makes the data in this field intuitively available. If spec
    is a spectrum, spec.x and spec.y give access to the x and y data, respectively,
    while spec.xseries and spec.yseries give the corresponding DataSeries.
    """

    table_name = "spectrum"
    column_attrs = {
        "name",
        "technique",
        "metadata",
        "sample_name",
        "field_id",
    }

    def __init__(
        self,
        name,
        technique=None,
        metadata=None,
        sample_name=None,
        reader=None,
        field=None,
        field_id=None,
    ):
        """Initiate a spectrum

        Args:
            name (str): The name of the spectrum
            metadata (dict): Free-form spectrum metadata. Must be json-compatible.
            technique (str): The spectrum technique
            sample_name (str): The sample name
            reader (Reader): The reader, if read from file
            field (Field): The Field containing the data (x, y, and tstamp)
            field_id (id): The id in the data_series table of the Field with the data,
                if the field is not yet loaded from backend.
        """
        super().__init__()
        self.name = name
        self.technique = technique
        self.metadata = metadata
        self.sample_name = sample_name
        self.reader = reader
        self._field = field or PlaceHolderObject(field_id, cls=Field)

        self._plotter = None
        # defining this method here gets it the right docstrings :D
        self.plot = self.plotter.plot

    @property
    def plotter(self):
        """The default plotter for Measurement is ValuePlotter."""
        if not self._plotter:
            from .plotters.spectrum_plotter import SpectrumPlotter

            # FIXME: I had to import here to avoid running into circular import issues

            self._plotter = SpectrumPlotter(spectrum=self)
        return self._plotter

    @classmethod
    def read(cls, path_to_file, reader, **kwargs):
        """Return a Measurement object from parsing a file with the specified reader

        Args:
            path_to_file (Path or str): The path to the file to read
            reader (str or Reader class): The (name of the) reader to read the file with.
            kwargs: key-word arguments are passed on to the reader's read() method.
        """
        if isinstance(reader, str):
            # TODO: see if there isn't a way to put the import at the top of the module.
            #    see: https://github.com/ixdat/ixdat/pull/1#discussion_r546437471
            from .readers import READER_CLASSES

            reader = READER_CLASSES[reader]()
        # print(f"{__name__}. cls={cls}")  # debugging
        return reader.read(path_to_file, cls=cls, **kwargs)

    @property
    def data_objects(self):
        """The data-containing objects that need to be saved when the spectrum is saved.

        For a field to be correctly saved and loaded, its axes_series must be saved
        first. So there are three series in the data_objects to return
        FIXME: with backend-specifying id's, field could check for itself whether
            its axes_series are already in the database.
        """
        series_list = self.field.axes_series
        series_list.append(self.field)
        return series_list

    @classmethod
    def from_data(
        cls,
        x,
        y,
        tstamp=None,
        x_name="x",
        y_name="y",
        x_unit_name=None,
        y_unit_name=None,
        **kwargs
    ):
        """Initiate a spectrum from data. Does so via cls.from_series

        Args:
            x (np array): x data
            y (np array): y data
            tstamp (timestamp): the timestamp of the spectrum. Defaults to None.
            x_name (str): Name of the x variable. Defaults to 'x'
            y_name (str): Name of the y variable. Defaults to 'y'
            x_unit_name (str): Name of the x unit. Defaults to None
            y_unit_name (str): Name of the y unit. Defaults to None
            kwargs: key-word arguments are passed on ultimately to cls.__init__
        """
        xseries = DataSeries(data=x, name=x_name, unit_name=x_unit_name)
        yseries = DataSeries(data=y, name=y_name, unit_name=y_unit_name)
        return cls.from_series(xseries, yseries, tstamp, **kwargs)

    @classmethod
    def from_series(cls, xseries, yseries, tstamp, **kwargs):
        """Initiate a spectrum from data. Does so via cls.from_field

        Args:
            xseries (DataSeries): a series with the x data
            yseries (DataSeries): a series with the y data. The y data should be a
                vector of the same length as the x data.
            tstamp (timestamp): the timestamp of the spectrum. Defaults to None.
            kwargs: key-word arguments are passed on ultimately to cls.__init__
        """
        tseries = TimeSeries(
            data=np.array([0]), tstamp=tstamp, unit_name="s", name="spectrum time / [s]"
        )
        field = Field(
            data=np.array([yseries.data]),
            axes_series=[xseries, tseries],
            name=yseries.name,
            unit_name=yseries.unit_name,
        )
        return cls.from_field(field, **kwargs)

    @classmethod
    def from_field(cls, field, **kwargs):
        """Initiate a spectrum from data. Does so via cls.from_field

        Args:
            field (Field): The field containing all the data of the spectrum.
                field.data is the y-data, which is considered to span x and t.
                field.axes_series[0] is a DataSeries with the x data.
                field.axes_series[1] is a TimeSeries with one time point.
            kwargs: key-word arguments are passed on ultimately to cls.__init__
        """
        spectrum_as_dict = kwargs
        spectrum_as_dict["field"] = field
        if "name" not in spectrum_as_dict:
            spectrum_as_dict["name"] = field.name
        return cls.from_dict(spectrum_as_dict)

    @property
    def field(self):
        """Since a spectrum can be loaded lazily, we make sure the field is loaded"""
        if isinstance(self._field, PlaceHolderObject):
            self._field = self._field.get_object()
        return self._field

    @property
    def field_id(self):
        """The id of the field"""
        return self.field.id

    @property
    def xseries(self):
        """The x DataSeries is the first axis of the field"""
        return self.field.axes_series[0]

    @property
    def x(self):
        """The x data is the data attribute of the xseries"""
        return self.xseries.data

    @property
    def x_name(self):
        """The name of the x variable is the name attribute of the xseries"""
        return self.xseries.name

    @property
    def yseries(self):
        """The yseries is a DataSeries reduction of the field"""
        return DataSeries(
            name=self.field.name, data=self.y, unit_name=self.field.unit_name
        )

    @property
    def y(self):
        """The y data is the data attribute of the field"""
        return self.field.data[0]

    @property
    def y_name(self):
        """The name of the y variable is the name attribute of the field"""
        return self.field.name

    @property
    def tseries(self):
        """The TimeSeries is the second of the axes_series of the field"""
        return self.field.axes_series[1]

    @property
    def tstamp(self):
        """The value with respect to epoch of the field's single time point"""
        tseries = self.tseries
        return tseries.data[0] + tseries.tstamp