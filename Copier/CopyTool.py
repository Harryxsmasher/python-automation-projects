import os
import sys
import subprocess
import json
import time
import shutil
import threading
import logging
import multiprocessing

# ===== AUTO INSTALL =====
def ensure(pkg):
    try:
        __import__(pkg)
    except:
        print(f"Installing {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

for p in ["psutil", "tqdm", "tkinterdnd2"]:
    ensure(p)

import psutil
from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk
from tkinter import ttk, messagebox
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===== AUTO-TUNE =====
def auto_tune():
    cpu = multiprocessing.cpu_count()
    ram = psutil.virtual_memory().total / (1024**3)

    if ram >= 128:
        return min(128, cpu*4), min(64, cpu*2), 64*1024*1024
    elif ram >= 32:
        return min(64, cpu*2), min(32, cpu), 32*1024*1024
    else:
        return min(16, cpu), min(8, cpu), 8*1024*1024

SCAN_WORKERS, COPY_WORKERS, BUFFER_SIZE = auto_tune()

# ===== SYSTEM INFO =====
def get_sys_info():
    cpu = multiprocessing.cpu_count()
    ram = psutil.virtual_memory().total / (1024**3)

    if ram >= 128:
        speed = "150–350 MB/s (network dependent)"
    elif ram >= 32:
        speed = "80–200 MB/s"
    else:
        speed = "30–100 MB/s"

    return cpu, round(ram,1), speed

# ===== CONFIG =====
STATE_FILE = "copy_state.json"
LOG_FILE = os.path.expanduser("~/Desktop/copy_log.txt")
MULTI_DRIVES = ["D:\\"]

logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

pause_flag = threading.Event()
pause_flag.set()

# ===== COPY LOGIC =====
def should_copy(src, dst):
    if not os.path.exists(dst):
        return True
    return (
        os.path.getsize(src) != os.path.getsize(dst) or
        int(os.path.getmtime(src)) != int(os.path.getmtime(dst))
    )

def save_state(files):
    with open(STATE_FILE, "w") as f:
        json.dump(files, f)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return None

def scan(src, ui):
    files=[]
    count=0

    for root,_,fs in os.walk(src):
        for f in fs:
            full=os.path.join(root,f)
            rel=os.path.relpath(full,src)
            files.append([full,rel])
            count+=1

            if count % 200 == 0:
                ui.update_scan(count)

    save_state(files)
    return files

def copy_file(src,dst):
    pause_flag.wait()

    try:
        if not should_copy(src,dst):
            return 0

        os.makedirs(os.path.dirname(dst),exist_ok=True)
        size=os.path.getsize(src)

        with open(src,'rb') as fsrc, open(dst,'wb') as fdst:
            while True:
                chunk=fsrc.read(BUFFER_SIZE)
                if not chunk: break
                fdst.write(chunk)

        logging.info(f"SUCCESS: {src}")
        return size

    except Exception as e:
        logging.error(f"{src} {e}")
        return 0

def choose_drive(i):
    return MULTI_DRIVES[i % len(MULTI_DRIVES)]

def run_copy(src,dst,ui):
    start=time.time()

    files = load_state()
    if files:
        ui.set_status("Resuming...")
    else:
        ui.set_status("Scanning...")
        files = scan(src,ui)

    total_size = sum(os.path.getsize(f[0]) for f in files)
    copied=0

    ui.set_status("Copying...")

    with ThreadPoolExecutor(max_workers=COPY_WORKERS) as ex:
        futures=[]
        for i,f in enumerate(files):
            drive = choose_drive(i)
            dest_path = os.path.join(drive, os.path.basename(dst), f[1])
            futures.append(ex.submit(copy_file, f[0], dest_path))

        for future in as_completed(futures):
            size=future.result()
            copied+=size

            percent = (copied/total_size)*100 if total_size else 0
            speed = copied/(time.time()-start)

            ui.update_progress(percent,speed)

    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)

    ui.set_status("✅ Completed")

# ===== GUI =====
class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("🔥 Ultra Copier Ultimate")
        self.geometry("700x500")
        self.configure(bg="#121212")

        self.src=tk.StringVar()
        self.dst=tk.StringVar()

        # Source
        tk.Label(self,text="Source",fg="white",bg="#121212").pack()
        e1=tk.Entry(self,textvariable=self.src,width=80)
        e1.pack()
        e1.drop_target_register(DND_FILES)
        e1.dnd_bind('<<Drop>>', lambda e:self.src.set(e.data.strip("{}")))

        # Destination
        tk.Label(self,text="Destination",fg="white",bg="#121212").pack()
        e2=tk.Entry(self,textvariable=self.dst,width=80)
        e2.pack()
        e2.drop_target_register(DND_FILES)
        e2.dnd_bind('<<Drop>>', lambda e:self.dst.set(e.data.strip("{}")))

        # ===== SYSTEM INFO PANEL =====
        cpu,ram,speed=get_sys_info()

        frame=tk.LabelFrame(self,text="📊 System Info & Tuning",fg="white",bg="#121212")
        frame.pack(fill="x",pady=10)

        tk.Label(frame,text=f"CPU: {cpu}",fg="white",bg="#121212").pack(anchor="w")
        tk.Label(frame,text=f"RAM: {ram} GB",fg="white",bg="#121212").pack(anchor="w")
        tk.Label(frame,text=f"Scan Threads: {SCAN_WORKERS}",fg="orange",bg="#121212").pack(anchor="w")
        tk.Label(frame,text=f"Copy Threads: {COPY_WORKERS}",fg="orange",bg="#121212").pack(anchor="w")
        tk.Label(frame,text=f"Buffer: {BUFFER_SIZE//(1024*1024)} MB",fg="orange",bg="#121212").pack(anchor="w")
        tk.Label(frame,text=f"Expected Speed: {speed}",fg="cyan",bg="#121212").pack(anchor="w")

        # Status
        self.status=tk.Label(self,text="Idle",fg="cyan",bg="#121212")
        self.status.pack()

        self.scan_lbl=tk.Label(self,text="Scanned: 0",fg="white",bg="#121212")
        self.scan_lbl.pack()

        self.progress=ttk.Progressbar(self,length=600)
        self.progress.pack(pady=10)

        self.speed_lbl=tk.Label(self,text="Speed: 0 MB/s",fg="white",bg="#121212")
        self.speed_lbl.pack()

        # Buttons
        tk.Button(self,text="START",command=self.start).pack()
        tk.Button(self,text="PAUSE",command=lambda: pause_flag.clear()).pack()
        tk.Button(self,text="RESUME",command=lambda: pause_flag.set()).pack()

    def update_scan(self,count):
        self.scan_lbl.config(text=f"Scanned: {count}")
        self.update_idletasks()

    def update_progress(self,percent,speed):
        self.progress['value']=percent
        self.speed_lbl.config(text=f"{speed/(1024**2):.2f} MB/s")
        self.update_idletasks()

    def set_status(self,text):
        self.status.config(text=text)

    def start(self):
        threading.Thread(target=run_copy,args=(self.src.get(),self.dst.get(),self)).start()

# ===== RUN =====
if __name__=="__main__":
    App().mainloop()
