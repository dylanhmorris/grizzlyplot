#!/usr/bin/env python3
# *_* coding: utf-8 *_*

"""
Base :class:`GrizzlyPlot` class, which
is used to specify plots for rendering
"""

import numpy as np
import polars as pl

from grizzlyplot.faceter import (
    AbstractFaceter, GridFaceter, WrapFaceter, NullFaceter)
from grizzlyplot.defaults import plot_defaults
from grizzlyplot.transforms import (
    dynamic_xspan_transform,
    dynamic_yspan_transform
)


class GrizzlyPlot:
    """
    GrizzlyPlot class

    This class is used to declaratively
    define a plot, which can then be
    rendered as a :class:`matplotlib.figure.Figure`
    using the :meth:`~grizzlyplot.GrizzlyPlot.render`
    method.

    Parameters
    ----------
    data : :py:class:`polars.DataFrame`
        Default DataFrame to query for data
        mapped to aesthetics, if no other one
        is provided. Default None
    mapping : :py:class:`dict`
        Aesthetic mapping associating aesthetic
        attributes that may be used by a geom,
        such as x coordinate, y coordinate,
        shape, or color, to data feature
        (typically column names
        in a tidy data table). Default `{}`.
    geoms : :py:class:`list`
        List of geometric objects ("geoms")
        of class :class:`~grizzlyplot.geom.Geom`
        to place on the plot. A geom has a set
        of associated aesthetic attributes that
        it accepts, either from the data as mapped
        by an aesthetic mapping or as fixed parameter
        values. For example,
        :class:`~grizzlyplot.geoms.GeomPoint` accepts
        lists of x and y coordinate values, each pair
        of which becomes the location of a plotted
        marker. See the :class:`~grizzlyplot.geoms.Geom`
        documentation for more.
    scales : :py:class:`dict`
        Dictionary associating aesthetic attributes
        such as the x-coordinate or y-coordinate
        to aesthetic scales of class
        :class:`~grizzlyplot.scales.Scale`.
        An aesthetic scale is a function that maps
        potential data or parameter values to
        the natural range of the aesthetic itself.
        For example, to plot categorical data such
        as car manufacturer names, e.g.
        ["Ford", "Toyota", "Volvo"]
        on the x-axis, we need to associate each
        manufacturer name with a numeric x-coordinate.
        See the :class:`~grizzlyplot.scales.Scale`
        documentation for more.
    facet : :py:class:`dict`
        Dictionary defining the faceting scheme,
        of if an explicit faceter class is to be
        provided, a dictionary of instantiation
        keyword arguments that will be unpacked
        and passed to the constructor or other
        callable specified in the faceter argument.
    faceter : :py:class:`str` | callable
        Which faceter to instantiate and thus which
        faceting scheme to implement. If faceter is `None` and
        set and `impute_faceting` is `True`, GrizzlyPlot will
        attempt to infer the desired faceter from the arguments
        of facet. Must provide the name of a built-in
        faceter as a string or a callable (such as a
        faceter class constructor) that will return
        a faceter object when passed the facet dict
        as a set of keyword arguments.
    impute_faceting : :py:
        Whether to attempt to impute the desired faceting
        scheme from the `facet` argument if `faceter` is
        not specified. Default `True`. If false and `faceter`
        is not specified, a ValueError will be raised when
        the user attempts to render the plot.

    """
    built_in_faceters = {
        "wrap": WrapFaceter,
        "grid": GridFaceter,
        "no": NullFaceter,
        "null": NullFaceter
    }

    def __init__(self,
                 data: pl.DataFrame = None,
                 mapping: dict = None,
                 geoms: list = None,
                 scales: dict = None,
                 facet: dict = None,
                 faceter: AbstractFaceter = None,
                 impute_faceting: bool = True,
                 **kwargs):

        if mapping is None:
            mapping = dict()
        if geoms is None:
            geoms = list()
        if scales is None:
            scales = dict()
        if facet is None:
            facet = dict()

        self.data = data
        self.mapping = mapping
        self.geoms = geoms
        self.scales = scales
        self.facet = facet
        self.faceter = faceter
        self.impute_faceting = impute_faceting
        self.params = kwargs

    def get_param(self, param, default=None):
        if default is None:
            default = plot_defaults.get(
                param, None)
        return self.params.get(
            param, default)

    def get_rendered_aesthetics(self):
        aes = []
        for geom in self.geoms:
            aes += geom.aesthetics
        result = list(set(aes))
        return result

    def get_aesthetic_scale(self, aesthetic):
        result = None
        if (
                self.scales is not None and
                aesthetic in self.scales.keys()
        ):
            result = self.scales[aesthetic]
        else:
            candidates = []
            for geom in self.geoms:
                g_default = geom.default_scales.get(
                    aesthetic,
                    None)
                if g_default is not None:
                    candidates.append(g_default)
            if len(candidates) < 1:
                raise ValueError("No scale specified "
                                 "for mapped aesthetic "
                                 "{} and no default found "
                                 "among given geoms"
                                 "".format(aesthetic))
            else:
                first = candidates[0]
                if not all([cand == first for
                            cand in candidates]):
                    raise ValueError("No scale specified "
                                     "for mapped aesthetic "
                                     "{} and clashing default "
                                     "scales among specified "
                                     "geoms: {} "
                                     "".format(aesthetic,
                                               [c for c in candidates]))
                else:
                    result = first
                pass
            pass
        return result

    def get_all_aesthetic_values(self, aesthetic):
        all_vals = []
        for geom in self.geoms:
            if aesthetic in geom.aesthetics:
                dat = geom.choose_data(
                    data=geom.data,
                    inherited_data=self.data)
                vals = geom.get_aesthetic_values(
                    aesthetic,
                    dat,
                    inherited_mapping=self.mapping,
                    inherited_params=self.params)
                if vals is not None:
                    if isinstance(vals, (str, float, int)):
                        vals = [vals]
                    else:
                        vals = list(np.unique(vals))
                    all_vals += vals
                pass
            pass

        return np.unique(all_vals)

    def initialize_scales(self, ax=None):
        rendered_aes = self.get_rendered_aesthetics()
        collated_scales = {aes: self.get_aesthetic_scale(aes)
                           for aes in rendered_aes}
        return {aes: scale.initialize(ax=ax)
                for aes, scale in collated_scales.items()}

    def render(self, ax=None, fig=None, **kwargs):
        faceter = self.get_faceter()
        n_facets = faceter.n_facets()

        fig, ax = faceter.get_axes(
            ax=ax,
            fig=fig,
            **kwargs)

        scales = self.initialize_scales(ax=ax)

        for i_facet in range(n_facets):
            self.render_facet(
                faceter,
                i_facet,
                scales=scales,
                ax=ax[i_facet])

        if (
                "xlabel" in self.params.keys() or
                self.get_param("autolabel_xaxis")
        ):
            fig.supxlabel(
                self.get_param(
                    "xlabel",
                    default=self.mapping.get("x", None)),
                x=self.get_param(
                    "xaxis_label_x"),
                y=self.get_param(
                    "xaxis_label_y"),
                transform=dynamic_xspan_transform(
                    fig, ax))
        if (
                "ylabel" in self.params.keys() or
                self.get_param("autolabel_yaxis")
        ):
            fig.supylabel(
                self.get_param(
                    "ylabel",
                    default=self.mapping.get("y", None)),
                x=self.get_param(
                    "yaxis_label_x"),
                y=self.get_param(
                    "yxaxis_label_y"),
                transform=dynamic_yspan_transform(
                    fig, ax))

        return (fig, ax)

    def impute_faceter(self):
        """
        Impute a faceter from the
        `facet` dict of the GrizzlPlot
        object
        """

        facet_vars = {
            x: self.facet.get(x, None)
            for x in ["row", "col", "wrap"]}

        for key, item in facet_vars.items():
            if isinstance(item, str):
                facet_vars[key] = [item]

        grid_facet = (
            facet_vars["row"] is not None or
            facet_vars["col"] is not None)
        wrap_facet = (facet_vars["wrap"] is not None)

        if grid_facet and wrap_facet:
            raise ValueError(
                "Cannot impute faceting with "
                "ambiguous faceting command. User "
                "specified both `wrap` and at "
                "least one of `row` and `col`, "
                "which leaves grid versus wrap faceting "
                "ambiguous")
        if grid_facet:
            faceter = GridFaceter(
                facet_mapping={
                    "row": facet_vars["row"],
                    "col": facet_vars["col"]
                },
                sharex=self.facet.get(
                    "sharex", True),
                sharey=self.facet.get(
                    "sharey", True),
                label=self.facet.get(
                    "label", True),
                label_rows=self.facet.get(
                    "label_rows", "right"),
                label_cols=self.facet.get(
                    "label_cols", "top"),
                col_label_loc=self.facet.get(
                    "col_label_loc", "top"),
                row_label_loc=self.facet.get(
                    "row_label_loc", "right")
            )

        elif wrap_facet:
            faceter = WrapFaceter(
                facet_mapping={
                    "wrap": facet_vars["wrap"]
                },
                sharex=self.facet.get(
                    "sharex", True),
                sharey=self.facet.get(
                    "sharey", True),
                label=self.facet.get(
                    "label", True),
                label_loc=self.facet.get(
                    "label_loc", "top")
            )

        else:
            faceter = NullFaceter()

        return faceter

    def get_faceter(self):

        if self.faceter is not None:
            if isinstance(self.faceter, str):
                constr = self.built_in_faceters.get(
                    self.faceter,
                    None)
                if constr is None:
                    raise ValueError(
                        "Unknown faceter name"
                        "{}. To reference a built-in "
                        "faceter, use one of the following "
                        "strings: {}. To provide your own "
                        "provide a callable that returns "
                        "a faceter object (such as a class "
                        "constructor)".format(
                            self.faceter,
                            self.built_in_faceters.keys()))
            elif callable(self.faceter):
                constr = self.faceter
            else:
                raise ValueError(
                    "faceter must either by a "
                    "string that refers to a built-in "
                    "faceter type or a callable that "
                    "returns a faceter. Got {}."
                    "".format(self.faceter))
            faceter = constr(**self.facet)

        elif self.impute_faceting:
            faceter = self.impute_faceter()

        else:
            raise ValueError(
                "No faceter explicitly specified "
                "and imputed faceting switched off")

        faceter.add_levels_from_data(
            self.data,
            error_msg_data_name=(
                "for {}"
                "".format(self.__class__.__name__)))

        for geom in self.geoms:
            faceter.add_levels_from_data(
                geom.data,
                error_msg_data_name=(
                    "for {}"
                    "".format(geom.__repr__())))

        return faceter

    def render_facet(
            self,
            faceter,
            i_facet,
            scales=None,
            ax=None):
        for geom in self.geoms:
            geom.render(
                ax=ax,
                data=faceter.subset(
                    geom.data,
                    i_facet),
                inherited_data=faceter.subset(
                    self.data,
                    i_facet),
                inherited_mapping=self.mapping,
                inherited_params=self.params,
                scales=scales)
        faceter.render_axes(
            i_facet,
            ax=ax)
        faceter.render_labels(
            i_facet,
            ax=ax,
            **self.facet.get("label_kwargs",
                             {}))
