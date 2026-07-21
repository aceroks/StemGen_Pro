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

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from stem_engine import StemEngine

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

        choose_song_button = Button(
            text="Choose Song",
            size_hint=(None, None),
            width=220,
            height=48,
            pos_hint={"center_x": 0.5},
            background_normal="",
            background_color=(0.0, 0.45, 1.0, 1.0),
            color=(1, 1, 1, 1)
        )

        choose_song_button.bind(on_press=self.show_song_picker)

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

        separate_button = Button(
            text="Separate Stems",
            size_hint=(None, None),
            width=300,
            height=60,
            pos_hint={"center_x": 0.5},
            on_press=self.separate_stems,
            background_normal="",
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
        layout.add_widget(choose_song_button)
        layout.add_widget(self.song_label)
        layout.add_widget(separate_button)
        layout.add_widget(status)
        layout.add_widget(self.open_output_button)

        return layout
    
    def file_selected(self, chooser, selection):
        if selection:
            filename = basename(selection[0])
            self.selected_file = selection[0]
            self.song_label.text = f"🎵  {filename}"
            print("Selected:", selection[0])
            self.status.text = "[b]Status[/b]\n\nReady for Stem Separation"
            if hasattr(self, "song_popup"):
                self.song_popup.dismiss()

    # -------------------------------------------------
    # Stem Separation
    # -------------------------------------------------
            
    def separate_stems(self, instance):
        if not hasattr(self, "selected_file"):
            self.status.text = (
                "[b]Status[/b]\n\n"
                "No Song Selected"
            )
            return

        filename = basename(self.selected_file)

        self.status.text = "[b]Status[/b]\n\nSeparating Stems..."

    # -------------------------------------------------
    # Output Folder
    # -------------------------------------------------

        output_folder = self.engine.separate(self.selected_file)

        if output_folder:
            self.output_folder = output_folder

            self.status.text = (
                "[b]Status[/b]\n\n"
                "✓ Complete\n\n"
                "Saved to Output Stems Folder"
            )

            self.open_output_button.disabled = False

if __name__ == "__main__":
    StemGenProApp().run()