
import pyttsx3

try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    print("--- Voces Disponibles (SAPI5) ---")
    for i, voice in enumerate(voices):
        print(f"Index: {i}")
        print(f"Name: {voice.name}")
        print(f"ID: {voice.id}")
        print(f"Languages: {voice.languages}")
        print("-" * 30)

except Exception as e:
    print(f"Error inicializando pyttsx3: {e}")
