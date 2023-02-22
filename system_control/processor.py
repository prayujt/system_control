#!/usr/bin/env python3

from system_control.movement_trackers.mouse_control import MouseControl
from system_control.movement_trackers.volume_control import VolumeControl


class Processor():
    def __init__(self, data):
        self.data = data

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
            MouseControl().start()

        elif self.match(possible_words, 'volume control'):
            VolumeControl().start()

    def match(self, possible_words, phrase):
        words = phrase.split(' ')
        for word in words:
            if word not in possible_words:
                return False
        return True
