import numpy as np
from goldbach import PrimeGenerator


class Factorizer:
    def __init__(self, n):
        if n <= 0:
            raise ValueError("only positive integers can be passed")

        self.n = n
        self._primes = PrimeGenerator(n + 1).primes
        self._factor_count = {}

    def factorize(self):
        if self.n == 1:
            self._factor_count = {1: 1}
            return

        n = self.n  # avoid changing self.n during factorization
        for p in self._primes:
            while n % p == 0:
                self.gather_factor(p)
                n //= p

        assert self._factor_count, "no factor counted"

    def gather_factor(self, factor):
        if factor in self._factor_count:
            self._factor_count[factor] += 1
        else:
            self._factor_count[factor] = 1

    @property
    def factor_count(self):
        if not self._factor_count:
            self.factorize()
        return self._factor_count

    def __str__(self):
        factor_substring = " * ".join(str(f) for f in self.factor_count for _ in range(self.factor_count[f]))
        return "Factorization of {} = {}".format(self.n, factor_substring)

    def __repr__(self):
        return "Factor Count of {} = {}".format(self.n, self.factor_count)


if __name__ == '__main__':
    for i in range(1, 100):
        print(Factorizer(i))
