"""Tests for :mod:`src.config`."""

from __future__ import annotations

from src import config


def test_required_columns_are_unique_and_non_empty() -> None:
    assert config.REQUIRED_COLUMNS
    assert len(config.REQUIRED_COLUMNS) == len(set(config.REQUIRED_COLUMNS))


def test_age_bins_match_labels() -> None:
    assert len(config.AGE_BINS) == len(config.AGE_LABELS) + 1
    assert list(config.AGE_BINS) == sorted(config.AGE_BINS)


def test_amount_bins_match_labels() -> None:
    assert len(config.AMOUNT_BINS) == len(config.AMOUNT_LABELS) + 1
    assert list(config.AMOUNT_BINS) == sorted(config.AMOUNT_BINS)


def test_mdr_rate_is_a_fraction() -> None:
    assert 0 < config.MDR_RATE < 1
    assert config.TRANSFER_FEE_RATE == 0


def test_ensure_directories_creates_every_path(monkeypatch, tmp_path) -> None:
    names = (
        "DATA_DIR",
        "RAW_DATA_DIR",
        "PROCESSED_DATA_DIR",
        "REPORTS_DIR",
        "SCREENSHOTS_DIR",
        "ASSETS_DIR",
        "POWERBI_DIR",
    )
    for name in names:
        monkeypatch.setattr(config, name, tmp_path / name.lower())

    config.ensure_directories()

    for name in names:
        assert (tmp_path / name.lower()).is_dir()
