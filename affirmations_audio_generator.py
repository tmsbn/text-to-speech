from pathlib import Path
from openai import OpenAI
import datetime, os, json


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

files = get_file_names_from_folder(input_folder_name)
print('input files:', files)

recent_files = filter_files_by_modified_time(files, input_folder_name)
print('recently modified input files:', recent_files)

client = OpenAI()

for file_name in recent_files:

    speech_file_path = Path(__file__).parent / output_folder_name / (file_name.split('.')[0] + ".mp3")
    input_file_path = Path(__file__).parent / input_folder_name / file_name

    # Read the input text from the file
    print('Generating voice for input:', input_file_path)
    with open(input_file_path, "r") as f:
        input_text = f.read()
        with open(config_file_path, 'r') as f:
            config_data = json.load(f)
            response = client.audio.speech.create(
                model=config_data.get("model"),
                voice=config_data.get("voice"),
                input=input_text,
        )
        response.write_to_file(speech_file_path)
        print('Output written to file path:', speech_file_path)




