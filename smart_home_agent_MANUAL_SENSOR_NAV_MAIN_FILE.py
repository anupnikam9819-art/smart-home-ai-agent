#!/usr/bin/env python3
"""
AI-Based Smart Home Automation and Energy Management Agent
Academic Prototype for Artificial Intelligence (Utility-Based Intelligent Agent)

Architecture:
  Perception -> AI Utility Decision Engine -> Action -> Environment Feedback

Priorities:
  1. Safety (Perimeter Door & Air Quality Hazards)
  2. User Comfort (Visual Comfort & Thermal Regulation)
  3. Energy Saving (Load Shedding & Conservation)
"""

import sys
import time
import random
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# ==========================================
# CONSTANTS & CONFIGURATION
# ==========================================
WINDOW_TITLE = "SmartHome AI - Intelligent Home Automation"
HEADER_TITLE = "SmartHome AI"
HEADER_SUBTITLE = "Intelligent Home Automation"
SYSTEM_STATUS = "● SYSTEM ONLINE"

# Power ratings in Watts
WATTAGE = {
    'light': 60,
    'fan': 75,
    'ac': 1200,
    'air_purifier': 80
}
TOTAL_MAX_WATTS = sum(WATTAGE.values())  # 1415 Watts

# Modern Color Palette
COLORS = {
    'sidebar_bg': '#0f172a',       # Deep Navy
    'sidebar_hover': '#1e293b',    # Slate Navy
    'sidebar_active': '#2563eb',   # Electric Blue
    'sidebar_text': '#f8fafc',
    'sidebar_muted': '#94a3b8',
    'main_bg': '#f1f5f9',          # Light Grey-Blue
    'card_bg': '#ffffff',          # Crisp White
    'card_border': '#e2e8f0',
    'text_primary': '#0f172a',
    'text_secondary': '#475569',
    'text_muted': '#94a3b8',
    'primary_blue': '#2563eb',
    'primary_hover': '#1d4ed8',
    'on_green': '#16a34a',         # Green badge
    'on_green_bg': '#dcfce7',
    'off_grey': '#64748b',         # Grey badge
    'off_grey_bg': '#f1f5f9',
    'alert_red': '#dc2626',        # Stop / Alert
    'alert_red_bg': '#fee2e2',
    'warning_amber': '#d97706',
    'warning_amber_bg': '#fef3c7',
}


# ==========================================
# 1. SENSOR SIMULATION & DATA MODELS
# ==========================================
class SensorData:
    def __init__(self, person=True, temp=28.0, light=35, door=False, air=75, timestamp=None):
        self.person = bool(person)
        self.temp = float(temp)
        self.light = int(light)
        self.door = bool(door)  # True = Open, False = Closed
        self.air = int(air)
        self.timestamp = timestamp or datetime.now().strftime("%H:%M:%S")

    def to_dict(self):
        return {
            'person': self.person,
            'temp': self.temp,
            'light': self.light,
            'door': self.door,
            'air': self.air,
            'timestamp': self.timestamp
        }


class SensorSimulator:
    """Generates realistic sensor variations for automatic monitoring."""
    def __init__(self):
        self.current = SensorData(person=True, temp=29.0, light=38, door=False, air=78)

    def next_reading(self) -> SensorData:
        # Dynamic bounded random walk
        temp_delta = random.uniform(-1.5, 1.5)
        new_temp = round(max(18.0, min(37.0, self.current.temp + temp_delta)), 1)

        light_delta = random.randint(-15, 15)
        new_light = max(5, min(95, self.current.light + light_delta))

        air_delta = random.randint(-12, 12)
        new_air = max(30, min(98, self.current.air + air_delta))

        # 25% chance of occupancy change
        new_person = not self.current.person if random.random() < 0.25 else self.current.person

        # 15% chance of door state change
        new_door = not self.current.door if random.random() < 0.15 else self.current.door

        self.current = SensorData(
            person=new_person,
            temp=new_temp,
            light=new_light,
            door=new_door,
            air=new_air,
            timestamp=datetime.now().strftime("%H:%M:%S")
        )
        return self.current


# ==========================================
# 2. AI UTILITY-BASED DECISION ENGINE
# ==========================================
class DecisionResult:
    def __init__(self, sensor: SensorData, mode: str):
        self.sensor = sensor
        self.mode = mode
        self.timestamp = sensor.timestamp
        self.light = False
        self.fan = False
        self.ac = False
        self.air_purifier = False
        self.door_status = "SECURE"
        self.reasons = []
        self.primary_reason = ""
        self.instant_watts = 0
        self.interval_used_kwh = 0.0
        self.interval_saved_kwh = 0.0


class UtilityAgentEngine:
    """
    Utility-Based Intelligent Agent.
    Evaluates perception states and selects actions maximizing utility
    under priorities: 1. Safety, 2. Comfort, 3. Energy Saving.
    """
    @staticmethod
    def evaluate(sensor: SensorData, mode: str, interval_sec: float = 7.0) -> DecisionResult:
        result = DecisionResult(sensor, mode)

        # ----------------------------------------------------
        # PRIORITY 1: SAFETY (Door status & Air quality)
        # ----------------------------------------------------
        if sensor.door:
            result.door_status = "ENTRY OPEN"
            result.reasons.append("Door open → ENTRY OPEN")
        else:
            result.door_status = "SECURE"
            result.reasons.append("Door closed → SECURE")

        # Air Quality Rule
        if sensor.air < 60:
            result.air_purifier = True
            result.reasons.append(f"Poor air quality ({sensor.air}%) < 60% → Air Purifier ON")
        else:
            result.air_purifier = False
            result.reasons.append(f"Good air quality ({sensor.air}%) ≥ 60% → Air Purifier OFF")

        # ----------------------------------------------------
        # PRIORITY 2 & 3: COMFORT & ENERGY SAVING
        # ----------------------------------------------------
        if not sensor.person:
            # Rule: If no person is detected: Light = OFF, Fan = OFF, AC = OFF
            result.light = False
            result.fan = False
            result.ac = False
            result.reasons.append("No person detected → appliances OFF for energy saving")
            result.primary_reason = "No person detected → appliances OFF for energy saving"
            if result.air_purifier:
                result.primary_reason += " (Air Purifier ON for air safety)"
        else:
            # Person is detected:
            actions = []

            # Light Rule:
            if sensor.light < 40:
                result.light = True
                result.reasons.append(f"Person detected + low brightness ({sensor.light}%) < 40% → Light ON")
                actions.append("Person detected + low brightness → Light ON")
            else:
                result.light = False
                result.reasons.append(f"Person detected + adequate brightness ({sensor.light}%) ≥ 40% → Light OFF")

            # Temperature Rule:
            if sensor.temp >= 30.0:
                result.ac = True
                result.fan = False
                result.reasons.append(f"Person detected + High temperature ({sensor.temp}°C ≥ 30°C) → AC ON, Fan OFF")
                actions.append("High temperature → AC ON")
            elif 25.0 <= sensor.temp < 30.0:
                result.fan = True
                result.ac = False
                result.reasons.append(f"Person detected + Moderate temperature ({sensor.temp}°C) → Fan ON, AC OFF")
                actions.append("Moderate temp → Fan ON")
            else:
                result.fan = False
                result.ac = False
                result.reasons.append(f"Person detected + Cool temperature ({sensor.temp}°C < 25°C) → AC & Fan OFF")

            result.primary_reason = " | ".join(actions) if actions else "Environment optimal; appliances standby"

        # Energy consumption calculation
        watts = 0
        if result.light:
            watts += WATTAGE['light']
        if result.fan:
            watts += WATTAGE['fan']
        if result.ac:
            watts += WATTAGE['ac']
        if result.air_purifier:
            watts += WATTAGE['air_purifier']

        result.instant_watts = watts
        # kWh = (Watts * hours) / 1000
        result.interval_used_kwh = (watts * interval_sec) / (3600.0 * 1000.0)
        saved_watts = max(0, TOTAL_MAX_WATTS - watts)
        result.interval_saved_kwh = (saved_watts * interval_sec) / (3600.0 * 1000.0)

        return result


# ==========================================
# 3. ENERGY & HISTORY MANAGERS
# ==========================================
class EnergyManager:
    def __init__(self):
        self.total_used_kwh = 0.0
        self.total_saved_kwh = 0.0

    def add(self, used_kwh: float, saved_kwh: float):
        self.total_used_kwh += used_kwh
        self.total_saved_kwh += saved_kwh

    def reset(self):
        self.total_used_kwh = 0.0
        self.total_saved_kwh = 0.0


class HistoryManager:
    def __init__(self):
        self.records = []
        self._next_id = 1

    def add_record(self, decision: DecisionResult):
        record = {
            'id': self._next_id,
            'time': decision.timestamp,
            'mode': decision.mode,
            'person': "Yes" if decision.sensor.person else "No",
            'temp': f"{decision.sensor.temp:.1f}°C",
            'light_in': f"{decision.sensor.light}%",
            'door': decision.door_status,
            'air': f"{decision.sensor.air}%",
            'light_out': "ON" if decision.light else "OFF",
            'fan_out': "ON" if decision.fan else "OFF",
            'ac_out': "ON" if decision.ac else "OFF",
            'purifier_out': "ON" if decision.air_purifier else "OFF",
            'used_kwh': decision.interval_used_kwh,
            'saved_kwh': decision.interval_saved_kwh,
            'reasoning': "\n".join(f"• {r}" for r in decision.reasons),
            'primary_reason': decision.primary_reason,
            'raw_decision': decision
        }
        self.records.append(record)
        self._next_id += 1
        return record

    def clear(self):
        self.records.clear()
        self._next_id = 1


# ==========================================
# 4. MODERN TKINTER GUI APPLICATION
# ==========================================
class SmartHomeDesktopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry("1160x740")
        self.minsize(980, 640)
        self.configure(bg=COLORS['main_bg'])

        # Core logic components
        self.simulator = SensorSimulator()
        self.energy_mgr = EnergyManager()
        self.history_mgr = HistoryManager()

        # State variables
        self.current_mode = tk.StringVar(value="AUTOMATIC")
        self.is_monitoring_active = False
        self.auto_timer_id = None
        self.current_decision = None

        # Build GUI Layout
        self._setup_styles()
        self._create_header()
        self._create_body_layout()

        # Initial default evaluation
        self._run_initial_seed()

    def _setup_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except Exception:
            pass

        style.configure('Treeview',
                        background='#ffffff',
                        foreground=COLORS['text_primary'],
                        fieldbackground='#ffffff',
                        font=('Segoe UI', 9),
                        rowheight=26)
        style.configure('Treeview.Heading',
                        background='#e2e8f0',
                        foreground=COLORS['text_primary'],
                        font=('Segoe UI', 9, 'bold'))
        style.map('Treeview', background=[('selected', '#dbeafe')], foreground=[('selected', '#1e3a8a')])

    def _create_header(self):
        header_frame = tk.Frame(self, bg=COLORS['sidebar_bg'], height=68)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        header_frame.pack_propagate(False)

        title_box = tk.Frame(header_frame, bg=COLORS['sidebar_bg'])
        title_box.pack(side=tk.LEFT, padx=24, pady=12)

        lbl_title = tk.Label(title_box, text=HEADER_TITLE, font=('Segoe UI', 15, 'bold'),
                             fg='#ffffff', bg=COLORS['sidebar_bg'])
        lbl_title.pack(anchor='w')

        lbl_sub = tk.Label(title_box, text=HEADER_SUBTITLE, font=('Segoe UI', 9),
                           fg=COLORS['sidebar_muted'], bg=COLORS['sidebar_bg'])
        lbl_sub.pack(anchor='w')

        status_box = tk.Frame(header_frame, bg=COLORS['sidebar_bg'])
        status_box.pack(side=tk.RIGHT, padx=24, pady=16)

        self.lbl_system_status = tk.Label(status_box, text=SYSTEM_STATUS,
                                          font=('Segoe UI', 9, 'bold'),
                                          fg='#22c55e', bg=COLORS['sidebar_bg'])
        self.lbl_system_status.pack(side=tk.RIGHT)

        self.lbl_mode_pill = tk.Label(status_box, text="AUTO MODE READY",
                                      font=('Segoe UI', 9, 'bold'),
                                      fg='#38bdf8', bg=COLORS['sidebar_hover'],
                                      padx=10, pady=4)
        self.lbl_mode_pill.pack(side=tk.RIGHT, padx=14)

    def _create_body_layout(self):
        body_container = tk.Frame(self, bg=COLORS['main_bg'])
        body_container.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.sidebar = tk.Frame(body_container, bg=COLORS['sidebar_bg'], width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        self.content_area = tk.Frame(body_container, bg=COLORS['main_bg'])
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=16)

        self.nav_buttons = {}
        pages = [
            ("dashboard", "🏠  Dashboard"),
            ("sensors", "📡  Sensors"),
            ("appliances", "💡  Appliances"),
            ("history", "📋  History")
        ]

        tk.Label(self.sidebar, text="NAVIGATION", font=('Segoe UI', 8, 'bold'),
                 fg=COLORS['sidebar_muted'], bg=COLORS['sidebar_bg']).pack(anchor='w', padx=20, pady=(20, 8))

        for page_key, label in pages:
            btn = tk.Button(self.sidebar, text=label, anchor='w', font=('Segoe UI', 10),
                            fg=COLORS['sidebar_text'], bg=COLORS['sidebar_bg'],
                            activebackground=COLORS['sidebar_active'], activeforeground='#ffffff',
                            bd=0, padx=20, pady=10, cursor='hand2',
                            command=lambda k=page_key: self.show_page(k))
            btn.pack(fill=tk.X, pady=2)
            self.nav_buttons[page_key] = btn

        agent_info_box = tk.Frame(self.sidebar, bg=COLORS['sidebar_hover'], padx=12, pady=12)
        agent_info_box.pack(side=tk.BOTTOM, fill=tk.X, padx=12, pady=16)

        tk.Label(agent_info_box, text="AGENT MODEL", font=('Segoe UI', 7, 'bold'),
                 fg=COLORS['sidebar_muted'], bg=COLORS['sidebar_hover']).pack(anchor='w')
        tk.Label(agent_info_box, text="Utility-Based Intelligent Agent", font=('Segoe UI', 8, 'bold'),
                 fg='#e2e8f0', bg=COLORS['sidebar_hover']).pack(anchor='w', pady=(2, 4))
        tk.Label(agent_info_box, text="Priorities:\n1. Safety\n2. User Comfort\n3. Energy Saving",
                 font=('Segoe UI', 8), justify=tk.LEFT, fg='#94a3b8', bg=COLORS['sidebar_hover']).pack(anchor='w')

        self.pages = {}
        self.pages['dashboard'] = self._build_dashboard_page()
        self.pages['sensors'] = self._build_sensors_page()
        self.pages['appliances'] = self._build_appliances_page()
        self.pages['history'] = self._build_history_page()

        self.show_page('dashboard')

    def show_page(self, page_key: str):
        for k, p in self.pages.items():
            p.pack_forget()
            self.nav_buttons[k].configure(bg=COLORS['sidebar_bg'])

        self.pages[page_key].pack(fill=tk.BOTH, expand=True)
        self.nav_buttons[page_key].configure(bg=COLORS['sidebar_active'])

    def _build_dashboard_page(self):
        page = tk.Frame(self.content_area, bg=COLORS['main_bg'])

        top_row = tk.Frame(page, bg=COLORS['main_bg'])
        top_row.pack(fill=tk.X, pady=(0, 14))

        c1 = self._create_card(top_row, "AI AGENT STATUS")
        c1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        self.dash_agent_status = tk.Label(c1, text="IDLE / READY", font=('Segoe UI', 13, 'bold'),
                                          fg=COLORS['primary_blue'], bg=COLORS['card_bg'])
        self.dash_agent_status.pack(anchor='w', pady=(4, 0))
        self.dash_agent_sub = tk.Label(c1, text="Select Automatic or Manual below", font=('Segoe UI', 8),
                                       fg=COLORS['text_muted'], bg=COLORS['card_bg'])
        self.dash_agent_sub.pack(anchor='w')

        c2 = self._create_card(top_row, "SIMULATED ENERGY USED")
        c2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        self.dash_energy_used = tk.Label(c2, text="0.0000 kWh", font=('Segoe UI', 13, 'bold'),
                                         fg='#ea580c', bg=COLORS['card_bg'])
        self.dash_energy_used.pack(anchor='w', pady=(4, 0))
        self.dash_watts = tk.Label(c2, text="Current Draw: 0 W", font=('Segoe UI', 8),
                                   fg=COLORS['text_muted'], bg=COLORS['card_bg'])
        self.dash_watts.pack(anchor='w')

        c3 = self._create_card(top_row, "ESTIMATED ENERGY SAVED")
        c3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))
        self.dash_energy_saved = tk.Label(c3, text="0.0000 kWh", font=('Segoe UI', 13, 'bold'),
                                          fg=COLORS['on_green'], bg=COLORS['card_bg'])
        self.dash_energy_saved.pack(anchor='w', pady=(4, 0))
        self.dash_saved_sub = tk.Label(c3, text="Saved vs Peak Load (1415W)", font=('Segoe UI', 8),
                                       fg=COLORS['text_muted'], bg=COLORS['card_bg'])
        self.dash_saved_sub.pack(anchor='w')

        mid_row = tk.Frame(page, bg=COLORS['main_bg'])
        mid_row.pack(fill=tk.BOTH, expand=True, pady=(0, 14))

        snap_card = self._create_card(mid_row, "LIVE SENSOR SNAPSHOT")
        snap_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self.dash_sensors = {}
        sensor_fields = [
            ("person", "Person / Motion:"),
            ("temp", "Temperature:"),
            ("light", "Light Level:"),
            ("door", "Door Status:"),
            ("air", "Air Quality:"),
            ("time", "Time of Reading:")
        ]
        grid_s = tk.Frame(snap_card, bg=COLORS['card_bg'])
        grid_s.pack(fill=tk.BOTH, expand=True, pady=6)

        for idx, (k, label_text) in enumerate(sensor_fields):
            row = idx
            tk.Label(grid_s, text=label_text, font=('Segoe UI', 9),
                     fg=COLORS['text_secondary'], bg=COLORS['card_bg']).grid(row=row, column=0, sticky='w', pady=4)
            val_lbl = tk.Label(grid_s, text="--", font=('Segoe UI', 9, 'bold'),
                               fg=COLORS['text_primary'], bg=COLORS['card_bg'])
            val_lbl.grid(row=row, column=1, sticky='e', padx=(20, 0), pady=4)
            grid_s.columnconfigure(1, weight=1)
            self.dash_sensors[k] = val_lbl

        app_card = self._create_card(mid_row, "SMART APPLIANCES CONTROL")
        app_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        self.dash_appliances = {}
        appliance_defs = [
            ("light", "💡 Smart Light", "60 W"),
            ("fan", "🌀 Smart Fan", "75 W"),
            ("ac", "❄ Smart AC", "1200 W"),
            ("air_purifier", "🌬 Air Purifier", "80 W")
        ]
        grid_a = tk.Frame(app_card, bg=COLORS['card_bg'])
        grid_a.pack(fill=tk.BOTH, expand=True, pady=6)

        for idx, (k, name, rating) in enumerate(appliance_defs):
            row = idx
            left_f = tk.Frame(grid_a, bg=COLORS['card_bg'])
            left_f.grid(row=row, column=0, sticky='w', pady=6)
            tk.Label(left_f, text=name, font=('Segoe UI', 9, 'bold'),
                     fg=COLORS['text_primary'], bg=COLORS['card_bg']).pack(anchor='w')
            tk.Label(left_f, text=f"Rated: {rating}", font=('Segoe UI', 8),
                     fg=COLORS['text_muted'], bg=COLORS['card_bg']).pack(anchor='w')

            badge = tk.Label(grid_a, text="OFF", font=('Segoe UI', 9, 'bold'),
                             fg=COLORS['off_grey'], bg=COLORS['off_grey_bg'],
                             padx=12, pady=3, width=6)
            badge.grid(row=row, column=1, sticky='e', padx=(20, 0), pady=6)
            grid_a.columnconfigure(1, weight=1)
            self.dash_appliances[k] = badge

        bottom_row = tk.Frame(page, bg=COLORS['main_bg'])
        bottom_row.pack(fill=tk.X)

        ctl_card = self._create_card(bottom_row, "CONTROL MODE & ACTIONS")
        ctl_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 8), ipadx=10)

        mode_select_box = tk.Frame(ctl_card, bg=COLORS['card_bg'])
        mode_select_box.pack(anchor='w', pady=(2, 10))

        tk.Radiobutton(mode_select_box, text="AUTOMATIC MODE", variable=self.current_mode,
                       value="AUTOMATIC", font=('Segoe UI', 9, 'bold'),
                       bg=COLORS['card_bg'], activebackground=COLORS['card_bg'],
                       command=self._on_mode_switched).pack(side=tk.LEFT, padx=(0, 14))

        tk.Radiobutton(mode_select_box, text="MANUAL MODE", variable=self.current_mode,
                       value="MANUAL", font=('Segoe UI', 9, 'bold'),
                       bg=COLORS['card_bg'], activebackground=COLORS['card_bg'],
                       command=self._on_mode_switched).pack(side=tk.LEFT)

        btn_box = tk.Frame(ctl_card, bg=COLORS['card_bg'])
        btn_box.pack(fill=tk.X, pady=4)

        self.btn_auto_action = tk.Button(btn_box, text="START AUTO MONITORING",
                                         font=('Segoe UI', 9, 'bold'),
                                         bg=COLORS['primary_blue'], fg='#ffffff',
                                         activebackground=COLORS['primary_hover'], activeforeground='#ffffff',
                                         bd=0, padx=14, pady=8, cursor='hand2',
                                         command=self.toggle_auto_monitoring)
        self.btn_auto_action.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_manual_action = tk.Button(btn_box, text="RUN MANUAL AI",
                                           font=('Segoe UI', 9, 'bold'),
                                           bg=COLORS['sidebar_bg'], fg='#ffffff',
                                           activebackground=COLORS['sidebar_hover'], activeforeground='#ffffff',
                                           bd=0, padx=14, pady=8, cursor='hand2',
                                           state=tk.DISABLED,
                                           command=self.run_manual_ai)
        self.btn_manual_action.pack(side=tk.LEFT)

        reason_card = self._create_card(bottom_row, "AI REASONING (UTILITY-BASED EXPLANATION)")
        reason_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        self.dash_reason_primary = tk.Label(reason_card, text="Awaiting agent evaluation...",
                                            font=('Segoe UI', 10, 'bold'),
                                            fg=COLORS['text_primary'], bg=COLORS['card_bg'],
                                            wraplength=480, justify=tk.LEFT)
        self.dash_reason_primary.pack(anchor='w', pady=(4, 2))

        self.dash_reason_details = tk.Label(reason_card, text="",
                                            font=('Segoe UI', 8),
                                            fg=COLORS['text_secondary'], bg=COLORS['card_bg'],
                                            wraplength=480, justify=tk.LEFT)
        self.dash_reason_details.pack(anchor='w')

        return page

    def _build_sensors_page(self):
        page = tk.Frame(self.content_area, bg=COLORS['main_bg'])

        self.banner_frame = tk.Frame(page, bg='#dbeafe', padx=16, pady=10)
        self.banner_frame.pack(fill=tk.X, pady=(0, 14))

        self.lbl_banner_text = tk.Label(self.banner_frame,
                                        text="AUTOMATIC MODE: Manual fields are disabled. AI will generate sensor values every 7 seconds.",
                                        font=('Segoe UI', 9, 'bold'), fg='#1e40af', bg='#dbeafe')
        self.lbl_banner_text.pack(anchor='w')

        split = tk.Frame(page, bg=COLORS['main_bg'])
        split.pack(fill=tk.BOTH, expand=True)

        left_card = self._create_card(split, "LIVE SENSOR READOUT (PERCEPTION)")
        left_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self.sensor_page_readouts = {}
        items = [
            ("person", "Person / Motion Sensor", "PIR Infrared"),
            ("temp", "Temperature Sensor", "DHT22 (°C)"),
            ("light", "Light Level Sensor", "LDR Photocell (%)"),
            ("door", "Door Contact Sensor", "Reed Magnetic Switch"),
            ("air", "Air Quality Sensor", "MQ-135 Gas / Particulate (%)")
        ]

        for k, title, desc in items:
            row_f = tk.Frame(left_card, bg=COLORS['card_bg'], pady=6)
            row_f.pack(fill=tk.X)
            t_f = tk.Frame(row_f, bg=COLORS['card_bg'])
            t_f.pack(side=tk.LEFT)
            tk.Label(t_f, text=title, font=('Segoe UI', 9, 'bold'),
                     fg=COLORS['text_primary'], bg=COLORS['card_bg']).pack(anchor='w')
            tk.Label(t_f, text=desc, font=('Segoe UI', 8),
                     fg=COLORS['text_muted'], bg=COLORS['card_bg']).pack(anchor='w')

            val = tk.Label(row_f, text="--", font=('Segoe UI', 10, 'bold'),
                           fg=COLORS['primary_blue'], bg=COLORS['card_bg'])
            val.pack(side=tk.RIGHT)
            self.sensor_page_readouts[k] = val
            ttk.Separator(left_card, orient='horizontal').pack(fill=tk.X, pady=2)

        self.manual_card = self._create_card(split, "MANUAL SENSOR INPUT")
        self.manual_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        self.man_temp_var = tk.StringVar(value="28.0")
        self.man_light_var = tk.StringVar(value="35")
        self.man_person_var = tk.StringVar(value="Detected")
        self.man_door_var = tk.StringVar(value="Closed")
        self.man_air_var = tk.StringVar(value="75")

        form = tk.Frame(self.manual_card, bg=COLORS['card_bg'])
        form.pack(fill=tk.BOTH, expand=True, pady=6)

        tk.Label(form, text="Temperature (°C) [-10 to 60]:", font=('Segoe UI', 9),
                 fg=COLORS['text_secondary'], bg=COLORS['card_bg']).grid(row=0, column=0, sticky='w', pady=6)
        self.entry_temp = tk.Entry(form, textvariable=self.man_temp_var, width=14, font=('Segoe UI', 9))
        self.entry_temp.grid(row=0, column=1, sticky='e', pady=6)

        tk.Label(form, text="Light Level (%) [0 to 100]:", font=('Segoe UI', 9),
                 fg=COLORS['text_secondary'], bg=COLORS['card_bg']).grid(row=1, column=0, sticky='w', pady=6)
        self.entry_light = tk.Entry(form, textvariable=self.man_light_var, width=14, font=('Segoe UI', 9))
        self.entry_light.grid(row=1, column=1, sticky='e', pady=6)

        tk.Label(form, text="Person / Motion:", font=('Segoe UI', 9),
                 fg=COLORS['text_secondary'], bg=COLORS['card_bg']).grid(row=2, column=0, sticky='w', pady=6)
        self.combo_person = ttk.Combobox(form, textvariable=self.man_person_var,
                                         values=["Detected", "Not Detected"], width=12, state="readonly")
        self.combo_person.grid(row=2, column=1, sticky='e', pady=6)

        tk.Label(form, text="Door Status:", font=('Segoe UI', 9),
                 fg=COLORS['text_secondary'], bg=COLORS['card_bg']).grid(row=3, column=0, sticky='w', pady=6)
        self.combo_door = ttk.Combobox(form, textvariable=self.man_door_var,
                                       values=["Closed", "Open"], width=12, state="readonly")
        self.combo_door.grid(row=3, column=1, sticky='e', pady=6)

        tk.Label(form, text="Air Quality (%) [0 to 100]:", font=('Segoe UI', 9),
                 fg=COLORS['text_secondary'], bg=COLORS['card_bg']).grid(row=4, column=0, sticky='w', pady=6)
        self.entry_air = tk.Entry(form, textvariable=self.man_air_var, width=14, font=('Segoe UI', 9))
        self.entry_air.grid(row=4, column=1, sticky='e', pady=6)

        form.columnconfigure(1, weight=1)

        tk.Label(self.manual_card, text="Quick Academic Presets:", font=('Segoe UI', 8, 'bold'),
                 fg=COLORS['text_muted'], bg=COLORS['card_bg']).pack(anchor='w', pady=(12, 4))

        preset_row = tk.Frame(self.manual_card, bg=COLORS['card_bg'])
        preset_row.pack(fill=tk.X, pady=2)

        p1 = tk.Button(preset_row, text="Hot (AC ON)", font=('Segoe UI', 8),
                       bg='#e2e8f0', bd=0, padx=6, pady=3, cursor='hand2',
                       command=lambda: self._set_preset(32.0, 30, "Detected", "Closed", 85))
        p1.pack(side=tk.LEFT, padx=(0, 4))

        p2 = tk.Button(preset_row, text="Warm (Fan ON)", font=('Segoe UI', 8),
                       bg='#e2e8f0', bd=0, padx=6, pady=3, cursor='hand2',
                       command=lambda: self._set_preset(27.5, 55, "Detected", "Closed", 80))
        p2.pack(side=tk.LEFT, padx=4)

        p3 = tk.Button(preset_row, text="Empty Home", font=('Segoe UI', 8),
                       bg='#e2e8f0', bd=0, padx=6, pady=3, cursor='hand2',
                       command=lambda: self._set_preset(33.0, 20, "Not Detected", "Closed", 80))
        p3.pack(side=tk.LEFT, padx=4)

        p4 = tk.Button(preset_row, text="Poor Air (<60%)", font=('Segoe UI', 8),
                       bg='#e2e8f0', bd=0, padx=6, pady=3, cursor='hand2',
                       command=lambda: self._set_preset(24.0, 60, "Detected", "Closed", 45))
        p4.pack(side=tk.LEFT, padx=4)

        self.btn_sensors_run_manual = tk.Button(self.manual_card, text="RUN MANUAL AI",
                                                font=('Segoe UI', 9, 'bold'),
                                                bg=COLORS['primary_blue'], fg='#ffffff',
                                                activebackground=COLORS['primary_hover'],
                                                bd=0, padx=16, pady=8, cursor='hand2',
                                                state=tk.DISABLED,
                                                command=self.run_manual_ai)
        self.btn_sensors_run_manual.pack(fill=tk.X, pady=(16, 4))

        return page

    def _set_preset(self, temp, light, person, door, air):
        if self.current_mode.get() != "MANUAL":
            messagebox.showinfo("Mode Notice", "Switch to MANUAL mode to load presets and run manual AI.")
            return
        self.man_temp_var.set(str(temp))
        self.man_light_var.set(str(light))
        self.man_person_var.set(person)
        self.man_door_var.set(door)
        self.man_air_var.set(str(air))

    def _build_appliances_page(self):
        page = tk.Frame(self.content_area, bg=COLORS['main_bg'])

        header_lbl = tk.Label(page, text="Smart Appliances Actuator Control",
                              font=('Segoe UI', 13, 'bold'),
                              fg=COLORS['text_primary'], bg=COLORS['main_bg'])
        header_lbl.pack(anchor='w', pady=(0, 12))

        grid = tk.Frame(page, bg=COLORS['main_bg'])
        grid.pack(fill=tk.BOTH, expand=True)

        app_specs = [
            ("light", "💡 Smart Light", "60 W",
             "Rule: Light = ON only when Person is Detected AND Ambient Light < 40%. Otherwise Light = OFF to conserve power."),
            ("fan", "🌀 Smart Fan", "75 W",
             "Rule: Fan = ON when Person is Detected AND Temp is between 25°C and 30°C (AC remains OFF). If Temp < 25°C or room is empty, Fan = OFF."),
            ("ac", "❄ Smart AC", "1200 W",
             "Rule: AC = ON when Person is Detected AND Temp >= 30°C (Fan turns OFF). Heavy load is disabled immediately when room is unoccupied."),
            ("air_purifier", "🌬 Air Purifier", "80 W",
             "Rule: Air Purifier = ON whenever Air Quality drops below 60% (Safety priority). Operates independently of room occupancy for health protection.")
        ]

        self.app_page_badges = {}

        for i, (k, name, rating, rule_desc) in enumerate(app_specs):
            row = i // 2
            col = i % 2
            card = self._create_card(grid, f"{name.upper()}  •  {rating}")
            card.grid(row=row, column=col, sticky='nsew', padx=8, pady=8)

            badge_frame = tk.Frame(card, bg=COLORS['card_bg'])
            badge_frame.pack(fill=tk.X, pady=(6, 12))

            tk.Label(badge_frame, text="Current Status:", font=('Segoe UI', 9),
                     fg=COLORS['text_secondary'], bg=COLORS['card_bg']).pack(side=tk.LEFT)

            b = tk.Label(badge_frame, text="OFF", font=('Segoe UI', 9, 'bold'),
                         fg=COLORS['off_grey'], bg=COLORS['off_grey_bg'],
                         padx=12, pady=4, width=6)
            b.pack(side=tk.LEFT, padx=12)
            self.app_page_badges[k] = b

            tk.Label(card, text="Agent Control Logic & Utility Justification:", font=('Segoe UI', 8, 'bold'),
                     fg=COLORS['text_muted'], bg=COLORS['card_bg']).pack(anchor='w', pady=(4, 2))

            tk.Label(card, text=rule_desc, font=('Segoe UI', 8),
                     fg=COLORS['text_secondary'], bg=COLORS['card_bg'],
                     wraplength=340, justify=tk.LEFT).pack(anchor='w')

            grid.rowconfigure(row, weight=1)
            grid.columnconfigure(col, weight=1)

        return page

    def _build_history_page(self):
        page = tk.Frame(self.content_area, bg=COLORS['main_bg'])

        top_f = tk.Frame(page, bg=COLORS['main_bg'])
        top_f.pack(fill=tk.X, pady=(0, 10))

        tk.Label(top_f, text="Decision History Log", font=('Segoe UI', 13, 'bold'),
                 fg=COLORS['text_primary'], bg=COLORS['main_bg']).pack(side=tk.LEFT)

        btn_clear = tk.Button(top_f, text="CLEAR HISTORY", font=('Segoe UI', 8, 'bold'),
                              bg=COLORS['alert_red'], fg='#ffffff',
                              activebackground='#b91c1c', activeforeground='#ffffff',
                              bd=0, padx=12, pady=6, cursor='hand2',
                              command=self.clear_history)
        btn_clear.pack(side=tk.RIGHT)

        tree_card = self._create_card(page, "SESSION DECISIONS TABLE (CLICK TO INSPECT)")
        tree_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        columns = ("id", "time", "mode", "person", "temp", "light_in", "door", "air",
                   "light_out", "fan_out", "ac_out", "purifier_out")

        self.tree = ttk.Treeview(tree_card, columns=columns, show='headings', selectmode='browse')

        col_configs = [
            ("id", "No", 45, 'center'),
            ("time", "Time", 75, 'center'),
            ("mode", "Mode", 80, 'center'),
            ("person", "Person", 65, 'center'),
            ("temp", "Temp", 65, 'center'),
            ("light_in", "Light", 65, 'center'),
            ("door", "Door", 85, 'center'),
            ("air", "Air", 60, 'center'),
            ("light_out", "Light", 55, 'center'),
            ("fan_out", "Fan", 55, 'center'),
            ("ac_out", "AC", 55, 'center'),
            ("purifier_out", "Purifier", 65, 'center')
        ]

        for col_id, heading_text, width, align in col_configs:
            self.tree.heading(col_id, text=heading_text)
            self.tree.column(col_id, width=width, anchor=align)

        tree_scroll_y = ttk.Scrollbar(tree_card, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y, pady=4)

        self.tree.bind('<<TreeviewSelect>>', self._on_history_row_selected)

        self.detail_card = self._create_card(page, "SELECTED RECORD INSPECTION")
        self.detail_card.pack(fill=tk.X)

        d_grid = tk.Frame(self.detail_card, bg=COLORS['card_bg'])
        d_grid.pack(fill=tk.X, pady=4)

        self.lbl_hist_detail_energy = tk.Label(d_grid, text="Energy: Select a record from above",
                                               font=('Segoe UI', 9, 'bold'),
                                               fg=COLORS['text_primary'], bg=COLORS['card_bg'])
        self.lbl_hist_detail_energy.pack(anchor='w')

        self.lbl_hist_detail_reason = tk.Label(d_grid, text="",
                                               font=('Segoe UI', 8),
                                               fg=COLORS['text_secondary'], bg=COLORS['card_bg'],
                                               justify=tk.LEFT)
        self.lbl_hist_detail_reason.pack(anchor='w', pady=(2, 0))

        return page

    def _on_history_row_selected(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        record_id = item['values'][0]
        rec = next((r for r in self.history_mgr.records if r['id'] == record_id), None)
        if rec:
            self.lbl_hist_detail_energy.config(
                text=f"Record #{rec['id']} ({rec['mode']}) at {rec['time']} | "
                     f"Interval Energy Used: {rec['used_kwh']:.6f} kWh | "
                     f"Estimated Saved: {rec['saved_kwh']:.6f} kWh"
            )
            self.lbl_hist_detail_reason.config(
                text=f"AI Reasoning Breakdown:\n{rec['reasoning']}"
            )

    def clear_history(self):
        if not self.history_mgr.records:
            return
        if messagebox.askyesno("Confirm Clear", "Clear all session decision records?"):
            self.history_mgr.clear()
            for row in self.tree.get_children():
                self.tree.delete(row)
            self.lbl_hist_detail_energy.config(text="Energy: Select a record from above")
            self.lbl_hist_detail_reason.config(text="")

    def _create_card(self, parent, title: str):
        # Return the actual card widget that callers can safely pack/grid.
        # The previous version returned a child widget whose parent was
        # `outer`, which caused Tkinter geometry-manager errors and left
        # the main content area blank.
        card = tk.Frame(parent, bg=COLORS['card_bg'], padx=14, pady=12,
                        highlightbackground=COLORS['card_border'],
                        highlightthickness=1)

        lbl = tk.Label(card, text=title, font=('Segoe UI', 8, 'bold'),
                       fg=COLORS['text_muted'], bg=COLORS['card_bg'])
        lbl.pack(anchor='w')
        return card

    def _on_mode_switched(self):
        mode = self.current_mode.get()
        if mode == "AUTOMATIC":
            self.lbl_mode_pill.config(text="AUTO MODE READY", fg='#38bdf8', bg=COLORS['sidebar_hover'])
            self.dash_agent_status.config(text="AUTO MODE READY", fg=COLORS['primary_blue'])
            self.dash_agent_sub.config(text="Click START AUTO MONITORING to begin periodic cycle")

            self.btn_auto_action.config(state=tk.NORMAL)
            self.btn_manual_action.config(state=tk.DISABLED)
            self.btn_sensors_run_manual.config(state=tk.DISABLED)

            self.entry_temp.config(state=tk.DISABLED)
            self.entry_light.config(state=tk.DISABLED)
            self.combo_person.config(state=tk.DISABLED)
            self.combo_door.config(state=tk.DISABLED)
            self.entry_air.config(state=tk.DISABLED)

            self.lbl_banner_text.config(
                text="AUTOMATIC MODE: Manual fields are disabled. AI will generate sensor values every 7 seconds.",
                fg='#1e40af', bg='#dbeafe'
            )
            self.banner_frame.config(bg='#dbeafe')
        else:
            if self.is_monitoring_active:
                self.stop_auto_monitoring()

            self.lbl_mode_pill.config(text="MANUAL INPUT READY", fg='#fbbf24', bg=COLORS['sidebar_hover'])
            self.dash_agent_status.config(text="MANUAL INPUT READY", fg='#d97706')
            self.dash_agent_sub.config(text="Enter values and click RUN MANUAL AI for one-shot decision")

            self.btn_auto_action.config(state=tk.DISABLED)
            self.btn_manual_action.config(state=tk.NORMAL)
            self.btn_sensors_run_manual.config(state=tk.NORMAL)

            self.entry_temp.config(state=tk.NORMAL)
            self.entry_light.config(state=tk.NORMAL)
            self.combo_person.config(state="readonly")
            self.combo_door.config(state="readonly")
            self.entry_air.config(state=tk.NORMAL)

            self.lbl_banner_text.config(
                text="MANUAL MODE: Enter values → click RUN MANUAL AI.",
                fg='#92400e', bg='#fef3c7'
            )
            self.banner_frame.config(bg='#fef3c7')

    def toggle_auto_monitoring(self):
        if self.is_monitoring_active:
            self.stop_auto_monitoring()
        else:
            self.start_auto_monitoring()

    def start_auto_monitoring(self):
        if self.current_mode.get() != "AUTOMATIC":
            self.current_mode.set("AUTOMATIC")
            self._on_mode_switched()

        self.is_monitoring_active = True
        self.btn_auto_action.config(text="STOP AUTO MONITORING", bg=COLORS['alert_red'],
                                    activebackground='#b91c1c')
        self.lbl_mode_pill.config(text="AUTO MONITORING ACTIVE", fg='#22c55e', bg=COLORS['sidebar_hover'])
        self.dash_agent_status.config(text="AUTO MONITORING ACTIVE", fg=COLORS['on_green'])
        self.dash_agent_sub.config(text="Cycle running: Generating simulated sensors every 7 seconds")

        self._auto_cycle()

    def stop_auto_monitoring(self):
        self.is_monitoring_active = False
        if self.auto_timer_id:
            self.after_cancel(self.auto_timer_id)
            self.auto_timer_id = None

        self.btn_auto_action.config(text="START AUTO MONITORING", bg=COLORS['primary_blue'],
                                    activebackground=COLORS['primary_hover'])
        self.lbl_mode_pill.config(text="AUTO MODE STOPPED", fg='#94a3b8', bg=COLORS['sidebar_hover'])
        self.dash_agent_status.config(text="AUTO MODE STOPPED", fg=COLORS['text_muted'])
        self.dash_agent_sub.config(text="Monitoring paused. Click START AUTO MONITORING to resume")

    def _auto_cycle(self):
        if not self.is_monitoring_active:
            return

        sensor = self.simulator.next_reading()
        decision = UtilityAgentEngine.evaluate(sensor, mode="AUTOMATIC", interval_sec=7.0)
        self._apply_decision(decision)
        self.auto_timer_id = self.after(7000, self._auto_cycle)

    def run_manual_ai(self):
        if self.current_mode.get() != "MANUAL":
            return

        try:
            temp_val = float(self.man_temp_var.get().strip())
            if not (-10.0 <= temp_val <= 60.0):
                messagebox.showerror("Validation Error", "Temperature must be between -10°C and 60°C.")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid numeric value for Temperature (-10 to 60).")
            return

        try:
            light_val = int(float(self.man_light_var.get().strip()))
            if not (0 <= light_val <= 100):
                messagebox.showerror("Validation Error", "Light Level must be an integer between 0% and 100%.")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid numeric value for Light Level (0 to 100).")
            return

        try:
            air_val = int(float(self.man_air_var.get().strip()))
            if not (0 <= air_val <= 100):
                messagebox.showerror("Validation Error", "Air Quality must be an integer between 0% and 100%.")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid numeric value for Air Quality (0 to 100).")
            return

        person_val = (self.man_person_var.get() == "Detected")
        door_val = (self.man_door_var.get() == "Open")

        sensor = SensorData(
            person=person_val,
            temp=temp_val,
            light=light_val,
            door=door_val,
            air=air_val,
            timestamp=datetime.now().strftime("%H:%M:%S")
        )

        decision = UtilityAgentEngine.evaluate(sensor, mode="MANUAL", interval_sec=10.0)
        self._apply_decision(decision)

        self.dash_agent_status.config(text="MANUAL DECISION COMPLETED", fg=COLORS['primary_blue'])
        self.lbl_mode_pill.config(text="MANUAL DECISION COMPLETED", fg='#38bdf8', bg=COLORS['sidebar_hover'])
        self.dash_agent_sub.config(text=f"Evaluated at {sensor.timestamp}. Decision saved in history.")

        # After running Manual AI, automatically open the Sensors page
        # so the user can immediately see the manual sensor inputs/readouts.
        self.show_page("sensors")

    def _apply_decision(self, decision: DecisionResult):
        self.current_decision = decision

        self.energy_mgr.add(decision.interval_used_kwh, decision.interval_saved_kwh)
        self.dash_energy_used.config(text=f"{self.energy_mgr.total_used_kwh:.4f} kWh")
        self.dash_energy_saved.config(text=f"{self.energy_mgr.total_saved_kwh:.4f} kWh")
        self.dash_watts.config(text=f"Current Draw: {decision.instant_watts} W")

        s = decision.sensor
        self.dash_sensors['person'].config(text="Detected" if s.person else "Not Detected",
                                           fg=COLORS['on_green'] if s.person else COLORS['text_muted'])
        self.dash_sensors['temp'].config(text=f"{s.temp:.1f} °C")
        self.dash_sensors['light'].config(text=f"{s.light} %")
        self.dash_sensors['door'].config(text=decision.door_status,
                                         fg=COLORS['alert_red'] if s.door else COLORS['on_green'])
        self.dash_sensors['air'].config(text=f"{s.air} %",
                                        fg=COLORS['alert_red'] if s.air < 60 else COLORS['on_green'])
        self.dash_sensors['time'].config(text=decision.timestamp)

        if hasattr(self, 'sensor_page_readouts'):
            self.sensor_page_readouts['person'].config(text="Detected" if s.person else "Not Detected")
            self.sensor_page_readouts['temp'].config(text=f"{s.temp:.1f} °C")
            self.sensor_page_readouts['light'].config(text=f"{s.light} %")
            self.sensor_page_readouts['door'].config(text=decision.door_status)
            self.sensor_page_readouts['air'].config(text=f"{s.air} %")

        app_states = {
            'light': decision.light,
            'fan': decision.fan,
            'ac': decision.ac,
            'air_purifier': decision.air_purifier
        }

        for k, is_on in app_states.items():
            text = "ON" if is_on else "OFF"
            fg = COLORS['on_green'] if is_on else COLORS['off_grey']
            bg = COLORS['on_green_bg'] if is_on else COLORS['off_grey_bg']

            if k in self.dash_appliances:
                self.dash_appliances[k].config(text=text, fg=fg, bg=bg)

            if hasattr(self, 'app_page_badges') and k in self.app_page_badges:
                self.app_page_badges[k].config(text=text, fg=fg, bg=bg)

        self.dash_reason_primary.config(text=decision.primary_reason)
        details_text = "\n".join(f"• {r}" for r in decision.reasons)
        self.dash_reason_details.config(text=details_text)

        rec = self.history_mgr.add_record(decision)
        if hasattr(self, 'tree'):
            item_id = self.tree.insert('', tk.END, values=(
                rec['id'], rec['time'], rec['mode'], rec['person'], rec['temp'],
                rec['light_in'], rec['door'], rec['air'],
                rec['light_out'], rec['fan_out'], rec['ac_out'], rec['purifier_out']
            ))
            self.tree.see(item_id)

    def _run_initial_seed(self):
        seed_sensor = SensorData(person=True, temp=28.5, light=35, door=False, air=75)
        decision = UtilityAgentEngine.evaluate(seed_sensor, mode="AUTOMATIC", interval_sec=1.0)
        self._apply_decision(decision)
        self._on_mode_switched()


def main():
    try:
        app = SmartHomeDesktopApp()
        app.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}", file=sys.stderr)


if __name__ == '__main__':
    main()
