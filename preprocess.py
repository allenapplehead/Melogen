import tensorflow as tf
import librosa
import os

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH

import audio_alignment_v2

import json

IN_FOLDER = 'D:/data/'
OUT_FOLDER = 'D:/clean_data/'

class SongPianoPair():
    def __init__(self, raw_song_audio, raw_piano_audio_path, output_song_midi_path, output_piano_midi_path, temp_song_audio_path="temp.wav"):
        self.raw_song_audio = raw_song_audio
        self.raw_piano_audio_path = raw_piano_audio_path
        self.raw_piano_midi = None

        self.temp_song_audio_path = temp_song_audio_path
        self.song_midi_path = output_song_midi_path
        self.piano_midi_path = output_piano_midi_path
        self.song_midi = None
        self.piano_midi = None

    def preprocess(self, basic_pitch_model):
        _, self.raw_piano_midi, _ = predict(self.raw_piano_audio_path, basic_pitch_model)
        audio_alignment_v2.align_song_piano(self, False)
        _, self.song_midi, _ = predict(self.temp_song_audio_path, basic_pitch_model)
        self.song_midi.write(self.song_midi_path)
        os.remove(self.temp_song_audio_path)

if __name__ == "__main__":
    basic_pitch_model = tf.saved_model.load(str(ICASSP_2022_MODEL_PATH))

    file_path = "data/songs.json"
    with open(file_path, "r") as json_file:
            songs_file = json.load(json_file)

    for song in songs_file["songs"]:
        song_file = song["filename"]
        song_num = int(song_file.split("_")[0])

        if song_num < 561:
            continue
        for piano_file in song["piano covers"]["filename"]:
            piano_cover_num = int(piano_file.split("_")[1])
            if song_num == 22 and piano_cover_num == 3:
                continue
            if song_num == 73 and piano_cover_num == 3:
                continue
            if song_num == 228 and piano_cover_num == 2:
                continue
            piano_file_size = os.path.getsize( IN_FOLDER + piano_file)
            song_file_size = os.path.getsize(IN_FOLDER + song_file)

            if piano_file_size > 70000000 or song_file_size > 70000000:
                continue
            try:

                song_audio, _ = librosa.load(IN_FOLDER + song_file , sr=audio_alignment_v2.Fs)
                name = os.path.splitext(piano_file)[0].split('_')[0] + "_" + os.path.splitext(piano_file)[0].split('_')[1]
                pair = SongPianoPair(song_audio, IN_FOLDER + piano_file, OUT_FOLDER + name + "_song.midi", OUT_FOLDER + name + "_cover.midi")
                pair.preprocess(basic_pitch_model)
            except Exception as e:
                print("Failed song", song_file, "cover", piano_file, "with exception", e)