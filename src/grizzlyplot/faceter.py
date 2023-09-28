import matplotlib.pyplot as plt
import numpy as np
from grizzlyplot.defaults import plot_defaults
import math


def label_where(loc, default=None):
    facet_label_pad_x = plot_defaults["facet_label_pad_x"]
    facet_label_pad_y = plot_defaults["facet_label_pad_y"]

    loc_dict = {
        "bottom": {
            "y": -facet_label_pad_y,
            "x": 0.5},

        "top": {
            "y": 1 + facet_label_pad_y,
            "x": 0.5},

        "left": {
            "y": 0.5,
            "x": -facet_label_pad_x,
            "rotation": 270},

        "right": {
            "y": 0.5,
            "x": 1 + facet_label_pad_x,
            "rotation": 270},
    }

    return loc_dict.get(loc, default)


class AbstractFaceter:
    facet_dimensions = set({})
    wrap_by_to_flatten_order = {
        "row": "C",
        "col": "F"
    }

    def __init__(self,
                 facet_mapping: dict = None,
                 wrap_by: str = "row",
                 sharex: bool | str = False,
                 sharey: bool | str = False,
                 label: bool | str = True):
        if facet_mapping is None:
            facet_mapping = dict()
        self.facet_mapping = facet_mapping
        self.wrap_by = wrap_by
        self.levels = dict()
        self.sharex = sharex
        self.sharey = sharey
        self.label = label
        self.validate_facet_mapping()

    def validate_facet_mapping(self):
        for dim in self.facet_mapping.keys():
            if dim not in self.facet_dimensions:
                raise ValueError("Facet mapping assigned for "
                                 "unknown facet dimension {} "
                                 "for faceter {}".format(
                                     dim,
                                     self))
            pass
        return True

    def is_dimension_mapped(self, dimension):
        return self.facet_mapping.get(
            dimension, None) is not None

    def n_facets(self):
        return np.prod(
            [self.n_levels(dim) if self.is_dimension_mapped(dim)
             else 1
             for dim in self.facet_dimensions],
            dtype=np.int_)

    def get_dimension_levels(self, dimension):
        if dimension not in self.facet_dimensions:
            raise ValueError("Faceter {} attempted to get levels "
                             "for unknown facet dimension "
                             "{}".format(self, dimension))
        return self.levels.get(dimension, None)

    def n_levels(self, dimension):
        if not self.is_dimension_mapped(dimension):
            result = 0
        else:
            dim_levels = self.get_dimension_levels(dimension)
            result = dim_levels.height
        return result

    def validate_facet_id(self, i_facet):
        if i_facet not in range(self.n_facets()):
            raise ValueError("Attempt to subset "
                             "data for a facet that "
                             "does not exist. Asked "
                             "for facet id {}; only {} "
                             "facet(s), with integer ids "
                             "0 through {}, "
                             "are defined.".format(
                                 i_facet,
                                 self.n_facets(),
                                 self.n_facets() - 1))

    def subset(self, data, i_facet):
        self.validate_facet_id(i_facet)

        if data is None:
            subset = None
        else:
            subset = data.clone()
            for dimension in self.facet_dimensions:
                if self.is_dimension_mapped(dimension):
                    dim_map = self.facet_mapping.get(
                        dimension, None)
                    dim_levels = self.get_dimension_levels(
                        dimension)
                    i_dim = self.dimension_id_from_facet_id(
                        dimension,
                        i_facet)
                    subset = subset.with_columns(
                        dim_map
                    ).join(
                        dim_levels.slice(i_dim, 1),
                        on=dim_map,
                        how="inner")
                    pass  # end if dimension mapped
                pass  # end loop over dimensions
            pass  # end else
        return subset

    def dimension_id_from_facet_id(self, dimension, i_facet):
        """
        Individual facet classes
        define functions to do this
        for each dimension
        """
        self.validate_facet_id(i_facet)
        return self.facet_id_mapper(dimension, i_facet)

    def get_axes(self,
                 ax=None,
                 fig=None,
                 **kwargs):

        if ax is not None:
            axis = self.coerce_axis_geometry(
                ax)
            if (fig is not None and not
                all([fig == ax.get_figure()
                     for ax in axis])):
                raise ValueError(
                    "Got a user-provided set of axes"
                    "and a user-provided figure, but "
                    "the axes do not all belong to the "
                    "figure")
            else:
                fig = axis[0].get_figure()
        else:
            fig, axis = self.subplots(
                fig=fig,
                **kwargs)
            axis = self.coerce_axis_geometry(
                axis)

        return fig, axis

    def render_axes(self,
                    i_facet,
                    ax=None):
        """
        Optional axis rendering logic
        that is facet id dependent
        can be implemented here
        """
        pass

    def coerce_axis_geometry(self,
                             axis):
        """
        By default, axes are row-wrapped,
        and thus flattened row-major
        (order='C').
        """
        if self.wrap_by not in self.wrap_by_to_flatten_order.keys():
            ValueError("Unknown faceter.wrap_by "
                       "value {} for faceter {}. "
                       "Expected one of the following: "
                       "{}".format(
                           self.wrap_by,
                           self,
                           self.wrap_by_to_flatten_order.keys()))

        return np.array(axis).flatten(
            order=self.wrap_by_to_flatten_order[self.wrap_by])

    def subplots(self,
                 fig=None,
                 **kwargs):
        """
        Create an appropriate set of subplots
        for plotting facets
        """
        if fig is None:
            fig = plt.figure(**kwargs)
        nrows, ncols = self.get_subplots_shape(fig=fig)
        axis = fig.subplots(
            nrows=nrows,
            ncols=ncols,
            sharex=self.sharex,
            sharey=self.sharey,
            **kwargs)
        return fig, axis

    def get_subplots_shape(self, fig=None):
        """
        This function is implemented in
        concrete Faceter subclasses
        to define grid (row, col)
        geometries for facet subplots.
        To define fancier geometries,
        override the :meth:subplots
        method.
        """
        raise NotImplementedError()

    def facet_id_mapper(
            self,
            dimension,
            i_facet):
        """
        Each non-abstract Faceter
        class must define mappings
        from facet ids {0,...n_facets - 1}
        to dimension level ranks {0, ... n_vals}
        for each dimension.
        """
        raise NotImplementedError()

    def get_facet_labels(self, i_facet, **kwargs):
        self.validate_facet_id(i_facet)
        labels = self.labeling_method(i_facet, **kwargs)
        return labels

    def labeling_method(self, i_facet, **kwargs):
        return []

    def render_labels(
            self,
            i_facet,
            ax=None,
            **kwargs):
        facet_labels = self.get_facet_labels(
            i_facet,
            **kwargs)

        for lbl in facet_labels:
            sty = lbl["style"]
            # labels are figure text
            # to avoid issues with
            # artists outside
            # axis bounds for tight/constrained
            # layout
            ax.figure.text(
                x=sty.get("x", None),
                y=sty.get("y", None),
                s=lbl["text"],
                transform=sty.get("transform",
                                  ax.transAxes),
                rotation=sty.get("rotation", 0),
                horizontalalignment=sty.get(
                    "ha", "center"),
                verticalalignment=sty.get(
                    "va", "center"),
                **kwargs)

    def add_levels_from_data(self,
                             data,
                             error_msg_data_name=""):
        for dim in self.facet_dimensions:
            if self.is_dimension_mapped(dim) and data is not None:
                mapped_expr = self.facet_mapping[dim]
                new_levels = data.select(
                    mapped_expr
                ).unique(
                ).sort(
                    mapped_expr
                )
                self.levels[dim] = self.concat_levels(
                    self.get_dimension_levels(dim),
                    new_levels)

    def concat_levels(self,
                      old_levels,
                      new_levels):
        if new_levels is None:
            levs = old_levels
        elif old_levels is None:
            levs = new_levels
        else:
            levs = old_levels.vstack(
                new_levels)
        if levs is not None:
            levs = levs.unique(
                maintain_order=True
            ).clone()
        return levs


class NullFaceter(AbstractFaceter):
    facet_dimensions = set({})

    def facet_id_mapper(self,
                        dimension,
                        i_facet):
        return 0

    def get_subplots_shape(self,
                           fig=None):
        return 1, 1


class GridFaceter(AbstractFaceter):
    facet_dimensions = set({"row", "col"})

    def __init__(self,
                 label_rows: bool | str = "right",
                 label_cols: bool | str = "top",
                 row_label_loc: bool | str = "right",
                 col_label_loc: bool | str = "top",
                 facet_mapping: dict = None,
                 **kwargs):
        if facet_mapping is None:
            facet_mapping = {
                "row": None,
                "col": None
            }
        super().__init__(facet_mapping=facet_mapping,
                         **kwargs)
        self.label_rows = label_rows
        self.label_cols = label_cols
        self.row_label_loc = row_label_loc
        self.col_label_loc = col_label_loc

    def n_rows(self):
        return max(1, self.n_levels("row"))

    def n_cols(self):
        return max(1, self.n_levels("col"))

    def rows_faceted(self):
        return self.n_levels("row") > 0

    def cols_faceted(self):
        return self.n_levels("col") > 0

    def get_subplots_shape(self,
                           fig=None):
        """
        Subclass specific row/col geometry
        function. For GridFaceter,
        it is simply defined by the
        number of row and column levels,
        respectively, if either is >= 1,
        and otherwise it is one.
        """
        return self.n_rows(), self.n_cols()

    def row_id(self, i_facet):
        return int(i_facet / self.n_cols())

    def col_id(self, i_facet):
        return int(i_facet -
                   self.n_cols() *
                   self.row_id(i_facet))

    def facet_id_mapper(
            self,
            dimension,
            i_facet):
        """
        Mapper for grid faceters.
        Facets are row-wrapped by
        default.
        """
        if dimension == "row":
            result = self.row_id(i_facet)
        elif dimension == "col":
            result = self.col_id(i_facet)
        else:
            raise ValueError("Unknown dimension {} "
                             "for faceter {}"
                             "".format(dimension,
                                       self))
        return result

    def labeling_method(self,
                        i_facet,
                        **kwargs):
        # default locs
        r_lbl = label_where("right")
        c_lbl = label_where("top")

        if isinstance(
                self.row_label_loc,
                dict):
            r_lbl.update(self.row_label_loc)
        elif isinstance(
                self.row_label_loc,
                str):
            r_lbl = label_where(
                self.row_label_loc,
                r_lbl)

        if isinstance(
                self.col_label_loc,
                dict):
            c_lbl.update(self.col_label_loc)
        elif isinstance(
                self.col_label_loc,
                str):
            c_lbl = label_where(
                self.col_label_loc,
                c_lbl)
        i_row = self.row_id(i_facet)
        i_col = self.col_id(i_facet)

        labels = []

        if (
                self.rows_faceted() and
                self.is_row_labeled(i_facet)
        ):
            label_text = "\n".join(
                [str(x) for x in
                 self.levels.get("row").slice(
                     i_row, 1).row(0)])
            labels.append(
                {"text": label_text,
                 "style": r_lbl})

        if (
                self.cols_faceted() and
                self.is_col_labeled(i_facet)
        ):
            label_text = "\n".join(
                [str(x) for x in
                 self.levels.get("col").slice(
                     i_col, 1).row(0)])
            labels.append(
                {"text": label_text,
                 "style": c_lbl})
        return labels

    def is_row_labeled(self, i_facet):
        if (
                not self.label or
                not self.label_rows or
                self.row_label_loc is None
        ):
            result = False
        elif self.label_rows == "left":
            result = self.col_id(i_facet) == 0
        elif self.label_rows == "right":
            result = self.col_id(i_facet) == self.n_cols() - 1
        elif (self.label_rows == "all"
              or self.label_rows is True):
            result = True
        else:
            result = False
        return result

    def is_col_labeled(self, i_facet):
        if not (self.label or
                not self.label_cols or
                self.col_label_loc is None):
            result = False
        elif self.label_cols == "top":
            result = self.row_id(i_facet) == 0
        elif self.label_cols == "bottom":
            result = self.row_id(i_facet) == self.n_rows() - 1
        elif (self.label_cols == "all" or
              self.label_cols is True):
            result = True
        else:
            result = False
        return result


class WrapFaceter(AbstractFaceter):
    facet_dimensions = set({"wrap"})

    def __init__(self,
                 *args,
                 facet_mapping: dict = None,
                 nrows: int = None,
                 ncols: int = None,
                 label_loc: str = None,
                 **kwargs):
        if facet_mapping is None:
            facet_mapping = {"wrap": None}
        self.nrows = nrows
        self.ncols = ncols
        self.label_loc = label_loc
        super().__init__(facet_mapping=facet_mapping,
                         **kwargs)

    def get_subplots_shape(
            self,
            fig=None):
        n_facets = self.n_facets()

        n_rows_use = self.nrows
        n_cols_use = self.ncols

        if n_rows_use is None:
            if n_cols_use is not None:
                n_rows_use = math.ceil(n_facets / n_cols_use)
            else:
                n_rows_use = math.ceil(math.sqrt(n_facets))
        if n_cols_use is None:
            n_cols_use = math.ceil(n_facets / n_rows_use)

        n_panels = n_rows_use * n_cols_use
        if not n_panels >= n_facets:
            raise ValueError(
                "Specified {} rows and {} cols, "
                "for a total of {} panels, "
                "but there are {} > {} facets to "
                "plot. To auto-set the subplot "
                "grid size, specify just one of "
                "nrows and ncols, and the other "
                "will be set automatically to "
                "accommodate the data"
                "".format(
                    n_rows_use,
                    n_cols_use,
                    n_panels,
                    n_facets,
                    n_panels))
        return n_rows_use, n_cols_use

    def facet_id_mapper(
            self,
            dimension,
            i_facet):
        """
        Mapper for wrap faceters.
        Facets are row-wrapped by
        default.
        """
        if dimension not in self.facet_dimensions:
            raise ValueError(
                "Unknown dimension {} "
                "for faceter {}"
                "".format(dimension, self))

        return i_facet
