#!/usr/bin/env python3

import cv2
import numpy as np
import mediapipe as mp
import time
import math
import pulsectl

from .movement_tracker import MovementTracker


class VolumeControl(MovementTracker):
    center_tracking_landmarks = set({0, 9, 13})
    volume_tracking_landmarks = set({4, 8})

    def start(self):
        cap = cv2.VideoCapture(0)
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(min_detection_confidence=0.75)
        mp_draw = mp.solutions.drawing_utils
        p_time = 0
        start_time = time.time()

        while True:
            c_time = time.time()
            fps = 1 / (c_time - p_time)
            p_time = c_time

            success, image = cap.read()
            cv2.putText(image, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image_rgb)

            if results.multi_hand_landmarks:
                if len(results.multi_hand_landmarks) > 1 and time.time() - start_time < 3:
                    continue
                elif len(results.multi_hand_landmarks) > 1:
                    break

                for handLms in results.multi_hand_landmarks:
                    avg_center_x, avg_center_y = 0, 0
                    volume_points = []

                    for idx, lm in enumerate(handLms.landmark):
                        if idx in self.center_tracking_landmarks:
                            h, w, c = image.shape
                            cx, cy = int(lm.x * w), int(lm.y * h)
                            avg_center_x += cx
                            avg_center_y += cy

                        elif idx in self.volume_tracking_landmarks:
                            h, w, c = image.shape
                            cx, cy = int(lm.x * w), int(lm.y * h)
                            volume_points.append([cx, cy])

                    avg_center_x = avg_center_x // len(self.center_tracking_landmarks)
                    avg_center_y = avg_center_y // len(self.center_tracking_landmarks)
                    cv2.circle(image, (avg_center_x, avg_center_y), 25, (255, 0, 255), cv2.FILLED)

                    hypot = math.hypot(*np.diff(volume_points, axis=0)[0])
                    cv2.line(image, volume_points[0], volume_points[1], (255, 0, 255), 3)

                    with pulsectl.Pulse() as pulse:
                        default_sink_name = pulse.server_info().default_sink_name
                        sinks = {s.index: s for s in pulse.sink_list()}
                        sink_index = next(index for index, sink in sinks.items() if sink.name == default_sink_name)
                        sink = sinks[sink_index]
                        sink.volume.value_flat = (0 if hypot < 5 else hypot - 5) / 40
                        pulse.volume_set(sink, sink.volume)

                    mp_draw.draw_landmarks(image, handLms, mp_hands.HAND_CONNECTIONS)

            # cv2.imshow("cv2", image)
            # cv2.waitKey(1)
