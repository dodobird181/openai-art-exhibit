from enums.AppState import AppState
from audio.input import AudioInput
from audio.speech_to_text import transcribe_file, NoSpeechToTextResults
from gpt.completion import CompletionSession, BadCompletionException
from audio.text_to_speech import generate_audio_from_transcript
from audio.output import play_output
import settings



class App():

    def __init__(self, is_verbose=settings.IS_APP_VERBOSE):
        if is_verbose: print('Initializing app...')
        self.is_verbose = is_verbose
        self.audio_input = AudioInput(is_verbose=is_verbose)
        self.completion_session = CompletionSession()
        self.state = AppState.LISTENING_FOR_INPUT

    def run(self):
        # Main app loop
        while True:
            try:

                if self.state == AppState.LISTENING_FOR_INPUT:
                    self.audio_input.listen_and_save()
                    self.state = AppState.SPEECH_TO_TEXT
                
                elif self.state == AppState.SPEECH_TO_TEXT:
                    transcript = transcribe_file(settings.APP_USER_VOCAL_FILE, is_verbose=self.is_verbose)
                    self.state = AppState.GPT_COMPLETION
                
                elif self.state == AppState.GPT_COMPLETION:
                    completion_text = self.completion_session.get(transcript, max_tokens=50, is_verbose=self.is_verbose)
                    self.state = AppState.TEXT_TO_SPEECH
                
                elif self.state == AppState.TEXT_TO_SPEECH:
                    generate_audio_from_transcript(completion_text, filename=settings.APP_GPT_COMPLETION_VOCAL_FILE, is_verbose=self.is_verbose)
                    self.state == AppState.PLAYING_OUTPUT
                
                elif self.state == AppState.PLAYING_OUTPUT:
                    play_output()
                    self.state == AppState.LISTENING_FOR_INPUT

            # If Speech-to-text transcription fails, try again.
            except NoSpeechToTextResults:
                self.state = AppState.LISTENING_FOR_INPUT
                continue

            # If no usable text is returned by GPT, listen again for voice input.
            except BadCompletionException as e:
                if self.is_verbose: print(f'Bad GPT completion exception: {e.args}')
                self.state == AppState.LISTENING_FOR_INPUT




        return
        audio_input = AudioInput()
        completion_session = CompletionSession()
        #audio_input.calibrate_mic()
        while True:
            audio_input.listen_and_save()
            transcript = transcribe_file('file.wav')
            gpt_completion = completion_session.get(transcript, max_tokens=50)
            print(f'Chat GPT: {gpt_completion}')
            text_to_speech.generate_audio_from_transcript(gpt_completion)
            self.play_output()
            """
            command = input("Continue (yes/no)?: ")
            if 'yes' in command:
                continue
            if 'no' in command:
                break
            """
        audio_input.shutdown()
        #transcribe_file('file.wav')
        #print(Completions().get('Write a short song about sanitary poop.', max_tokens=50))

        #recognizer = sr.Recognizer(key=settings.GOOGLE_CLOUD_API_KEY)
        #with sr.Microphone() as source:                # use the default microphone as the audio source
        #    audio = recognizer.listen(source)                   # listen for the first phrase and extract it into audio data

        
