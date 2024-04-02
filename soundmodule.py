import numpy as np
from scipy.io.wavfile import write
import random
import os
import configparser  # Add this import

CONFIG_FILE = 'settings.txt'  # Add this line
# Default settings
intro_duration = 0.2  # seconds
test_duration = 1.0   # seconds
space_duration = 1.0  # seconds

def get_current_settings():
    return intro_duration, test_duration, space_duration
def midi_to_frequency(midi_note):
    return 2 ** ((midi_note - 69) / 12) * 440
    # A4 MIDI note is 69 and should return a frequency of 440 Hz
    print(midi_to_frequency(69))  # Expected output: 440


def create_note(frequency, duration, sample_rate=44100, fade_in_duration=0.01, fade_out_duration=0.1):
    samples = np.arange(duration * sample_rate)
    waveform = np.sin(2 * np.pi * frequency * samples / sample_rate)

    # Calculate the number of samples for fade in and fade out
    fade_in_samples = int(fade_in_duration * sample_rate)
    fade_out_samples = int(fade_out_duration * sample_rate)

    # Ensure waveform is long enough for fade in and fade out
    if len(waveform) > fade_in_samples + fade_out_samples:
        fade_in = np.linspace(0, 1, fade_in_samples)
        waveform[:fade_in_samples] *= fade_in

        fade_out = np.linspace(1, 0, fade_out_samples)
        waveform[-fade_out_samples:] *= fade_out
    else:
        # For very short waveforms, adjust or skip fading
        # This example simply normalizes the waveform without fading
        waveform = waveform * (32767 / np.max(np.abs(waveform)))

    max_val = np.max(np.abs(waveform))
    if max_val > 0:
        waveform = waveform * (32767 / max_val)
    waveform = np.nan_to_num(waveform).astype(np.int16)

    return waveform

def set_durations(intro_dur, test_dur, space_dur):
    return intro_dur, test_dur, space_dur


def load_settings():
    config = configparser.ConfigParser()
    try:
        config.read(CONFIG_FILE)

        try:
            intro_speed = float(config['DEFAULT']['intro_speed'])
            test_speed = float(config['DEFAULT']['test_speed'])
            space_between = float(config['DEFAULT']['space_between'])
        except ValueError:
            print("Invalid settings detected. Resetting to default values.")
            intro_speed = 0.2
            test_speed = 1.0
            space_between = 1.0
            save_settings(intro_speed, test_speed, space_between)

        print("Settings loaded:", intro_speed, test_speed, space_between) 
        return intro_speed, test_speed, space_between

    except (KeyError, FileNotFoundError) as e:  
        print("Error loading settings:", e)
        intro_speed = 0.2
        test_speed = 1.0
        space_between = 1.0
        save_settings(intro_speed, test_speed, space_between)

    return intro_speed, test_speed, space_between

def save_settings(intro_speed, test_speed, space_between):
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'intro_speed': str(intro_speed),
        'test_speed': str(test_speed),
        'space_between': str(space_between)
    }
    print("Saving settings...")

    with open(CONFIG_FILE, 'w') as file:
        config.write(file)


def apply_settings(intro_speed_entry, test_speed_entry, space_between_entry):
    # Get values from the Entry widgets and convert them to floats
    intro_speed = float(intro_speed_entry.get())
    test_speed = float(test_speed_entry.get())
    space_between = float(space_between_entry.get())

    print("Applying settings:", intro_speed, test_speed, space_between)

    # Update the global settings variables directly
    global intro_duration, test_duration, space_duration
    intro_duration = intro_speed if intro_speed else 0.2
    test_duration = test_speed if test_speed else 1.0
    space_duration = space_between if space_between else 1.0

    # Save settings after making changes
    save_settings(intro_duration, test_duration, space_duration)  # Pass the float values

    # Now load the new settings
    intro_speed, test_speed, space_between = load_settings() 

    print("Settings loaded:", intro_speed, test_speed, space_between)

    # Update the global settings variables directly
    intro_duration = float(intro_speed) if intro_speed else 0.2
    test_duration = float(test_speed) if test_speed else 1.0
    space_duration = float(space_between) if space_between else 1.0

    # Save settings after making changes
    save_settings() 

def generate_chord(root_note, duration, sample_rate=44100):
    # Calculate frequencies for root, third, and fifth
    root_freq = midi_to_frequency(root_note)
    third_freq = midi_to_frequency(root_note + 4)  # Major third
    fifth_freq = midi_to_frequency(root_note + 7)  # Perfect fifth
    
    # Time array
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # Generate sine waves for each note
    root_wave = np.sin(2 * np.pi * root_freq * t)
    third_wave = np.sin(2 * np.pi * third_freq * t)
    fifth_wave = np.sin(2 * np.pi * fifth_freq * t)
    
    # Combine the waves
    chord_wave = root_wave + third_wave + fifth_wave
    chord_wave = chord_wave * (32767 / np.max(np.abs(chord_wave)))  # Normalize volume
    chord_wave = chord_wave.astype(np.int16)  # Convert to int16 format
    
    return chord_wave

def generate_solfege_map_for_root(root_note, note_range=36):
    # Base solfege sequence, repeating for multiple octaves
    base_solfege_sequence = ['do', 'di/ra', 're', 'ri/me', 'mi', 'fa', 'fi/se', 'sol', 'si/le', 'la', 'li/te', 'ti'] * 3  # Extended for range
    
    # Generate solfege map for the specified range
    solfege_map = {}
    start_note = root_note - 12  # Start one octave below for more coverage
    for i in range(note_range):
        note = start_note + i
        solfege_name = base_solfege_sequence[i % len(base_solfege_sequence)]
        solfege_map[note] = solfege_name

    return solfege_map

def on_root_note_change(event=None):
    global root_note_var
    root_note = int(root_note_var.get())


def generate_sequence(sound_type, intro_duration, test_duration, space_duration, root_note, num_notes, note_range, sample_rate=44100):
    folder_name = "test_file_folder"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Generate intro part based on sound_type
    if sound_type == "chord":
        intro_audio = generate_chord(root_note, intro_duration, sample_rate)
    else:  # Assuming 'scale'
        intro_audio = np.array([])
        intro_notes = list(range(root_note, root_note + note_range))[:num_notes]
        for note in intro_notes:
            frequency = midi_to_frequency(note)
            waveform = create_note(frequency, intro_duration / len(intro_notes), sample_rate)
            intro_audio = np.concatenate((intro_audio, waveform))

    max_val = np.max(np.abs(intro_audio))
    if max_val > 0:
        intro_audio = intro_audio * (32767 / max_val)
    intro_audio = np.nan_to_num(intro_audio).astype(np.int16)


    silence_between_intro_and_test = np.zeros(int(sample_rate * space_duration), dtype=np.int16)

    # Dynamic solfege map for generating test notes and names
    solfege_map = generate_solfege_map_for_root(root_note, 36)
    midi_notes = random.sample(range(root_note, root_note + note_range), num_notes)
    solfege_names = [solfege_map.get(note, "note_{}".format(note)) for note in midi_notes]

    test_audio = np.array([])
    for note in midi_notes:
        frequency = midi_to_frequency(note)
        waveform = create_note(frequency, test_duration, sample_rate)
        test_audio = np.concatenate((test_audio, waveform))

    max_val = np.max(np.abs(test_audio))
    if max_val > 0:
        test_audio = test_audio * (32767 / max_val)
    test_audio = np.nan_to_num(test_audio).astype(np.int16)


    combined_audio = np.concatenate((intro_audio, silence_between_intro_and_test, test_audio))

    sanitized_solfege_names = [name.replace('/', '|') for name in solfege_names]

    # Use sanitized names to construct the filename
    if 'n/a' in sanitized_solfege_names:
        filename = "sequence_{}_{}.wav".format(root_note, random.randint(1000, 9999))  # Fallback filename
    else:
        filename = "_".join(sanitized_solfege_names) + ".wav"  # Sanitized filename

    filepath = os.path.join(folder_name, filename)
    write(filepath, sample_rate, combined_audio)
    print(f"Root Note: {root_note}, Frequency: {midi_to_frequency(root_note)}")



    return filepath, filename



print("Settings in use: ", intro_duration, test_duration, space_duration) 



    
