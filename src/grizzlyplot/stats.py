#!/usr/bin/env python3

# filename: stats.py
# description: stat classes
# inheriting from base class Stat

import numpy as np
import KDEpy


class Stat():
    pass


class StatIdentity(Stat):

    def __init__(self):
        pass

    def __call__(self, group_vals, scales):
        return group_vals


class StatPointInterval(Stat):

    def __init__(self,
                 point_estimate_func=None,
                 interval_func=None,
                 interval_lower=0.025,
                 interval_upper=0.975,
                 interval_axes=None):
        if point_estimate_func is None:
            point_estimate_func = np.median
        if interval_func is None:
            interval_func = np.quantile
        if interval_axes is None:
            interval_axes = ["x", "y"]

        self.point_estimate_func = point_estimate_func
        self.interval_func = interval_func
        self.interval_lower = interval_lower
        self.interval_upper = interval_upper
        self.interval_axes = interval_axes

    def get_errors(
            self,
            values,
            point_estimate):
        """
        Get properly formatted
        upper and lower errors
        """
        return np.abs(
            np.vstack(
                [self.interval_func(
                    values,
                    self.interval_lower),
                 self.interval_func(
                     values,
                     self.interval_upper)
                 ]) -
            point_estimate)

    def __call__(self, group_vals, scales):

        result = dict(group_vals)

        for axis in self.interval_axes:
            point = self.point_estimate_func(
                group_vals[axis])
            error = self.get_errors(
                group_vals[axis],
                point)
            result[axis] = point
            result[axis + "err"] = error

        return result


class StatDensity(Stat):

    support_axis_to_density_axis = {
        "x": "y",
        "y": "x"}

    def __init__(self,
                 estimator_function=None,
                 support_axis="y",
                 n_points=None,
                 autolimit_margin=0.05,
                 kernel="gaussian",
                 bw="silverman",
                 **kwargs):
        if estimator_function is None:
            estimator_function = KDEpy.FFTKDE
        self.estimator_function = estimator_function(
            kernel=kernel,
            bw=bw)
        if support_axis in ["x", "y"]:
            self.support_axis = support_axis
            self.density_axis = (
                self.support_axis_to_density_axis.get(
                    self.support_axis, None))
        else:
            raise ValueError("Unsupported support axis"
                             "{}".format(support_axis))
        self.n_points = n_points
        # passed to the estimator

    def __call__(self, group_vals, scales):
        ax_scale = scales[self.support_axis]
        vals_to_fit = ax_scale.transform(
            group_vals[self.support_axis])

        support, density = self.estimator_function.fit(
            vals_to_fit
        ).evaluate(
            self.n_points
        )

        result = dict(group_vals)
        result["support"] = ax_scale.invert(support)
        result["density"] = density

        return result
