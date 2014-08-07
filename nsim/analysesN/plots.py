# Copyright 2014 Matthew J. Aburn
# 
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See <http://www.gnu.org/licenses/>.

"""
Various plotting routines for a multiple simulation

(This interface will be changed after the distributed array class 
 is implemented)
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import numbers


def plot(multiple_sim, title=None):
    """Plot results of a multiple simulation, such as RepeatedSim or NetworkSim
    """
    ylabelprops = dict(rotation=0,
                       horizontalalignment='right',
                       verticalalignment='center',
                       x=-0.01)
    if title is None:
        title=u'output at each node'
    fig = plt.figure()
    n = len(multiple_sim)
    for i in range(n):
        ax = fig.add_subplot(n, 1, i+1)
        ts = multiple_sim[i].output
        ax.plot(ts.tspan, ts)
        ax.set_ylabel('node ' + str(i), **ylabelprops)
        plt.setp(ax.get_xticklabels(), visible=False)
    fig.axes[0].set_title(title)
    plt.setp(fig.axes[n-1].get_xticklabels(), visible=True)
    fig.axes[n-1].set_xlabel('time (s)')
    fig.show()
    return fig


def phase_histogram(msim, times, nbins=30, colormap=mpl.cm.Blues):
    """Plot a polar histogram of a phase variable's probability distribution
    Args:
      msim: MultipleSimulation (assumes that msim.output is an angle variable)
      times (float or sequence of floats): The target times at which 
        to plot the distribution
      nbins (int): number of histogram bins
      colormap
    """
    snaps = msim.snapshots(0.0, msim.periods().mean()).mod2pi()
    if isinstance(times, numbers.Number):
        times = np.array([times], dtype=np.float64)
    indices = snaps.tspan.searchsorted(times)
    if indices[-1] == len(snaps.tspan):
        indices[-1] -= 1
    nplots = len(indices)
    fig = plt.figure()
    n = np.zeros((nbins, nplots))
    for i in xrange(nplots):
        index = indices[i]
        time = snaps.tspan[index]
        phases = snaps[index, 0, :]
        ax = fig.add_subplot(1, nplots, i + 1, projection='polar')
        n[:,i], bins, patches = ax.hist(phases, nbins, (-np.pi, np.pi), 
                                        normed=True, histtype='bar')
        ax.set_title('time = %d s' % time)
        ax.set_xticklabels(['0', r'$\frac{\pi}{4}$', r'$\frac{\pi}{2}$', 
                            r'$\frac{3\pi}{4}$', r'$\pi$', r'$\frac{-3\pi}{4}$',
                            r'$\frac{-\pi}{2}$', r'$\frac{-\pi}{4}$'])
    nmin, nmax = n.min(), n.max()
    #TODO should make a custom colormap instead of reducing color dynamic range:
    norm = mpl.colors.Normalize(1.2*nmin - 0.2*nmax, 
                                0.6*nmin + 0.4*nmax, clip=True)
    for i in xrange(nplots):
        ax = fig.get_axes()[i]
        ax.set_ylim(0, nmax)
        for this_n, thispatch in zip(n[:,i], ax.patches):
            color = colormap(norm(this_n))
            thispatch.set_facecolor(color)
            thispatch.set_edgecolor(color)
    fig.show()
