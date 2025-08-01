import SpeechRecognition as sr

r = sr.Recognizer()

while True:
    try:
        with sr.Microphone() as source:
            print("say something")
            audio = r.listen(source)
            text = r.recognize_google(audio)
            text = text.lower()
            print("recognized text : {text}")

    except:
        print("not recognized your voice")
        r = sr.Recognizer()
        continue