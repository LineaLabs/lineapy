"""
Utilities for computing statistics on benchmark data.

Translated from https://github.com/jupyterlab/jupyterlab/blob/82df0b635dae2c1a70a7c41fe7ee7af1c1caefb2/galata/src/benchmarkReporter.ts#L150-L244
which was originally added in https://github.com/jupyterlab/benchmarks/blob/f55db969bf4d988f9d627ba187e28823a50153ba/src/compare.ts#L136-L213
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import mean, variance
from typing import List

__all__ = ["distribution_change"]


@dataclass
class DistributionChange:
    """
    Change between two distributions
    """

    # Mean value
    mean: float
    # Spread around the mean value
    confidence_interval: float
    # The confidence interval level, i.e. 0.95 for a 95% confidence interval
    confidence_interval_level: float

    def __str__(self):
        """
        Format a performance changes like `between 20.1% slower and 30.3% faster (95% CI)`.
        """
        return (
            f"between {format_percent(self.mean + self.confidence_interval)} "
            f"and {format_percent(self.mean - self.confidence_interval)} "
            f"({self.confidence_interval_level * 100}% CI)"
        )


@dataclass
class Distribution:
    """
    Statistical description of a distribution
    """

    mean: float
    variance: float

    @classmethod
    def from_data(cls, data: List[float]) -> Distribution:
        return cls(mean(data), variance(data))


def performance_change(
    old_distribution: Distribution,
    new_distribution: Distribution,
    n: float,
    confidence_interval: float,
) -> DistributionChange:
    import scipy.stats

    """
    Quantifies the performance changes between two measures systems. Assumes we gathered
    n independent measurement from each, and calculated their means and variance.

    Based on the work by Tomas Kalibera and Richard Jones. See their paper
    "Quantifying Performance Changes with Effect Size Confidence Intervals", section 6.2,
    formula "Quantifying Performance Change".

    However, it simplifies it to only assume one level of benchmarks, not multiple levels.
    If you do have multiple levels, simply use the mean of the lower levels as your data,
    like they do in the paper.

    :param old_distribution: The old distribution
    :param new_distribuation: The new distribution
    :param n:  The number of samples from each system (must be equal)
    :param confidence_interval:  The confidence interval for the results.
    """
    yO, sO = old_distribution.mean, old_distribution.variance
    yN, sN = new_distribution.mean, new_distribution.variance
    dof = n - 1
    alpha = 1 - confidence_interval
    t = scipy.stats.t.ppf(alpha / 2, dof)
    old_factor = square(yO) - (square(t) * sO) / n
    new_factor = square(yN) - (square(t) * sN) / n
    mean_num = yO * yN
    ci_num = sqrt(square(yO * yN) - new_factor * old_factor)
    return DistributionChange(
        mean=mean_num / old_factor,
        confidence_interval=ci_num / old_factor,
        confidence_interval_level=confidence_interval,
    )


def distribution_change(
    old_measures: List[float],
    new_measures: List[float],
    confidence_interval: float = 0.95,
) -> DistributionChange:
    """
    Compute the performance change based on a number of old and new measurements.

    Based on the work by Tomas Kalibera and Richard Jones. See their paper
    "Quantifying Performance Changes with Effect Size Confidence Intervals", section 6.2,
    formula "Quantifying Performance Change".

    Note: The measurements must have the same length. As fallback, you could use the minimum
    size of the two measurement sets.

    :param old_measures: The list of timings from the old system
    :param new_measures: The list of timings from the new system
    :param confidence_interval:  The confidence interval for the results.
        The default is a 95% confidence interval (95% of the time the true mean will be
        between the resulting mean +- the resulting CI)

    # Test against the example in the paper, from Table V, on pages 18-19

    >>> res = distribution_change(
    ...     old_measures=[
    ...         round(mean([9, 11, 5, 6]), 1),
    ...         round(mean([16, 13, 12, 8]), 1),
    ...         round(mean([15, 7, 10, 14]), 1),
    ...     ],
    ...     new_measures=[
    ...         round(mean([10, 12, 6, 7]), 1),
    ...         round(mean([9, 1, 11, 4]), 1),
    ...         round(mean([8, 5, 3, 2]), 1),
    ...     ],
    ...     confidence_interval=0.95
    ... )
    >>> from math import isclose
    >>> assert isclose(res.mean, 68.3 / 74.5, rel_tol=0.05)
    >>> assert isclose(res.confidence_interval, 60.2 / 74.5, rel_tol=0.05)
    """
    n = len(old_measures)
    if n != len(new_measures):
        raise ValueError("Data have different length")
    return performance_change(
        Distribution.from_data(old_measures),
        Distribution.from_data(new_measures),
        n,
        confidence_interval,
    )


def format_percent(percent: float) -> str:
    if percent < 1:
        return f"{((1 - percent) * 100):.1f}% faster"

    return f"{((percent - 1) * 100):.1f}% slower"


def square(x: float) -> float:
    return x**2
