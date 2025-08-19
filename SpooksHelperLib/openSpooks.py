import numpy as np
import matplotlib.pyplot as plt
import subprocess
import os
import tkinter as tk
import tkinter.scrolledtext as tkst
import time
import sys

from datetime import datetime
from pathlib import Path
from tkinter import ttk
from tkinter import filedialog

def OpenSpooks(dev_mode = False, spoof_path = None):
    ################### OPEN WINSPOOKS ###################################
    ######### Check in WinSpooks is running - if not -> Run
    ######### (necessary for license check)
    print("Program started...")

    try:
        res = subprocess.check_output(['tasklist'], text=True).splitlines()
    except Exception as e:
        print("Error checking tasklist:", e)
        return

    is_running = any('WinSpooks.exe' in line for line in res)

    if not is_running:
        # Determine the path (real or spoofed)
        if dev_mode:
            spooks_path = Path(spoof_path) if spoof_path else Path("C:/FakeProgramFiles/WinSpooks/WinSpooks.exe")
            print(f"Dev mode: Would launch {spooks_path}")
            return  # Skip launching in dev mode
        else:
            spooks_path = Path("C:/Program Files (x86)/WinSpooks/WinSpooks.exe")
            if spooks_path.exists():
                subprocess.Popen([str(spooks_path)])
                time.sleep(0.5)
            else:
                print(f"WinSpooks.exe not found at {spooks_path}")
    
    # Optional cleanup (not necessary in Python, but fine)
    res = None
