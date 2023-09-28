# GrizzlyPlot

## A Python library for grammar-of-graphics style plotting with Matplotlib and Polars

## Introduction
GrizzlyPlot is a lightweight library for [declarative](https://stackoverflow.com/questions/1784664/what-is-the-difference-between-declarative-and-imperative-paradigm-in-programmin) plotting ([data visualization](https://clauswilke.com/dataviz)) in Python. It uses [Polars DataFrames](https://www.pola.rs/) to represent data and [Matplotlib](https://matplotlib.org/) as its plotting backend.

It aims to make basic Python statistical graphics work less painful and more intuitive, while still giving users access to Matplotlib's powerful low-level tools for customization, theming, and publication-ready figure production.

## Getting started

### Warning: not-even-alpha release
GrizzlyPlot is still very much in early-phase development. Many things are not documented. There may be quirks and bugs. Please help by filing issues as you find them, or better yet by contributing and making a pull request.

### Installation
The easiest way for most people to install GrizzlyPlot will be by using the `pip` package manager for Python to install directly from this GitHub repository:

```bash
pip install git+https://github.com/dylanhmorris/grizzlyplot.git
```

If you run into issues, try manually downloading the repo, navigating to the top-level directory containing `pyproject.toml` and running

```bash
pip install .
```

## Design Principles
GrizzlyPlot is designed for plotting "[tidy data](https://vita.had.co.nz/papers/tidy-data.pdf)": tabular data in which each row represents exactly one observation.

GrizzlyPlot's plotting aims to follow the principles of a "grammar of graphics" as described by [Leland Wilkinson](https://en.wikipedia.org/wiki/Leland_Wilkinson) and elaborated/implemented by [Hadley Wickham](https://hadley.nz/) and collaborators in the superb and widely-used [ggplot2](https://ggplot2.tidyverse.org/) package for [R](https://www.r-project.org/). Grizzlyplot is heavily inspired by and indebted to that work.

Strictly speaking, a core ``GrizzlyPlot`` object is a *description* of the desired plot. A "grammar of graphics" is what allows us to describe it---namely, as a collection of datasets, aesthetic mappings, aesthetic objects ("geoms"), scalings, and statistical transformations. To render (create) the plot is to read this description and act upon it. The meat of GrizzlyPlot lies in implementing ``render()`` methods that do this for you, so that what you see is, ideally, what you described.
