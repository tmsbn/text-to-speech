from pathlib import Path
from openai import OpenAI
import datetime, os, json
from enum import Enum
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

class API_TYPE(Enum):
    OPEN_AI = 1
    ELEVEN_LABS = 2



def filter_files_by_modified_time(file_list, folder, minutes=1):
  """
  Filters a list of file names to include only those modified in the last 
  'minutes'.

  Args:
    file_list: A list of file names (strings).
    minutes: The number of minutes in the past to check for modification.

  Returns:
    A list of file names that were modified within the specified time.
  """

  filtered_files = []
  now = datetime.datetime.now()

  for file_name in file_list:
    file_path = os.path.join(folder, file_name)
    try:
      # Get the modification time of the file
      modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))  
      
      # Calculate the time difference
      time_diff = now - modified_time 

      # Check if the file was modified within the last 'minutes'
      if time_diff.total_seconds() <= minutes * 60:  
        filtered_files.append(file_name)

    except FileNotFoundError:
      print(f"Warning: File not found: {file_name}")

  return filtered_files


def get_file_names_from_folder(folder_path):
  """
  Reads all file names from a given folder and returns a list.

  Args:
    folder_path: The path to the folder.

  Returns:
    A list of file names (strings) in the folder.
  """

  file_names = []
  for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    if os.path.isfile(file_path):
      file_names.append(filename)
  return file_names

# main program
input_folder_name = 'text'
output_folder_name = 'audio'
config_file_path = "config.json"


def generate_response_with_openai(config_data, input_file_path:str, speech_file_path:str):
      
      client = OpenAI()
      # Read the input text from the file
      print('Generating voice for input:', input_file_path)
      with open(input_file_path, "r") as f:
          input_text = f.read()

          # Generate response using openAI
          response = client.audio.speech.create(
              model=config_data.get("model"),
              voice=config_data.get("voice"),
              speed=config_data.get("speed"),
              input=input_text)
          response.write_to_file(speech_file_path)
      print('Output written to file path:', speech_file_path)

   
def generate_response_with_eleven_labs(config_data, input_file_path:str,  speech_file_path:str):
    
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    print('elevenLabs API key', ELEVENLABS_API_KEY)
    client = ElevenLabs(
        api_key=ELEVENLABS_API_KEY,
    )

    # Read the input text from the file
    print('Generating voice for input:', input_file_path)
    with open(input_file_path, "r") as f:
        input_text = f.read()

        response = client.text_to_speech.convert(
          voice_id="8Es4wFxsDlHBmFWAOWRS", # William Shanks
          output_format="mp3_22050_32",
          text=input_text,
          model_id="eleven_turbo_v2_5", # Low Latency
          voice_settings=VoiceSettings(
              stability=0.0,
              similarity_boost=1.0,
              style=0.0,
              use_speaker_boost=True,
          ),
        )

        # Writing the audio to a file
        with open(speech_file_path, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)
        print('Output written to file path:', speech_file_path)

with open(config_file_path, 'r') as f:
    
    config_data = json.load(f)

    api_type = None
    if "api" in config_data and config_data.get("api") == "elevenlabs":
       api_type = API_TYPE.ELEVEN_LABS
    else:
       api_type = API_TYPE.OPEN_AI

    print('API type', api_type)   

    files = get_file_names_from_folder(input_folder_name)
    print('input files:', files)
    recent_files = None

    print('config', config_data)


    # Decide to process all files or just the recently modified files
    if "process_all" in config_data and config_data["process_all"]:
      recent_files = files
    else:
      recent_files = filter_files_by_modified_time(files, input_folder_name)
    print('recently modified input files:', recent_files)

    for file_name in recent_files:

        speech_file_output_folder = Path(__file__).parent / output_folder_name

        # create output folder if doesn't exist
        Path(speech_file_output_folder).mkdir(parents=True, exist_ok=True)

        speech_file_path = speech_file_output_folder / (file_name.split('.')[0] + ".mp3")
        input_file_path = Path(__file__).parent / input_folder_name / file_name

        if api_type == API_TYPE.OPEN_AI:
          generate_response_with_openai(config_data, input_file_path, speech_file_path)
        else:
          generate_response_with_eleven_labs(config_data, input_file_path, speech_file_path)



