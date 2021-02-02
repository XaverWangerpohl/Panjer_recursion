from distributions import Distribution

class Insurance:
    """This class models an insurance following a collective model and is a framework for calculating properties of
    the total damage claim distribution"""
    _N:Distribution
    _X:Distribution
    """expected value of S"""
    _ex_Value:float
    """variance of S"""
    _variance:float
    g:list


    def __init__(self,n_o_c:Distribution,a_p_c:Distribution):
        self._N = n_o_c
        self._X = a_p_c
        """compare Wald's equations"""
        self._ex_Value = n_o_c._ex_Value*a_p_c._ex_Value
        self._variance = n_o_c._ex_Value*a_p_c._variance+n_o_c._variance*a_p_c._ex_Value ** 2
        self.g = [self._N.pgf(self._X.prob(0))]
        if self._N._pan == 1 :
            self.g[0] = 0
            self.g.append(self._N.prob(1)*self._X.prob(1))

    def __str__(self):
        T=""
        B =""
        if self._N._trunc ==1:
            T="tr"
        if self._X._trunc == 1:
            B="tr"
        if self._N._value2 == None:
            N = self._N._type+"("+str(self._N._value1)+")"
        else:
            N = self._N._type+"("+str(self._N._value1)+","+str(self._N._value2)+")"

        if self._X._value2 == None:
            X = self._X._type+"("+str(self._X._value1)+")"
        else:
            X = self._X._type+"("+str(self._X._value1)+","+str(self._X._value2)+")"
        return N+T+X+B

    def ruin(self,p: float):
        """returns the minimal income of the insurance to achieve a probability of ruin less than p"""
        G = self.g[0]
        i = 0
        while G <= (1-p):
            i += 1
            G += self.prob_S(i)
        return i


    def prob_S(self, k:int):
        """returns P(S=k)"""
        n = len(self.g)
        if n-1 >=k:
            return self.g[k]
        while n<=k:
            if self._N._pan == 0:
                self.g.append(self.helpsum(n)/(1-self._N._a*self._X.prob(0)))
            else:
                self.g.append((self.helpsum(n)+self._N.prob(1)*self._X.prob(n)) / (1 - self._N._a * self._X.prob(0)))
            n = n+1

        return self.g[k]

    def cantelli(self,c:float):
        """ returns Cantelli Inequation for P(S<=E(S)+c)"""
        return self._variance/(c**2 + self._variance)


    """for the calculation of prob_S"""
    def helpsum(self, n:int):
        r = 0
        for k in range(1,n+1):
            r += (self._N._a + self._N._b*k/n)*self.g[n-k]*self._X.prob(k)
        return r

