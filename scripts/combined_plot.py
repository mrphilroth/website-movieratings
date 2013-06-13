import codecs
import numpy as np
import pylab as plt
import pandas as pd
import matplotlib as mpl
from scipy import optimize

# Use an inner merge to keep only movies where both sites returned a score
mfn = "../data/metacritic_scores.csv"
rfn = "../data/rottentomatoes_scores.csv"
mdf = pd.io.parsers.read_csv(codecs.open(mfn, 'r', 'utf-8', 'replace'))
rdf = pd.io.parsers.read_csv(codecs.open(rfn, 'r', 'utf-8', 'replace'))
df = pd.merge(mdf, rdf, how='inner')

# 2D histogram with bin fixes
hist, (x, y) = np.histogramdd((df.rtscore, df.mcscore),
                              bins=(101, 101),
                              range=((-0.5, 100.5), (-0.5, 100.5)))
hist = np.ravel(np.array(hist, dtype=np.float64))
x = x[:-1] + (x[1] - x[0]) / 2.0
y = y[:-1] + (y[1] - y[0]) / 2.0

# Form a list of all (x, y) pairs
fpairs = np.ravel(np.dstack(np.meshgrid(x, y)))
apairs = np.reshape(fpairs, (len(fpairs) / 2, 2))

# Get a list of only the (x, y) pairs where a dot is placed
compairs = np.compress(hist, apairs, axis=0)
comhist = np.compress(hist, hist)

# Fit a rank 3 polynominal to the data
f = lambda x, p : np.poly1d(p)(x)
errf = lambda p, x, y : f(x, p) - y
pbest, code = optimize.leastsq(errf, np.ones(4), (df.rtscore, df.mcscore))

# Calculate and sort by the distance of the mcscore to the fit
df['error'] = np.abs(df.mcscore - f(df.rtscore, pbest))
df = df.sort('error', ascending=False)

# Write out a list of the ten movies with the largest error for the blog post
ptfile = open("../data/posttext.txt", "w")
for i in range(10) :
    row = df.iloc[i]
    ptfile.write("| {} |".format(row['title']))
    ptfile.write(' {} |'.format(row['year']))
    ptfile.write(' [{}]'.format(row['rtscore']))
    ptfile.write('({}) |'.format(row['rtlink']))
    ptfile.write(' [{}]'.format(row['mcscore']))
    ptfile.write('({})\n'.format(row['mclink']))
ptfile.close()

# Form the scatter plot with colors related to the number of points
plt.figure(figsize=(8, 6))
plt.scatter(compairs.T[1], compairs.T[0], marker='s', s=5,
            c=comhist, cmap=plt.get_cmap('jet'), edgecolor='None')

# Plot the fit and a 90% band around it
xplot = np.arange(-2, 102, 0.1)
nplevel = float(df.iloc[int(0.1 * len(df))]['error'])
plt.plot(xplot, f(xplot, pbest), color='k', ls='--', lw=3)
plt.plot(xplot, f(xplot, pbest) + nplevel, color='k', ls='--', lw=1)
plt.plot(xplot, f(xplot, pbest) - nplevel, color='k', ls='--', lw=1)

# Plot formatting
plt.colorbar(ticks=np.arange(np.max(hist)) + 1)
plt.title('Rotten Tomatoes versus Metacritic')
plt.xlabel('Rotten Tomatoes Score')
plt.ylabel('Metacritic Score')
plt.xlim((-1, 101))
plt.ylim((-1, 101))
plt.grid(True)
plt.savefig('../data/movieratings_scatter.png')
plt.clf()
