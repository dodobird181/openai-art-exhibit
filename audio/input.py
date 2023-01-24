from __future__ import annotations
import settings
import pyaudio
import wave
import collections
import math
import audioop


class AudioInput():

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    SAMPLE_RATE = 44100
    CHUNK_SIZE = 1024

    DEFAULT_RECORD_SECONDS = 5
    DEFAULT_WAVE_OUTPUT_FILENAME = settings.APP_USER_VOCAL_FILE

    def __init__(self, is_verbose=True):
        self.audio = pyaudio.PyAudio()
        self.is_verbose = is_verbose
        self.energy_threshold = 3500 # minimum audio energy to consider for recording
        self.pause_threshold = 2 # seconds of quiet time before a phrase is considered complete
        self.quiet_duration = 1 # amount of quiet time to keep on both sides of the recording

    def uses_audio_stream(function):
        """
        Decorator function that initializes the `self.audio_stream` attribute on
        an instance of `AudioInput` and then closes it afterwards.
        """
        def wrapper(self, *args, **kwargs):
            self.audio_stream = self.audio.open(
                frames_per_buffer=self.CHUNK_SIZE,
                channels=self.CHANNELS,
                rate=self.SAMPLE_RATE,
                format=self.FORMAT,
                input=True)
            value = function(self, *args, **kwargs)
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio_stream = None
            return value
        return wrapper

    @uses_audio_stream
    def calibrate_mic(self, calibration_seconds=10, top_percent_to_average=.05) -> None:
        """
        Set the `AudioInput`'s `energy_threshold` to the average energy
        recorded during calibration.
        """
        if self.is_verbose:
            print(f'* Calibrating microphone (for {calibration_seconds} seconds.)')
        
        # Save the audio energies over a period of time
        energies = []
        sample_width = pyaudio.get_sample_size(self.FORMAT)
        frames_per_second = frames_per_second = self.SAMPLE_RATE / self.CHUNK_SIZE
        num_frames = int(frames_per_second * calibration_seconds)
        for _ in range(0, num_frames):
            data = self.audio_stream.read(self.CHUNK_SIZE)
            energy = audioop.rms(data, sample_width)
            energies.append(energy)

        # Grab the highest energies as a percent of total energies
        energies = sorted(energies, reverse=True)
        top_n_population = int(len(energies) * top_percent_to_average)
        highest_energies = energies[:top_n_population]
        
        average_energy = sum(highest_energies) / len(highest_energies)
        self.energy_threshold = average_energy

        if self.is_verbose:
            print(f'* Finished calibration (average energy is {average_energy}).')
        

    @uses_audio_stream
    def listen(self, timeout=None) -> bytes:
        """
        TODO
        """
        # record audio data as raw samples
        frames = collections.deque()
        assert self.pause_threshold >= self.quiet_duration >= 0
        sample_width = pyaudio.get_sample_size(self.FORMAT)
        seconds_per_buffer = (self.CHUNK_SIZE + 0.0) / self.SAMPLE_RATE
        pause_buffer_count = int(math.ceil(self.pause_threshold / seconds_per_buffer)) # number of buffers of quiet audio before the phrase is complete
        quiet_buffer_count = int(math.ceil(self.quiet_duration / seconds_per_buffer)) # maximum number of buffers of quiet audio to retain before and after
        elapsed_time = 0

        if self.is_verbose:
            print('* Listening for input...')

        # store audio input until the phrase starts
        while True:
            elapsed_time += seconds_per_buffer
            if timeout and elapsed_time > timeout: # handle timeout if specified
                raise TimeoutError("listening timed out")

            buffer = self.audio_stream.read(self.CHUNK_SIZE)
            if len(buffer) == 0: break # reached end of the stream
            frames.append(buffer)

            # check if the audio input has stopped being quiet
            energy = audioop.rms(buffer, sample_width) # energy of the audio signal
            if energy > self.energy_threshold:
                break

            if len(frames) > quiet_buffer_count: # ensure we only keep the needed amount of quiet buffers
                frames.popleft()
        
        if self.is_verbose:
            print('* Recording phrase...')

        # read audio input until the phrase ends
        pause_count = 0
        while True:
            buffer = self.audio_stream.read(self.CHUNK_SIZE)
            if len(buffer) == 0: break # reached end of the stream
            frames.append(buffer)

            # check if the audio input has gone quiet for longer than the pause threshold
            energy = audioop.rms(buffer, sample_width) # energy of the audio signal
            if energy > self.energy_threshold * 0.9:
                pause_count = 0
            else:
                pause_count += 1
            if pause_count > pause_buffer_count: # end of the phrase
                break

        if self.is_verbose:
            print('* End of phrase.')

        # obtain frame data
        for i in range(quiet_buffer_count, pause_count): frames.pop() # remove extra quiet frames at the end
        frame_data = b"".join(list(frames))

        return frame_data

    @uses_audio_stream
    def record(self, record_seconds=DEFAULT_RECORD_SECONDS) -> bytes:
        """
        Record audio for a pre-determined amount of time and return bytes.
        """
        
        # Print start message
        if self.is_verbose:
            print('* Recording...')

        # Append bytes in the stream to a list of bytes in memory
        frame_accumulator = []
        frames_per_second = self.SAMPLE_RATE / self.CHUNK_SIZE
        num_frames = int(frames_per_second * record_seconds)
        for _ in range(0, num_frames):
            data = self.audio_stream.read(self.CHUNK_SIZE)
            frame_accumulator.append(data)
        
        # Print end message
        if self.is_verbose:
            print('* Finished recording.')
        
        # Concat all bytes in the list and return bytes
        return b''.join(frame_accumulator)

    def save_bytes_to_wav_file(self, bytes, filename=DEFAULT_WAVE_OUTPUT_FILENAME) -> None:
        """
        The side-effect of this function is to save bytes to a .wav file.
        """
        waveFile = wave.open(filename, 'wb')
        waveFile.setnchannels(self.CHANNELS)
        waveFile.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        waveFile.setframerate(self.SAMPLE_RATE)
        waveFile.writeframes(bytes)
        waveFile.close()

    def record_and_save(
        self, 
        record_seconds=DEFAULT_RECORD_SECONDS, 
        filename=DEFAULT_WAVE_OUTPUT_FILENAME) -> AudioInput:
        """
        The side-effect of this function is to record audio and save it as a .wav file.
        This function returns this object for further operations.
        """
        bytes = self.record()
        self.save_bytes_to_wav_file(bytes, filename)
        return self

    def listen_and_save(
        self, 
        timeout=None, 
        filename=DEFAULT_WAVE_OUTPUT_FILENAME) -> AudioInput:
        """
        The side-effect of this function is to record audio and save it as a .wav file.
        This function returns this object for further operations.
        """
        bytes = self.listen(timeout=timeout)
        self.save_bytes_to_wav_file(bytes, filename)
        return self
    
    def shutdown(self) -> None:
        """
        Terminate PyAudio instance to free-up system resources.
        """
        self.audio.terminate()
