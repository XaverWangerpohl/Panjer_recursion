from distributions import Distribution


class Insurance:
    """This class models an insurance following a collective model and is a framework for calculating properties of
    the total damage claim distribution"""
    _N: Distribution
    _X: Distribution
    """expected value of S"""
    _ex_value: float
    """variance of S"""
    _variance: float
    _g: list

    def __init__(self, n_o_c: Distribution, a_p_c: Distribution):
        self._N = n_o_c
        self._X = a_p_c
        """compare Wald's equations"""
        self._ex_value = n_o_c.get_ex_value() * a_p_c.get_ex_value()
        self._variance = n_o_c.get_ex_value() * a_p_c.get_variance() + n_o_c.get_variance() * a_p_c.get_ex_value() ** 2
        self._g = [self._N.get_pgf(self._X.get_prob(0))]
        if self._N.get_pan() == 1:
            self._g[0] = 0
            self._g.append(self._N.get_prob(1) * self._X.get_prob(1))

    def __str__(self):
        t = ""
        b = ""
        if self._N.get_trunc() == 1:
            t = "tr"
        if self._X.get_trunc() == 1:
            b = "tr"
        if self._N.get_value2() is None:
            n = self._N.get_typ() + "(" + str(self._N.get_value1()) + ")"
        else:
            n = self._N.get_typ() + "(" + str(self._N.get_value1()) + "," + str(self._N.get_value2()) + ")"

        if self._X.get_value2() is None:
            x = self._X.get_typ() + "(" + str(self._X.get_value1()) + ")"
        else:
            x = self._X.get_typ() + "(" + str(self._X.get_value1()) + "," + str(self._X.get_value2()) + ")"
        return n + t + x + b

    def get_premium(self, p: float):
        """returns the minimal income of the insurance to achieve a probability of ruin less than p"""
        prob_sum = self._g[0]
        i = 0
        while prob_sum <= (1 - p):
            i += 1
            prob_sum += self.get_prob_s(i)
        return i

    def get_prob_s(self, k: int):
        """returns P(S=k)"""
        n = len(self._g)
        """cheks if the probability has already been calculated"""
        if n - 1 >= k:
            return self._g[k]
        """panjer recursion"""
        while n <= k:
            """case N in Pan(0)"""
            if self._N.get_pan() == 0:
                self._g.append(self.helpsum(n) / (1 - self._N.get_a() * self._X.get_prob(0)))
            else:
                """case N in Pan(1)"""
                self._g.append(
                    (self.helpsum(n) + self._N.get_prob(1) * self._X.get_prob(n)) / (1 - self._N.get_a() * self._X.get_prob(0)))
            n = n + 1

        return self._g[k]
    """getter metods"""
    def get_ex_value(self):
        return self._ex_value

    def get_variance(self):
        return self._variance

    def get_cantelli_prob(self, c: float):
        """ returns Cantelli Inequation for P(S<=E(S)+c)"""
        return self._variance / (c ** 2 + self._variance)

    def get_cantelli_premium(self, p: float):
        """returns the minimal premium, such that the probability
        of ruin is smaller than p by cantelli's inequality  """
        """solve cantelli inequality for c"""
        c = ((self._variance/p)-self._variance)**(1/2)
        return self._ex_value+c

    """for the calculation of prob_S"""

    def helpsum(self, n: int):
        r = 0
        for k in range(1, n + 1):
            r += (self._N.get_a() + self._N.get_b() * k / n) * self._g[n - k] * self._X.get_prob(k)
        return r
