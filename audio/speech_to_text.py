from google.cloud import speech
import io
import settings
from audio.input import AudioInput

class NoSpeechToTextResults(Exception):
    """
    Raised when the speech-to-text translator returns no results.
    """
    pass

def transcribe_file(speech_file, is_verbose=True) -> str:
    """Transcribe the given audio file."""

    if is_verbose: print('* Transcribing audio file...')

    client = speech.SpeechClient(client_options={
        'quota_project_id': settings.GOOGLE_CLOUD_QUOTA_PROJECT_ID,
        'api_key': settings.GOOGLE_CLOUD_API_KEY})

    with io.open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=AudioInput.SAMPLE_RATE,
        language_code="en-CA",
    )

    response = client.recognize(config=config, audio=audio)

    if len(response.results) == 0:
        raise NoSpeechToTextResults()

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    results = ''
    for result in response.results:
        # TODO: Handle error response
        results += result.alternatives[0].transcript + '.'
    
    if is_verbose:
        print(f'>> Finished transcription: {results}')
    
    return results