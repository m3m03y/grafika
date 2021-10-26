import matplotlib.pyplot as plt
import numpy as np

class Cube():
  def __init__(self):
    r, g, b = np.indices((21,21,21)) / 20.0
    rc = self.midpoints(r)
    gc = self.midpoints(g)
    bc = self.midpoints(b)

    sphere = rc > -1

    colors = np.zeros(sphere.shape + (3,))
    colors[..., 0] = rc
    colors[..., 1] = gc
    colors[..., 2] = bc

    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(projection='3d')
    ax.voxels(r, g, b, sphere,
              facecolors=colors,
              linewidth=0,
              shade=False)
    plt.axis('off')
    plt.show()

  def midpoints(self,x):
    sl = ()
    for i in range(x.ndim):
        x = (x[sl + np.index_exp[:-1]] + x[sl + np.index_exp[1:]]) / 2.0
        sl += np.index_exp[:]
    return x

if __name__=='__main__':
  Cube()