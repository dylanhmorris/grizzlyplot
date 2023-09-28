from grizzlyplot import GrizzlyPlot
import grizzlyplot.faceter as faceter
import polars as pl
import numpy as np
import pytest


def test_facet_definition_in_grizzlyplot():
    some_numbers = [1, 2, 3, 4]
    n_unique_numbers = np.unique(some_numbers).size
    some_letters = ["a", "b", "c", "c"]
    n_unique_letters = np.unique(some_letters).size

    test_plot = GrizzlyPlot(
        data=pl.DataFrame({
            "number_data": some_numbers,
            "letter_data": some_letters}),
        facet=dict(
            row="letter_data",
            col="number_data")
    )

    row_col_faceter = test_plot.get_faceter()

    assert isinstance(row_col_faceter,
                      faceter.GridFaceter)
    assert isinstance(row_col_faceter,
                      faceter.AbstractFaceter)

    assert row_col_faceter.n_cols() == n_unique_numbers
    assert row_col_faceter.n_rows() == n_unique_letters
    expected_n_facets = n_unique_numbers * n_unique_letters
    assert row_col_faceter.n_facets() == expected_n_facets

    fig, ax = row_col_faceter.get_axes()

    assert all([fig == axis.get_figure()
                for axis in ax])
    coerced = row_col_faceter.coerce_axis_geometry(
        ax)
    assert coerced.shape == (expected_n_facets,)

    test_plot_no_col = GrizzlyPlot(
        data=pl.DataFrame({
            "number_data": some_numbers,
            "letter_data": some_letters}),
        facet=dict(
            row="letter_data")
    )

    row_col_faceter_no_col = test_plot_no_col.get_faceter()

    assert isinstance(row_col_faceter_no_col,
                      faceter.GridFaceter)
    assert isinstance(row_col_faceter_no_col,
                      faceter.AbstractFaceter)

    assert row_col_faceter_no_col.n_cols() == 1
    assert row_col_faceter_no_col.n_rows() == n_unique_letters
    expected_n_facets_no_col = 1 * n_unique_letters
    assert row_col_faceter_no_col.n_facets() == expected_n_facets_no_col

    fig_no_col, ax_no_col = row_col_faceter_no_col.get_axes()

    assert all([fig_no_col == axis.get_figure()
                for axis in ax_no_col])
    coerced_no_col = row_col_faceter_no_col.coerce_axis_geometry(
        ax_no_col)
    assert coerced_no_col.shape == (expected_n_facets_no_col,)

    test_plot_no_row = GrizzlyPlot(
        data=pl.DataFrame({
            "number_data": some_numbers,
            "letter_data": some_letters}),
        facet=dict(
            col="letter_data")
    )
    row_col_faceter_no_row = test_plot_no_row.get_faceter()

    assert isinstance(row_col_faceter_no_row,
                      faceter.GridFaceter)
    assert isinstance(row_col_faceter_no_row,
                      faceter.AbstractFaceter)

    assert row_col_faceter_no_row.n_cols() == n_unique_letters
    assert row_col_faceter_no_row.n_rows() == 1
    expected_n_facets_no_row = n_unique_letters * 1
    assert row_col_faceter_no_row.n_facets() == expected_n_facets_no_row

    fig_no_row, ax_no_row = row_col_faceter_no_row.get_axes()

    assert all([fig_no_row == axis.get_figure()
                for axis in ax_no_row])
    coerced_no_row = row_col_faceter_no_row.coerce_axis_geometry(
        ax_no_row)
    assert coerced_no_row.shape == (expected_n_facets_no_row,)


def test_facet_definition_with_explicit_argument():
    some_numbers = [8, 23, 6, 16, 8, 2, 2, 5]
    n_unique_numbers = np.unique(some_numbers).size
    some_letters = ["a", "b", "c", "c", "z", "z", "c", "q"]
    n_unique_letters = np.unique(some_letters).size

    test_plot_explicit_constructor = GrizzlyPlot(
        data=pl.DataFrame({
            "number_data": some_numbers,
            "letter_data": some_letters}),
        facet=dict(
            facet_mapping=dict(
                row="letter_data",
                col="number_data")),
        faceter=faceter.GridFaceter,
        impute_faceting=False
    )
    test_plot_explicit_string = GrizzlyPlot(
        data=pl.DataFrame({
            "number_data": some_numbers,
            "letter_data": some_letters}),
        facet=dict(
            facet_mapping=dict(
                row="letter_data",
                col="number_data")),
        faceter="grid",
        impute_faceting=False
    )

    for plot in [test_plot_explicit_constructor,
                 test_plot_explicit_string]:
        test_faceter = plot.get_faceter()

        assert isinstance(test_faceter,
                          faceter.GridFaceter)
        assert isinstance(test_faceter,
                          faceter.AbstractFaceter)

        assert test_faceter.n_cols() == n_unique_numbers
        assert test_faceter.n_rows() == n_unique_letters
        expected_n_facets = n_unique_numbers * n_unique_letters
        assert test_faceter.n_facets() == expected_n_facets

        fig, ax = test_faceter.get_axes()

        assert all([fig == axis.get_figure()
                    for axis in ax])
        coerced = test_faceter.coerce_axis_geometry(
            ax)
        assert coerced.shape == (expected_n_facets,)


def test_faceter_validation():
    some_numbers = [8, 23, 6, 16, 8, 2, 2, 5]
    some_letters = ["a", "b", "c", "c", "z", "z", "c", "q"]

    test_plot_unknown_string = GrizzlyPlot(
        data=pl.DataFrame({
            "number_data": some_numbers,
            "letter_data": some_letters}),
        facet=dict(
            facet_mapping=dict(
                row="letter_data",
                col="number_data")),
        faceter="gridx",
        impute_faceting=False
    )
    with pytest.raises(ValueError):
        test_plot_unknown_string.get_faceter()

    test_plot_neither_string_nor_callable = GrizzlyPlot(
        data=pl.DataFrame({
            "number_data": some_numbers,
            "letter_data": some_letters}),
        facet=dict(
            facet_mapping=dict(
                row="letter_data",
                col="number_data")),
        faceter=5232,
        impute_faceting=False
    )
    with pytest.raises(ValueError):
        test_plot_neither_string_nor_callable.get_faceter()


def test_wrap_faceter_by_col():
    pass
