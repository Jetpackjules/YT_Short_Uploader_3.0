from gtts import gTTS
from helper import get_media_duration


def freeSpeak(filename, text_for_tts):
    # Convert the text to speech
    tts = gTTS(text_for_tts, lang='en-au')
    audio_path = f'output\\Audiofiles\\{filename}.mp3'
    tts.save(audio_path)

    speed_up_audio(audio_path, 1.45)
    duration = get_media_duration(audio_path)
    return duration


# a9ad61e19ef91f6814895c0a5f310ee9
from elevenlabs import generate, play, Voice, VoiceSettings
import os

def speak11(filename, text, api_key="a9ad61e19ef91f6814895c0a5f310ee9"):
    # Set up the environment variable for ElevenLabs API key
    os.environ["ELEVEN_API_KEY"] = api_key
    voice_settings = VoiceSettings(stability=0.63, similarity_boost=1.0, clarity=1.0)
 
    # Generate audio with specified text, voice model, and settings
    audio = generate(
        text=text,
        voice=Voice(
            voice_id="iP95p4xoKVk53GoZ742B",  # Replace with the correct voice ID for Chris
            settings=voice_settings
        ),
        model="eleven_monolingual_v1"  # Or replace with the correct model if necessary
    )

    # Ensure the Audiofiles directory exists
    # os.makedirs("output\\audiofiles", exist_ok=True)
    filepath = f"output\\audiofiles\\{filename}.mp3"

    # Save the audio to a file
    with open(filepath, "wb") as audio_file:
        audio_file.write(audio)

    # You may need additional libraries or methods to calculate the length of the generated audio file
    # This part is just a placeholder as calculating exact duration might require examining the file
    # Typically, you might use a library like PyDub or similar to analyze the MP3 file's length
    duration = helper.get_media_duration(filepath)

    return duration





import helper

# def echoSpeak(filename, text):
#     command = f'echogarden speak "{text}" sample_audio\\{filename}.mp3 --overwrite'
#     helper.run(command)

voices = [
  "en_GB-alan-low",
  "en_GB-alan-medium",
  "en_GB-semaine-medium",
  "en_GB-danny-low",
  "en_GB-alba-medium",
  "en_GB-aru-medium",
  "en_GB-southern_english_female-low",
  "en_GB-northern_english_male-medium",
  "en_GB-vctk-medium",
  "en_GB-jenny_dioco-medium",
  "en_GB-cori-high",
  "en_US-amy-low",
  "en_US-amy-medium",
  "en_US-kathleen-low",
  "en_US-lessac-low",
  "en_US-lessac-medium",
  "en_US-lessac-high",
  "en_US-libritts-high",
  "en_US-libritts_r-medium",
  "en_US-ryan-low",
  "en_US-ryan-medium",
  "en_US-ryan-high",
  "en_US-joe-medium",
  "en_US-kusal-medium",
  "en_US-arctic-medium",
  "en_US-l2arctic-medium",
  "en_US-hfc_male-medium",
  "en_US-hfc_female-medium",
  "en_US-kristin-medium",
  "en_US-ljspeech-high",
  "en_US-ljspeech-medium"
]


def echoSpeak(filename, text):
    # Base command parts
    # DEFAULT ENGINE IS VITS!
    command_parts = [
        f'echogarden speak "{text}"',
        f'sample_audio\\{filename}.mp3',
        '--overwrite',
        "--engine=vits",
        f'--voice={filename}'           
        ]

    # Join all parts into the final command string
    command = ' '.join(command_parts)
    helper.run(command)

# if __name__ == "__main__":
#     # echoSpeak("test2", "Hello you, this is echogarden sample audio for reddit posts! I am happy to be here.")
#     t=0
#     for voice in voices:
#         echoSpeak(voice, "Hello you, this is echogarden sample audio for reddit posts! I am happy to be here.")
#         t+=1
#         print(f"{t}/{len(voices)}")


import os
from google.cloud import texttospeech
import random
import subprocess


voice_num = 0
def googleTTS(filename, text):
    global voice_num
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="auths\\the-respect-419200-e26dd672601b.json"

    voices = ["en-US-Journey-F", "en-US-Journey-D"]
    voice_num += 1
    voice = voices[(voice_num % 2)]

    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", name=voice
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3, pitch=random.uniform(0.0, 0.0), speaking_rate=3.88, effects_profile_id=["handset-class-device"]
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open(f'output\\Audiofiles\\{filename}.mp3', "wb") as out:
        out.write(response.audio_content)

    speed_up_audio(f'output\\Audiofiles\\{filename}.mp3', 1.25)

    duration = helper.get_media_duration(f'output\\Audiofiles\\{filename}.mp3')

    return duration


def speed_up_audio(input_path, speed=1.30):
    # Construct the output file path
    output_path = f'output\\Audiofiles\\speedup.mp3'

    # Build the ffmpeg command
    command = [
        'ffmpeg',
        '-y',  # Overwrite output file without asking
        '-i', input_path,  # Input file
        '-filter:a', f"atempo={speed}",  # Audio filter with speed change
        output_path  # Output file
    ]

    # Run the ffmpeg command
    subprocess.run(command, check=True)

    # Overwrite the original file with the sped-up version
    subprocess.run(['move', '/Y', output_path, input_path], shell=True, check=True)


if __name__ == "__main__":
    googleTTS("testGoogle", 'as a former active H addict i will say i would not wish withdrawals on anyone. they are truly  hellacious. i feel blessed to have gotten out of all that before fentanyl took over, i would be dead now probably')
    googleTTS("testGoogle", 'as a former active H addict i will say i would not wish withdrawals on anyone. they are truly  hellacious. i feel blessed to have gotten out of all that before fentanyl took over, i would be dead now probably')
