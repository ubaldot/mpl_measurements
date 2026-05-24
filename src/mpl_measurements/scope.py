import numpy as np


def compute_window_stats(xdata, ydata, x1, x2):
    xmin, xmax = sorted([x1, x2])
    mask = (xdata >= xmin) & (xdata <= xmax)
    y_win = ydata[mask]

    if len(y_win) == 0:
        return np.nan, np.nan, np.nan

    y_min = np.min(y_win)
    y_max = np.max(y_win)
    rms = np.sqrt(np.mean(y_win**2))

    return y_min, y_max, rms


# =========================================================
# State container
# =========================================================
class AxisState:
    def __init__(self):
        self.selected_line = None
        self.cursor_lines = []
        self.cursor_points = []
        self.positions = []


# =========================================================
# Main interactive controller
# =========================================================
class InteractiveScope:
    def __init__(self, fig, axes, info_text):
        self.fig = fig
        self.axes = axes
        self.info_text = info_text

        # state per axis
        self.state = {ax: AxisState() for ax in axes}

        # connect events (store IDs for future cleanup)
        self.cid_pick = fig.canvas.mpl_connect("pick_event", self.on_pick)
        self.cid_click = fig.canvas.mpl_connect(
            "button_press_event", self.on_click
        )
        self.cid_key = fig.canvas.mpl_connect("key_press_event", self.on_key)

    # -----------------------------------------------------
    # Line selection
    # -----------------------------------------------------
    def on_pick(self, event):
        ax = event.artist.axes
        state = self.state[ax]

        state.selected_line = event.artist

        # reset visual emphasis
        for line in ax.get_lines():
            line.set_linewidth(1)

        state.selected_line.set_linewidth(3)

        self.info_text.set_text(
            f"{ax.get_title()}\n"
            f"Selected: {state.selected_line.get_label()}\n"
            "Click twice to place cursors"
        )

        self.fig.canvas.draw_idle()

    # -----------------------------------------------------
    # Cursor placement
    # -----------------------------------------------------
    def on_click(self, event):
        ax = event.inaxes
        if ax not in self.state:
            return

        state = self.state[ax]
        line = state.selected_line
        if line is None or event.xdata is None:
            return

        xdata = line.get_xdata()
        ydata = line.get_ydata()

        # snap to nearest sample
        idx = np.argmin(np.abs(xdata - event.xdata))
        x_sel, y_sel = xdata[idx], ydata[idx]

        color = line.get_color()

        vline = ax.axvline(x_sel, color=color, linestyle="--")
        (point,) = ax.plot(x_sel, y_sel, "o", color=color)

        state.cursor_lines.append(vline)
        state.cursor_points.append(point)
        state.positions.append((x_sel, y_sel))

        # keep only last 2 cursors
        if len(state.cursor_lines) > 2:
            state.cursor_lines.pop(0).remove()
            state.cursor_points.pop(0).remove()
            state.positions.pop(0)

        self.update_measurements(ax, state)

    # -----------------------------------------------------
    # Measurements + UI update
    # -----------------------------------------------------
    def update_measurements(self, ax, state):
        line = state.selected_line

        if line is None:
            return

        if len(state.positions) < 2:
            self.info_text.set_text(
                f"{ax.get_title()}\n{line.get_label()}\nClick second point"
            )
            self.fig.canvas.draw_idle()
            return

        (x1, y1), (x2, y2) = state.positions

        xdata = line.get_xdata()
        ydata = line.get_ydata()

        y_min, y_max, rms = compute_window_stats(xdata, ydata, x1, x2)

        dx = x2 - x1
        dy = y2 - y1

        self.info_text.set_text(
            f"{ax.get_title()}\n"
            f"{line.get_label()}\n\n"
            f"P1: ({x1:.3f}, {y1:.3f})\n"
            f"P2: ({x2:.3f}, {y2:.3f})\n\n"
            f"Δx = {dx:.3f}\n"
            f"Δy = {dy:.3f}\n\n"
            f"Min = {y_min:.3f}\n"
            f"Max = {y_max:.3f}\n"
            f"RMS = {rms:.3f}"
        )

        self.fig.canvas.draw_idle()

    # -----------------------------------------------------
    # Reset
    # -----------------------------------------------------
    def on_key(self, event):
        if event.key != "r":
            return

        for ax, state in self.state.items():
            for l in state.cursor_lines:
                l.remove()
            for p in state.cursor_points:
                p.remove()

            state.cursor_lines.clear()
            state.cursor_points.clear()
            state.positions.clear()

        self.info_text.set_text("Reset — select a line")
        self.fig.canvas.draw_idle()
