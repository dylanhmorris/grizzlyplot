#!/usr/bin/env python3

from grizzlyplot import GrizzlyPlot
import grizzlyplot.geoms as geoms
import pytest


def test_can_render():
    plot = GrizzlyPlot(
        geoms=[
            geoms.GeomHLines(
                yintercept=23,
                xmin=1,
                xmax=5,
                lw=3,
                color="blue"),
            geoms.GeomAxHLines(
                yintercept=-3,
                left_limit=0.25,
                right_limit=0.75,
                lw=1.5,
                color="darkred"),
            geoms.GeomAxVLines(
                xintercept=6,
                bottom_limit=0.25,
                top_limit=0.75,
                lw=3,
                color="blue"),
            geoms.GeomVLines(
                xintercept=-3,
                ymin=-1,
                ymax=10,
                lw=3,
                color="darkgreen")
        ]
    )

    plot.render()
