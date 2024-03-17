from gtts import gTTS

def speak(filename, text_for_tts):
    # Convert the text to speech
    tts = gTTS(text_for_tts, lang='en')
    audio_file = f'Audiofiles\\{filename}.mp3'
    tts.save(audio_file)
    print("TTS TEXT ------------------------------")
    print(text_for_tts)
    print(f'Generated audio file: {audio_file}')

    return audio_file
# a9ad61e19ef91f6814895c0a5f310ee9
from elevenlabs import generate, play, Voice, VoiceSettings
import os

def generate_and_save_audio(text, filename, api_key="a9ad61e19ef91f6814895c0a5f310ee9"):
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
    os.makedirs("Audiofiles", exist_ok=True)
    filepath = f"Audiofiles/{filename}.mp3"

    # Save the audio to a file
    with open(filepath, "wb") as audio_file:
        audio_file.write(audio)

    # You may need additional libraries or methods to calculate the length of the generated audio file
    # This part is just a placeholder as calculating exact duration might require examining the file
    # Typically, you might use a library like PyDub or similar to analyze the MP3 file's length
    duration = "Unknown"  # Placeholder, replace with actual duration calculation

    return filepath, duration

# Example usage
text = "Hello, this is a test using ElevenLabs."
filename = "test_audio2"
filepath, duration = generate_and_save_audio(text, filename)
print(f"File saved to: {filepath}, Duration: {duration} seconds")
