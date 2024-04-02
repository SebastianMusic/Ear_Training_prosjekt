import tkinter as tk
import threading
import pygame
import os
from soundmodule import generate_sequence, load_settings, save_settings

# Initialize the mixer
pygame.mixer.init()

# Define global variables
global filename_label, generate_btn, intro_speed_entry, test_speed_entry, space_between_entry, filename, sound_type_var, root_note_var, num_notes_entry, note_range_slider
filename = ""
sound_type_var = None

def apply_settings():
    # Access global settings variables
    global intro_duration, test_duration, space_duration

    # Get values from the Entry widgets and convert them to floats
    intro_duration = float(intro_speed_entry.get())
    test_duration = float(test_speed_entry.get())
    space_duration = float(space_between_entry.get())

    print("Applying settings:", intro_duration, test_duration, space_duration)

    # Save settings after making changes
    save_settings(intro_duration, test_duration, space_duration)

def play_sound_and_generate():
    global filename, sound_type_var

    apply_settings()
    root_note = int(root_note_var.get())
    num_notes = int(num_notes_entry.get())
    note_range = note_range_slider.get()

    filepath, filename = generate_sequence(sound_type_var.get(), intro_duration, test_duration, space_duration, root_note, num_notes, note_range)

    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        print(f"Playing sound from {filepath}")
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
    else:
        print(f"Failed to generate valid audio at {filepath}")
    generate_btn.config(state=tk.DISABLED)
    threading.Thread(target=wait_for_playback_to_finish).start()

def wait_for_playback_to_finish():
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    # Re-enable the generate button after playback finishes
    generate_btn.config(state=tk.NORMAL)

def stop_audio():
    pygame.mixer.music.fadeout(500)

def reveal_filename():
    # Use the global filename variable
    filename_label.config(text=f"Filename: {filename}" if filename else "Please generate a sound first.")

def main():
    global intro_speed_entry, test_speed_entry, space_between_entry, filename_label, generate_btn, sound_type_var
    global root_note_var, num_notes_entry, note_range_slider  # Add this line

    window = tk.Tk()
    window.title("Solfege Ear Training")
    window.geometry("400x250")

    # Define the function load_initial_settings inside main before calling it
    def load_initial_settings():
        # Access the entry widgets directly since they're in the same scope
        intro_speed, test_speed, space_between = load_settings()

        intro_speed_entry.delete(0, tk.END)
        test_speed_entry.delete(0, tk.END)
        space_between_entry.delete(0, tk.END)

        intro_speed_entry.insert(0, str(intro_speed))
        test_speed_entry.insert(0, str(test_speed))
        space_between_entry.insert(0, str(space_between))

    # Initialize the sound type variable after creating the Tk window
    sound_type_var = tk.StringVar(value="scale")

    # Define the GUI elements

    # GUI setup...
    # Inside the main() function, after other GUI elements setup

    # Dropdown for root note selection
    root_note_label = tk.Label(window, text="Root Note (MIDI):")
    root_note_label.pack()
    root_note_var = tk.StringVar(window)
    root_note_var.set("60")  # default value
    root_note_options = [str(i) for i in range(21, 109)]  # MIDI note numbers for piano keys
    root_note_menu = tk.OptionMenu(window, root_note_var, *root_note_options)
    root_note_menu.pack()

    # Entry for number of notes
    num_notes_label = tk.Label(window, text="Number of Notes:")
    num_notes_label.pack()
    num_notes_entry = tk.Entry(window)
    num_notes_entry.insert(0, "8")  # default value
    num_notes_entry.pack()

    # Slider for note range
    note_range_label = tk.Label(window, text="Note Range (Semitones):")
    note_range_label.pack()
    note_range_slider = tk.Scale(window, from_=1, to_=36, orient=tk.HORIZONTAL)
    note_range_slider.set(12)  # default value, one octave
    note_range_slider.pack()

    intro_speed_label = tk.Label(window, text="Intro Speed (s):")
    intro_speed_label.pack()
    intro_speed_entry = tk.Entry(window)
    intro_speed_entry.pack()

    test_speed_label = tk.Label(window, text="Test Speed (s):")
    test_speed_label.pack()
    test_speed_entry = tk.Entry(window)
    test_speed_entry.pack()

    space_between_label = tk.Label(window, text="Space Between (s):")
    space_between_label.pack()
    space_between_entry = tk.Entry(window)
    space_between_entry.pack()

    # Radio Buttons for Scale and Chord selection
    scale_radio = tk.Radiobutton(window, text="Scale", variable=sound_type_var, value="scale")
    scale_radio.pack()
    chord_radio = tk.Radiobutton(window, text="Chord", variable=sound_type_var, value="chord")
    chord_radio.pack()

    # Add the generate and stop buttons
    generate_btn = tk.Button(window, text="Generate", command=play_sound_and_generate)
    generate_btn.pack(pady=5)

    stop_btn = tk.Button(window, text="Stop", command=stop_audio)
    stop_btn.pack(pady=5)

    # Add the reveal button
    reveal_btn = tk.Button(window, text="Reveal", command=reveal_filename)
    reveal_btn.pack(pady=5)

    # Add the filename label
    filename_label = tk.Label(window, text="")
    filename_label.pack(pady=10)

    # Add an "Apply Settings" button to the GUI
    apply_settings_btn = tk.Button(window, text="Apply Settings", command=apply_settings)
    apply_settings_btn.pack(pady=5)

    # Load initial settings
    load_initial_settings()

    window.mainloop()

    def load_initial_settings():
        # No need to declare global here since we're inside main
        intro_speed, test_speed, space_between = load_settings()

        intro_speed_entry.delete(0, tk.END)
        test_speed_entry.delete(0, tk.END)
        space_between_entry.delete(0, tk.END)

        intro_speed_entry.insert(0, str(intro_speed))
        test_speed_entry.insert(0, str(test_speed))
        space_between_entry.insert(0, str(space_between))

if __name__ == "__main__":
    main()