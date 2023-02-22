#!/usr/bin/env python3

import cv2
import mediapipe as mp
import numpy as np
import time
import os

from .movement_tracker import MovementTracker


class MouseControl(MovementTracker):
    center_tracking_landmarks = set({0, 9, 13})
    closed_tracking_landmarks = set({4, 8, 12, 16, 20})

    def start(self):
        cap = cv2.VideoCapture(0)
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(min_detection_confidence=0.75)
        mp_draw = mp.solutions.drawing_utils
        p_time = 0
        start_time = time.time()

        avg_center_x_prev, avg_center_y_prev = 0, 0

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

                    X = np.empty([1, 0])
                    Y = np.empty([1, 0])

                    for idx, lm in enumerate(handLms.landmark):
                        if idx in self.center_tracking_landmarks:
                            h, w, c = image.shape
                            cx, cy = int(lm.x * w), int(lm.y * h)
                            avg_center_x += cx
                            avg_center_y += cy
                        if idx in self.closed_tracking_landmarks:
                            X = np.append(X, cx)
                            Y = np.append(Y, cy)

                    avg_center_x = avg_center_x // len(self.center_tracking_landmarks)
                    avg_center_y = avg_center_y // len(self.center_tracking_landmarks)
                    cv2.circle(image, (avg_center_x, avg_center_y), 25, (255, 0, 255), cv2.FILLED)

                    mp_draw.draw_landmarks(image, handLms, mp_hands.HAND_CONNECTIONS)

                    if not (avg_center_x_prev == 0 and avg_center_y_prev == 0):
                        os.system(f'xdotool mousemove_relative -- {(avg_center_x_prev - avg_center_x) * 3} {(avg_center_y - avg_center_y_prev) * 3}')

                    # print("X", X)
                    # print("Y", Y)

                    avg_center_x_prev, avg_center_y_prev = avg_center_x, avg_center_y
            else:
                avg_center_x_prev, avg_center_y_prev = 0, 0

            # cv2.imshow("cv2", image)
            # cv2.waitKey(1)
