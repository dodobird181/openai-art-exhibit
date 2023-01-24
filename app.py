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
        self.latest_vocal_transcript = None

    def listen_for_input(self) -> AppState:
        """
        Listen for audio-input and save to a .wav file.
        """
        self.audio_input.listen_and_save() # Blocking call
        return AppState.SPEECH_TO_TEXT

    def run_speech_to_text(self) -> AppState:
        """
        Run speech-to-text conversion using Google Cloud's API.
        """
        self.latest_vocal_transcript = transcribe_file( # Blocking call
            settings.APP_USER_VOCAL_FILE, 
            is_verbose=self.is_verbose)
        return AppState.GPT_COMPLETION
    
    def run_gpt_completion(self) -> AppState:
        """
        Run GPT's completions feature against the `latest_vocal_transcript`.
        """
        self.gpt_completion_transcript = self.completion_session.get( # Blocking call
            prompt=self.latest_vocal_transcript, 
            is_verbose=self.is_verbose,
            max_tokens=50)
        return AppState.TEXT_TO_SPEECH
    
    def run_text_to_speech(self) -> AppState:
        """
        Run text-to-speech conversion using Google Cloud's API.
        """
        generate_audio_from_transcript( # Blocking call
            filename=settings.APP_GPT_COMPLETION_VOCAL_FILE,
            transcript=self.gpt_completion_transcript,
            is_verbose=self.is_verbose)
        return AppState.PLAYING_OUTPUT

    def play_speech_output(self) -> AppState:
        """
        Play the latest audio output.
        """
        play_output()
        return AppState.LISTENING_FOR_INPUT

    def exit_app(self) -> AppState:
        # Do Nothing
        return AppState.EXITING_APP

    def run(self):
        """
        Main app loop.
        """
        cases = {
            AppState.LISTENING_FOR_INPUT: self.listen_for_input,
            AppState.SPEECH_TO_TEXT: self.run_speech_to_text,
            AppState.GPT_COMPLETION: self.run_gpt_completion,
            AppState.TEXT_TO_SPEECH: self.run_text_to_speech,
            AppState.PLAYING_OUTPUT: self.play_speech_output,
            AppState.EXITING_APP: self.exit_app}

        try:
            self.state = cases[self.state]()

        # If Speech-to-text transcription fails, listen again for voice input.
        except NoSpeechToTextResults:
            self.state = AppState.LISTENING_FOR_INPUT

        # If no usable text is returned by GPT, listen again for voice input.
        except BadCompletionException as e:
            if self.is_verbose: print(f'Bad GPT completion exception: {e.args}')
            self.state == AppState.LISTENING_FOR_INPUT
        
        # Keep running or exit app
        if self.state != AppState.EXITING_APP:
            self.run()
        else:
            print('Exiting app...')




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

        
