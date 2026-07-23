from demucs.api import Separator, save_audio
from pathlib import Path


class StemEngine:

    def __init__(self):
        print("Initializing Demucs...")
        self.separator = Separator()
        print("Demucs ready!")

    def separate(self, input_file, progress_callback=None):

        print(f"Separating: {input_file}")

        origin, separated = self.separator.separate_audio_file(input_file)

        input_path = Path(input_file)

        output_folder = (
            input_path.parent /
            "StemGen_Output" /
            input_path.stem
        )

        output_folder.mkdir(parents=True, exist_ok=True)

        for stem, source in separated.items():

            output_file = output_folder / f"{stem}.wav"

            print(f"Saving {output_file.name}")

            save_audio(
                source,
                str(output_file),
                samplerate=self.separator.samplerate
            )

        print("Finished separating.")

        return str(output_folder)   