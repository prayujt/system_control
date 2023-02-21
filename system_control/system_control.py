import queue
import sys
import json
import sounddevice as sd
import argparse

from vosk import Model, KaldiRecognizer

from system_control.hand_movements.mouse_control import MouseControl

q = queue.Queue()


def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def main():
    devices = sd.query_devices()
    audio_idx = 0
    sample_rate = 48000

    parser = argparse.ArgumentParser(
        prog='system_control',
        description='An implementation of Linux system control through offline speech recognition and computer vision ',
        epilog='Text at the bottom of help'
    )

    parser.add_argument('model')
    parser.add_argument('-m', '--microphone_name')

    args = parser.parse_args()

    if args.microphone_name is not None:
        for idx in range(0, len(devices)):
            if args.microphone_name in devices[idx]['name']:
                audio_idx = idx
                sample_rate = devices[idx]['default_samplerate']
    else:
        print("No microphone provided... Using default.")

    device_info = sd.query_devices(audio_idx, "input")
    sample_rate = device_info["default_samplerate"]
    model = Model(args.model)

    with sd.RawInputStream(samplerate=sample_rate, blocksize=8092, device=audio_idx, dtype="int16", channels=1, callback=callback):
        rec = KaldiRecognizer(model, sample_rate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if result["text"] == "activate hand tracking":
                    MouseControl().start()
            else:
                partial = json.loads(rec.PartialResult())['partial']
                if partial != '':
                    print(partial)
