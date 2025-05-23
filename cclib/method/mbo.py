# Copyright (c) 2025, the cclib development team
#
# This file is part of cclib (http://cclib.github.io) and is distributed under
# the terms of the BSD 3-Clause License.

"""Calculation of Mayer's bond orders based on data parsed by cclib."""

import random

from cclib.method.density import Density

import numpy


class MBO(Density):
    """Mayer's bond orders"""

    def __init__(self, *args):
        super().__init__(logname="MBO", *args)

    def __str__(self):
        """Return a string representation of the object."""
        return f"Mayer's bond order of {self.data}"

    def __repr__(self):
        """Return a representation of the object."""
        return f'Mayer\'s bond order("{self.data}")'

    def calculate(self, indices=None, fupdate=0.05):
        """Calculate Mayer's bond orders."""

        retval = super().calculate(fupdate)
        if not retval:  # making density didn't work
            return False

        # Do we have the needed info in the ccData object?
        if not (hasattr(self.data, "aooverlaps") or hasattr(self.data, "fooverlaps")):
            self.logger.error("Missing overlap matrix")
            return False  # let the caller of function know we didn't finish

        if not indices:
            # Build list of groups of orbitals in each atom for atomresults.
            if hasattr(self.data, "aonames"):
                names = self.data.aonames
                overlaps = self.data.aooverlaps
            elif hasattr(self.data, "fonames"):
                names = self.data.fonames
                overlaps = self.data.fooverlaps
            else:
                self.logger.error("Missing aonames or fonames")
                return False

            atoms = []
            indices = []

            name = names[0].split("_")[0]
            atoms.append(name)
            indices.append([0])

            for i in range(1, len(names)):
                name = names[i].split("_")[0]
                try:
                    index = atoms.index(name)
                except ValueError:  # not found in atom list
                    atoms.append(name)
                    indices.append([i])
                else:
                    indices[index].append(i)

        self.logger.info("Creating attribute fragresults: array[3]")
        size = len(indices)

        # Determine number of steps, and whether process involves beta orbitals.
        PS = []
        PS.append(numpy.dot(self.density[0], overlaps))
        nstep = size**2  # approximately quadratic in size
        unrestricted = len(self.data.mocoeffs) == 2
        if unrestricted:
            self.fragresults = numpy.zeros([2, size, size], "d")
            PS.append(numpy.dot(self.density[1], overlaps))
        else:
            self.fragresults = numpy.zeros([1, size, size], "d")

        # Intialize progress if available.
        if self.progress:
            self.progress.initialize(nstep)

        step = 0
        for i in range(len(indices)):
            if self.progress and random.random() < fupdate:
                self.progress.update(step, "Mayer's Bond Order")

            for j in range(i + 1, len(indices)):
                tempsumA = 0
                tempsumB = 0

                for a in indices[i]:
                    for b in indices[j]:
                        if unrestricted:
                            tempsumA += 2 * PS[0][a][b] * PS[0][b][a]
                            tempsumB += 2 * PS[1][a][b] * PS[1][b][a]
                        else:
                            tempsumA += PS[0][a][b] * PS[0][b][a]

                self.fragresults[0][i, j] = tempsumA
                self.fragresults[0][j, i] = tempsumA

                if unrestricted:
                    self.fragresults[1][i, j] = tempsumB
                    self.fragresults[1][j, i] = tempsumB

        if self.progress:
            self.progress.update(nstep, "Done")

        return True
