import numpy as np
import matplotlib.pyplot as plt

from mpl_measurements import InteractiveScope

x = np.linspace(0, 10, 1000)

fig, axs = plt.subplots(1, 1, figsize=(10, 6), sharex=True, squeeze=False)
axs = axs.flatten()
fig.subplots_adjust(right=0.78)

for ii, ax in enumerate(axs):
    ax.plot(x, np.sin(x + ii), label=f"sin {ii}", picker=5)
    ax.plot(x, np.cos(x + ii), label=f"cos {ii}", picker=5)
    ax.set_title(f"Axes {ii}")
    ax.legend()

scope = InteractiveScope(fig)

plt.show()
