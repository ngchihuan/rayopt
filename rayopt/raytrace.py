# -*- coding: utf8 -*-
#
#   pyrayopt - raytracing for optical imaging systems
#   Copyright (C) 2012 Robert Jordens <jordens@phys.ethz.ch>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function, absolute_import, division

import numpy as np

from .utils import public


@public
class Trace(object):
    def __init__(self, system):
        self.system = system

    def allocate(self):
        self.length = len(self.system)

    def propagate(self):
        self.z = self.system.track
        self.origins = self.system.origins
        self.mirrored = self.system.mirrored

    def from_axis(self, y, i=None, ref=0):
        y = np.atleast_3d(y) # zi, rayi, xyz
        if i is None:
            i = np.searchsorted(y[:, ref, 2], self.z)
        ys = []
        for j, yi in enumerate(np.vsplit(y, i)):
            if yi.ndim <= 1:
                continue
            j = min(self.length - 1, j)
            zi, ei, oi = self.z[j], self.system[j], self.origins[j]
            yj = yi.reshape(-1, 3)
            yj = oi + ei.from_axis(yj - (0, 0, zi))
            ys.append(yj.reshape(yi.shape))
        ys = np.vstack(ys)
        return ys

    def print_coeffs(self, coeff, labels, sum=True):
        yield (u"%2s %1s" + u"% 10s" * len(labels)) % (
                (u"#", u"T") + tuple(labels))
        fmt = u"%2s %1s" + u"% 10.4g" * len(labels)
        for i, a in enumerate(coeff):
            yield fmt % ((i, self.system[i].type) + tuple(a))
        if sum:
            yield fmt % ((u" ∑", u"") + tuple(coeff.sum(0)))

    def align(self):
        self.system.align(self.n)
        self.propagate()
