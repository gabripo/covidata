# -*- coding: utf-8 -*-
"""
Test of execution for SIR library
"""

import numpy as np
import lib_sir_model as sir

t = np.linspace(0, 199, 101)

jp = sir.SIRmodel(1, 0.00002856, 0.29819303)

jpres = jp.simulate(t, [15e3, 1, 0])
jp.set_name("Japan")

fig_jp = jp.plotres()

#fig_jp.savefig("fig_jp.png")