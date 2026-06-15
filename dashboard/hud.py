import tkinter as tk
import logging
import threading
import time
import sys
import queue
from dashboard.widgets import CornerFrame, MiniProgressBar, StatCell, TaskItem

logger = logging.getLogger("EDITH.Dashboard")

FONT_FAMILY = ("Rajdhani", "Share Tech Mono", "Consolas", "Courier")

class EdithHUD:
    def __init__(self, brain=None) -> None:
        self.brain = brain
        if brain:
            brain.hud = self
        self.root = None
        self.running = False
        self.current_mode = "Idle"
        
        # Dimensions & States
        self.width = 280
        self.height = 420
        self.is_expanded = False
        self.is_tray_minimized = False
        
        # Thread-safe message queue
        self.update_queue = queue.Queue()
        
        # Animation variables
        self.pulse_radius = 14
        self.pulse_dir = 1
        self.pulse_speed = 1
        self.pulse_time_step = 0
        self.blink_state = True
        
        self.cpu_meter_val = 35.0
        self.ram_meter_val = 60.0

        # Build UI immediately on the main thread during initialization
        self.running = True
        self._build_ui()

    def start(self) -> None:
        """Starts the Tkinter window loop (blocks on main thread)."""
        if self.root:
            self.root.mainloop()

    def stop(self) -> None:
        """Closes HUD window."""
        self.running = False
        if self.root:
            try:
                self.root.destroy()
            except Exception:
                pass

    def _position_bottom_right(self, width: int, height: int) -> None:
        """Positions the window at the bottom-right corner of the primary screen."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = screen_width - width - 20
        y = screen_height - height - 50
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _set_dimensions(self, width: int, height: int) -> None:
        """Adjusts window size and re-centers bottom-right position."""
        self.width = width
        self.height = height
        self._position_bottom_right(width, height)

    def _start_drag(self, event) -> None:
        self.drag_x = event.x
        self.drag_y = event.y

    def _on_drag(self, event) -> None:
        deltax = event.x - self.drag_x
        deltay = event.y - self.drag_y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def _toggle_expand(self, event=None) -> None:
        """Toggles between standard corner view (280x420) and full expanded view (500x700)."""
        if self.is_tray_minimized:
            self._restore_from_tray()
            return
            
        if self.is_expanded:
            self.is_expanded = False
            self._set_dimensions(280, 420)
        else:
            self.is_expanded = True
            self._set_dimensions(500, 700)

    def _toggle_tray(self, event=None) -> None:
        """Toggles minimizing to system tray handle."""
        if self.is_tray_minimized:
            self._restore_from_tray()
        else:
            self._minimize_to_tray()

    def _minimize_to_tray(self) -> None:
        """Collapses window to a tiny borderless cyan circle handle in the corner."""
        self.is_tray_minimized = True
        
        w, h = 24, 24
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - w - 20
        y = screen_height - h - 50
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        
        self.container.pack_forget()
        self.tray_dot_canvas.pack(fill="both", expand=True)

    def _restore_from_tray(self) -> None:
        """Restores HUD window back to active frame configuration."""
        self.is_tray_minimized = False
        
        self.tray_dot_canvas.pack_forget()
        self.container.pack(fill="both", expand=True)
        
        w = 500 if self.is_expanded else 280
        h = 700 if self.is_expanded else 420
        self._set_dimensions(w, h)

    def _build_ui(self) -> None:
        self.root = tk.Tk()
        self.root.title("EDITH HUD")
        self.root.configure(bg="#050d12")
        
        # Disable window borders / decorations
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        self._position_bottom_right(self.width, self.height)
        
        # Drag bindings
        self.root.bind("<ButtonPress-1>", self._start_drag)
        self.root.bind("<B1-Motion>", self._on_drag)
        self.root.bind("<Double-Button-1>", self._toggle_expand)
        self.root.bind("<Button-3>", self._toggle_tray)

        # Minimalist tray handle widget canvas
        self.tray_dot_canvas = tk.Canvas(self.root, width=24, height=24, bg="#050d12", highlightthickness=0)
        self.tray_dot_canvas.create_oval(4, 4, 20, 20, fill="#00d4ff", outline="#ffffff", width=1.5)
        self.tray_dot_canvas.bind("<Button-1>", lambda e: self._restore_from_tray())
        self.tray_dot_canvas.bind("<Double-Button-1>", lambda e: self._restore_from_tray())

        # Main Corner brackets Frame
        self.container = CornerFrame(self.root, bg="#050d12", border_color="#00d4ff")
        self.container.pack(fill="both", expand=True)

        # --- HEADER SECTION ---
        header_frame = tk.Frame(self.container, bg="#050d12")
        header_frame.pack(fill="x", padx=10, pady=(10, 2))
        
        # 3 Title bar control buttons aligned to the right
        btn_frame = tk.Frame(header_frame, bg="#050d12")
        btn_frame.pack(side="right", padx=5)
        
        btn_font = (FONT_FAMILY, 8, "bold")
        
        # Minimize button
        min_btn = tk.Button(btn_frame, text="—", bg="#050d12", fg="#00d4ff", activebackground="#102027", activeforeground="#00d4ff", relief="flat", font=btn_font, width=2, command=self._minimize_to_tray)
        min_btn.pack(side="left", padx=1)
        
        # Fullscreen / Expand button
        expand_btn = tk.Button(btn_frame, text="⛶", bg="#050d12", fg="#00d4ff", activebackground="#102027", activeforeground="#00d4ff", relief="flat", font=btn_font, width=2, command=self._toggle_expand)
        expand_btn.pack(side="left", padx=1)
        
        # Close button (styled red highlight on active)
        close_btn = tk.Button(btn_frame, text="✕", bg="#050d12", fg="#f38ba8", activebackground="#f38ba8", activeforeground="#050d12", relief="flat", font=btn_font, width=2, command=self._on_close)
        close_btn.pack(side="left", padx=1)
        
        self.header_canvas = tk.Canvas(header_frame, bg="#050d12", height=35, highlightthickness=0)
        self.header_canvas.pack(side="left", fill="x", expand=True)
        self.header_canvas.bind("<Configure>", lambda e: self._redraw_header())

        # --- MODE & CLOCK BAR ---
        mode_bar = tk.Frame(self.container, bg="#050d12")
        mode_bar.pack(fill="x", padx=15, pady=2)
        
        self.mode_label = tk.Label(mode_bar, text="MODE: IDLE", bg="#050d12", fg="#CDD6F4", font=(FONT_FAMILY, 8, "bold"))
        self.mode_label.pack(side="left")
        
        self.clock_lbl = tk.Label(mode_bar, text="00:00:00", bg="#050d12", fg="#00d4ff", font=(FONT_FAMILY, 8, "bold"))
        self.clock_lbl.pack(side="right")

        # --- WAVEFORM BAR ---
        self.wave_canvas = tk.Canvas(self.container, bg="#050d12", height=15, highlightthickness=0)
        self.wave_canvas.pack(fill="x", padx=15, pady=2)

        # --- HEARD TEXT BAR ---
        self.heard_label = tk.Label(self.container, text="HEARD: IDLE", bg="#050d12", fg="#00d4ff", font=(FONT_FAMILY, 8, "italic"), anchor="w")
        self.heard_label.pack(fill="x", padx=15, pady=2)

        # --- CHAT AREA ---
        chat_container = tk.Frame(self.container, bg="#050d12")
        chat_container.pack(fill="both", expand=True, padx=15, pady=5)
        
        # Scrolled Text Box replaced with styled scroll bubble frame container
        self.chat_canvas = tk.Canvas(chat_container, bg="#050d12", highlightthickness=0, height=80)
        
        # Thin sci-fi scrollbar
        scrollbar = tk.Scrollbar(chat_container, orient="vertical", command=self.chat_canvas.yview, width=8, bd=0, highlightthickness=0)
        scrollbar.pack(side="right", fill="y")
        
        self.chat_canvas.pack(side="left", fill="both", expand=True)
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.chat_scroll_frame = tk.Frame(self.chat_canvas, bg="#050d12")
        self.chat_canvas_window = self.chat_canvas.create_window((0, 0), window=self.chat_scroll_frame, anchor="nw")
        
        # Configure scrollregion and dynamic width update
        self.chat_scroll_frame.bind("<Configure>", lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))
        self.chat_canvas.bind("<Configure>", lambda e: self.chat_canvas.itemconfig(self.chat_canvas_window, width=e.width))
        
        # Mousewheel scrolling bindings for ease of use
        def _on_mousewheel(event):
            try:
                self.chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass
        self.chat_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Input typing field
        input_frame = tk.Frame(chat_container, bg="#050d12")
        input_frame.pack(fill="x", pady=(2, 5))
        
        self.entry_field = tk.Entry(input_frame, bg="#102027", fg="#CDD6F4", insertbackground="#CDD6F4", font=(FONT_FAMILY, 9), highlightbackground="#1e3b2b", highlightthickness=1)
        self.entry_field.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=2)
        self.entry_field.bind("<Return>", lambda e: self._send_text_message())
        
        send_btn = tk.Button(input_frame, text="SEND", bg="#102027", fg="#00d4ff", activebackground="#0b2533", activeforeground="#00d4ff", relief="flat", font=(FONT_FAMILY, 8, "bold"), command=self._send_text_message)
        send_btn.pack(side="right", padx=1)

        # --- STATS GRID (2x2) ---
        stats_grid = tk.Frame(self.container, bg="#050d12")
        stats_grid.pack(fill="x", padx=15, pady=5)
        stats_grid.columnconfigure(0, weight=1, uniform="group1")
        stats_grid.columnconfigure(1, weight=1, uniform="group1")
        
        self.battery_cell = StatCell(stats_grid, "Battery", "100%", 100, color="#00d4ff")
        self.battery_cell.grid(row=0, column=0, padx=(0, 5), pady=2, sticky="nsew")
        
        self.tasks_cell = StatCell(stats_grid, "Tasks", "0 Active", 0, color="#a6e3a1")
        self.tasks_cell.grid(row=0, column=1, padx=(5, 0), pady=2, sticky="nsew")
        
        self.mem_cell = StatCell(stats_grid, "Memory", "0%", 0, color="#fab387")
        self.mem_cell.grid(row=1, column=0, padx=(0, 5), pady=2, sticky="nsew")
        
        self.class_cell = StatCell(stats_grid, "Next Class", "None", 0, color="#f38ba8")
        self.class_cell.grid(row=1, column=1, padx=(5, 0), pady=2, sticky="nsew")

        # --- TASKS QUEUE LIST ---
        self.tasks_list_frame = tk.Frame(self.container, bg="#050d12")
        self.tasks_list_frame.pack(fill="x", padx=10, pady=2)
        self._populate_tasks_list()

        # --- CONTROLS ROW ---
        ctrl_row = tk.Frame(self.container, bg="#050d12")
        ctrl_row.pack(fill="x", padx=10, pady=(5, 10))
        
        self.mic_btn = tk.Button(ctrl_row, text="🎙️ MIC", bg="#102027", fg="#CDD6F4", activebackground="#0b2533", activeforeground="#00d4ff", relief="flat", font=(FONT_FAMILY, 8, "bold"), command=self._toggle_mic)
        self.mic_btn.pack(side="left", fill="x", expand=True, padx=2)
        
        self.dnd_btn = tk.Button(ctrl_row, text="🌙 DND", bg="#102027", fg="#CDD6F4", activebackground="#0b2533", activeforeground="#00d4ff", relief="flat", font=(FONT_FAMILY, 8, "bold"), command=self._toggle_dnd)
        self.dnd_btn.pack(side="left", fill="x", expand=True, padx=2)
        
        self.mute_btn = tk.Button(ctrl_row, text="🔊 MUTE", bg="#102027", fg="#CDD6F4", activebackground="#0b2533", activeforeground="#00d4ff", relief="flat", font=(FONT_FAMILY, 8, "bold"), command=self._toggle_mute)
        self.mute_btn.pack(side="left", fill="x", expand=True, padx=2)
        
        self.sleep_btn = tk.Button(ctrl_row, text="💤 SLEEP", bg="#102027", fg="#CDD6F4", activebackground="#0b2533", activeforeground="#00d4ff", relief="flat", font=(FONT_FAMILY, 8, "bold"), command=self._toggle_sleep)
        self.sleep_btn.pack(side="left", fill="x", expand=True, padx=2)

        # Setup standard Windows window closing protocols
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Style initial states
        self._update_mic_button_style()
        self._update_mute_button_style()
        self._update_dnd_button_style()
        self._update_sleep_button_style()

        # Background refresher loop for system metrics simulation
        def refresh_stats():
            import random
            while self.running:
                try:
                    cpu_val = min(max(self.cpu_meter_val + random.uniform(-4, 4), 5), 95)
                    ram_val = min(max(self.ram_meter_val + random.uniform(-1, 1), 10), 90)
                    
                    def update_meters():
                        try:
                            if self.root:
                                self.cpu_meter_val = cpu_val
                                self.ram_meter_val = ram_val
                        except Exception:
                            pass
                    if self.root:
                        self.root.after(0, update_meters)
                    time.sleep(3.0)
                except Exception:
                    break

        refresher = threading.Thread(target=refresh_stats, daemon=True)
        refresher.start()

        # Start loops & queue processing
        self._animate_pulse()
        self._periodic_check()
        self.process_queue()

    def _redraw_header(self) -> None:
        self.header_canvas.delete("static")
        w = self.header_canvas.winfo_width()
        h = self.header_canvas.winfo_height()
        if w < 10 or h < 10:
            return
            
        cx, cy = 20, h // 2
        self.arc_reactor_center = (cx, cy)
        
        self.header_canvas.create_text(42, h // 2, text="EDITH", fill="#00d4ff", font=(FONT_FAMILY, 12, "bold"), anchor="w", tags="static")
        self.status_dot_center = (w - 15, h // 2)

    def _draw_arc_reactor(self, cx: int, cy: int, radius: int, pulse_val: float) -> None:
        self.header_canvas.delete("reactor")
        
        if self.current_mode == "Listening":
            color = "#a6e3a1"  # Green
        elif self.current_mode == "Processing":
            color = "#00d4ff"  # Cyan
        elif self.current_mode == "Speaking":
            color = "#fab387"  # Orange
        elif self.current_mode == "DND":
            color = "#f38ba8"  # Red
        else:
            color = "#00d4ff"  # Cyan
            
        self.header_canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline=color, width=1.5, tags="reactor")
        
        core_r = int(radius * 0.4 * pulse_val)
        self.header_canvas.create_oval(cx - core_r, cy - core_r, cx + core_r, cy + core_r, fill="#050d12", outline=color, width=1.5, tags="reactor")
        self.header_canvas.create_oval(cx - core_r + 2, cy - core_r + 2, cx + core_r - 2, cy + core_r - 2, fill=color, width=0, tags="reactor")
        
        import math
        for i in range(8):
            angle = i * (2 * math.pi / 8)
            x1 = cx + int((core_r + 2) * math.cos(angle))
            y1 = cy + int((core_r + 2) * math.sin(angle))
            x2 = cx + int((radius - 1) * math.cos(angle))
            y2 = cy + int((radius - 1) * math.sin(angle))
            self.header_canvas.create_line(x1, y1, x2, y2, fill=color, width=1.5, tags="reactor")

    def _populate_tasks_list(self) -> None:
        for child in self.tasks_list_frame.winfo_children():
            child.destroy()
            
        t1 = TaskItem(self.tasks_list_frame, "Assist Shield: Active", "done")
        t1.pack(fill="x", pady=1)
        
        t2 = TaskItem(self.tasks_list_frame, "Timetable Sync: Idle", "queued")
        t2.pack(fill="x", pady=1)
        
        t3 = TaskItem(self.tasks_list_frame, "Voice Engine: Ready", "pending")
        t3.pack(fill="x", pady=1)

    def update_status(self, mode: str) -> None:
        """Thread-safe queuing of mode status update."""
        self.update_queue.put(('status', mode))

    def _set_status(self, mode: str) -> None:
        self.current_mode = mode
        self.mode_label.config(text=f"MODE: {mode.upper()}")
        
        if mode == "Listening":
            self.mode_label.config(fg="#a6e3a1")
        elif mode == "Processing":
            self.mode_label.config(fg="#00d4ff")
        elif mode == "Speaking":
            self.mode_label.config(fg="#fab387")
        elif mode == "DND":
            self.mode_label.config(fg="#f38ba8")
        else:
            self.mode_label.config(fg="#cdd6f4")

    def update_recognized_text(self, text: str) -> None:
        """Thread-safe queuing of recognized text update."""
        self.update_queue.put(('recognized_text', text))

    def _set_recognized_text(self, text: str) -> None:
        self.heard_label.config(text=f"HEARD: {text.upper()}")

    def add_chat_message(self, sender: str, text: str) -> None:
        """Thread-safe queuing of chat message."""
        self.update_queue.put(('chat', sender, text))

    def _insert_chat_message(self, sender: str, text: str) -> None:
        children = self.chat_scroll_frame.winfo_children()
        if len(children) >= 100:
            children[0].destroy()
            
        bubble = tk.Frame(self.chat_scroll_frame, bg="#050d12")
        bubble.pack(fill="x", pady=2, anchor="e" if sender == "Boss" else "w")
        
        bg_color = "#102027" if sender == "Boss" else "#0b2533"
        fg_color = "#00d4ff" if sender == "Boss" else "#F5C2E7"
        
        lbl = tk.Label(
            bubble, 
            text=f"{sender.upper()}: {text}", 
            bg=bg_color, 
            fg=fg_color, 
            font=(FONT_FAMILY, 8), 
            padx=8, 
            pady=4, 
            justify="left", 
            wraplength=170
        )
        lbl.pack(anchor="e" if sender == "Boss" else "w")
        
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def _send_text_message(self) -> None:
        text = self.entry_field.get().strip()
        if not text:
            return
        self.entry_field.delete(0, "end")
        
        self.add_chat_message("Boss", text)
        
        # Process input asynchronously in a background thread to prevent UI freezing
        def process():
            if self.brain:
                self.update_status("Processing")
                response = self.brain.process_input(text)
                if response:
                    from voice.speaker import EdithSpeaker
                    speaker = EdithSpeaker(brain=self.brain)
                    speaker.speak(response)
                else:
                    self.update_status("Idle")
        
        threading.Thread(target=process, daemon=True).start()

    def _toggle_mic(self) -> None:
        from voice.listener import EdithListener
        if not hasattr(EdithListener, "mic_enabled"):
            EdithListener.mic_enabled = True
        EdithListener.mic_enabled = not EdithListener.mic_enabled
        status_str = "ON" if EdithListener.mic_enabled else "OFF"
        self._insert_chat_message("System", f"Microphone is {status_str}")
        self._update_mic_button_style()

    def _update_mic_button_style(self) -> None:
        from voice.listener import EdithListener
        mic_on = getattr(EdithListener, "mic_enabled", True)
        if mic_on:
            self.mic_btn.config(text="🎙️ MIC: ON", bg="#102027", fg="#00d4ff")
        else:
            self.mic_btn.config(text="🎙️ MIC: OFF", bg="#f38ba8", fg="#11111b")

    def _toggle_mute(self) -> None:
        from voice.speaker import EdithSpeaker
        EdithSpeaker.muted = not EdithSpeaker.muted
        status_str = "Muted" if EdithSpeaker.muted else "Unmuted"
        self._insert_chat_message("System", f"Voice output is {status_str}")
        self._update_mute_button_style()

    def _update_mute_button_style(self) -> None:
        from voice.speaker import EdithSpeaker
        if EdithSpeaker.muted:
            self.mute_btn.config(text="🔇 MUTE: ON", bg="#f38ba8", fg="#11111b")
        else:
            self.mute_btn.config(text="🔊 MUTE:OFF", bg="#102027", fg="#cdd6f4")

    def _toggle_dnd(self) -> None:
        if self.brain:
            new_state = not self.brain.context.dnd_mode
            self.brain.context.set_dnd(new_state)
            status_str = "ON" if new_state else "OFF"
            self._insert_chat_message("System", f"DND Mode is {status_str}")
            self._update_dnd_button_style()
            mode_str = "DND" if new_state else "Idle"
            self.update_status(mode_str)

    def _update_dnd_button_style(self) -> None:
        if self.brain and self.brain.context.dnd_mode:
            self.dnd_btn.config(text="🌙 DND: ON", bg="#fab387", fg="#11111b")
        else:
            self.dnd_btn.config(text="🔆 DND: OFF", bg="#102027", fg="#cdd6f4")

    def _toggle_sleep(self) -> None:
        if self.brain:
            if not hasattr(self.brain, "is_sleeping"):
                self.brain.is_sleeping = False
            self.brain.is_sleeping = not self.brain.is_sleeping
            status_str = "Sleeping" if self.brain.is_sleeping else "Awake"
            self._insert_chat_message("System", f"System: {status_str}")
            self._update_sleep_button_style()
            
            mode_str = "Idle" if not self.brain.is_sleeping else "Sleeping"
            self.update_status(mode_str)

    def _update_sleep_button_style(self) -> None:
        is_sleeping = False
        if self.brain and hasattr(self.brain, "is_sleeping"):
            is_sleeping = self.brain.is_sleeping
            
        if is_sleeping:
            self.sleep_btn.config(text="💤 AWAKE", bg="#fab387", fg="#11111b")
        else:
            self.sleep_btn.config(text="💤 SLEEP", bg="#102027", fg="#cdd6f4")

    def _periodic_check(self) -> None:
        if not self.running or not self.root:
            return
            
        self.clock_lbl.config(text=time.strftime("%H:%M:%S"))
        
        self._update_dnd_button_style()
        self._update_mute_button_style()
        self._update_mic_button_style()
        self._update_sleep_button_style()
        
        self._refresh_realtime_metrics()
        
        self.root.after(1000, self._periodic_check)

    def _refresh_realtime_metrics(self) -> None:
        bat = 90
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                bat = int(battery.percent)
        except Exception:
            pass
        self.battery_cell.update_stat(f"{bat}%", bat)

        # Real system memory usage
        mem_pct = 50
        try:
            import psutil
            mem_pct = int(psutil.virtual_memory().percent)
        except Exception:
            pass
        self.mem_cell.update_stat(f"{mem_pct}%", mem_pct)

        tasks = 0
        if self.brain and hasattr(self.brain, "tasks"):
            tasks = len(self.brain.tasks.queue)
        if tasks == 0:
            tasks = int(self.cpu_meter_val / 20)
        self.tasks_cell.update_stat(f"{tasks} Active", min(tasks * 20, 100))

        # Dynamic Next Class countdown from schedule database
        class_text = "None"
        class_progress = 0
        if self.brain and self.brain.memory:
            try:
                import datetime
                now = datetime.datetime.now()
                day_name = now.strftime("%A").lower()
                
                raw_schedule = self.brain.memory.get_all_memories_by_topic("academic_schedule")
                upcoming_classes = []
                
                for key, val in raw_schedule.items():
                    if key.startswith(day_name):
                        parts = key.split("_")
                        if len(parts) >= 2:
                            time_str = parts[1].replace(":", "")  # remove colon if any, e.g. "09:00" -> "0900"
                            if len(time_str) == 4 and time_str.isdigit():
                                hr = int(time_str[:2])
                                mn = int(time_str[2:])
                                class_time = now.replace(hour=hr, minute=mn, second=0, microsecond=0)
                                if class_time > now:
                                    subject = val.split("|")[0]
                                    time_diff = class_time - now
                                    upcoming_classes.append((time_diff, subject))
                
                if upcoming_classes:
                    upcoming_classes.sort(key=lambda x: x[0])
                    closest_diff, closest_subject = upcoming_classes[0]
                    total_seconds = int(closest_diff.total_seconds())
                    hrs = total_seconds // 3600
                    mins = (total_seconds % 3600) // 60
                    
                    if hrs > 0:
                        class_text = f"{hrs}h {mins}m ({closest_subject})"
                    else:
                        class_text = f"{mins}m ({closest_subject})"
                        
                    remaining_mins = total_seconds / 60.0
                    if remaining_mins <= 15:
                        class_progress = 100
                    elif remaining_mins >= 240:
                        class_progress = 0
                    else:
                        class_progress = int((240 - remaining_mins) / 225.0 * 100)
                else:
                    class_text = "None today"
                    class_progress = 0
            except Exception as e:
                logger.error(f"Error calculating next class countdown: {e}")
                class_text = "Error"
                class_progress = 0

        self.class_cell.update_stat(class_text, class_progress)

    def _animate_pulse(self) -> None:
        if not self.running or not self.root:
            return
            
        self.pulse_time_step += 1
        import math
        pulse_val = 1.0 + 0.12 * math.sin(self.pulse_time_step * 0.2)
        
        if hasattr(self, "arc_reactor_center"):
            cx, cy = self.arc_reactor_center
            self._draw_arc_reactor(cx, cy, 12, pulse_val)
            
        if hasattr(self, "status_dot_center"):
            dx, dy = self.status_dot_center
            dot_color = "#a6e3a1" if (self.blink_state or self.current_mode == "Listening") else "#1e3b2b"
            self.header_canvas.delete("status_dot")
            self.header_canvas.create_oval(dx - 3, dy - 3, dx + 3, dy + 3, fill=dot_color, width=0, tags="status_dot")
            if self.pulse_time_step % 12 == 0:
                self.blink_state = not self.blink_state

        w = self.wave_canvas.winfo_width()
        h = self.wave_canvas.winfo_height()
        if w > 5 and h > 5:
            self.wave_canvas.delete("waveform")
            bar_width = 3
            spacing = 5
            num_bars = 5
            start_x = (w - (num_bars * bar_width + (num_bars - 1) * spacing)) // 2
            
            import random
            is_active = (self.current_mode == "Listening" or self.current_mode == "Speaking")
            for i in range(num_bars):
                bx = start_x + i * (bar_width + spacing)
                if is_active:
                    bar_h = int(5 + 8 * math.sin(self.pulse_time_step * 0.45 + i) + random.uniform(-1.5, 1.5))
                    bar_h = min(max(bar_h, 2), h - 2)
                else:
                    bar_h = 2
                    
                by1 = (h - bar_h) // 2
                by2 = by1 + bar_h
                self.wave_canvas.create_rectangle(bx, by1, bx + bar_width, by2, fill="#00d4ff", width=0, tags="waveform")
                
        self.root.after(40, self._animate_pulse)

    def process_queue(self) -> None:
        """Processes the thread-safe update queue on the main thread."""
        try:
            while True:
                item = self.update_queue.get_nowait()
                if item[0] == 'chat':
                    self._insert_chat_message(item[1], item[2])
                elif item[0] == 'status':
                    self._set_status(item[1])
                elif item[0] == 'recognized_text':
                    self._set_recognized_text(item[1])
        except queue.Empty:
            pass
        finally:
            if self.running and self.root:
                self.root.after(100, self.process_queue)

    def _on_close(self) -> None:
        self.stop()
        if self.brain:
            self.brain.shutdown()
        sys.exit(0)
