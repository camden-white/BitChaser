#!/usr/bin/env python

"""Create plots to display on documentation."""

from bitchaser.data.load import (
    load_latest,
    load_snapshot,
)

btc_snapshot = load_snapshot()
btc_latest = load_latest()
