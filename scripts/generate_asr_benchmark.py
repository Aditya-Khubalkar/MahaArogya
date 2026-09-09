# -*- coding: utf-8 -*-
import json
import os
import pyttsx3

def generate_benchmark():
    dataset_path = r"C:\MahaArogya\data\test\asr_100_utterances.json"
    output_dir = r"C:\MahaArogya\data\test\asr_samples"
    
    os.makedirs(output_dir, exist_ok=True)
    
    with open(dataset_path, "r", encoding="utf-8") as f:
        utterances = json.load(f)
    
    engine = pyttsx3.init()
    
    # Optional: configure voices depending on the language if available
    voices = engine.getProperty('voices')
    
    generated_count = 0
    skipped_count = 0
    
    for utt in utterances:
        # Build the expected filename, e.g. asr_mr_01.wav
        filename = f"asr_{utt['id']}.wav"
        output_path = os.path.join(output_dir, filename)
        
        if os.path.exists(output_path):
            skipped_count += 1
            continue
            
        text = utt["reference"]
        
        # Simple voice selection attempt based on OS voices
        # Usually Windows has a default English voice, and possibly Hindi
        # We will just rely on the default if specific languages aren't found
        selected_voice = None
        if utt['category'] == 'Hindi' or utt['category'] == 'Marathi':
            for voice in voices:
                if 'hi' in voice.languages or 'Hindi' in voice.name:
                    selected_voice = voice.id
                    break
        
        if selected_voice:
            engine.setProperty('voice', selected_voice)
        else:
            engine.setProperty('voice', voices[0].id)
            
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        generated_count += 1
        
    print(f"Generated: {generated_count}, Skipped (already existed): {skipped_count}")

if __name__ == "__main__":
    generate_benchmark()
