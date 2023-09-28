#!/usr/bin/env python3

# filename: position.py
# description: position adjustment
# classes

import numpy as np
from collections import Counter


class Position():

    def __call__(self, group_scaled_values, scales):
        raise NotImplementedError()


class PositionIdentity(Position):

    def __call__(self, group_scaled_values, scales):
        return group_scaled_values


class PositionDodge(Position):

    def __init__(self,
                 offset_x: float = None,
                 offset_y: float = None):
        self.offsets = dict()
        if offset_x is not None:
            self.offsets["x"] = offset_x
        if offset_y is not None:
            self.offsets["y"] = -offset_y

    def get_clashing_values(self,
                            group_scaled_values,
                            coord):
        n_groups = len(group_scaled_values)
        val_counts = Counter()
        grp_ranks = [None] * n_groups
        grp_vals = [None] * n_groups
        for i_grp, group_vals in enumerate(
                group_scaled_values):
            grp_uniqs = np.unique(group_vals[coord])
            if not grp_uniqs.size < 2:
                raise ValueError("Need unique coord "
                                 "values for each group "
                                 "to use PositionDodge")
            if grp_uniqs.size > 0:
                val = grp_uniqs[0]
                grp_vals[i_grp] = val
                grp_ranks[i_grp] = val_counts[val]
                val_counts.update({val})
        grp_clash_counts = [
            val_counts[grp_val] for grp_val in grp_vals]
        return grp_clash_counts, grp_ranks

    def position_from_rank(self, n_clashes, rank):
        delta = np.where(n_clashes > 1,
                         1 / n_clashes,
                         0)
        pos = (rank - 0.5 * n_clashes + 0.5) * delta
        return pos

    def transform(self,
                  vals_to_transform,
                  n_clashes,
                  offset,
                  group_rank):

        vals_to_transform = vals_to_transform + (
            offset * self.position_from_rank(
                n_clashes, group_rank))
        return vals_to_transform

    def __call__(self, group_scaled_values, scales):
        result = list(group_scaled_values)
        for coord, offset in self.offsets.items():
            grp_clash_counts, grp_ranks = self.get_clashing_values(
                group_scaled_values,
                coord)
            for i_group, group_vals in enumerate(
                    group_scaled_values):
                result[i_group][coord] = self.transform(
                    group_vals[coord],
                    grp_clash_counts[i_group],
                    offset,
                    grp_ranks[i_group])
        return result
