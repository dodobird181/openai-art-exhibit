import openai
import settings
import collections

class GPTException(Exception):
    """
    Base class for all Chat GPT exceptions.
    """
    pass

class BadCompletionException(GPTException):
    """
    Raised when the response returned by Chat GPT's API does not contain any usable text.
    """
    pass

class CompletionSession():

    DEFAULT_MODEL = 'text-davinci-003'
    MAX_SESSION_HISTORY_LENGTH = 2 # The number of prompt + answer combinations we want to save.

    def __init__(self):
        openai.api_key = settings.CHAT_GPT_API_KEY
        self.session_history = collections.deque()

    def __get_response_text(self, completion_response) -> str:
        """
        Get the response text from a completion response object, or raise a
        `BadCompletionException` exception if the completion response doesn't
        contain any text information.
        """
        if completion_response is None:
            raise BadCompletionException('No completion response was returned.')
        elif completion_response['choices'] is None:
            raise BadCompletionException('Key \'choices\' does not exist on completion_response.')
        elif len(completion_response['choices']) == 0:
            raise BadCompletionException('Choices is empty.')
        
        text = str(completion_response['choices'][0]['text'])
        if text.isspace() or text == '':
            raise BadCompletionException('No text returned.')
        else:
            return text

    def __get_session_history(self) -> str:
        """
        Build the session history and return as a String.
        """
        history = ''
        for phrase in self.session_history:
            history += phrase

    def __add_to_session_history(self, text: str) -> None:
        """
        Appends a string of text to the session history.
        """
        self.session_history.appendleft(text)
        if len(self.session_history) >= self.MAX_SESSION_HISTORY_LENGTH * 2:
            self.session_history.pop()

    def get(self, prompt, model=DEFAULT_MODEL, is_verbose=True, **kwargs) -> str:
        """
        Send a new prompt to Chat GPT (along with the session history,)
        and return it's answer as a string.
        """
        if is_verbose: print('* Sending to Chat GPT...')
        self.__add_to_session_history(prompt)
        session_history = self.__get_session_history()
        try:
            response = openai.Completion.create(
                prompt=session_history,
                model=model,
                **kwargs)
            completion_text = self.__get_response_text(response)
            self.__add_to_session_history(completion_text)
            if is_verbose: print('* Received Chat GPT response.')
            return completion_text
        
        # Wrap any generic exception as a GPT exception
        except Exception as e:
            raise GPTException from e
