#!/usr/bin/env python3

# filename: defaults.py
# description: runtime
# configuration customization
# for GrizzlyPlot

plot_defaults = dict(

    facet_label_pad_x=0.05,
    facet_label_pad_y=0.15,
    facet_label_size="large",

    autolabel_xaxis=True,
    autolabel_yaxis=True,

    xaxis_label_x=None,  # get defaults from
    xaxis_label_y=None,  # figure.supxlabel
    yaxis_label_x=None,  # get defaults from
    yaxis_label_y=None,  # figure.supylabel
    legend=False
)
