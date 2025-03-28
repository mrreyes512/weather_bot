import os, sys
from openai import OpenAI
import httpx
import urllib3
import logging

# Disable InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


directory_name = os.path.basename(os.getcwd())
log_file = os.path.join(os.getcwd(), f"{directory_name}.log")
log = logging.getLogger(__name__)
formatter = logging.Formatter(
            '%(asctime)s | %(levelname).4s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler(log_file, mode='a')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

log.addHandler(file_handler)
log.addHandler(stdout_handler)
class MY_LLM(OpenAI):
    """
    MY_LLM is an extension of the OpenAI model, designed to interface with Cigna's AI COE LLM.
    This class abstracts the underlying language model, and abstracts a few common functions.
    
    1. Set the system prompt, this allows you set the personality of the AI.
    2. Set the context, this allows you to send data to analyze.
    3. Contextual Questions allows you to retain conversation history.

    It ensures flexibility by allowing the underlying LLM to be changed without requiring modifications 
    to the existing codebase that utilizes this class.

    Attributes:
        system_prompt (str): The system prompt used for initializing the conversation.
        conversation_history (list): The history of the conversation, maintaining context across interactions.

    Releases:
        v1.0 - 2025-02; Mark Reyes <mark.reyes@evernorth.com>

    Bugs: 
        1. Prompt MUST be set before Context.
    """

    def __init__(self, environment_url, projectname, api_key, api_version="2023-05-15"):
        """
        Initializes the MY_LLM class with the given parameters and sets up the environment variables.

        Args:
            environment_url (str): The base URL of the environment.
            projectname (str): The name of the project.
            api_key (str): The API key for authentication.
            api_version (str, optional): The API version to be used. Defaults to "2023-05-15".
        """
        os.environ["OPENAI_API_TYPE"] = "azure"
        os.environ["OPENAI_API_BASE"] = f"https://{environment_url}/api/v1/ai/{projectname}/OAI"
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_API_VERSION"] = api_version

        super().__init__(
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url=os.environ.get("OPENAI_API_BASE"),
            http_client=httpx.Client(verify=False)
        )
        self.system_prompt = None
        self.conversation_history = []

    def set_prompt(self, prompt_file_path):
        """
        Sets the system prompt from a file.

        Args:
            prompt_file_path (str): The path to the file containing the system prompt.
        """
        try:
            with open(prompt_file_path, 'r') as file:
                self.system_prompt = file.read()
            log.info(f"System prompt set from file: {prompt_file_path}")
        except Exception as e:
            log.error(f"Failed to set system prompt from file: {e}")

    def set_context(self, context):
        """
        Sets the context for the conversation.

        Args:
            context (str): The context to be added to the conversation history.
        """
        log.info(f"Context set. Trust me, I'm a professional.")
        if self.system_prompt and not self.conversation_history:
            self.conversation_history.append({
                "role": "system",
                "content": self.system_prompt,
            })
        self.conversation_history.append({
            "role": "user",
            "content": context,
        })

    def ask_question(self, question, model=None):
        """
        Asks a question to the language model and returns the response.

        Args:
            question (str): The question to be asked.
            model (str, optional): The model to be used for generating the response. Defaults to None.

        Returns:
            str: The response from the language model.
        """
        log.info(f"Preparing Question: {question}")
        if model is None:
            model = "ai-coe-gpt4-auto:analyze"  # Default model
        messages = self.conversation_history.copy() if self.conversation_history else []
        if self.system_prompt and not messages:
            messages.append({
                "role": "system",
                "content": self.system_prompt,
            })
        messages.append({
            "role": "user",
            "content": question,
        })

        try:
            chat_completion = self.chat.completions.create(
                messages=messages,
                model=model,
            )
        except Exception as e:
            log.error(f"FAILED TO CREATE CONNECTION. Check VPN connection. - Error: {e}")
        
        response = chat_completion.choices[0].message.content

        if self.conversation_history:
            self.conversation_history.append({
                "role": "assistant",
                "content": response,
            })
        return response