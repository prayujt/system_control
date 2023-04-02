#!/usr/bin/env python3

from system_control.movement_trackers.mouse_control import MouseControl
from system_control.movement_trackers.volume_control import VolumeControl
from system_control.actions import ActionsProcessor


class Processor():
    def __init__(self, data, camera_index):
        self.data = data
        self.camera_index = camera_index

    def gather(self):
        possible_words = set()
        for alternative in self.data['alternatives']:
            if 'result' in alternative:
                for word in alternative['result']:
                    possible_words.add(word['word'])
        return possible_words

    def process(self):
        possible_words = self.gather()
        print('\nWords:')
        for word in possible_words:
            print(word)
        print()

        if self.match(possible_words, 'mouse control'):
            MouseControl().start(self.camera_index)

        elif self.match(possible_words, 'volume control'):
            VolumeControl().start(self.camera_index)

        else:
            ActionsProcessor(possible_words).process()

    def match(self, possible_words, phrase):
        words = phrase.split(' ')
        for word in words:
            if word not in possible_words:
                return False
        return True
