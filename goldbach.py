from abc import ABC, abstractmethod
import numpy as np


def ceil(x):
    return int(np.ceil(x))


class PrimeGenerator:
    def __init__(self, n):
        self.n = n
        self._primes = None

    def generate_primes(self):
        self._primes = list(range(2, self.n))

        for i in range(2, self.n):
            for j in range(2, min(i, ceil(np.sqrt(i)) + 1)):
                if i % j == 0:
                    self._primes.pop(self._primes.index(i))
                    break

    @property
    def primes(self):
        if self._primes is None:
            self.generate_primes()
        return self._primes


class Validator(ABC):
    def __init__(self):
        pass

    @staticmethod
    def map_run_id(run_id):
        """map run_id to the primary argument of the statement"""
        return run_id

    def validate(self, n_runs, verbose=True):
        for run in range(n_runs):
            if not self.argument(run, verbose=verbose):
                return False

        return True

    @abstractmethod
    def argument(self, run_id, verbose=True) -> bool:
        return True


class GoldbachValidator(Validator):
    @staticmethod
    def map_run_id(run_id):
        """map run_id to the primary argument of the statement"""
        return run_id * 2 + 6

    def argument(self, run_id, verbose=True):
        n = self.map_run_id(run_id)
        primes = PrimeGenerator(n + 1).primes

        for p in primes:
            if (n - p) in primes:
                if verbose:
                    print("{} = {} + {}".format(n, p, n - p), end="\n" if (run_id + 1) % 5 == 0 else " ")
                return True

        if verbose:
            print("{} cannot be divided as the sum of two primes".format(n))
        return False


if __name__ == '__main__':
    success = GoldbachValidator().validate(50)
    if success:
        print("Argument validated")
    else:
        print("Argument disproved")
