"""Synthesizes speech from the input string of text or ssml.
Make sure to be working in a virtual environment.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""
from google.cloud import texttospeech
import settings

DEFAULT_AUDIO_OUTPUT_FILENAME = 'output.wav'

def generate_audio_from_transcript(transcript: str, filename=DEFAULT_AUDIO_OUTPUT_FILENAME, is_verbose=True) -> None:
    """
    Generate an audio file using text-to-speech 
    """

    if is_verbose: print('* Running text-to-speech...')

    # Instantiates a client
    client = texttospeech.TextToSpeechClient(client_options={
        'quota_project_id': settings.GOOGLE_CLOUD_QUOTA_PROJECT_ID,
        'api_key': settings.GOOGLE_CLOUD_API_KEY})

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=transcript)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-AU", 
        ssml_gender=texttospeech.SsmlVoiceGender.MALE,
        name='en-AU-Neural2-B',
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # The response's audio_content is binary.
    
    with open(filename, "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
    
    if is_verbose: print('* Finished running text-to-speech.')