#!/usr/bin/env python3
# *_* coding: utf-8 *_*

"""
description: geometric object classes
inheriting from base
:class:`~grizzlyplot.geom.Geom`
"""

import numpy as np
from grizzlyplot.geom import Geom
import grizzlyplot.stats as stats
from scipy.integrate import simpson


class GeomXY(Geom):
    """
    GeomXY class

    Basic XY scatter geom, from which
    specific geoms such as :class:`GeomPoint`
    inherit.

    Parameters
    ----------
    data : :class:`polar.DataFrame`
        DataFrame to query for data
        for this geom. Geom-level data
        takes priority over
        plot-level data if both are
        provided. Default None
    mapping : :py:class:`dict`
        Aesthetic mapping for this geom,
        associating aesthetic
        attributes that may be used by the geom,
        such as x coordinate, y coordinate,
        shape, or color, to data feature
        (typically column names
        in a tidy data table). Default `{}`.
        Geom-level aesthetic mappings take priority
        over plot-level ones if both are provided.
    """

    aesthetics = frozenset({
        "x",
        "y",
        "color",
        "marker",
        "alpha",
        "lw",
        "markeredgecolor"})
    grouped_aesthetics = frozenset([
        aes for aes in aesthetics
        if aes not in ["x", "y"]])
    legend_excluded_aesthetics = frozenset({
        "x", "y"})
    required_aesthetics = frozenset({
        "x", "y"})

    def render_group(
            self,
            group_vals=None,
            scales=None,
            ax=None):

        ax.plot(
            group_vals["x"],
            group_vals["y"],
            marker=group_vals["marker"],
            color=group_vals["color"],
            alpha=group_vals["alpha"],
            lw=group_vals["lw"],
            markeredgecolor=group_vals["markeredgecolor"])


class GeomPoint(GeomXY):
    default_aesthetic_values = {
        "marker": "o",
        "lw": 0}


class GeomLine(GeomXY):
    pass


class GeomPointLine(GeomXY):
    default_aesthetic_values = {
        "marker": "o",
        "lw": 1}


class GeomHLines(Geom):
    aesthetics = frozenset({
        "yintercept",
        "xmin",
        "xmax",
        "color",
        "alpha",
        "lw",
        "ls"})
    grouped_aesthetics = frozenset([
        aes for aes in aesthetics
    ])

    legend_excluded_aesthetics = frozenset([
        "yintercept",
        "xmin",
        "xmax"
    ])

    required_aesthetics = frozenset([
        "yintercept",
        "xmin",
        "xmax"
    ])

    default_aesthetic_values = {
        "color": "k",
        "ls": "solid",
        "lw": 1,
        "alpha": 1}

    def render_group(
            self,
            group_vals=None,
            scales=None,
            ax=None):
        ax.hlines(y=group_vals["yintercept"],
                  xmin=group_vals["xmin"],
                  xmax=group_vals["xmax"],
                  color=group_vals["color"],
                  alpha=group_vals["alpha"],
                  lw=group_vals["lw"],
                  ls=group_vals["ls"])


class GeomAxHLines(Geom):

    aesthetics = frozenset({
        "yintercept",
        "left_limit",
        "right_limit",
        "color",
        "alpha",
        "lw",
        "ls"})

    grouped_aesthetics = frozenset([
        aes for aes in aesthetics
    ])

    legend_excluded_aesthetics = frozenset({
        "yintercept",
        "left_limit",
        "right_limit"
    })

    required_aesthetics = frozenset({
        "yintercept"
    })

    default_aesthetic_values = {
        "color": "k",
        "ls": "solid",
        "lw": 1,
        "alpha": 1,
        "left_limit": 0,
        "right_limit": 1}

    def render_group(
            self,
            group_vals=None,
            scales=None,
            ax=None):
        ax.axhline(y=group_vals["yintercept"],
                   xmin=group_vals["left_limit"],
                   xmax=group_vals["right_limit"],
                   color=group_vals["color"],
                   alpha=group_vals["alpha"],
                   lw=group_vals["lw"],
                   ls=group_vals["ls"])


class GeomVLines(Geom):

    aesthetics = frozenset({
        "xintercept",
        "ymin",
        "ymax",
        "color",
        "alpha",
        "lw",
        "ls"})

    grouped_aesthetics = frozenset([
        aes for aes in aesthetics
    ])

    required_aesthetics = frozenset({
        "xintercept",
        "ymin",
        "ymax"
        })

    legend_excluded_aesthetics = frozenset({
        "xintercept",
        "ymin",
        "ymax"
    })

    default_aesthetic_values = {
        "color": "k",
        "ls": "solid",
        "lw": 1,
        "alpha": 1}

    def render_group(
            self,
            group_vals=None,
            scales=None,
            ax=None):
        ax.vlines(x=group_vals["xintercept"],
                  ymin=group_vals["ymin"],
                  ymax=group_vals["ymax"],
                  color=group_vals["color"],
                  alpha=group_vals["alpha"],
                  lw=group_vals["lw"],
                  ls=group_vals["ls"])


class GeomAxVLines(Geom):
    aesthetics = frozenset({
        "xintercept",
        "bottom_limit",
        "top_limit",
        "color",
        "alpha",
        "lw",
        "ls"
    })

    grouped_aesthetics = frozenset([
        aes for aes in aesthetics
    ])

    required_aesthetics = frozenset({
        "xintercept"
    })

    legend_excluded_aesthetics = frozenset({
        "xintercept",
        "bottom_limit",
        "top_limit"
    })

    default_aesthetic_values = {
        "color": "k",
        "ls": "solid",
        "lw": 1,
        "alpha": 1,
        "bottom_limit": 0,
        "top_limit": 1}

    def render_group(
            self,
            group_vals=None,
            scales=None,
            ax=None):
        ax.axvline(
            x=group_vals["xintercept"],
            ymin=group_vals["bottom_limit"],
            ymax=group_vals["top_limit"],
            color=group_vals["color"],
            alpha=group_vals["alpha"],
            lw=group_vals["lw"],
            ls=group_vals["ls"])


class GeomExponential(Geom):

    legend_excluded_aesthetics = frozenset({
        "rate",
        "n_points",
        "base"
    })

    default_aesthetic_values = {
        "color": "k",
        "marker": None,
        "lw": 1,
        "alpha": 1,
        "n_points": 100,
        "base": np.exp(1)
    }

    def render_group(
            self,
            group_vals=None,
            scales=None,
            ax=None,
            time_axis=None):
        if time_axis == "x":
            value_axis = "y"
        elif time_axis == "y":
            value_axis = "x"
        else:
            raise ValueError(
                "Unknown time_axis {}."
                "Must specify time_axis='x'"
                "or time_axis='y'".format(
                    time_axis))

        times = np.linspace(
            group_vals[time_axis + "min"],
            group_vals[time_axis + "max"],
            group_vals["n_points"])
        log_intercept = np.log(
            group_vals[value_axis + "intercept"])
        values = np.exp(
            log_intercept +
            np.log(group_vals["base"]) *
            group_vals["rate"] * times).flatten()
        if time_axis == "x":
            xs, ys = times, values
        elif time_axis == "y":
            ys, xs = times, values
        else:
            raise ValueError(
                "Unknown time_axis {}."
                "Must specify time_axis='x'"
                "or time_axis='y'".format(
                    time_axis))
        ax.plot(
            xs,
            ys,
            marker=group_vals["marker"],
            color=group_vals["color"],
            alpha=group_vals["alpha"],
            lw=group_vals["lw"])


class GeomExponentialX(GeomExponential):
    aesthetics = frozenset({
        "rate",
        "yintercept",
        "xmin",
        "xmax",
        "n_points",
        "base",
        "color",
        "marker",
        "alpha",
        "lw"
    })

    required_aesthetics = frozenset({
        "rate",
        "yintercept",
        "xmin",
        "xmax",
        "n_points",
        "base"
    })

    grouped_aesthetics = frozenset([
        aes for aes in aesthetics
    ])

    def render_group(
            self,
            group_vals=None,
            scales=None,
            ax=None):
        super().render_group(
            group_vals=group_vals,
            scales=scales,
            ax=ax,
            time_axis="x")


class GeomExponentialY(GeomExponential):
    aesthetics = frozenset({
        "rate",
        "xintercept",
        "ymin",
        "ymax",
        "n_points",
        "base",
        "color",
        "marker",
        "alpha",
        "lw"})

    required_aesthetics = frozenset({
        "rate",
        "xintercept",
        "ymin",
        "ymax",
        "n_points",
        "base"
    })

    grouped_aesthetics = frozenset([
        aes for aes in aesthetics
    ])

    def render_group(
            self,
            group_vals=None,
            scales=None,
            ax=None):
        super().render_group(
            group_vals=group_vals,
            scales=scales,
            ax=ax,
            time_axis="y")


class GeomPointInterval(Geom):
    aesthetics = frozenset({
        "x",
        "y",
        "color",
        "marker",
        "alpha",
        "lw",
        "markersize",
        "markeredgecolor",
        "markeredgewidth",
        "markerfacecolor"})

    grouped_aesthetics = frozenset([
        aes for aes in aesthetics
        if aes not in ["x", "y"]])

    required_aesthetics = frozenset({
        "x",
        "y"})
    
    default_aesthetic_values = {
        "color": "k",
        "marker": "o",
        "lw": 1,
        "alpha": 1,
        "markersize": 1,
        "markeredgecolor": "k",
        "markeredgewidth": 0.5,
        "markerfacecolor": None
    }

    def __init__(self,
                 stat=None,
                 **kwargs):
        if stat is None:
            stat = stats.StatPointInterval()
        super().__init__(stat=stat,
                         **kwargs)

    def render_group(
            self,
            group_vals=None,
            scales=None,
            ax=None):

        ax.errorbar(group_vals["x"],
                    group_vals["y"],
                    xerr=group_vals["xerr"],
                    yerr=group_vals["yerr"],
                    marker=group_vals["marker"],
                    color=group_vals["color"],
                    alpha=group_vals["alpha"],
                    lw=group_vals["lw"],
                    markersize=group_vals["markersize"],
                    markeredgecolor=group_vals["markeredgecolor"],
                    markeredgewidth=group_vals["markeredgewidth"],
                    markerfacecolor=group_vals["markerfacecolor"])


class GeomPointIntervalX(GeomPointInterval):
    grouped_aesthetics = frozenset([
        aes for aes in GeomPointInterval.aesthetics
        if aes not in ["x"]])


class GeomPointIntervalY(GeomPointInterval):
    grouped_aesthetics = frozenset([
        aes for aes in GeomPointInterval.aesthetics
        if aes not in ["y"]])


class GeomDensity(Geom):
    aesthetics = frozenset({
        "fillcolor",
        "linecolor",
        "marker",
        "linealpha",
        "fillalpha",
        "ls",
        "lw",
        "support",
        "density"})

    grouped_aesthetics = frozenset([
        aes for aes in aesthetics
        if aes not in ["support", "density"]])

    required_aesthetics = frozenset()

    default_aesthetic_values = {
        "color": "k",
        "marker": None,
        "lw": 1,
        "ls": "solid",
        "linealpha": 1}

    def __init__(
            self,
            stat=None,
            support_axis="x",
            **kwargs):
        if stat is None:
            stat = stats.StatDensity(
                support_axis=support_axis,
                **kwargs)
        if support_axis in ["x", "y"]:
            self.support_axis = support_axis
        else:
            raise ValueError(
                "Unknown support axis "
                "{}".format(support_axis))
        self.aesthetics = frozenset(
            list(self.aesthetics) + [self.support_axis])
        self.required_aesthetics = frozenset(
            list(self.required_aesthetics) +
            [support_axis])
        super().__init__(stat=stat,
                         **kwargs)

    def render_group(
            self,
            group_vals=None,
            scales=None,
            ax=None):

        if self.support_axis == "x":
            xs = group_vals["support"]
            ys = group_vals["density"]
            ax.set_ylabel("density")
            fill_func = ax.fill_between
        elif self.support_axis == "y":
            ys = group_vals["support"]
            xs = group_vals["density"]
            fill_func = ax.fill_betweenx
            ax.set_xlabel("density")
        else:
            raise ValueError(
                "Unknown support "
                "axis {}".format(self.support_axis))

        ax.plot(
            xs,
            ys,
            marker=group_vals["marker"],
            color=group_vals["linecolor"],
            alpha=group_vals["linealpha"],
            lw=group_vals["lw"],
            ls=group_vals["ls"])
        fill_func(
            group_vals["support"],
            group_vals["density"],
            color=group_vals["fillcolor"],
            alpha=group_vals["fillalpha"])


class GeomViolin(Geom):
    aesthetics = frozenset({
        "fillcolor",
        "linecolor",
        "marker",
        "linealpha",
        "fillalpha",
        "ls",
        "lw",
        "support",
        "density",
        "violinwidth",
        "norm",
        "trimtails"})

    grouped_aesthetics = frozenset([
        aes for aes in aesthetics
        if aes not in ["support", "density"]])

    required_aesthetics = frozenset()

    default_aesthetic_values = {
        "linecolor": "none",
        "fillcolor": "white",
        "marker": None,
        "lw": 1,
        "ls": "solid",
        "linealpha": 1,
        "fillalpha": 1,
        "norm": "area",
        "violinwidth": 1,
        "trimtails": 0}

    def __init__(
            self,
            stat=None,
            support_axis="y",
            **kwargs):
        if stat is None:
            stat = stats.StatDensity(
                support_axis=support_axis,
                **kwargs)
        if support_axis in ["x", "y"]:
            self.support_axis = support_axis
            if support_axis == "x":
                self.position_axis = "y"
            else:
                self.position_axis = "x"
        else:
            raise ValueError("Unknown support axis "
                             "{}".format(support_axis))
        axes = [self.support_axis, self.position_axis]
        self.aesthetics = frozenset(
            list(self.aesthetics) + axes)
        self.required_aesthetics = frozenset(
            list(self.required_aesthetics) +
            axes)
        self.grouped_aesthetics = frozenset(
            list(self.grouped_aesthetics) +
            [self.position_axis])
        super().__init__(stat=stat,
                         **kwargs)

    def transform_density(self,
                          density,
                          transformed_support,
                          norm,
                          violinwidth):
        if norm == "area":
            return self.area_transform(density,
                                       transformed_support,
                                       violinwidth)
        elif norm == "max":
            return self.max_transform(density,
                                      violinwidth)
        else:
            raise ValueError(
                "Unknown violin plot norm {}".format(norm))

    def area_transform(self,
                       density,
                       transformed_support,
                       violinwidth):
        return (0.5 * violinwidth * density /
                simpson(density, transformed_support))

    def max_transform(self, density, violinwidth):
        return 0.5 * violinwidth * density / np.max(density)

    def render_group(
            self,
            group_vals=None,
            scales=None,
            ax=None):
        ax_scale = scales[self.support_axis]
        trans_support = ax_scale.transform(
            group_vals["support"])

        dens_delta = self.transform_density(
            group_vals["density"],
            trans_support,
            group_vals["norm"],
            group_vals["violinwidth"]
        )

        trim_mask = dens_delta > (
            group_vals["trimtails"] *
            np.max(dens_delta))

        dens_delta = dens_delta[trim_mask]
        trimmed_support = group_vals["support"][trim_mask]

        dens_plus = (
            group_vals[self.position_axis] +
            dens_delta)
        dens_minus = (
            group_vals[self.position_axis] -
            dens_delta)

        if self.support_axis == "x":
            xs_plus, xs_minus, ys_plus, ys_minus = (
                trimmed_support,
                trimmed_support,
                dens_plus,
                dens_minus)
            fill_func = ax.fill_between
        elif self.support_axis == "y":
            ys_plus, ys_minus, xs_plus, xs_minus = (
                trimmed_support,
                trimmed_support,
                dens_plus,
                dens_minus)
            fill_func = ax.fill_betweenx
        else:
            raise ValueError(
                "Unknown support "
                "axis {}".format(self.support_axis))

        ax.plot(
            xs_plus, ys_plus,
            marker=group_vals["marker"],
            color=group_vals["linecolor"],
            alpha=group_vals["linealpha"],
            lw=group_vals["lw"],
            ls=group_vals["ls"])
        ax.plot(
            xs_minus, ys_minus,
            marker=group_vals["marker"],
            color=group_vals["linecolor"],
            alpha=group_vals["linealpha"],
            lw=group_vals["lw"],
            ls=group_vals["ls"])
        fill_func(
            trimmed_support,
            dens_plus,
            dens_minus,
            color=group_vals["fillcolor"],
            alpha=group_vals["fillalpha"])
