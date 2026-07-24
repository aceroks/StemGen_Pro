"""
StemGen_Pro
Version 1.0.0

Main user interface for selecting a song, separating stems,
and opening the output folder.

Author: Steve Altomare
"""

# -------------------------------------------------
# Imports
# -------------------------------------------------
import subprocess
from os.path import basename, expanduser
from threading import Thread

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line
from math import sin

from stem_engine import StemEngine

class ActivityWave(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size_hint = (1, 0.05)

        self.running = False
        self.phase = 0

        with self.canvas:
            Color(0.25, 0.25, 0.25, 1)
            self.base_line = Line(width=1.2)

            Color(0.15, 0.65, 1.0, 1)
            self.pulse = Line(width=3)

        self.bind(pos=self.update_graphics,
                  size=self.update_graphics)

    def start(self):
        if self.running:
            return

        self.running = True
        self.event = Clock.schedule_interval(
            self.animate,
            1 / 30
        )

    def stop(self):
        self.running = False

        if hasattr(self, "event"):
            self.event.cancel()

        self.pulse.points = []

    def animate(self, dt):
        self.phase += 2

        if self.phase > 100:
            self.phase = 0

        self.update_graphics()

    def update_graphics(self, *args):

        line_width = 120

        left = self.center_x - line_width / 2
        right = self.center_x + line_width / 2
        y = self.center_y

        self.base_line.points = [
            left, y,
            right, y
        ]

        x = left + (line_width * self.phase / 100)

        if self.running:
            self.pulse.points = [
                x - 8, y,
                x + 8, y
            ]
        else:
            self.pulse.points = []

# -------------------------------------------------
# StemGen_Pro Application Class
# -------------------------------------------------

class StemGenProApp(App):

    # -------------------------------------------------
    # Song Selection
    # -------------------------------------------------

    def show_song_picker(self, instance):

        content = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=10
        )

        chooser = FileChooserListView(
            path=expanduser("~/Desktop/StemGen_TestSongs"),
            filters=["*.wav", "*.mp3", "*.flac", "*.aiff", "*.m4a"]
        )

        chooser.bind(selection=self.file_selected)

        content.add_widget(chooser)

        close_button = Button(
            text="Cancel",
            size_hint=(1, None),
            height=45
        )

        content.add_widget(close_button)

        self.song_popup = Popup(
            title="Choose Song",
            content=content,
            size_hint=(0.90, 0.90)
        )

        close_button.bind(on_press=self.song_popup.dismiss)

        self.song_popup.open()

    def open_output_folder(self, instance):
        if hasattr(self, "output_folder"):
            subprocess.run(["open", self.output_folder], check=False)

    def build(self):
        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=20,
            size_hint=(1, 1)
        )
        self.engine = StemEngine()

        title = Label(
            text="StemGen_Pro",
            font_size=28,
            size_hint=(1, 0.11)
        )

        self.choose_song_button = Button(
            text="Choose Song",
            size_hint=(None, None),
            width=220,
            height=48,
            pos_hint={"center_x": 0.5},
            background_normal="",
            background_color=(0.0, 0.45, 1.0, 1.0),
            color=(1, 1, 1, 1)
        )

        self.choose_song_button.bind(on_press=self.show_song_picker)

        self.song_label = Label(
            text="",
            size_hint=(1, 0.10)
        )

        status = Label(
            text="[b]Status[/b]\n\nNo Song Selected",
            markup=True,
            halign="center",
            valign="middle",
            size_hint=(1, 0.12)
        )

        status.bind(size=status.setter("text_size"))

        self.status = status

        output_box = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=(0, 8),
            size_hint=(1, 0.18)
        )

        output_title = Label(
            text="[b]4-Stem* AI Separation[/b]",
            markup=True,
            font_size="20sp",
            halign="center",
            valign="middle"
        )
        output_title.bind(size=output_title.setter("text_size"))

        output_box.add_widget(output_title)

        output_stems = Label(
            text="Vocals      Drums      Bass      Everything Else",
            halign="center",
            valign="middle"
        )
        output_stems.bind(size=output_stems.setter("text_size"))

        output_box.add_widget(output_stems)

        output_note = Label(
            text="*saved as WAV files",
            font_size="13sp",
            halign="center",
            valign="middle",
            size_hint=(1, None),
            height=24
        )
        output_note.bind(size=output_note.setter("text_size"))

        output_box.add_widget(output_note)

        self.separate_button = Button(
            text="Separate Stems",
            size_hint=(None, None),
            width=300,
            height=60,
            pos_hint={"center_x": 0.5},
            on_press=self.separate_stems,
            background_normal="",
            background_down="",
            background_color=(0.0, 0.45, 1.0, 1.0),
            color=(1, 1, 1, 1)
        )
        self.open_output_button = Button(
            text="Open Output Stems Folder",
            size_hint=(None, None),
            width=300,
            height=48,
            pos_hint={"center_x": 0.5},
            background_normal="",
            background_color=(0.0, 0.45, 1.0, 1.0),
            color=(1, 1, 1, 1),
            disabled=True,
            on_press=self.open_output_folder
        )

        layout.add_widget(title)
        layout.add_widget(output_box)
        layout.add_widget(self.choose_song_button)
        layout.add_widget(self.song_label)
        layout.add_widget(self.separate_button)
        layout.add_widget(status)

        self.activity = ActivityWave()
        layout.add_widget(self.activity)

        layout.add_widget(self.open_output_button)

        return layout
    
    def file_selected(self, chooser, selection):
        if selection:
            filename = basename(selection[0])
            self.selected_file = selection[0]
            self.song_label.text = f"🎵  {filename}"
            print("Selected:", selection[0])
            self.status.text = "[b]Status[/b]\n\nReady for Stem Separation"
            self.choose_song_button.background_color = (0.55, 0.55, 0.55, 1)

            if hasattr(self, "song_popup"):
                self.song_popup.dismiss()

    # -------------------------------------------------
    # Stem Separation
    # -------------------------------------------------
            
    def separate_stems(self, instance):
        if getattr(self, "is_separating", False):
            return
    
        if not hasattr(self, "selected_file"):
            self.status.text = (
                "[b]Status[/b]\n\n"
                "No Song Selected"
            )
            return

        self.status.text = (
            "[b]Status[/b]\n\n"
            "Separating stems..."
        )

        self.activity.start()

        self.is_separating = True
        self.separate_button.background_color = (0.55, 0.55, 0.55, 1)

        self.open_output_button.disabled = True

        separation_thread = Thread(
            target=self.run_separation,
            daemon=True
        )
        separation_thread.start()

    def run_separation(self):
        output_folder = self.engine.separate(
            self.selected_file,
            self.update_progress
        )

        if output_folder:
            Clock.schedule_once(
                lambda dt: self.separation_complete(output_folder),
                0
            )

    def update_progress(self, message):
        Clock.schedule_once(
            lambda dt: setattr(
                self.status,
                "text",
                f"[b]Status[/b]\n\n{message}"
            ),
            0
        )

    def separation_complete(self, output_folder):
        self.output_folder = output_folder

        self.activity.stop()

        self.status.text = (
            "[b]Status[/b]\n\n"
            "✓ Complete\n\n"
            "Saved to Output Stems Folder"
        )

        self.is_separating = False
        self.choose_song_button.background_color = (0.0, 0.45, 1.0, 1.0)
        self.separate_button.background_color = (0.0, 0.45, 1.0, 1.0)
                                                 
        self.open_output_button.disabled = False

    def separation_failed(self, message):
        self.status.text = (
            "[b]Status[/b]\n\n"
            f"Error:\n{message}"
        )

        self.separate_button.text = "Separate Stems"
        self.separate_button.disabled = False

if __name__ == "__main__":
    StemGenProApp().run()