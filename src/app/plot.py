import matplotlib.pyplot as plt
import numpy as np
import io


def create_plot(data, title, ylabel, label):
    fig, ax = plt.subplots()
    ax.plot(np.arange(len(data)), data, color="blue", marker="o", label=label)
    ax.set_xlabel("Tiempo (días)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True)
    ax.legend()
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf
