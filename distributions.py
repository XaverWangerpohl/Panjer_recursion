
import math as m


class Distribution:
    """ Interface class of a Distribution"""

    def __init__(self, type: str, value1: float, value2: float, trunc = False):

        """looks for the distribution type"""
        if type == "B":
            X = Bin(value1, value2,trunc)
        elif type == "NB":
            X = Nbin(value1, value2,trunc)
        elif type == "P":
            X = P(value1, None,trunc)
        elif type == "LOG":
            X = Logd(value1, None)
        elif type == "GEO":
            X = Geo(value1, value2)
        self._Dist = X
        self._type = X._type
        self._value1 = X._value1
        self._value2 = X._value2
        self._ex_Value = X._ex_Value
        self._variance = X._variance
        self._a = X._a
        self._b = X._b
        self._pan = X._pan
        self._trunc = X._trunc


    def prob(self, k: int):
        return self._Dist.prob(k)

    def pgf(self, t: float):
        """returns m_X(t)"""
        return self._Dist.pgf(t)


class Bin:
    """ Represents a binomial distribution """
    _type: str
    _value1: int
    _value2: float
    _ex_Value: float
    _variance: float
    _a: float
    _b: float
    _pan: int
    _trunc: int

    def __init__(self, n,p, trunc = False):
        self._type = "B"
        self._value1 = int(n)
        self._value2 = p
        self._ex_Value = n * p
        self._variance = n * p * (1 - p)
        self._a = -p / (1 - p)
        self._b = p*(n+1) / (1 - p)
        self._pan = 0
        self._trunc = int(trunc)
        if trunc:
            self._pan = 1

    def prob(self, k: int):
        """returns P(X=n)"""
        x=ext_binom(self._value1, k) * self._value2 ** k * (1 - self._value2) ** (self._value1 - k)
        """1st truncation:"""
        if self._pan==1:
            if k==0:
                return 0
            x=x/(1- (1 - self._value2) ** (self._value1))
        return x

    def pgf(self, t: float):
        """returns m_X(t)"""
        x = (1 - self._value2 + self._value2 * t) ** self._value1
        return x


class Nbin:
    """ Represents a  negative binomial distribution """
    _type: str
    _value1: float
    _value2: float
    _ex_Value: float
    _variance: float
    _a: float
    _b: float
    _pan: int
    _trunc: int

    def __init__(self, beta, p, trunc = False):
        self._type = "NB"
        self._value1 = beta
        self._value2 = p
        self._ex_Value = beta * p / (1 - p)
        self._variance = beta * p / (1 - p) ** 2
        self._a = (beta - 1) * p
        self._b = p
        self._pan = 0
        self._trunc = int(trunc)
        if trunc:
            self._pan = 1

    def prob(self, k: int):
        """returns P(X=n)"""
        x=ext_binom(self._value1 + k - 1, k) * self._value2 ** k * (1 - self._value2) ** self._value1
        """1st truncation:"""
        if self._pan==1:
            if k==0:
                return 0
            x =x /(1-(1 - self._value2) ** self._value1)
        return x

    def pgf(self, t: float):
        """returns m_X(t)"""
        x = ((1 - self._value2 * t) / (1 - self._value2)) ** -self._value1
        return x


class P:
    """ Represents a  Poisson distribution """
    _type: str
    _value1: float
    _value2: None
    _ex_Value: float
    _variance: float
    _a: float
    _b: float
    _pan: int
    _trunc: int

    def __init__(self, alpha, value2=None, trunc = False):
        self._type = "P"
        self._value1 = alpha
        self._value2 = value2
        self._ex_Value = alpha
        self._variance = alpha
        self._a = 0
        self._b = alpha
        self._pan = 0
        self._trunc = int(trunc)
        if trunc:
            self._pan = 1

    def prob(self, k):
        """returns P(X=n)"""
        x =m.exp(-self._value1) * self._value1 ** k / m.factorial(k)
        """1st truncation:"""
        if self._pan == 1:
            if k == 0:
                return 0
            x = x / (1 -m.exp(-self._value1))
        return x

    def pgf(self, t: float):
        """returns m_X(t)"""
        x= m.exp(-self._value1 * (1 - t))
        return x


class Logd:
    """ Represents a logarithmic distribution """
    _type: str
    _value1: float
    _value2: None
    _ex_Value: float
    _variance: float
    _a: float
    _b: float
    _pan: int
    _trunc: int

    def __init__(self, p, value2=None):
        self._type = "LOG"
        self._value1 = p
        self._value2 = value2
        self._ex_Value = -1 * m.log(1 - p) * p / (1 - p)
        self._variance = (-m.log(1 - p) - p) / (m.log(1 - p)) ** 2 * p / (1 - p) ** 2
        self._a = p
        self._b = -p
        self._pan = 1
        self._trunc = 0


    def prob(self, k: int):
        """returns P(X=n)"""
        if k == 0:
            return 0
        return -1 / m.log(1 - self._value1) * self._value1 ** k / k

    def pgf(self, t: float):
        """returns m_X(t)"""
        return m.log(1 - self._value1 * t) / m.log(1 - self._value1)


class Geo:
    """ Represents a geometric distribution """
    _type: str
    _value1: int
    _value2: float
    _ex_Value: float
    _variance: float
    _a: float
    _b: float
    _pan: int
    _trunc: int

    def __init__(self, n, p):
        self._type = "GEO"
        self._value1 = n
        self._value2 = p
        self._ex_Value = n / p
        self._variance = n * (1 - p) / p ** 2
        self._a = None
        self._b = None
        self._trunc = 0
        self._pan = 1


    def prob(self, k):
        """returns P(X=n)"""
        if k == 0:
            return 0
        return ext_binom(k - 1, self._value1 - 1) * self._value2 ** self._value1 * ((1 - self._value2) ** (
                k - self._value1))

    def pgf(self, t: float):
        """returns m_X(t)"""

        x = ((self._value2 * t) / (1 - (1 - self._value2) * t)) ** self._value1

        return x


def ext_binom(n: float, k: int):
    """ calculates real valued binomial coefficient"""
    res = 1
    for i in range(1, k+1):
        res *= (n+1-i)/i
    return res
