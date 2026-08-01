"""Functions for generating predictions from models."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.api as sm
from numpy.typing import NDArray

# from typing import cast
from scipy.optimize import differential_evolution
from statsmodels.regression.linear_model import (
    RegressionResultsWrapper,
)

from bitchaser.config import GENESIS, HALVINGS, HIGHS, LOWS
from bitchaser.data.load import load_snapshot

DATE_COLUMN: str = "date"
PRICE_COLUMN: str = "close"
DABL_COLUMN: str = "dabl"
LOG_DABL_COLUMN: str = "log_dabl"
LOG_PRICE_COLUMN: str = "log_close"

SECONDS_PER_DAY = 86_400.0

BITCOIN_LAUNCH_DATE: pd.Timestamp = pd.Timestamp(
    GENESIS,
    tz="UTC",
)

# Allows the covariance estimate to account for as much as
# one year of dependence in daily residuals.
HAC_MAX_LAGS: int = 365

CONFIDENCE_LEVEL: float = 0.95

snapshot: pd.DataFrame = load_snapshot()

# print(f"Loaded {len(snapshot):,} snapshot observations.")

Interval = tuple[float, float]


def dabl(date: pd.Timestamp | str) -> float:
    """Return days after Bitcoin's launch (DABL)."""
    if isinstance(date, str):
        date = pd.Timestamp(date, tz="UTC")
    return (date - pd.Timestamp(GENESIS, tz="UTC")) / pd.Timedelta(days=1)


@dataclass(frozen=True, slots=True)
class LogLogPowerLawFit:
    """Results from a Bitcoin log-log power-law regression."""

    results: RegressionResultsWrapper
    coefficient: float
    exponent: float
    smearing_factor: float
    hac_max_lags: int


def prepare_snapshot(snapshot: pd.DataFrame) -> pd.DataFrame:
    """Prepare Bitcoin closing-price data for log-log regression.

    The function copies the supplied snapshot and therefore does not
    mutate the DataFrame returned by load_snapshot().
    """

    required_columns: set[str] = {
        DATE_COLUMN,
        PRICE_COLUMN,
        "high",
        "low",
    }
    missing_columns: set[str] = required_columns.difference(snapshot.columns)

    if missing_columns:
        missing: str = ", ".join(sorted(missing_columns))
        raise ValueError(f"Snapshot is missing required columns: {missing}")

    frame: pd.DataFrame = snapshot.loc[
        :,
        [
            DATE_COLUMN,
            PRICE_COLUMN,
            "high",
            "low",
        ],
    ].copy()

    frame[DATE_COLUMN] = pd.to_datetime(
        frame[DATE_COLUMN],
        utc=True,
        errors="raise",
    ).dt.normalize()

    price_columns = [
        PRICE_COLUMN,
        "high",
        "low",
    ]

    for column in price_columns:
        frame[column] = pd.to_numeric(
            frame[column],
            errors="raise",
        ).astype("float64")

    frame = frame.sort_values(
        DATE_COLUMN,
        ignore_index=True,
    )

    if (
        frame[
            [
                DATE_COLUMN,
                PRICE_COLUMN,
                "high",
                "low",
            ]
        ]
        .isna()
        .any()
        .any()
    ):
        raise ValueError(
            "The date, close, high, and low columns must not contain missing values."
        )

    if frame[DATE_COLUMN].duplicated().any():
        raise ValueError("The snapshot contains duplicate UTC dates.")

    prices: NDArray[np.float64] = frame[
        [
            PRICE_COLUMN,
            "high",
            "low",
        ]
    ].to_numpy(dtype=np.float64)

    if not np.isfinite(prices).all():
        raise ValueError("Close, high, and low prices must all be finite.")

    if np.any(prices <= 0.0):
        raise ValueError("Logarithmic calculations require strictly positive prices.")

    close: NDArray[np.float64] = frame[PRICE_COLUMN].to_numpy(dtype=np.float64)

    date_gaps: pd.Series = frame[DATE_COLUMN].diff().dropna()

    if not date_gaps.eq(pd.Timedelta(days=1)).all():
        raise ValueError(
            "The snapshot must contain consecutive daily observations "
            "for the HAC lag length to represent calendar days."
        )

    frame[DABL_COLUMN] = (frame[DATE_COLUMN] - BITCOIN_LAUNCH_DATE).dt.days.astype(
        "int64"
    )

    if (frame[DABL_COLUMN] <= 0).any():
        raise ValueError("DABL must be strictly positive before taking logarithms.")

    day: NDArray[np.float64] = frame[DABL_COLUMN].to_numpy(dtype=np.float64)

    frame[LOG_DABL_COLUMN] = np.log(day)
    frame[LOG_PRICE_COLUMN] = np.log(close)

    return frame


def make_design_matrix(
    day: NDArray[np.float64],
) -> pd.DataFrame:
    """Construct the OLS design matrix for log(day)."""

    if day.ndim != 1:
        raise ValueError("day must be a one-dimensional array.")

    if not np.isfinite(day).all():
        raise ValueError("day values must all be finite.")

    if np.any(day <= 0.0):
        raise ValueError("day values must all be strictly positive.")

    return pd.DataFrame(
        {
            "const": np.ones(
                day.size,
                dtype=np.float64,
            ),
            LOG_DABL_COLUMN: np.log(day),
        }
    )


def fit_log_log_power_law(
    frame: pd.DataFrame,
    *,
    hac_max_lags: int = HAC_MAX_LAGS,
) -> LogLogPowerLawFit:
    """Fit a Bitcoin power law using OLS in logarithmic space.

    HAC covariance changes the estimated standard errors, confidence
    intervals, and hypothesis tests. It does not change the OLS
    coefficient estimates themselves.
    """

    if hac_max_lags < 1:
        raise ValueError("hac_max_lags must be positive.")

    if hac_max_lags >= len(frame):
        raise ValueError("hac_max_lags must be smaller than the sample size.")

    day: NDArray[np.float64] = frame[DABL_COLUMN].to_numpy(dtype=np.float64)
    log_price: NDArray[np.float64] = frame[LOG_PRICE_COLUMN].to_numpy(dtype=np.float64)

    design: pd.DataFrame = make_design_matrix(day)

    results = sm.OLS(
        endog=log_price,
        exog=design,
        missing="raise",
    ).fit(
        cov_type="HAC",
        cov_kwds={
            "maxlags": hac_max_lags,
            "kernel": "bartlett",
            "use_correction": True,
        },
        use_t=True,
    )

    # results: RegressionResultsWrapper = cast(
    #     RegressionResultsWrapper,
    #     results,
    # )

    parameters: NDArray[np.float64] = np.asarray(
        results.params,
        dtype=np.float64,
    )
    residuals: NDArray[np.float64] = np.asarray(
        results.resid,
        dtype=np.float64,
    )

    intercept: float = float(parameters[0])
    exponent: float = float(parameters[1])

    return LogLogPowerLawFit(
        results=results,
        coefficient=float(np.exp(intercept)),
        exponent=exponent,
        smearing_factor=float(np.mean(np.exp(residuals))),
        hac_max_lags=hac_max_lags,
    )


def predict_log_prices(
    fitted_model: LogLogPowerLawFit,
    day: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Predict the conditional mean of log closing price."""

    predictions = fitted_model.results.predict(make_design_matrix(day))

    return np.asarray(
        predictions,
        dtype=np.float64,
    )


def predict_median_prices(
    fitted_model: LogLogPowerLawFit,
    day: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Predict the conditional median price in dollars."""

    return np.exp(
        predict_log_prices(
            fitted_model,
            day,
        )
    )


def predict_mean_prices(
    fitted_model: LogLogPowerLawFit,
    day: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Predict conditional mean price using Duan smearing."""

    median_price: NDArray[np.float64] = predict_median_prices(
        fitted_model,
        day,
    )

    return fitted_model.smearing_factor * median_price


def parameter_confidence_intervals(
    fitted_model: LogLogPowerLawFit,
    *,
    confidence_level: float = CONFIDENCE_LEVEL,
) -> tuple[Interval, Interval]:
    """Return robust confidence intervals for a and b."""

    if not 0.0 < confidence_level < 1.0:
        raise ValueError("confidence_level must be between zero and one.")

    alpha: float = 1.0 - confidence_level

    intervals: NDArray[np.float64] = np.asarray(
        fitted_model.results.conf_int(alpha=alpha),
        dtype=np.float64,
    )

    coefficient_interval: Interval = (
        float(np.exp(intervals[0, 0])),
        float(np.exp(intervals[0, 1])),
    )
    exponent_interval: Interval = (
        float(intervals[1, 0]),
        float(intervals[1, 1]),
    )

    return coefficient_interval, exponent_interval


btc_snapshot_subset = snapshot.loc[
    (snapshot["date"] >= pd.Timestamp(HALVINGS[0], tz="UTC"))
    & (snapshot["date"] <= pd.Timestamp("2026-07-17", tz="UTC"))
]

regression_frame: pd.DataFrame = prepare_snapshot(snapshot)

power_law_fit: LogLogPowerLawFit = fit_log_log_power_law(
    regression_frame,
    hac_max_lags=HAC_MAX_LAGS,
)

coefficient_interval, exponent_interval = parameter_confidence_intervals(power_law_fit)

# print(
#     "Fitted median trend:\n"
#     f"close = {power_law_fit.coefficient:.10g} "
#     f"* DABL^{power_law_fit.exponent:.8f}"
# )

# print(
#     "\nCoefficient a:"
#     f"\n  Estimate: {power_law_fit.coefficient:.10g}"
#     f"\n  95% CI:   "
#     f"({coefficient_interval[0]:.10g}, "
#     f"{coefficient_interval[1]:.10g})"
# )

# print(
#     "\nExponent b:"
#     f"\n  Estimate: {power_law_fit.exponent:.8f}"
#     f"\n  95% CI:   "
#     f"({exponent_interval[0]:.8f}, "
#     f"{exponent_interval[1]:.8f})"
# )

# print(f"\nLog-space R²: {power_law_fit.results.rsquared:.6f}")

# print(f"HAC maximum lag: {power_law_fit.hac_max_lags} days")

# print(f"Duan smearing factor: {power_law_fit.smearing_factor:.6f}")

observed_dabl: NDArray[np.float64] = regression_frame[DABL_COLUMN].to_numpy(
    dtype=np.float64
)

regression_frame["fitted_median_close"] = predict_median_prices(
    power_law_fit,
    observed_dabl,
)

regression_frame["fitted_mean_close"] = predict_mean_prices(
    power_law_fit,
    observed_dabl,
)

regression_frame["log_residual"] = np.asarray(
    power_law_fit.results.resid,
    dtype=np.float64,
)

regression_frame["residual_percent"] = np.expm1(regression_frame["log_residual"])

regression_frame["fitted_log_close"] = predict_log_prices(
    power_law_fit,
    observed_dabl,
)


def normalize_utc_date(
    date: str | pd.Timestamp,
) -> pd.Timestamp:
    """Return a normalized UTC timestamp."""

    prediction_date: pd.Timestamp = pd.Timestamp(date)

    if prediction_date.tzinfo is None:
        prediction_date = prediction_date.tz_localize("UTC")
    else:
        prediction_date = prediction_date.tz_convert("UTC")

    return prediction_date.normalize()


def predict_median_price(
    fitted_model: LogLogPowerLawFit,
    date: str | pd.Timestamp,
) -> float:
    """Predict Bitcoin's median power-law price on a date."""

    day: float = dabl(date)

    predicted_prices: NDArray[np.float64] = predict_median_prices(
        fitted_model,
        np.array(
            [day],
            dtype=np.float64,
        ),
    )

    return float(predicted_prices[0])


def predict_mean_price(
    fitted_model: LogLogPowerLawFit,
    date: str | pd.Timestamp,
) -> float:
    """Predict Bitcoin's smearing-adjusted mean price on a date."""

    day: float = dabl(date)

    predicted_prices: NDArray[np.float64] = predict_mean_prices(
        fitted_model,
        np.array(
            [day],
            dtype=np.float64,
        ),
    )

    return float(predicted_prices[0])


def get_row(date: str | pd.Timestamp) -> pd.Series:
    """Return the row for the given date."""
    timestamp: pd.Timestamp = pd.to_datetime(date, utc=True).normalize()
    return snapshot.loc[snapshot["date"] == timestamp].iloc[0]


def local_extreme(extreme: str, cerca: str, margin: int) -> pd.Series:
    """Return the row with the extreme price around a date."""

    start_date: pd.Timestamp = pd.to_datetime(cerca, utc=True) - pd.Timedelta(
        days=margin
    )
    end_date: pd.Timestamp = pd.to_datetime(cerca, utc=True) + pd.Timedelta(days=margin)

    if start_date > end_date:
        raise ValueError("start must be on or before end.")

    date_mask: pd.Series = snapshot["date"].between(
        start_date,
        end_date,
        inclusive="both",
    )

    period: pd.DataFrame = snapshot.loc[date_mask]

    if period.empty:
        raise ValueError("No Bitcoin observations exist between those dates.")

    if extreme == "high":
        index = int(period["high"].idxmax())
    elif extreme == "low":
        index = int(period["low"].idxmin())
    else:
        raise ValueError("Argument `extreme` must be 'high' or 'low'.")

    return snapshot.loc[index].copy()


## timing model


@dataclass(frozen=True)
class BitcoinCycleTimingModel:
    """Fixed-duration Bitcoin cycle timing model."""

    anchor_date: pd.Timestamp
    anchor_cycle_number: int
    bear_days: float
    bull_days: float
    halving_to_high_days: float

    @property
    def cycle_days(self) -> float:
        """Return the fitted high-to-high cycle duration."""
        return self.bear_days + self.bull_days

    @property
    def first_halving_cycle_number(self) -> int:
        """Return the cycle associated with the first halving."""
        return self.anchor_cycle_number

    def predict_high(self, cycle_number: int) -> pd.Timestamp:
        """Predict the high date for a numbered Bitcoin cycle."""
        if cycle_number < 1:
            raise ValueError("cycle_number must be at least 1.")

        cycle_offset = cycle_number - self.anchor_cycle_number

        return self.anchor_date + pd.to_timedelta(
            cycle_offset * self.cycle_days,
            unit="D",
        )

    def predict_low(self, cycle_number: int) -> pd.Timestamp:
        """Predict the low following a numbered cycle high."""
        return self.predict_high(cycle_number) + pd.to_timedelta(
            self.bear_days,
            unit="D",
        )

    def predict_halving(self, cycle_number: int) -> pd.Timestamp:
        """Predict the halving preceding a numbered cycle high."""
        if cycle_number < self.first_halving_cycle_number:
            raise ValueError(
                f"cycle_number must be at least {self.first_halving_cycle_number}."
            )

        return self.predict_high(cycle_number + 1) - pd.to_timedelta(
            self.halving_to_high_days,
            unit="D",
        )


def fit_cycle_timing_model(
    event_dates: list[str | pd.Timestamp],
    halving_dates: list[str | pd.Timestamp],
    *,
    first_cycle_number: int = 1,
) -> tuple[BitcoinCycleTimingModel, pd.DataFrame]:
    """
    Fit fixed bear, bull, and halving-to-high durations.

    Parameters
    ----------
    event_dates:
        Chronological market events arranged as:

            high, low, high, low, ..., high

    halving_dates:
        Chronological Bitcoin halving timestamps.

        Each halving is associated with the cycle high that follows it.

    first_cycle_number:
        Cycle number assigned to the first high in event_dates.

    Returns
    -------
    tuple[BitcoinCycleTimingModel, pd.DataFrame]
        The fitted model and observation-level residual table.
    """

    if len(event_dates) < 3:
        raise ValueError("At least three market event dates are required.")

    if len(event_dates) % 2 == 0:
        raise ValueError(
            "event_dates must end with a high and therefore contain "
            "an odd number of dates."
        )

    if not halving_dates:
        raise ValueError("At least one halving date is required.")

    if first_cycle_number < 1:
        raise ValueError("first_cycle_number must be at least 1.")

    market_dates = pd.DatetimeIndex(
        pd.to_datetime(
            event_dates,
            utc=True,
        )
    )

    halving_index = pd.DatetimeIndex(
        pd.to_datetime(
            halving_dates,
            utc=True,
        )
    )

    if not market_dates.is_monotonic_increasing:
        raise ValueError("event_dates must be chronological.")

    if not halving_index.is_monotonic_increasing:
        raise ValueError("halving_dates must be chronological.")

    # Do not call .normalize() here. Halving timestamps contain meaningful
    # hour, minute, and second information.
    origin = min(
        market_dates.min(),
        halving_index.min(),
    )

    # ------------------------------------------------------------
    # Market-event rows
    # ------------------------------------------------------------

    market_event_indices = np.arange(
        len(market_dates),
        dtype=np.int64,
    )

    market_cycle_offsets = market_event_indices // 2

    # Even indices are highs; odd indices are lows.
    market_is_low = market_event_indices % 2

    market_cycle_numbers = (first_cycle_number + market_cycle_offsets).astype(np.int64)

    # High k:
    #   anchor + k * bear + k * bull
    #
    # Low k:
    #   anchor + (k + 1) * bear + k * bull
    market_bear_counts = market_cycle_offsets + market_is_low
    market_bull_counts = market_cycle_offsets

    market_design = np.column_stack(
        [
            np.ones(len(market_dates), dtype=np.float64),
            market_bear_counts.astype(np.float64),
            market_bull_counts.astype(np.float64),
            np.zeros(len(market_dates), dtype=np.float64),
        ]
    )

    market_observed_days = np.asarray(
        (market_dates - origin).total_seconds() / SECONDS_PER_DAY,
        dtype=np.float64,
    )

    # ------------------------------------------------------------
    # Halving rows
    # ------------------------------------------------------------

    halving_numbers = np.arange(
        1,
        len(halving_index) + 1,
        dtype=np.int64,
    )

    # The first halving receives the same number as the first
    # preceding high/low pair.
    halving_cycle_numbers = first_cycle_number + halving_numbers - 1

    # Zero-based offsets of the preceding cycles:
    # halving 1 -> offset 0
    # halving 2 -> offset 1
    # halving 3 -> offset 2
    halving_cycle_offsets = halving_cycle_numbers - first_cycle_number

    # A halving occurs in the transition to the following high.
    # Therefore, halving 1 is one full cycle interval after high 1,
    # halving 2 is two full intervals after high 1, and so on.
    halving_interval_counts = halving_cycle_offsets + 1

    if np.any(halving_cycle_offsets < 0):
        raise ValueError(
            "A halving cannot be associated with a cycle before first_cycle_number."
        )

    # Halving preceding high k:
    #
    #   anchor
    #   + k * bear
    #   + k * bull
    #   - halving_to_high_days
    #
    # The final design-matrix column is therefore -1.
    halving_design = np.column_stack(
        [
            np.ones(len(halving_index), dtype=np.float64),
            halving_interval_counts.astype(np.float64),
            halving_interval_counts.astype(np.float64),
            -np.ones(len(halving_index), dtype=np.float64),
        ]
    )

    halving_observed_days = np.asarray(
        (halving_index - origin).total_seconds() / SECONDS_PER_DAY,
        dtype=np.float64,
    )

    # ------------------------------------------------------------
    # Joint least-squares fit
    # ------------------------------------------------------------

    design_matrix = np.vstack(
        [
            market_design,
            halving_design,
        ]
    )

    observed_days = np.concatenate(
        [
            market_observed_days,
            halving_observed_days,
        ]
    )

    coefficients, _, rank, _ = np.linalg.lstsq(
        design_matrix,
        observed_days,
        rcond=None,
    )

    if rank < 4:
        raise ValueError("The observations do not identify all four model parameters.")

    (
        anchor_offset,
        bear_days,
        bull_days,
        halving_to_high_days,
    ) = coefficients

    if bear_days <= 0:
        raise ValueError(f"Fitted bear duration is not positive: {bear_days:.2f} days.")

    if bull_days <= 0:
        raise ValueError(f"Fitted bull duration is not positive: {bull_days:.2f} days.")

    if not 0 < halving_to_high_days < bull_days:
        raise ValueError(
            "The fitted halving does not fall between the preceding "
            "low and the following high. "
            f"bull_days={bull_days:.2f}, "
            f"halving_to_high_days={halving_to_high_days:.2f}."
        )

    model = BitcoinCycleTimingModel(
        anchor_date=origin
        + pd.to_timedelta(
            anchor_offset,
            unit="D",
        ),
        anchor_cycle_number=first_cycle_number,
        bear_days=float(bear_days),
        bull_days=float(bull_days),
        halving_to_high_days=float(halving_to_high_days),
    )

    # ------------------------------------------------------------
    # Results table
    # ------------------------------------------------------------

    fitted_days = design_matrix @ coefficients
    residual_days = observed_days - fitted_days

    event_types = np.concatenate(
        [
            np.where(
                market_is_low == 0,
                "high",
                "low",
            ),
            np.full(
                len(halving_index),
                "halving",
                dtype=object,
            ),
        ]
    )

    cycle_numbers = np.concatenate(
        [
            market_cycle_numbers,
            halving_cycle_numbers,
        ]
    )

    event_numbers = np.concatenate(
        [
            np.full(
                len(market_dates),
                np.nan,
                dtype=np.float64,
            ),
            halving_numbers.astype(np.float64),
        ]
    )

    observed_dates = market_dates.append(halving_index)

    results = pd.DataFrame(
        {
            "cycle_number": cycle_numbers,
            "event": event_types,
            "event_number": pd.array(
                event_numbers,
                dtype="Int64",
            ),
            "observed_date": observed_dates,
            "fitted_date": origin
            + pd.to_timedelta(
                fitted_days,
                unit="D",
            ),
            "residual_days": residual_days,
            "absolute_residual_days": np.abs(residual_days),
            "squared_residual_days": residual_days**2,
        }
    )

    results = results.sort_values("observed_date").reset_index(drop=True)

    return model, results


model, timing_results = fit_cycle_timing_model(
    event_dates=[HIGHS[1], LOWS[1], HIGHS[2], LOWS[2], HIGHS[3], LOWS[3], HIGHS[4]],
    halving_dates=[HALVINGS[1], HALVINGS[2], HALVINGS[3]],
    first_cycle_number=2,
)

# print(f"Anchor cycle: {model.anchor_cycle_number}")
# print(f"Fitted anchor date: {model.anchor_date}")
# print(f"Bear duration: {model.bear_days:.2f} days")
# print(f"Bull duration: {model.bull_days:.2f} days")
# print(f"Full cycle: {model.cycle_days:.2f} days")

## Sine model

# Slant Sine


# --------------------------------------------------
# Model configuration
# --------------------------------------------------

FIXED_PERIOD_YEARS = model.cycle_days / 365.25
FIXED_ANGULAR_FREQUENCY = 2.0 * np.pi / FIXED_PERIOD_YEARS

DECAY_BOUNDS = (0.0, 3.0)

RISE_FRACTION_MODEL = model.bull_days / model.cycle_days
RISE_ALLOWANCE = 0.001
# u is the proportion of each period spent increasing.
# u = 0.50 is an ordinary sine wave. Larger values create
# a longer rise and a shorter, steeper decline.
RISE_FRACTION_BOUNDS = (
    RISE_FRACTION_MODEL - RISE_ALLOWANCE,
    RISE_FRACTION_MODEL + RISE_ALLOWANCE,
)

# One complete phase interval is sufficient because the
# waveform is periodic in phase with period 2*pi.
PHASE_SHIFT_BOUNDS = (-np.pi, np.pi)


def to_utc_timestamp(value: str | pd.Timestamp) -> pd.Timestamp:
    """Convert a date-like value to a UTC-aware timestamp."""
    timestamp = pd.Timestamp(value)

    if timestamp.tzinfo is None:
        return timestamp.tz_localize("UTC")

    return timestamp.tz_convert("UTC")


FIT_START_DATE = to_utc_timestamp(HALVINGS[0])


# --------------------------------------------------
# Slanted sinusoidal waveform
# --------------------------------------------------


def slanted_sine_wave(
    phase: float | NDArray[np.float64],
    rise_fraction: float,
) -> float | NDArray[np.float64]:
    """
    Evaluate the smooth slanted sinusoidal waveform s_u(phase).

    Define the position q within one cycle by

        q = ((phase + pi/2) / (2*pi)) mod 1.

    Then

        s_u = -cos(pi*q/u),                  0 <= q < u
              cos(pi*(q-u)/(1-u)),           u <= q < 1.

    The phase offset is chosen so that

        s_0.5(phase) = sin(phase)

    exactly. Thus, rise_fraction=0.50 reproduces the ordinary
    sine model, while rise_fraction>0.50 lengthens the rise and
    compresses the fall.
    """
    if not np.isfinite(rise_fraction):
        raise ValueError("rise_fraction must be finite.")

    if not 0.0 < rise_fraction < 1.0:
        raise ValueError("rise_fraction must be strictly between 0 and 1.")

    phase_array = np.asarray(phase, dtype=np.float64)

    if not np.all(np.isfinite(phase_array)):
        raise ValueError("phase must contain only finite values.")

    cycle_position = np.mod(
        (phase_array + np.pi / 2.0) / (2.0 * np.pi),
        1.0,
    )

    rising_values = -np.cos(np.pi * cycle_position / rise_fraction)

    falling_values = np.cos(
        np.pi * (cycle_position - rise_fraction) / (1.0 - rise_fraction)
    )

    values = np.where(
        cycle_position < rise_fraction,
        rising_values,
        falling_values,
    )

    if values.ndim == 0:
        return float(values)

    return np.asarray(values, dtype=np.float64)


# --------------------------------------------------
# Fixed-period damped slanted-sine model
# --------------------------------------------------


@dataclass(frozen=True)
class AsymmetricCycleResidualFit:
    """
    Fitted damped slanted-sine residual model:

        r(x) = A s_u(omega*x + phi) / x^c

    where

        x     = YABL,
        A     = nonnegative amplitude,
        omega = fixed angular frequency,
        phi   = fitted phase shift,
        c     = fitted decay exponent,
        u     = fitted fraction of each period spent increasing.

    The period is fixed at

        T = model.cycle_days / 365.25,
        omega = 2*pi / T.

    The residual center remains fixed at zero. The class name is
    retained for compatibility with existing BitChaser notebook code.
    """

    amplitude: float
    angular_frequency: float
    phase_shift: float
    decay_exponent: float
    rise_fraction: float

    @property
    def period_years(self) -> float:
        """Return the fixed cycle period in years."""
        return 2.0 * np.pi / self.angular_frequency

    @property
    def rise_years(self) -> float:
        """Return the increasing portion of one period in years."""
        return self.period_years * self.rise_fraction

    @property
    def fall_years(self) -> float:
        """Return the decreasing portion of one period in years."""
        return self.period_years * (1.0 - self.rise_fraction)

    def predict(
        self,
        x: float | NDArray[np.float64],
    ) -> float | NDArray[np.float64]:
        """Predict the log residual at YABL x."""
        x_array = np.asarray(x, dtype=np.float64)

        if np.any(x_array <= 0.0):
            raise ValueError("YABL values must be positive.")

        phase = self.angular_frequency * x_array + self.phase_shift

        oscillation = np.asarray(
            slanted_sine_wave(
                phase,
                self.rise_fraction,
            ),
            dtype=np.float64,
        )

        values = (
            self.amplitude
            * oscillation
            / np.power(
                x_array,
                self.decay_exponent,
            )
        )

        if values.ndim == 0:
            return float(values)

        return values

    def lower(
        self,
        x: float | NDArray[np.float64],
    ) -> float | NDArray[np.float64]:
        """Return the decaying lower envelope."""
        x_array = np.asarray(x, dtype=np.float64)

        if np.any(x_array <= 0.0):
            raise ValueError("YABL values must be positive.")

        values = -self.amplitude / np.power(
            x_array,
            self.decay_exponent,
        )

        if values.ndim == 0:
            return float(values)

        return values

    def upper(
        self,
        x: float | NDArray[np.float64],
    ) -> float | NDArray[np.float64]:
        """Return the decaying upper envelope."""
        x_array = np.asarray(x, dtype=np.float64)

        if np.any(x_array <= 0.0):
            raise ValueError("YABL values must be positive.")

        values = self.amplitude / np.power(
            x_array,
            self.decay_exponent,
        )

        if values.ndim == 0:
            return float(values)

        return values


# --------------------------------------------------
# Fit amplitude, phase, decay, and rise fraction
# --------------------------------------------------


def fit_asymmetric_cycle_residual(
    x: NDArray[np.float64],
    residuals: NDArray[np.float64],
    *,
    angular_frequency: float = FIXED_ANGULAR_FREQUENCY,
    decay_bounds: tuple[float, float] = DECAY_BOUNDS,
    rise_fraction_bounds: tuple[
        float,
        float,
    ] = RISE_FRACTION_BOUNDS,
    phase_shift_bounds: tuple[
        float,
        float,
    ] = PHASE_SHIFT_BOUNDS,
) -> AsymmetricCycleResidualFit:
    """
    Fit

        r(x) = A s_u(omega*x + phi) / x^c.

    The angular frequency is fixed by model.cycle_days. The fitted
    nonlinear parameters are decay exponent c, rise fraction u, and
    phase shift phi.

    For each nonlinear candidate, the model remains linear in A, so
    the nonnegative amplitude is solved directly by least squares.
    """
    x = np.asarray(x, dtype=np.float64)
    residuals = np.asarray(residuals, dtype=np.float64)

    if x.ndim != 1:
        raise ValueError("x must be one-dimensional.")

    if residuals.ndim != 1:
        raise ValueError("residuals must be one-dimensional.")

    if len(x) != len(residuals):
        raise ValueError("x and residuals must have equal lengths.")

    if len(x) < 6:
        raise ValueError("At least six observations are required.")

    if not np.all(np.isfinite(x)):
        raise ValueError("x must contain only finite values.")

    if not np.all(np.isfinite(residuals)):
        raise ValueError("residuals must contain only finite values.")

    if np.any(x <= 0.0):
        raise ValueError("All YABL values must be positive.")

    if not np.isfinite(angular_frequency):
        raise ValueError("angular_frequency must be finite.")

    if angular_frequency <= 0.0:
        raise ValueError("angular_frequency must be positive.")

    minimum_decay, maximum_decay = decay_bounds

    if not np.all(np.isfinite(decay_bounds)):
        raise ValueError("decay_bounds must be finite.")

    if minimum_decay < 0.0:
        raise ValueError("The minimum decay exponent cannot be negative.")

    if maximum_decay <= minimum_decay:
        raise ValueError("The maximum decay exponent must exceed the minimum.")

    minimum_rise_fraction, maximum_rise_fraction = rise_fraction_bounds

    if not np.all(np.isfinite(rise_fraction_bounds)):
        raise ValueError("rise_fraction_bounds must be finite.")

    if not 0.0 < minimum_rise_fraction < 1.0:
        raise ValueError("The minimum rise fraction must be between 0 and 1.")

    if not 0.0 < maximum_rise_fraction < 1.0:
        raise ValueError("The maximum rise fraction must be between 0 and 1.")

    if maximum_rise_fraction <= minimum_rise_fraction:
        raise ValueError("The maximum rise fraction must exceed the minimum.")

    minimum_phase_shift, maximum_phase_shift = phase_shift_bounds

    if not np.all(np.isfinite(phase_shift_bounds)):
        raise ValueError("phase_shift_bounds must be finite.")

    if maximum_phase_shift <= minimum_phase_shift:
        raise ValueError("The maximum phase shift must exceed the minimum.")

    def construct_model(
        decay_exponent: float,
        rise_fraction: float,
        phase_shift: float,
    ) -> tuple[float, NDArray[np.float64]]:
        """Solve amplitude for fixed nonlinear parameters."""
        damping = 1.0 / np.power(
            x,
            decay_exponent,
        )

        phase = angular_frequency * x + phase_shift

        oscillation = np.asarray(
            slanted_sine_wave(
                phase,
                rise_fraction,
            ),
            dtype=np.float64,
        )

        basis = damping * oscillation

        denominator = float(
            np.dot(
                basis,
                basis,
            )
        )

        if denominator <= np.finfo(np.float64).tiny:
            raise RuntimeError("The slanted-sine basis has effectively zero norm.")

        unconstrained_amplitude = float(
            np.dot(
                basis,
                residuals,
            )
            / denominator
        )

        # A is defined as nonnegative. The fitted phase chooses
        # the orientation of the waveform.
        amplitude = max(
            0.0,
            unconstrained_amplitude,
        )

        fitted_values = np.asarray(
            amplitude * basis,
            dtype=np.float64,
        )

        return amplitude, fitted_values

    def objective(
        nonlinear_parameters: NDArray[np.float64],
    ) -> float:
        decay_exponent = float(nonlinear_parameters[0])

        rise_fraction = float(nonlinear_parameters[1])

        phase_shift = float(nonlinear_parameters[2])

        _, fitted_values = construct_model(
            decay_exponent,
            rise_fraction,
            phase_shift,
        )

        errors = fitted_values - residuals

        return float(np.mean(errors**2))

    result = differential_evolution(
        objective,
        bounds=[
            (
                minimum_decay,
                maximum_decay,
            ),
            (
                minimum_rise_fraction,
                maximum_rise_fraction,
            ),
            (
                minimum_phase_shift,
                maximum_phase_shift,
            ),
        ],
        strategy="best1bin",
        maxiter=750,
        popsize=20,
        tol=1e-9,
        atol=1e-10,
        init="sobol",
        polish=True,
        seed=42,
        workers=1,
        updating="immediate",
    )

    if not np.isfinite(result.fun):
        raise RuntimeError(
            "Slanted-sine optimization failed to produce a finite objective value."
        )

    if not result.success:
        print(
            f"Warning: optimization did not report full convergence: {result.message}"
        )

    decay_exponent = float(result.x[0])

    rise_fraction = float(result.x[1])

    phase_shift = float(result.x[2])

    amplitude, _ = construct_model(
        decay_exponent,
        rise_fraction,
        phase_shift,
    )

    return AsymmetricCycleResidualFit(
        amplitude=amplitude,
        angular_frequency=float(angular_frequency),
        phase_shift=phase_shift,
        decay_exponent=decay_exponent,
        rise_fraction=rise_fraction,
    )


# --------------------------------------------------
# Ensure the log residual exists
# --------------------------------------------------

if "log_residual" not in regression_frame.columns:
    regression_frame["log_residual"] = np.asarray(
        power_law_fit.results.resid,
        dtype=np.float64,
    )


# --------------------------------------------------
# Prepare the fitting data
# --------------------------------------------------

cycle_frame = (
    regression_frame[
        [
            DATE_COLUMN,
            DABL_COLUMN,
            "log_residual",
        ]
    ]
    .dropna()
    .sort_values(DATE_COLUMN)
    .reset_index(drop=True)
    .copy()
)

cycle_frame[DATE_COLUMN] = pd.to_datetime(
    cycle_frame[DATE_COLUMN],
    utc=True,
)

x_years = cycle_frame[DABL_COLUMN].to_numpy(dtype=np.float64) / 365.25

observed_residuals = cycle_frame["log_residual"].to_numpy(dtype=np.float64)

fit_mask = (cycle_frame[DATE_COLUMN] >= FIT_START_DATE).to_numpy()

fit_x_years = x_years[fit_mask]

fit_residuals = observed_residuals[fit_mask]


# --------------------------------------------------
# Fit the model
# --------------------------------------------------

# Keep this variable name for compatibility with the existing
# compound predict_price() function.
asymmetric_cycle_fit = fit_asymmetric_cycle_residual(
    fit_x_years,
    fit_residuals,
)


# --------------------------------------------------
# Evaluate the fitted cycle and envelopes
# --------------------------------------------------

fitted_residuals = np.asarray(
    asymmetric_cycle_fit.predict(x_years),
    dtype=np.float64,
)

lower_envelope = np.asarray(
    asymmetric_cycle_fit.lower(x_years),
    dtype=np.float64,
)

upper_envelope = np.asarray(
    asymmetric_cycle_fit.upper(x_years),
    dtype=np.float64,
)


# --------------------------------------------------
# Model diagnostics
# --------------------------------------------------

fit_predictions = np.asarray(
    asymmetric_cycle_fit.predict(fit_x_years),
    dtype=np.float64,
)

errors = fit_residuals - fit_predictions

rmse = float(np.sqrt(np.mean(errors**2)))

residual_sum_of_squares = float(np.sum(errors**2))

total_sum_of_squares = float(np.sum((fit_residuals - np.mean(fit_residuals)) ** 2))

if total_sum_of_squares == 0.0:
    r_squared = float("nan")

else:
    r_squared = 1.0 - residual_sum_of_squares / total_sum_of_squares


# --------------------------------------------------
# Print fixed and fitted parameters
# --------------------------------------------------

# print(
#     f"Amplitude:            "
#     f"{asymmetric_cycle_fit.amplitude:.6f}"
# )

# print(
#     f"Decay exponent:       "
#     f"{asymmetric_cycle_fit.decay_exponent:.6f}"
# )

# print(
#     f"Rise fraction (u):    "
#     f"{asymmetric_cycle_fit.rise_fraction:.6f} "
#     f"({asymmetric_cycle_fit.rise_fraction:.2%})"
# )

# print(
#     f"Fall fraction:        "
#     f"{1.0 - asymmetric_cycle_fit.rise_fraction:.6f} "
#     f"({1.0 - asymmetric_cycle_fit.rise_fraction:.2%})"
# )

# print(
#     f"Fixed period:         "
#     f"{asymmetric_cycle_fit.period_years:.6f} years"
#     f" = "
#     f"{asymmetric_cycle_fit.period_years * 365.25:.6f} days"
# )

# print(
#     f"Rising duration:      "
#     f"{asymmetric_cycle_fit.rise_years:.6f} years"
#     f" = "
#     f"{asymmetric_cycle_fit.rise_years * 365.25:.6f} days"
# )

# print(
#     f"Falling duration:     "
#     f"{asymmetric_cycle_fit.fall_years:.6f} years"
#     f" = "
#     f"{asymmetric_cycle_fit.fall_years * 365.25:.6f} days"
# )

# print(
#     f"Cycle days:           "
#     f"{model.cycle_days:.6f} days"
# )

# print(
#     f"Phase shift:          "
#     f"{asymmetric_cycle_fit.phase_shift:.6f} radians"
# )

# print(
#     f"RMSE:                 "
#     f"{rmse:.6f}"
# )

# print(
#     f"R-squared:            "
#     f"{r_squared:.6f}"
# )

# print(
#     "\nResidual model:\n"
#     "r(x) = "
#     f"{asymmetric_cycle_fit.amplitude:.6f} "
#     "s_u("
#     f"{asymmetric_cycle_fit.angular_frequency:.6f}x "
#     f"{asymmetric_cycle_fit.phase_shift:+.6f}"
#     ") / "
#     f"x^{asymmetric_cycle_fit.decay_exponent:.6f}, "
#     f"u = {asymmetric_cycle_fit.rise_fraction:.6f}"
# )

# print(
#     "\nUpper envelope:\n"
#     "U(x) = "
#     f"{asymmetric_cycle_fit.amplitude:.6f}"
#     " / "
#     f"x^{asymmetric_cycle_fit.decay_exponent:.6f}"
# )

# print(
#     "\nLower envelope:\n"
#     "L(x) = -"
#     f"{asymmetric_cycle_fit.amplitude:.6f}"
#     " / "
#     f"x^{asymmetric_cycle_fit.decay_exponent:.6f}"
# )


# --------------------------------------------------
# Warn when fitted values approach search boundaries
# --------------------------------------------------


def is_near_bound(
    value: float,
    bounds: tuple[
        float,
        float,
    ],
    *,
    fraction: float = 0.01,
) -> bool:
    """Return whether a value is close to either bound."""
    lower_bound, upper_bound = bounds

    tolerance = fraction * (upper_bound - lower_bound)

    return value <= lower_bound + tolerance or value >= upper_bound - tolerance


if is_near_bound(
    asymmetric_cycle_fit.decay_exponent,
    DECAY_BOUNDS,
):
    print("\nWarning: decay_exponent is near a DECAY_BOUNDS boundary.")


if is_near_bound(
    asymmetric_cycle_fit.rise_fraction,
    RISE_FRACTION_BOUNDS,
):
    print("\nWarning: rise_fraction is near a RISE_FRACTION_BOUNDS boundary.")

## Predict price


def predict_price(
    date: str | pd.Timestamp,
    power_law_model: LogLogPowerLawFit = power_law_fit,
    residual_model: AsymmetricCycleResidualFit = asymmetric_cycle_fit,
) -> float:
    """
    Predict the Bitcoin price using the power-law median
    and the damped sin log-residual model.

    The combined model is:

        predicted_price
            = median_price * exp(predicted_log_residual)
    """
    median_price = predict_median_price(
        power_law_model,
        date,
    )

    predicted_price = (
        median_price
        # * np.exp(predicted_log_residual) # Cyclic model needs work
    )

    return float(predicted_price)


## Main (test)


def main() -> None:
    """For testing price prediction"""
    date = pd.to_datetime(input("Date: "), utc=True)
    print(f"${predict_price(date):,.2f}")


if __name__ == "__main__":
    main()
