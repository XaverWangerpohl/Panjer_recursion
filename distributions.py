import math as m


class Distribution:
    """ Interface class of a Distribution"""
    _type: str
    _value1: int
    _value2: float
    _ex_value: float
    _variance: float
    _a: float
    _b: float
    _pan: int
    _trunc: int
    def __init__(self, typ: str, value1: float, value2: float, trunc: int):

        """looks for the distribution type"""
        if typ == "B":
            dist = Bin(value1, value2, trunc)
        elif typ == "NB":
            dist = NBin(value1, value2, trunc)
        elif typ == "P":
            dist = P(value1, trunc)
        elif typ == "LOG":
            dist = Log(value1, trunc)
        elif typ == "ENB":
            dist = ENB(value1, value2, trunc)
        """set the attributes accordingly"""
        self._dist = dist
        self._typ = dist.typ
        self._value1 = dist.value1
        self._value2 = dist.value2
        self._ex_value = dist.ex_value
        self._variance = dist.variance
        self._a = dist.a
        self._b = dist.b
        self._pan = dist.pan
        self._trunc = dist.trunc
    """getter methods for the attributes and methods"""

    def get_typ(self):
        return self._typ

    def get_value1(self):
        return self._value1

    def get_value2(self):
        return self._value2

    def get_ex_value(self):
        return self._ex_value

    def get_variance(self):
        return self._variance

    def get_a(self):
        return self._a

    def get_b(self):
        return self._b

    def get_pan(self):
        return self._pan

    def get_trunc(self):
        return self._trunc

    def get_prob(self, k: int):
        return self._dist.prob(k)

    def get_pgf(self, t: float):
        """returns m_X(t)"""
        return self._dist.pgf(t)


class TruncHelper:
    """This class provides the framework for distributions to be truncated."""
    trunc_sums: list
    probabilities: list
    trunc: int

    def __init__(self, typ: str, value1: float, value2: float, trunc: int):
        d = Distribution(typ=typ, value1=value1, value2=value2, trunc=0)
        """_probabilities saves the probabilities of the non truncated distribution up until trunc-1"""
        self.probabilities = []
        for i in range(trunc):
            self.probabilities.append(d.get_prob(i))
        """"_trunc sums saves the values of the sums returned by set_trunc_sums"""
        self.trunc_sums = set_trunc_sums(trunc, d)
        self.trunc = trunc

    def set_ex_v_var(self, ex_value: float, variance: float):
        """returns expected value and variance of the truncated distribution
        with the formulas of the thesis((2.8)and(2.9))"""
        new_ex_value = (ex_value - self.trunc_sums[1]) / (1 - self.trunc_sums[0])
        new_variance = (variance + (ex_value ** 2) - self.trunc_sums[2]) / (1 - self.trunc_sums[0]) - new_ex_value ** 2
        return [new_ex_value, new_variance]

    def set_prob(self, x: float, k: int):
        """returns P(Xtrunc=k) of the truncated random variable, where x = P(X=k) """
        if self.trunc > k:
            return 0
        return x / (1 - self.trunc_sums[0])

    def set_pgf(self, x: float, t: float):
        """analogous to set_prob but with the pgf"""
        tr_sum = 0
        for i in range(len(self.probabilities)):
            tr_sum += self.probabilities[i] * t ** i

        return (x - tr_sum) / (1 - self.trunc_sums[0])


"""The possible distributions are implemented here"""


class Bin:
    """ Represents a binomial distribution """
    typ: str
    value1: int
    value2: float
    ex_value: float
    variance: float
    a: float
    b: float
    pan: int
    trunc: int
    tr_help: TruncHelper

    def __init__(self, n, p, trunc):
        self.typ = "B"
        self.value1 = int(n)
        self.value2 = p
        self.ex_value = n * p
        self.variance = n * p * (1 - p)
        self.a = -p / (1 - p)
        self.b = p * (n + 1) / (1 - p)
        self.pan = trunc
        self.trunc = trunc
        """change expected value and variance, if the distribution is truncated"""
        if trunc != 0:
            self.tr_help = TruncHelper(typ=self.typ, value1=self.value1, value2=self.value2, trunc=trunc)
            """set new expected value and variance"""
            ex_val_and_v = self.tr_help.set_ex_v_var(ex_value=self.ex_value, variance=self.variance)
            self.ex_value = ex_val_and_v[0]
            self.variance = ex_val_and_v[1]

    def prob(self, k: int):
        """returns P(X=n)"""
        x = ext_binom(self.value1, k) * self.value2 ** k * (1 - self.value2) ** (self.value1 - k)
        """truncation:"""
        if self.trunc != 0:
            x = self.tr_help.set_prob(x, k)
        return x

    def pgf(self, t: float):
        """returns m_X(t)"""
        x = (1 - self.value2 + self.value2 * t) ** self.value1
        """truncation:"""
        if self.trunc != 0:
            x = self.tr_help.set_pgf(x, t)
        return x


class NBin:
    """ Represents a  negative binomial distribution """
    typ: str
    value1: float
    value2: float
    ex_value: float
    variance: float
    a: float
    b: float
    pan: int
    trunc: int
    tr_help: TruncHelper

    def __init__(self, beta, p, trunc):
        self.typ = "NB"
        self.value1 = beta
        self.value2 = p
        self.ex_value = beta * p / (1 - p)
        self.variance = beta * p / (1 - p) ** 2
        self.a = p
        self.b = (beta - 1) * p
        self.pan = trunc
        self.trunc = trunc
        """change expected value and variance, if the distribution is truncated"""
        if trunc != 0:
            self.tr_help = TruncHelper(typ=self.typ, value1=self.value1, value2=self.value2, trunc=trunc)
            """set new expected value and variance"""
            ex_val_and_v = self.tr_help.set_ex_v_var(ex_value=self.ex_value, variance=self.variance)
            self.ex_value = ex_val_and_v[0]
            self.variance = ex_val_and_v[1]

    def prob(self, k: int):
        """returns P(X=n)"""
        x = ext_binom(self.value1 + k - 1, k) * self.value2 ** k * (1 - self.value2) ** self.value1
        """truncation:"""
        if self.trunc != 0:
            x = self.tr_help.set_prob(x, k)
        return x

    def pgf(self, t: float):
        """returns m_X(t)"""
        x = ((1 - self.value2 * t) / (1 - self.value2)) ** -self.value1
        """truncation:"""
        if self.trunc != 0:
            x = self.tr_help.set_pgf(x, t)
        return x


class P:
    """ Represents a  Poisson distribution """
    typ: str
    value1: float
    value2: None
    ex_value: float
    variance: float
    a: float
    b: float
    pan: int
    trunc: int
    tr_help: TruncHelper

    def __init__(self, alpha, trunc):
        self.typ = "P"
        self.value1 = alpha
        self.value2 = None
        self.ex_value = alpha
        self.variance = alpha
        self.a = 0
        self.b = alpha
        self.pan = trunc
        self.trunc = trunc
        """change expected value and variance, if the distribution is truncated"""
        if trunc != 0:
            self.tr_help = TruncHelper(typ=self.typ, value1=self.value1, value2=self.value2, trunc=trunc)
            """set new expected value and variance"""
            ex_val_and_v = self.tr_help.set_ex_v_var(ex_value=self.ex_value, variance=self.variance)
            self.ex_value = ex_val_and_v[0]
            self.variance = ex_val_and_v[1]

    def prob(self, k: int):
        """returns P(X=n)"""
        x = m.exp(-self.value1) * self.value1 ** k / m.factorial(k)
        """truncation:"""
        if self.trunc != 0:
            x = self.tr_help.set_prob(x, k)
        return x

    def pgf(self, t: float):
        """returns m_X(t)"""
        x = m.exp(-self.value1 * (1 - t))
        """truncation:"""
        if self.trunc != 0:
            x = self.tr_help.set_pgf(x, t)
        return x


class Log:
    """ Represents a logarithmic distribution """
    typ: str
    value1: float
    value2: None
    ex_value: float
    variance: float
    a: float
    b: float
    pan: int
    trunc: int
    tr_help: TruncHelper

    def __init__(self, p, trunc):
        self.typ = "LOG"
        self.value1 = p
        self.value2 = None
        self.ex_value = -1 / m.log(1 - p) * p / (1 - p)
        self.variance = (-m.log(1 - p) - p) / ((m.log(1 - p)) ** 2) * p / (1 - p) ** 2
        self.a = p
        self.b = -p
        self.pan = max([1, trunc])
        self.trunc = trunc
        """change expected value and variance, if the distribution is truncated"""
        if trunc != 0:
            self.tr_help = TruncHelper(typ=self.typ, value1=self.value1, value2=self.value2, trunc=trunc)
            """set new expected value and variance"""
            ex_val_and_v = self.tr_help.set_ex_v_var(ex_value=self.ex_value, variance=self.variance)
            self.ex_value = ex_val_and_v[0]
            self.variance = ex_val_and_v[1]

    def prob(self, k: int):
        """returns P(X=n)"""
        if k == 0:
            return 0
        x = -1 / m.log(1 - self.value1) * self.value1 ** k / k
        """truncation:"""
        if self.trunc != 0:
            x = self.tr_help.set_prob(x, k)
        return x

    def pgf(self, t: float):
        """returns m_X(t)"""
        x = m.log(1 - self.value1 * t) / m.log(1 - self.value1)
        """truncation:"""
        if self.trunc != 0:
            x = self.tr_help.set_pgf(x, t)
        return x


class ENB:
    """ Represents a extended negative binomial distribution with n=1 """
    typ: str
    value1: int
    value2: float
    ex_value: float
    variance: float
    a: float
    b: float
    pan: int
    trunc: int
    tr_help: TruncHelper

    def __init__(self, beta, p, trunc):
        self.typ = "ENB"
        self.value1 = beta
        self.value2 = p
        """calculates the expected value and variance of the non truncated distribution"""
        self.ex_value = (beta * p * (1 - p) ** (-beta - 1)) / ((1 - p) ** (-beta) - 1)
        self.variance = (beta * (beta + 1) * p * p * (1 - p) ** (-beta - 2)) / (
                (1 - p) ** (-beta) - 1) + self.ex_value - self.ex_value ** 2
        self.a = p
        self.b = (beta - 1) * p
        self.trunc = trunc
        self.pan = max([1, trunc])
        """change expected value and variance, if the distribution is truncated"""
        if trunc != 0:
            self.tr_help = TruncHelper(typ=self.typ, value1=self.value1, value2=self.value2, trunc=trunc)
            """set new expected value and variance"""
            ex_val_and_v = self.tr_help.set_ex_v_var(ex_value=self.ex_value, variance=self.variance)
            self.ex_value = ex_val_and_v[0]
            self.variance = ex_val_and_v[1]

    def prob(self, k):
        """returns P(X=n)"""
        if k == 0:
            return 0
        x = ext_binom(self.value1 + k - 1, k) * self.value2 ** k / ((1 - self.value2) ** (-self.value1) - 1)
        """truncation:"""
        if self.trunc != 0:
            x = self.tr_help.set_prob(x, k)
        return x

    def pgf(self, t: float):
        """returns m_X(t)"""
        x = ((1 - self.value2 * t) ** (-self.value1) - 1) / ((1 - self.value2) ** (-self.value1) - 1)
        """truncation:"""
        if self.trunc != 0:
            x = self.tr_help.set_pgf(x, t)
        return x


def ext_binom(n: float, k: int):
    """ calculates real valued binomial coefficient"""
    res = 1
    for i in range(1, k + 1):
        res *= (n + 1 - i) / i
    return res


def set_trunc_sums(n: int, d: Distribution):
    """calculates the sums for truncation (probability, expected value and variance)
       n: n-truncation
       X: Distribution without truncation
    """
    res = [0, 0, 0]
    if n != 0:
        for i in range(n):
            res[0] += d.get_prob(i)
            res[1] += i * d.get_prob(i)
            res[2] += (i ** 2) * d.get_prob(i)
    return res
