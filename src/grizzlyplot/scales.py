#!/usr/bin/env python3

# filename: scales.py
# description: scale classes inheriting from class Scale

import numpy as np
import matplotlib.scale as mscale
from matplotlib.category import StrCategoryConverter, UnitData


class Scale():

    def __init__(self, **kwargs):
        pass

    def initialize(self, ax=None):
        return self

    def __call__(self, x):
        raise NotImplementedError()

    def invert(self, x):
        raise NotImplementedError()

    def is_discrete(self):
        return False


class ScaleIdentity(Scale):

    def __init__(self, **kwargs):
        pass

    def __call__(self, x):
        return x

    def transform(self, x):
        return x

    def invert(self, x):
        return x

    def __eq__(self, x):
        return isinstance(x, type(self))


class ScaleDiscrete(Scale):

    def __call__(self, x):
        raise NotImplementedError()

    def is_discrete(self):
        return True


class ScaleDiscreteManual(ScaleDiscrete):
    def __init__(self,
                 mapping: dict = None,
                 strict=False,
                 **kwargs):

        if mapping is None:
            mapping = dict()

        keyvals = [[None, None]] + [
            [key, val] for key, val in
            mapping.items()]
        self.keys = np.array(
            [keyval[0] for keyval in keyvals]
        )[:, np.newaxis]

        self.vals = np.array(
            [keyval[1] for keyval in keyvals])

        self.strict = strict

        super().__init__(**kwargs)

    def __call__(self, x):
        if x is None:
            result = None
        else:
            if isinstance(x, (str, int, float)):
                x = np.array([x])
            elif isinstance(x, list):
                x = np.array(x).flatten()
            elif isinstance(x, np.ndarray):
                x = x.flatten()
            else:
                raise ValueError(
                    "Unsupported input type {} "
                    "for {}"
                    "".format(type(x),
                              type(self)))
            mask = np.argmax(
                x == self.keys,
                axis=0)
            result = self.vals[mask]

            if self.strict:
                test_array = (result == np.array(None))
                if np.any(test_array):
                    ind = np.argmax(test_array)
                    key = x[ind]
                    raise ValueError(
                        "{} could not match requested "
                        "key '{}'".format(self.__repr__(),
                                          key))
                pass  # end if strict
            pass  # end if/else on x is None
        return result


class ScaleColorManual(ScaleDiscreteManual):

    def __init__(self,
                 **kwargs):
        super().__init__(**kwargs)


class ScaleAxis(Scale):

    def __init__(self, scale_name="linear", axis=None):
        allowable = mscale.get_scale_names()
        if scale_name not in allowable:
            raise ValueError(
                "Unknown scale name "
                "{} for ScaleAxis. "
                "Allowed values: {}"
                "".format(scale_name,
                          allowable))
        if axis not in ["x", "y"]:
            raise ValueError(
                "Base ScaleAxis must be "
                "initialized with axis='x' "
                "or axis='y'. Did you mean "
                "to use a ScaleX* or ScaleY* "
                "object?")
        self.scale_name = scale_name
        self.which_axis = axis

    def initialize(self, ax=None):
        self._mscale = mscale.scale_factory(self.scale_name,
                                            ax[0])
        self.ax = ax
        if self.which_axis == "x":
            for axis in self.ax:
                axis.set_xscale(self.scale_name)
        elif self.which_axis == "y":
            for axis in self.ax:
                axis.set_yscale(self.scale_name)
        else:
            raise ValueError(
                "Attempted to set "
                "axis scale for invalid "
                "axis {}".format(self.which_axis))

        return self

    def __call__(self, x):
        return x

    def transform(self, x):
        transform = self._mscale.get_transform()
        return transform.transform(x)

    def invert(self, x):
        inverse = self._mscale.get_transform().inverted()
        return inverse.transform(x)


class ScaleX(ScaleAxis):
    def __init__(self, scale_name="linear", **kwargs):
        super().__init__(scale_name=scale_name,
                         axis="x",
                         **kwargs)


class ScaleY(ScaleAxis):
    def __init__(self, scale_name="linear", **kwargs):
        super().__init__(scale_name=scale_name, axis="y", **kwargs)


class ScaleAxisCategorical(ScaleAxis):

    def initialize(self, ax=None):
        super().initialize(ax=ax)
        self.udat = UnitData()

        return self

    def __call__(self, x):

        x = np.array(x).astype("str")

        result = StrCategoryConverter.convert(x,
                                              self.udat,
                                              self.ax[0])
        if self.which_axis == "x":
            for axis in self.ax:
                axis.xaxis.update_units(x)
        elif self.which_axis == "y":
            for axis in self.ax:
                axis.yaxis.update_units(x)
        else:
            raise ValueError(
                "Attempted to call "
                "axis scale for invalid "
                "axis {}".format(self.which_axis))
        return result

    def invert(self, x):
        inverse_map = {val: key for key, val in
                       self.udat._mapping.items()}
        return inverse_map.get(x, None)

    def is_discrete(self):
        return True


class ScaleXCategorical(ScaleAxisCategorical):

    def __init__(self, **kwargs):
        super().__init__(axis="x", **kwargs)


class ScaleYCategorical(ScaleAxisCategorical):

    def __init__(self, **kwargs):
        super().__init__(axis="y", **kwargs)
