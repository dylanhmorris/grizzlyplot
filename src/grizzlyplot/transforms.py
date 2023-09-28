#!/usr/bin/env python3

# filename: transforms.py
# description: lower level helper functions
# for placing of matplotlib artists

from matplotlib.figure import Figure
from matplotlib.axes import Axes

from matplotlib.transforms import (
    Transform,
    BboxTransformFrom,
    Bbox,
    blended_transform_factory)

import numpy as np


class DynamicTransform(Transform):
    """
    Transforms that recheck
    figure and axis properties
    each time they are called,
    using a transform_getter function
    """
    input_dims = 2
    output_dims = 2

    def __init__(self,
                 transform_getter: callable,
                 figure: Figure = None,
                 axes: Axes = None,
                 **kwargs):
        self.transform_getter = transform_getter
        self.figure = figure
        self.axes = axes
        if (
                self.axes is None and
                self.figure is not None
        ):
            self.axes = self.figure.axes
        super().__init__(**kwargs)

    def refresh(self):
        self._transform = self.transform_getter(
            self.figure, self.axes)

    def transform(self, values):
        self.refresh()
        return self._transform.transform(values)

    def inverted(self):
        self.refresh()
        return self._transform.inverted()


def get_bbox_from_axes(fig, axes):
    bbox = None

    for axis in np.array(axes).flatten():

        data_to_figure = axis.transData + fig.transSubfigure.inverted()
        dat_x, dat_y = axis.get_xlim(), axis.get_ylim()
        bbox_lim = [data_to_figure.transform([dat_x[0], dat_y[0]]),
                    data_to_figure.transform([dat_x[1], dat_y[1]])]
        if bbox is None:
            bbox = Bbox(bbox_lim)
        else:
            bbox = bbox.union([bbox, Bbox(bbox_lim)])
        pass

    return bbox


def get_bbox_from_gridspec(fig, gs):
    axes = [ax for ax in fig.axes if ax.get_gridspec() == gs]
    return get_bbox_from_axes(fig, axes)


def get_axspan_transform(fig, axes):
    return (
        BboxTransformFrom(
            get_bbox_from_axes(fig, axes)).inverted() +
        fig.transSubfigure)


def get_xspan_transform(fig, axes):
    return blended_transform_factory(
        get_axspan_transform(fig, axes),
        fig.transSubfigure
    )


def get_yspan_transform(fig, axes):
    return blended_transform_factory(
        fig.transSubfigure,
        get_axspan_transform(fig, axes)
    )


def dynamic_axspan_transform(
        fig, axes=None):
    return DynamicTransform(
        get_axspan_transform,
        figure=fig,
        axes=axes)


def dynamic_xspan_transform(
        fig, axes=None):
    return DynamicTransform(
        get_xspan_transform,
        figure=fig,
        axes=axes)


def dynamic_yspan_transform(
        fig, axes=None):
    return DynamicTransform(
        get_yspan_transform,
        figure=fig,
        axes=axes)
