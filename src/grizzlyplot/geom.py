#!/usr/bin/env python3

# filename: geom.py
# description: base Geom class

from grizzlyplot.scales import ScaleIdentity
from grizzlyplot.stats import Stat, StatIdentity
from grizzlyplot.position import Position, PositionIdentity
import polars as pl
import numpy as np
from collections import namedtuple


class Geom:
    """
    Geometric object base class

    This class is used to define
    geometric objects ("Geoms") which
    express data attributes as visual
    featuers (e.g. an x/y scatter point
    point expresses one data feature
    as the left-right (x) position
    of the point and another as the
    up-down (y) position.

    Parameters
    ----------
    data : :class:`polars.DataFrame`
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
    inherit_data : :py:class:`bool`, default :py:data:`True`
        If a mapped data column is missing
        from the provided Geom-level `data`,
        look for it in plot-level `data`?
    inherit_mapping : :py:class:`bool`, default :py:data:`True`
        If an implemented aesthetic mapping is missing
        from the provided Geom-level `mapping`,
        look for it in plot-level `mapping`?
    inherit_params : :py:class:`bool`, default :py:data:`True`
        If a potentially used parameter is missing
        from the provided Geom-level `params`,
        look for it in plot-level `params`?
    """
    aesthetics = frozenset()
    grouped_aesthetics = frozenset()
    legend_excluded_aesthetics = frozenset()
    required_aesthetics = frozenset()

    def __init__(
            self,
            data: pl.DataFrame = None,
            mapping: dict = None,
            inherit_data: bool = True,
            inherit_mapping: bool = True,
            inherit_params: bool = True,
            stat: Stat = None,
            position: Position = None,
            name: str = "",
            **kwargs):

        if stat is None:
            stat = StatIdentity()
        if position is None:
            position = PositionIdentity()

        self.data = data
        self.mapping = mapping
        self.inherit_data = inherit_data
        self.inherit_mapping = inherit_mapping
        self.inherit_params = inherit_params
        self.stat = stat
        self.position = position
        self.name = name
        self.params = kwargs

        if not hasattr(self, "default_aesthetic_values"):
            self.default_aesthetic_values = {}
        if not hasattr(self, "aesthetic_aliases"):
            self.aesthetic_aliases = {}

        if not hasattr(self, "default_scales"):
            self.default_scales = {aes: ScaleIdentity() for
                                   aes in self.aesthetics}

        if not set(self.grouped_aesthetics).issubset(
                set(self.aesthetics)):
            raise ValueError(
                "Attempt to specify grouped_aesthetics "
                "that are not among the Geom's specified "
                "aesthetics. Got:\n"
                "aesthetics: {}\n"
                "grouped_aesthetics: {}\n\n"
                "".format(
                    self.aesthetics,
                    self.grouped_aesthetics))
        if not set(self.required_aesthetics).issubset(
                set(self.aesthetics)):
            raise ValueError(
                "Attempt to specify required_aesthetics "
                "that are not among the Geom's specified "
                "aesthetics. Got:\n"
                "aesthetics: {}\n"
                "required_aesthetics: {}\n\n"
                "".format(
                    self.aesthetics,
                    self.required_aesthetics))

    def choose_data(
            self,
            data=None,
            inherited_data=None):
        if (
                data is None and
                self.inherit_data
        ):
            dat = inherited_data
        else:
            dat = data
        return dat

    def get_combined_mapping(
            self,
            inherited_mapping=None):
        if (
                self.inherit_mapping and
                inherited_mapping is not None
        ):
            if self.params is not None:
                # this avoids an error
                # if the global mapping
                # has a column not in the
                # geom data that the geom
                # requires, but the geom
                # specifies it as a parameter
                inherited_mapping = {
                    key: val for key, val in
                    inherited_mapping.items() if
                    key not in self.params.keys()}
            if self.mapping is not None:
                mapping = dict(inherited_mapping,
                               **self.mapping)
            else:
                mapping = inherited_mapping
        else:
            mapping = self.mapping

        return mapping

    def get_groups(
            self,
            data=None,
            mapping=None):

        mapped_exprs = [
            mapping[aes] for aes in self.grouped_aesthetics
            if aes in mapping.keys()
        ]
        additional_exprs = mapping.get("group", [])

        if type(additional_exprs) in [str, pl.Expr]:
            additional_exprs = [additional_exprs]

        group_exprs = list(set(additional_exprs + mapped_exprs))

        if len(group_exprs) > 0:
            result = data.sort(
                group_exprs
            ).partition_by(
                group_exprs,
                maintain_order=True
            )

        else:
            result = [data]
        return result

    def render(
            self,
            ax=None,
            data=None,
            inherited_data=None,
            inherited_mapping=None,
            inherited_params=None,
            scales=None):

        data = self.choose_data(
            data=data,
            inherited_data=inherited_data)
        comb_mapping = self.get_combined_mapping(
            inherited_mapping=inherited_mapping)

        groups = self.get_groups(
            data=data,
            mapping=comb_mapping)

        group_scaled_values = [
            self.get_scaled_values(
                group_data,
                scales=scales,
                inherited_mapping=inherited_mapping,
                inherited_params=inherited_params)
            for group_data in groups
        ]

        group_render_values = self.position(
            group_scaled_values,
            scales)

        for values in group_render_values:
            self.validate_render_values(values)
            self.render_group(
                group_vals=values,
                scales=scales,
                ax=ax)

    def render_group(
            group_vals=None,
            scales=None,
            ax=None):
        raise NotImplementedError()

    def get_aesthetic_values(
            self,
            aesthetic,
            data,
            inherited_mapping,
            inherited_params):

        result = None

        if (
                self.mapping is not None and
                aesthetic in self.mapping.keys()
        ):
            mapped_expr = self.mapping[aesthetic]
            selection = data.select(mapped_expr)
            result = selection.to_series().to_numpy()
        elif (self.params is not None and
              aesthetic in self.params.keys()):
            result = self.params[aesthetic]
        elif (inherited_mapping is not None and
              aesthetic in inherited_mapping.keys() and
              self.inherit_mapping):
            mapped_expr = inherited_mapping[aesthetic]
            selection = data.select(mapped_expr)
            result = selection.to_series().to_numpy()
        elif (inherited_params is not None and
              aesthetic in inherited_params.keys()
              and self.inherit_params):
            result = inherited_params[aesthetic]
        else:
            result = self.default_aesthetic_values.get(
                aesthetic, None)
        return result

    def get_scaled_value(
            self,
            aesthetic,
            data,
            inherited_mapping,
            inherited_params,
            scales):
        if scales is None:
            raise ValueError("No scales provided")
        scale = scales[aesthetic]
        unscaled = self.get_aesthetic_values(
            aesthetic,
            data,
            inherited_mapping,
            inherited_params)
        if scale is None:
            raise ValueError("No scale given for "
                             "aesthetic {}".format(aesthetic))
        scaled = scale(unscaled)
        if (
                scaled is not None and
                aesthetic in self.grouped_aesthetics and
                not isinstance(scaled, (str, float, int))
        ):
            if isinstance(scaled, list):
                scaled = np.array(scaled)
            if not np.all(scaled == scaled[0]) == 1:
                print(scale)
                print(scaled)
                raise ValueError("For aesthetic {}, "
                                 "geom {} received multiple scaled "
                                 "values for a grouped aesthetic "
                                 "within a single group; need to "
                                 "have exactly one value per group "
                                 "to render. Check groupings and "
                                 "aesthetic scales"
                                 "".format(
                                     aesthetic,
                                     self.__repr__()))
            scaled = scaled[0]
        return scaled

    def get_scaled_values(
            self,
            data,
            scales=None,
            inherited_mapping=None,
            inherited_params=None):

        scaled_values = {
            aes: self.get_scaled_value(
                aes,
                data,
                inherited_mapping,
                inherited_params,
                scales)
            for aes in self.aesthetics}

        scaled_vals = self.stat(scaled_values, scales)

        return scaled_vals

    def validate_render_values(self, render_vals):
        for aes in self.required_aesthetics:
            if render_vals.get(aes, None) is None:
                raise ValueError(
                    "{} missing a mapping or parameter "
                    "for required aesthetic {}"
                    "".format(
                        self.__repr__(),
                        aes))
        self._render_value_validation_logic(render_vals)
        return True

    def _render_value_validation_logic(self, render_vals):
        pass

    def check_facetable(self,
                        facet_vars):
        if self.data is None:
            pass
        else:
            for var in facet_vars:
                if var not in self.data.columns:
                    raise ValueError(
                        "{} missing required faceting variable "
                        "{}".format(self.__repr__(),
                                    var))
                pass
            pass
        return True

    def __repr__(self):
        return "{} '{}'".format(
            self.__class__.__name__,
            self.name)
