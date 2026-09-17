"""Tests for :mod:`src.visualization`.

Every chart is rendered headlessly with ``save=False`` so the suite never writes
PNGs and stays fast.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import pytest
from matplotlib.figure import Figure

from src import visualization


def test_plot_registry_is_complete() -> None:
    assert len(visualization.ALL_PLOTS) == 16
    assert all(callable(func) for func in visualization.ALL_PLOTS)


@pytest.mark.parametrize(
    "plot_function",
    visualization.ALL_PLOTS,
    ids=[func.__name__ for func in visualization.ALL_PLOTS],
)
def test_each_plot_returns_a_figure(plot_function, featured_df: pd.DataFrame) -> None:
    figure = plot_function(featured_df, save=False)
    assert isinstance(figure, Figure)
    plt.close(figure)


def test_generate_all_plots_returns_every_figure(featured_df: pd.DataFrame) -> None:
    figures = visualization.generate_all_plots(featured_df, save=False)
    assert len(figures) == len(visualization.ALL_PLOTS)
    for figure in figures:
        plt.close(figure)
