import numpy as np


def as_is(x):
    return x


def MHz(f):
    return f * 1e-6


def pF(C):
    return C * 1e12


def kOhm(R):
    return R * 1e-3


def dB(x):
    return 20 * np.log10(x)


def mV(U):
    return U * 1e3


def per_MHz(x):
    return x * 1e6


def kHz(f):
    return f * 1e-3


def uH(L):
    return L * 1e6
