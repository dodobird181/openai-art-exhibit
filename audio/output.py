import pathlib
from pydub import AudioSegment
from pydub.playback import play

dir_path = pathlib.Path(__file__).parent.resolve()
output_sound_path = str(dir_path) + '/output.wav'

def play_output() -> None:
    """
    Play the output sound.
    """
    sound = AudioSegment.from_wav(self.output_sound_path)
    play(sound)