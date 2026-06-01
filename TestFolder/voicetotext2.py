import os
# ✅ FFmpeg path (NO admin needed)
os.environ["PATH"] = r"C:\ffmpeg\bin;" + os.environ["PATH"]

import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import whisper
import datetime
import time
import threading

recording = []
is_recording = False
stream = None
start_time = None

selected_device = None
selected_channels = None
selected_fs = None


# ✅ AUTO-DETECT ACTIVE MIC (WITH REAL SIGNAL)
def find_active_mic():
    print("\n🔍 Searching for ACTIVE microphone...\n")
    devices = sd.query_devices()

    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            try:
                fs = int(dev['default_samplerate'])
                channels = dev['max_input_channels']

                buffer = []

                def test_callback(indata, frames, time_info, status):
                    buffer.append(np.linalg.norm(indata))

                test_stream = sd.InputStream(
                    device=i,
                    channels=channels,
                    samplerate=fs,
                    callback=test_callback
                )

                test_stream.start()
                time.sleep(1.0)
                test_stream.stop()
                test_stream.close()

                # ✅ Check real signal
                if len(buffer) > 0 and max(buffer) > 0.01:
                    print(f"✅ Using MIC: {dev['name']}")
                    return i, channels, fs

            except:
                continue

    print("❌ No active microphone found")
    return None, None, None


# ✅ dB CALCULATION
def calculate_db(indata):
    rms = np.sqrt(np.mean(indata**2))
    if rms == 0:
        return -100
    return 20 * np.log10(rms)


# ✅ EQUALIZER + dB DISPLAY
def print_audio_meter(indata):
    db = calculate_db(indata)

    bar_len = int((db + 60) * 1.5)  # scale
    bar_len = max(0, min(50, bar_len))

    bar = "█" * bar_len + "-" * (50 - bar_len)

    print(f"\r🎤 {db:6.1f} dB | [{bar}]", end="", flush=True)


# ✅ CALLBACK
def callback(indata, frames, time_info, status):
    if is_recording:
        recording.append(indata.copy())
        print_audio_meter(indata)


# ✅ START RECORDING
def start_recording():
    global is_recording, recording, stream, start_time
    global selected_device, selected_channels, selected_fs

    if selected_device is None:
        selected_device, selected_channels, selected_fs = find_active_mic()

        if selected_device is None:
            return

    recording = []
    is_recording = True
    start_time = time.time()

    stream = sd.InputStream(
        device=selected_device,
        channels=selected_channels,
        samplerate=selected_fs,
        callback=callback
    )

    stream.start()

    print("\n✅ Recording started... speak now\n")

    threading.Thread(target=timer, daemon=True).start()


# ✅ STOP RECORDING
def stop_recording():
    global is_recording, stream

    if not is_recording:
        print("⚠️ Not recording")
        return

    is_recording = False
    time.sleep(0.5)

    stream.stop()
    stream.close()

    duration = time.time() - start_time
    print(f"\n\n✅ Recording stopped ({duration:.2f} sec)")

    if len(recording) == 0:
        print("❌ No audio captured")
        return

    audio = np.concatenate(recording)

    # ✅ convert to mono if needed
    if selected_channels > 1:
        audio = audio.mean(axis=1)

    if np.max(audio) == 0:
        print("❌ Silence detected")
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    wav_file = f"recording_{timestamp}.wav"
    txt_file = f"recording_{timestamp}.txt"

    write(wav_file, selected_fs, audio)
    print(f"✅ Audio saved: {wav_file}")

    # ✅ Whisper transcription
    print("Transcribing...")
    model = whisper.load_model("base")
    result = model.transcribe(wav_file)

    with open(txt_file, "w") as f:
        f.write(result["text"])

    print(f"✅ Text saved: {txt_file}")
    print("📝", result["text"])


# ✅ TIMER
def timer():
    while is_recording:
        elapsed = time.time() - start_time
        print(f"\n⏱ {elapsed:.1f} sec", end="", flush=True)
        time.sleep(2)


# ✅ MAIN LOOP
print("\nControls: s = start | p = stop | q = quit")

while True:
    cmd = input("\nEnter command: ").lower()

    if cmd == 's':
        start_recording()

    elif cmd == 'p':
        stop_recording()

    elif cmd == 'q':
        print("Exiting...")
        break

    else:
        print("Invalid input")