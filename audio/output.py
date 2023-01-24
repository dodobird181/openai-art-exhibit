import pathlib
import settings
from pydub import AudioSegment
from pydub.playback import play

dir_path = pathlib.Path(__file__).parent.parent.resolve()
output_sound_path = str(dir_path) + '/' + settings.APP_GPT_COMPLETION_VOCAL_FILE

def play_output() -> None:
    """
    Play the output sound.
    """
    sound = AudioSegment.from_wav(output_sound_path)
    play(sound)