from gtts import gTTS
from helper import get_media_duration


def freeSpeak(filename, text_for_tts):
    # Convert the text to speech
    tts = gTTS(text_for_tts, lang='en-au')
    audio_path = f'output/Audiofiles/{filename}.mp3'
    tts.save(audio_path)

    speed_up_audio(audio_path, 1.45)
    duration = get_media_duration(audio_path)
    return duration


# a9ad61e19ef91f6814895c0a5f310ee9


def speak11(filename, text, api_key="a9ad61e19ef91f6814895c0a5f310ee9"):
    from elevenlabs import generate, play, Voice, VoiceSettings
    import os
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
    # os.makedirs("output/audiofiles", exist_ok=True)
    filepath = f"output/audiofiles/{filename}.mp3"

    # Save the audio to a file
    with open(filepath, "wb") as audio_file:
        audio_file.write(audio)

    # You may need additional libraries or methods to calculate the length of the generated audio file
    # This part is just a placeholder as calculating exact duration might require examining the file
    # Typically, you might use a library like PyDub or similar to analyze the MP3 file's length
    duration = get_media_duration(filepath)

    return duration





from helper import get_media_duration, run


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
        f'sample_audio/{filename}.mp3',
        '--overwrite',
        "--engine=vits",
        f'--voice={filename}'           
        ]

    # Join all parts into the final command string
    command = ' '.join(command_parts)
    run(command)

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
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="auths/the-respect-419200-e26dd672601b.json"

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

    with open(f'output/Audiofiles/{filename}.mp3', "wb") as out:
        out.write(response.audio_content)

    speed_up_audio(f'output/Audiofiles/{filename}.mp3', 1.25)

    duration = get_media_duration(f'output/Audiofiles/{filename}.mp3')

    return duration


def speed_up_audio(input_path, speed=1.30):
    # Construct the output file path
    output_path = f'output/Audiofiles/speedup.mp3'

    # Build the ffmpeg command
    command = [
        'ffmpeg',
        '-y',  # Overwrite output file without asking
        '-i', input_path,  # Input file
        '-filter:a', f"atempo={speed}",  # Audio filter with speed change
        output_path  # Output file
    ]

    # Run the ffmpeg command
    # subprocess.run(command, check=True)
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Move the output file to the input file (BROKEN)
    # os.replace(output_path, input_path)
    
    # Overwrite the original file with the sped-up version
    # subprocess.run(['move', '/Y', output_path, input_path], shell=True, check=True)

    import shutil
    shutil.copyfile(output_path, input_path)


from pathlib import Path
from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
import logging

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def openAItts(filename, text):
    global voice_num
    #Voice options: alloy, echo, fable, onyx, nova, and shimmer
    voices = ["echo", "echo"] # (<- need 2 for %2) Fable and shimmer are also pretty good (Used to use ECHO AND nova but removed fem echo for uniformity)
    voice_num += 1
    voice = voices[(voice_num % 2)]

    api_key_base = "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"
    client = OpenAI(api_key=api_key_base)
    speech_file_path = Path(__file__).parent / f'output/Audiofiles/{filename}.mp3'
    
    #This is code to circumvent the OpenAi TTS-1-HD rate limit of 5 RPM (retries after exponential wait times!)
    @retry(wait=wait_random_exponential(min=10, max=60), stop=stop_after_attempt(6))
    def completion_with_backoff(**kwargs):
        logger.info("Attempting API call... (again maybe)")
        return client.audio.speech.create(**kwargs)

    try:
        response = completion_with_backoff(
            model="tts-1-hd",
            voice=voice,
            input=text
        )
        response.write_to_file(speech_file_path)
        # response.stream_to_file(speech_file_path)
        print(f"Audio file '{filename}' saved successfully.")
    except Exception as e:
        print(f"Error in openAItts: {str(e)}")
        return 0  # Return 0 duration in case of error

    speed_up_audio(f'output/Audiofiles/{filename}.mp3', 1.25)
    print(f"Audio file '{filename}' saved successfully.")
    duration = get_media_duration(f'output/Audiofiles/{filename}.mp3')
    return duration



if __name__ == "__main__":
    # googleTTS("testGoogle-man", 'While in a deep sleep on the beach when you are lost in slumber hearing the waves, feeling the warmth of the sun that makes you feel so cozy, and smelling the salt in the air.')
    # googleTTS("testGoogle-fem", 'While in a deep sleep on the beach when you are lost in slumber hearing the waves, feeling the warmth of the sun that makes you feel so cozy, and smelling the salt in the air.')
    test_text_200 = "The forest was quiet, with only the occasional rustle of leaves as a breeze passed through. The tall trees stood like silent sentinels, their branches creating a canopy that filtered the sunlight into soft, dappled patterns on the ground. It was a place of peace, where the busyness of the world seemed far away. A narrow path wound its way through the trees, leading deeper into the heart of the woods. The air was cool and fresh, filled with the earthy scent of moss and damp soil. As they walked along the path, the figure felt a sense of calm wash over them. There was something about being in nature that always brought clarity. The sounds of birds chirping in the distance, the occasional snap of a twig underfoot, and the whisper of the wind through the trees all combined to create a symphony of quietude. Each step felt deliberate, each breath more purposeful. It was as if the weight of the world had been lifted, if only for a little while. Deeper into the forest, a small stream appeared, its water bubbling over rocks as it wound its way through the landscape. The figure stopped by the edge, crouching down to dip their fingers into the cool, clear water. It was a reminder of the simplicity and beauty that could still be found in the world, untouched by human hands. As the sun began to lower in the sky, casting long shadows, the forest seemed to change. The air grew cooler, and the sounds of the day gave way to the quiet hum of evening. It was time to leave, but the sense of peace lingered. The figure turned and made their way back along the path, knowing they would return to this place again."
    
    
    
    # CHAR: WORD = TIME
    # 704 : 114 = 34s
    # 594 : 105 = 30s
    # 534 : 92 = 26s
    # 258 : 48 = 12s
    # 859 : 156 = 42s
    # 1868 : 340 = 92s
    # 1615 : 296 = 80s


    openAItts("testOpenAI_timing", test_text_200)

