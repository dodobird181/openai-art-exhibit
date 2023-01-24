"""
All possible macro-states the application can be in.
"""
from enum import Enum, auto

class AppState(Enum):
    LISTENING_FOR_INPUT = auto()
    SPEECH_TO_TEXT = auto()
    GPT_COMPLETION = auto()
    TEXT_TO_SPEECH = auto()
    PLAYING_OUTPUT = auto()
    EXITING_APP = auto()
