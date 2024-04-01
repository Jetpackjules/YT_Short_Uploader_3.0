from gtts import gTTS
from moviepy.editor import AudioFileClip, vfx
from pydub import AudioSegment
from pydub.playback import play
from helper import get_media_duration


def speak(filename, text_for_tts, speed=2.5, pitch_factor=0.45):
    # Convert the text to speech
    tts = gTTS(text_for_tts, lang='en-au')
    audio_path = f'output\\Audiofiles\\{filename}.mp3'
    tts.save(audio_path)
    # # Increase speed for slow tts audio:
    # audio_clip = AudioFileClip(audio_file)
    # audio_clip = audio_clip.fx(vfx.speedx, speed)
    
    # audio_clip.write_audiofile(audio_file, codec='libmp3lame')
    # audio_clip.close()
   # Load the audio file with pydub
    # Load the audio file with Pydub
    # Load the audio file with Pydub
    audio = AudioSegment.from_mp3(audio_path)
    
    # Speed up the audio clip (this changes speed and pitch together)
    sped_up_audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * speed)})
    
    # Apply pitch correction (this changes pitch without altering speed)
    corrected_pitch_audio = sped_up_audio._spawn(sped_up_audio.raw_data, overrides={"frame_rate": int(sped_up_audio.frame_rate * pitch_factor)})
    
    # Export the modified audio
    corrected_pitch_audio.export(audio_path, format="mp3")

    print(f'Generated audio file: {audio_path}')

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
    duration = get_mp3_duration(filepath)

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
        f'D:\\Miniconda_Projects\\YT_Shorts_Uploader_3.0\\sample_audio\\{filename}.mp3',
        '--overwrite',
        "--engine=vits",
        f'--voice={filename}'           
        ]

    # Join all parts into the final command string
    command = ' '.join(command_parts)
    helper.run(command)

if __name__ == "__main__":
    # echoSpeak("test2", "Hello you, this is echogarden sample audio for reddit posts! I am happy to be here.")
    t=0
    for voice in voices:
        echoSpeak(voice, "Hello you, this is echogarden sample audio for reddit posts! I am happy to be here.")
        t+=1
        print(f"{t}/{len(voices)}")
