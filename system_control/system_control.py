import queue
import sys
import json
import sounddevice as sd
import argparse
import time
import os

from vosk import Model, KaldiRecognizer

from .processor import Processor

q = queue.Queue()


def process(result):
    pass


def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def main():
    devices = sd.query_devices()
    audio_idx = 0
    sample_rate = 48000

    parser = argparse.ArgumentParser(
        prog="system_control",
        description="An implementation of Linux system control through offline speech recognition and computer vision ",
        epilog="Text at the bottom of help",
    )

    parser.add_argument("model")
    parser.add_argument("-m", "--microphone_name")
    parser.add_argument("-c", "--camera_index")
    parser.add_argument("-w", "--word_file")

    args = parser.parse_args()
    if args.microphone_name is not None:
        for idx in range(0, len(devices)):
            if args.microphone_name in devices[idx]["name"]:
                audio_idx = idx
                sample_rate = devices[idx]["default_samplerate"]
    else:
        print("No microphone provided... Using default.")

    device_info = sd.query_devices(audio_idx, "input")
    sample_rate = device_info["default_samplerate"]
    model = Model(args.model)

    with sd.RawInputStream(
        samplerate=sample_rate,
        blocksize=8092,
        device=audio_idx,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        rec = KaldiRecognizer(model, sample_rate)
        rec.SetWords(True)
        rec.SetMaxAlternatives(20)

        last_partial = ""
        time_ = time.time()
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                if args.word_file is not None:
                    word_file = open(args.word_file, 'w')
                    data = {
                        "finished": True,
                        "words": last_partial
                    }
                    word_file.write(json.dumps(data))
                    word_file.close()

                Processor(json.loads(rec.Result()), args.camera_index if args.camera_index is not None else 0).process()
                time.sleep(0.5)
                os.system('eww close voice_recognition')
            else:
                partial = json.loads(rec.PartialResult())["partial"]
                partial = partial[4:] if partial[0:3] == "the" else partial

                if partial[0:8] == "computer":
                    partial = partial[9:] if partial[0:8] == "computer" else partial

                    os.system('eww open voice_recognition')
                    word_file = open(args.word_file, 'w')
                    data = {
                        "finished": False,
                        "words": "Listening..." if partial == "" else partial
                    }
                    word_file.write(json.dumps(data))
                    word_file.close()

                if partial == last_partial:

                    if time.time() - time_ > 4:
                        word_file = open(args.word_file, 'w')
                        data = {
                            "finished": False,
                            "words": ""
                        }
                        word_file.write(json.dumps(data))
                        word_file.close()

                        last_partial = ""
                        rec.Reset()
                        time_ = time.time()
                        os.system('eww close voice_recognition')
                    continue

                if partial != "":
                    if args.word_file is not None:
                        word_file = open(args.word_file, 'w')
                        data = {
                            "finished": False,
                            "words": partial
                        }
                        word_file.write(json.dumps(data))
                        word_file.close()

                    last_partial = partial
                    time_ = time.time()
                    print(partial)

                else:
                    if args.word_file is not None:
                        word_file = open(args.word_file, 'w')
                        data = {
                            "finished": False,
                            "words": ""
                        }
                        word_file.write(json.dumps(data))
                        word_file.close()
