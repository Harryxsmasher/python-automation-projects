import sys, os, subprocess, time, datetime

# ===========================
# ✅ SAFE LOG (FINAL FIX)
# ===========================
def log(msg):
    safe = str(msg).encode("utf-8", errors="ignore").decode("utf-8")
    print(safe + "\n", flush=True)

# ===========================
# ✅ PREVENT VRED PYTHON
# ===========================
if "VREDPro" in sys.executable:
    log("ERROR: Running inside VRED Python")
    sys.exit()

log("Running Python: " + sys.executable)

# ===========================
# ✅ FFMPEG FIX
# ===========================
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
os.environ["FFMPEG_BINARY"] = FFMPEG_PATH
os.environ["PATH"] = r"C:\ffmpeg\bin;" + os.environ["PATH"]

# ===========================
# ✅ IMPORTS
# ===========================
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import whisper

# ===========================
# ✅ STORAGE
# ===========================
BASE_FOLDER = r"C:\Users\50008944\Desktop\ReviewTranscribes"
os.makedirs(BASE_FOLDER, exist_ok=True)

STOP_FILE  = r"C:\Users\50008944\Desktop\VTT\stop.txt"
PAUSE_FILE = r"C:\Users\50008944\Desktop\VTT\pause.txt"

SCENE_NAME = os.environ.get("VRED_SCENE_NAME", "UnknownScene")
safe_scene = SCENE_NAME.replace(" ", "_")

for f in [STOP_FILE, PAUSE_FILE]:
    if os.path.exists(f):
        os.remove(f)

# ===========================
# ✅ MIC DETECTION
# ===========================
def find_mic():
    log("Searching microphone...")
    devices = sd.query_devices()

    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            try:
                fs = int(dev['default_samplerate'])
                buf = []

                def cb(indata, frames, t, status):
                    buf.append(np.linalg.norm(indata))

                s = sd.InputStream(device=i, channels=1, samplerate=fs, callback=cb)
                s.start(); time.sleep(1)
                s.stop(); s.close()

                if buf and max(buf) > 0.001:
                    log("Using MIC: " + dev['name'])
                    return i, fs
            except:
                continue

    log("No active mic found")
    sys.exit()

device, fs = find_mic()

# ===========================
# ✅ AUDIO
# ===========================
recording = []
last_log = 0

def calc_db(indata):
    rms = np.sqrt(np.mean(indata**2))
    return -100 if rms == 0 else 20*np.log10(rms)

def callback(indata, frames, t, status):
    global recording, last_log

    if os.path.exists(PAUSE_FILE):
        return

    recording.append(indata.copy())

    now = time.time()
    if now - last_log < 0.08:
        return

    last_log = now
    log(f"LEVEL:{round(calc_db(indata),1)}")

# ===========================
# ✅ START RECORDING
# ===========================
log("Recording started")
start = time.time()

stream = sd.InputStream(device=device, channels=1, samplerate=fs, callback=callback)
stream.start()

last_time = 0
paused = False

while True:
    now = time.time()
    elapsed = now - start

    if os.path.exists(PAUSE_FILE):
        if not paused:
            log("PAUSED")
            paused = True
        time.sleep(0.2)
        continue
    else:
        if paused:
            log("RESUMED")
            paused = False

    if now - last_time >= 1:
        log(f"TIME:{round(elapsed,1)}")
        last_time = now

    if elapsed > 2 and os.path.exists(STOP_FILE):
        log("STOP")
        os.remove(STOP_FILE)
        break

    time.sleep(0.1)

# ===========================
# ✅ STOP
# ===========================
stream.stop()
stream.close()

log("Recording stopped")

if len(recording) == 0:
    log("ERROR: No audio")
    sys.exit()

audio = np.concatenate(recording)

if np.max(audio) == 0:
    log("ERROR: Silence")
    sys.exit()

# ===========================
# ✅ SAVE FILES
# ===========================
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

wav = os.path.join(BASE_FOLDER, f"{safe_scene}_VoiceNote_{ts}.wav")
txt = os.path.join(BASE_FOLDER, f"{safe_scene}_VoiceNote_{ts}.txt")

write(wav, fs, audio)
log("AUDIO:" + wav)

# ===========================
# ✅ TRANSCRIBE
# ===========================
log("TRANSCRIBING")

model = whisper.load_model("base")
result = model.transcribe(wav, fp16=False)

with open(txt, "w", encoding="utf-8") as f:
    f.write(result["text"])

# ✅ SAFE PRINT (NO CRASH)
log("TEXT:" + result["text"])
log("DONE")