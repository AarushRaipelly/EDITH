import tkinter as tk

class CornerFrame(tk.Canvas):
    """A canvas container that draws futuristic L-shaped cyan brackets in its corners."""
    def __init__(self, parent, bg="#050d12", border_color="#00d4ff", **kwargs) -> None:
        super().__init__(parent, bg=bg, highlightthickness=0, **kwargs)
        self.border_color = border_color
        self.bind("<Configure>", self.draw_brackets)

    def draw_brackets(self, event=None) -> None:
        self.delete("bracket")
        w = self.winfo_width()
        h = self.winfo_height()
        length = 12
        thick = 2
        c = self.border_color

        # Top-Left Bracket
        self.create_line(0, 0, length, 0, fill=c, width=thick, tags="bracket")
        self.create_line(0, 0, 0, length, fill=c, width=thick, tags="bracket")

        # Top-Right Bracket
        self.create_line(w, 0, w - length, 0, fill=c, width=thick, tags="bracket")
        self.create_line(w, 0, w, length, fill=c, width=thick, tags="bracket")

        # Bottom-Left Bracket
        self.create_line(0, h, length, h, fill=c, width=thick, tags="bracket")
        self.create_line(0, h, 0, h - length, fill=c, width=thick, tags="bracket")

        # Bottom-Right Bracket
        self.create_line(w, h, w - length, h, fill=c, width=thick, tags="bracket")
        self.create_line(w, h, w, h - length, fill=c, width=thick, tags="bracket")

class MiniProgressBar(tk.Canvas):
    """A super thin custom progress bar matching the cyan futuristic styling."""
    def __init__(self, parent, value=0.0, color="#00d4ff", bg="#102027", height=3, **kwargs) -> None:
        super().__init__(parent, height=height, bg=bg, highlightthickness=0, **kwargs)
        self.value = value
        self.color = color
        self.bg_color = bg
        self.bind("<Configure>", self.draw)

    def draw(self, event=None) -> None:
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        
        # Draw background bar
        self.create_rectangle(0, 0, w, h, fill=self.bg_color, width=0)
        
        # Draw filled progress bar
        ratio = min(max(self.value / 100.0, 0.0), 1.0)
        filled_width = int(w * ratio)
        if filled_width > 0:
            self.create_rectangle(0, 0, filled_width, h, fill=self.color, width=0)

    def update_value(self, val: float) -> None:
        self.value = val
        self.draw()

class StatCell(tk.Frame):
    """A grid cell displaying a small label, value, and thin progress bar."""
    def __init__(self, parent, label: str, value_str: str, progress_val: float, color="#00d4ff", bg="#050d12") -> None:
        super().__init__(parent, bg=bg)
        # Category label in cyan
        self.lbl = tk.Label(self, text=label.upper(), bg=bg, fg="#00d4ff", font=("Courier", 8, "bold"))
        self.lbl.pack(anchor="w")

        # Metric value in light gray
        self.val_lbl = tk.Label(self, text=value_str, bg=bg, fg="#CDD6F4", font=("Courier", 9, "bold"))
        self.val_lbl.pack(anchor="w", pady=(0, 1))

        # Thin indicator progress bar
        self.pbar = MiniProgressBar(self, value=progress_val, color=color, bg="#102027", height=2)
        self.pbar.pack(fill="x", expand=True)

    def update_stat(self, value_str: str, progress_val: float) -> None:
        self.val_lbl.config(text=value_str)
        self.pbar.update_value(progress_val)

class TaskItem(tk.Frame):
    """A single task list item with status dot and left-aligned text."""
    def __init__(self, parent, text: str, status="queued", bg="#050d12") -> None:
        super().__init__(parent, bg=bg)
        
        dot_color = "#00d4ff"  # cyan (queued)
        if status == "done":
            dot_color = "#a6e3a1"  # green
        elif status == "pending":
            dot_color = "#fab387"  # orange

        self.dot = tk.Label(self, text="●", bg=bg, fg=dot_color, font=("Courier", 8))
        self.dot.pack(side="left", padx=(5, 2))

        self.lbl = tk.Label(self, text=text, bg=bg, fg="#CDD6F4", font=("Courier", 8), anchor="w")
        self.lbl.pack(side="left", fill="x", expand=True)
