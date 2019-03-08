from abc import ABC, abstractmethod
import numpy as np


def ceil(x):
    """ceil an input and return as an integer"""
    return int(np.ceil(x))


class PrimeGenerator:
    def __init__(self, n):
        """
        generator of prime numbers less than n
        :param n: ceil for prime list (excluded)
        """
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
        """fetch a list of prime numbers under self.n"""
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
        """
        validate the statement for n = 1, 2, ..., (n_runs - 1), returns True is all runs pass
        :param n_runs: number of run
        :param verbose: verbosity (level) to be passed to self.argument()
        :return: bool, truth of all statement
        """
        for run in range(n_runs):
            if self.statement(self.__class__.map_run_id(run), verbose=verbose):
                if verbose and (run + 1) % 5 == 0 or run == n_runs - 1:
                    print()
            else:
                return False

        return True

    @abstractmethod
    def statement(self, k, verbose=True) -> bool:
        """
        a statement that is either True or False for some certain k
        :param k: primary argument of the statement
        :param verbose: verbosity (level)
        :return: bool, truth of the statement
        """
        return True


class GoldbachValidator(Validator):
    @staticmethod
    def map_run_id(run_id):
        """map run_id to the primary argument of the statement"""
        return run_id * 2 + 6

    def statement(self, k, verbose=True):
        """
        statement that an even number k can be written as p1 + p2 where p1 and p2 are prime numbers
        :param verbose: print the primes found
        :return: bool, value of the statement
        """
        primes = PrimeGenerator(k + 1).primes

        for p in primes:
            if (k - p) in primes:
                if verbose:
                    print("{} = {} + {}".format(k, p, k - p), end="\t\t")
                return True

        if verbose:
            print("{} cannot be written as the sum of two primes".format(k))
        return False


if __name__ == '__main__':
    success = GoldbachValidator().validate(n_runs=48)
    if success:
        print("Goldbach Conjecture Validated")
    else:
        print("Goldbach Conjecture Disproved")
