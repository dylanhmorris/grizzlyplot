#!/usr/bin/env python3

import grizzlyplot as gp
import grizzlyplot.geoms as geoms
import polars as pl
import numpy as np
import pytest

df_test = pl.DataFrame(
    {
        "a": [1, 2, 3],
        "b": ["x", "y", "z"],
        "c": [2.5, 3.6, 4.7]
    }
)


def test_string_geom_level_mapping():
    """
    Test that string based
    mappings correctly
    map dataframe columns
    to aesthetics at the
    geom level
    """
    geom = geoms.GeomXY(
        mapping=dict(
            x="a",
            y="b",
            color="c")
    )
    aes_vals = {aes:
                geom.get_aesthetic_values(
                    aesthetic=aes,
                    data=df_test,
                    inherited_mapping=None,
                    inherited_params=None)
                for aes in ["x", "y", "color"]}
    expected = {
        "x": df_test["a"].to_numpy(),
        "y": df_test["b"].to_numpy(),
        "color": df_test["c"].to_numpy()
    }

    for aes in expected.keys():
        assert np.all(expected[aes] == aes_vals[aes])


def test_string_plot_level_mapping():
    """
    Test that string based
    mappings correctly
    map dataframe columns
    to aesthetics at the
    plot level
    """
    plot = gp.GrizzlyPlot(
        mapping=dict(
            x="a",
            y="b",
            color="c"),
        geoms=[
            geoms.GeomXY(
                inherit_mapping=True)
        ],
        x=5,
        y=4,
        color="blue")

    geom = plot.geoms[0]

    aes_vals = {aes:
                geom.get_aesthetic_values(
                    aesthetic=aes,
                    data=df_test,
                    inherited_mapping=plot.mapping,
                    inherited_params=plot.params)
                for aes in ["x", "y", "color"]}
    expected = {
        "x": df_test["a"].to_numpy(),
        "y": df_test["b"].to_numpy(),
        "color": df_test["c"].to_numpy()
    }

    for aes in expected.keys():
        assert np.all(expected[aes] == aes_vals[aes])


def test_expression_geom_level_mapping():
    """
    Test that expression-based
    mappings correctly
    map dataframe columns
    to aesthetics at the
    geom level
    """
    geom = geoms.GeomXY(
        mapping=dict(
            x=pl.col("a") + pl.col("c"),
            y=pl.col("b") + pl.col("b"),
            color=pl.col("b") + pl.col("a"))
    )

    assert np.all(
        geom.get_aesthetic_values(
            aesthetic="x",
            data=df_test,
            inherited_mapping=None,
            inherited_params=None) ==
        df_test.select(
            pl.col("a") + pl.col("c")
        ).to_series().to_numpy()
    )

    assert np.all(
        geom.get_aesthetic_values(
            aesthetic="y",
            data=df_test,
            inherited_mapping=None,
            inherited_params=None) ==
        df_test.select(
            pl.col("b") + pl.col("b")
        ).to_series().to_numpy()
    )

    # attempt to do invalid expression computation
    # raises Error
    with pytest.raises(pl.exceptions.ComputeError):
        geom.get_aesthetic_values(
            aesthetic="color",
            data=df_test,
            inherited_mapping=None,
            inherited_params=None)

    # fixing invalid computation
    # succeeds as expected
    geom.mapping["color"] = (
        pl.col("b").cast(pl.Utf8) +
        pl.col("a").cast(pl.Utf8))

    assert np.all(
        geom.get_aesthetic_values(
            aesthetic="color",
            data=df_test,
            inherited_mapping=None,
            inherited_params=None) ==
        df_test.select(
            pl.col("b") + pl.col("a").cast(pl.Utf8)
        ).to_series().to_numpy()
    )


def test_expression_plot_level_mapping():
    """
    Test that expression-based
    mappings correctly
    map dataframe columns
    to aesthetics at the
    plot level
    """
    plot = gp.GrizzlyPlot(
        mapping=dict(
            x=pl.col("a") + pl.col("c"),
            y=pl.col("b") + pl.col("b"),
            color=pl.col("b") + pl.col("a")),
        geoms=[
            geoms.GeomXY(
                inherit_mapping=True)
        ],
        x=5,
        y=4,
        color="blue")

    geom = plot.geoms[0]
    
    assert np.all(
        geom.get_aesthetic_values(
            aesthetic="x",
            data=df_test,
            inherited_mapping=plot.mapping,
            inherited_params=plot.params) ==
        df_test.select(
            pl.col("a") + pl.col("c")
        ).to_series().to_numpy()
    )

    assert np.all(
        geom.get_aesthetic_values(
            aesthetic="y",
            data=df_test,
            inherited_mapping=plot.mapping,
            inherited_params=plot.params) ==
        df_test.select(
            pl.col("b") + pl.col("b")
        ).to_series().to_numpy()
    )

    # attempt to do invalid expression computation
    # raises Error
    with pytest.raises(pl.exceptions.ComputeError):
        geom.get_aesthetic_values(
            aesthetic="color",
            data=df_test,
            inherited_mapping=plot.mapping,
            inherited_params=plot.params)

    # fixing invalid computation
    # succeeds as expected
    plot.mapping["color"] = (
        pl.col("b").cast(pl.Utf8) +
        pl.col("a").cast(pl.Utf8))

    assert np.all(
        geom.get_aesthetic_values(
            aesthetic="color",
            data=df_test,
            inherited_mapping=plot.mapping,
            inherited_params=plot.params) ==
        df_test.select(
            pl.col("b") + pl.col("a").cast(pl.Utf8)
        ).to_series().to_numpy()
    )
