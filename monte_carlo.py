import numpy as np
from abc import ABC, abstractmethod
from copy import deepcopy


class Interval:
    def __init__(self, a, b):
        """
        An interval of the form [a, b)
        endpoints a and b are automatically swapped if b <= a to ensure correctness
        :param a: either of the endpoints of the interval
        :param b: the other endpoint of the interval
        """
        if a < b:
            self.lower, self.upper = a, b
        else:
            self.upper, self.lower = b, a

    def __contains__(self, x):
        """
        determine whether a number lies within the interval [lower, upper)
        :param x: int, float or any other form that supports ordinal comparison with built-in python numbers
        :return: bool
        """
        return self.lower <= x < self.upper

    def __eq__(self, other):
        """
        determin whether two intervals are the same
        :param other: an other interval used for comparison
        :return: bool
        """
        return (self.lower == other.lower) and (self.upper == other.upper)

    def __repr__(self):
        """
        internal string representation of the instance
        """
        return "<{}: lower={}, upper={}>".format(self.__class__.__name__, self.lower, self.upper)

    def __str__(self):
        """
        printable string representation of the instance
        """
        return "[{}, {})".format(self.lower, self.upper)

    @property
    def bounds(self):
        """
        fetches the lower bound and upper bound as a tuple
        """
        return self.lower, self.upper

    @property
    def measure(self):
        """
        fetches the length of the interval
        """
        return self.upper - self.lower

    @staticmethod
    def parse(interval):
        """
        parse the input into a standard `Interval` instance
        :param interval: tuple, list or Interval
        :return: Interval
        """
        if isinstance(interval, (list, tuple)):
            return Interval(*interval)
        elif isinstance(interval, Interval):
            return deepcopy(interval)
        else:
            raise TypeError("interval unrecognized")

    def discretize(self, num=10000):
        return np.linspace(self.lower, self.upper, num=num, endpoint=True)

    def split_at(self, number):
        """
        split this interval into two sub-intervals at given number
        None is returned in place of either sub-interval if empty
        :param number: number by which this interval is splitted
        :return: tuple of Intervals or tuple of None and Interval
        """
        if number in self:
            return Interval(self.lower, number), Interval(number, self.upper)
        elif number < self.lower:
            return None, deepcopy(self)
        else:
            return deepcopy(self), None


class BaseIntegrator(ABC):
    def __init__(self, f):
        """
        An integrator that computes integral of function f on any bounded interval
        :param f: a callable that represents a mapping f: R -> R
        """
        if not callable(f):
            raise TypeError("function not callable: {}".format(f))

        self.f = f

    @abstractmethod
    def compute_integral(self, domain):
        """
        compute the integral of self.f  on the given interval
        :param domain: Interval, tuple, or list; interval on which self.f is integrated
        :return: float; the integral of self.f on `domain`
        """
        raise NotImplementedError("method not implemented in {}".format(self.__class__))


class MonteCarloIntegrator(BaseIntegrator):
    def compute_integral(self, domain, n_tests=10000):
        """
        use Monte Carlo method to compute the integral of self.f  on the given interval
        :param domain: Interval, tuple, or list; interval on which self.f is integrated
        :param n_tests: int, number of tests to run respectively on positive and negative ranges
        :return: float, the integral of self.f on `domain`
        """
        domain = Interval.parse(domain)
        # trailing underscore in `range_` is meant to avoid shadowing the built-in `range` function
        range_ = self._get_range(domain)

        # since integral can take a negative value when f(x) < 0, we split the range at 0
        neg_range, pos_range = range_.split_at(0)

        pos_integral = 0. if pos_range is None else pos_range.lower * domain.measure
        pos_integral += self._monte_carlo_test(domain, pos_range, n_tests)

        neg_integral = 0. if neg_range is None else (-neg_range.upper) * domain.measure
        neg_integral += self._monte_carlo_test(domain, neg_range, n_tests)

        return pos_integral - neg_integral

    def _get_range(self, domain, n_steps=1000):
        """
        get the range of the self.f on `domain` on which self.f is assumed to be continuous
        :param domain: Interval, where the range is computed
        :param n_steps: number of steps used for discretization
        :return: Interval, representing the range of self.f on `domain`
        """
        # discretize domain and range for computability
        discrete_domain = domain.discretize(n_steps)
        discrete_range = self.f(discrete_domain)
        # HACK: assuming continuity of self.f
        return Interval(np.min(discrete_range), np.max(discrete_range))

    def _monte_carlo_test(self, x_interval, y_interval, n_tests=10000):
        """
        returns the area hit in a monte carlo test on given intervals
        :param x_interval: Interval or None (empty interval)
        :param y_interval: Interval or None (empty interval)
        :param n_tests: number of tests to run
        :return: estimation of the area
        """
        # if either of the intervals are empty, return 0 (as a float)
        if x_interval is None or y_interval is None:
            return 0.

        hits = 0
        for test in range(n_tests):
            x = np.random.uniform(*x_interval.bounds)
            y = np.random.uniform(*y_interval.bounds)
            if y in Interval(0, self.f(x)):
                hits += 1

        return hits / n_tests * x_interval.measure * y_interval.measure


class RiemannIntegrator(BaseIntegrator):
    def compute_integral(self, domain, n_steps=10000):
        discrete_domain = domain.discretize(n_steps)
        discrete_range = self.f(discrete_domain)
        return np.sum(discrete_range) * domain.measure / n_steps


if __name__ == '__main__':
    integrator = MonteCarloIntegrator(lambda x: np.power(x, 2) + 4 * x * np.sin(x))
    interval = Interval(2, 3)
    integral = integrator.compute_integral(interval, n_tests=10000)

    print("Integral on {} = {}".format(interval.bounds, integral))
