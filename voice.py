import speech_recognition as sr
import re

def listen_for_command():
    """
    Listen for voice input and convert it to text
    Returns the recognized text or None if recognition fails
    """
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    print("Listening for command... (speak now)")
    
    with microphone as source:
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            # Listen for audio with timeout
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            print("Processing...")
            
            # Convert speech to text using Google's speech recognition
            text = recognizer.recognize_google(audio)
            print(f"You said: '{text}'")
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("Timeout: No speech detected")
            return None
        except sr.UnknownValueError:
            print("Could not understand the audio")
            return None
        except sr.RequestError as e:
            print(f"Error with speech recognition service: {e}")
            return None

def process_fan_command(text):
    """
    Process the voice command and return boolean based on fan control
    Returns True for "turn on", False for "turn off", None for unrecognized commands
    """
    if text is None:
        return None
    
    # Define patterns for turn on commands
    turn_on_patterns = [
        r'turn\s+on\s+.*fan',
        r'switch\s+on\s+.*fan',
        r'start\s+.*fan',
        r'fan\s+on',
        r'turn\s+.*fan\s+on'
    ]
    
    # Define patterns for turn off commands
    turn_off_patterns = [
        r'turn\s+off\s+.*fan',
        r'switch\s+off\s+.*fan',
        r'stop\s+.*fan',
        r'fan\s+off',
        r'turn\s+.*fan\s+off'
    ]
    
    # Check for turn on patterns
    for pattern in turn_on_patterns:
        if re.search(pattern, text):
            return True
    
    # Check for turn off patterns
    for pattern in turn_off_patterns:
        if re.search(pattern, text):
            return False
    
    # If no pattern matches, return None
    return None

def main():
    """
    Main function to run the voice-controlled fan system
    """
    print("Voice-Controlled Fan System")
    print("Say commands like:")
    print("- 'Turn on the fan'")
    print("- 'Turn off the fan'")
    print("- 'Switch on fan'")
    print("- 'Fan off'")
    print("\nPress Ctrl+C to exit\n")
    
    try:
        while True:
            # Listen for voice command
            command_text = listen_for_command()
            
            # Process the command
            result = process_fan_command(command_text)
            
            if result is True:
                print("Output: True (Fan turned ON)")
            elif result is False:
                print("Output: False (Fan turned OFF)")
            else:
                print("Command not recognized. Please try again.")
            
            print("-" * 40)
            
    except KeyboardInterrupt:
        print("\nExiting program...")

# Alternative function for testing without microphone
def test_with_text_input():
    """
    Test function that takes text input instead of voice (for testing purposes)
    """
    print("Text Input Test Mode")
    print("Type commands like 'turn on the fan' or 'turn off the fan'")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("Enter command: ").lower()
        
        if user_input == 'quit':
            break
            
        result = process_fan_command(user_input)
        
        if result is True:
            print("Output: True (Fan turned ON)")
        elif result is False:
            print("Output: False (Fan turned OFF)")
        else:
            print("Command not recognized. Please try again.")
        
        print("-" * 30)

if __name__ == "__main__":
    # Check if speech recognition is available
    try:
        import speech_recognition as sr
        # Run main voice recognition program
        main()
    except ImportError:
        print("SpeechRecognition library not found.")
        print("Install it with: pip install SpeechRecognition pyaudio")
        print("Running in text input mode instead...\n")
        test_with_text_input()