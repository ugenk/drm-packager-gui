#!/usr/bin/env python3
import subprocess
import os
import glob
import json
import tkinter as tk
from tkinter import filedialog, messagebox, BooleanVar

class ShakaPackagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Shaka Packager GUI")

        # Input Directory
        self.input_dir_label = tk.Label(root, text="Input Directory")
        self.input_dir_label.grid(row=0, column=0, padx=10, pady=10)

        self.input_dir_entry = tk.Entry(root, width=50)
        self.input_dir_entry.grid(row=0, column=1, padx=10, pady=10)
        self.input_dir_entry.insert(0, '~/Movies/test')

        self.input_dir_button = tk.Button(root, text="Browse", command=self.browse_input_dir)
        self.input_dir_button.grid(row=0, column=2, padx=10, pady=10)

        # Output Directory
        self.output_dir_label = tk.Label(root, text="Output Directory")
        self.output_dir_label.grid(row=1, column=0, padx=10, pady=10)

        self.output_dir_entry = tk.Entry(root, width=50)
        self.output_dir_entry.grid(row=1, column=1, padx=10, pady=10)
        self.output_dir_entry.insert(0, '~/Movies/test2')

        self.output_dir_button = tk.Button(root, text="Browse", command=self.browse_output_dir)
        self.output_dir_button.grid(row=1, column=2, padx=10, pady=10)

        # DRM Selection
        self.widevine_var = BooleanVar(value=True)
        self.playready_var = BooleanVar(value=False)
        self.fairplay_var = BooleanVar(value=False)

        self.drm_label = tk.Label(root, text="Select DRM Systems:")
        self.drm_label.grid(row=2, column=0, padx=10, pady=10)

        self.widevine_checkbox = tk.Checkbutton(root, text="Widevine", variable=self.widevine_var)
        self.widevine_checkbox.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.playready_checkbox = tk.Checkbutton(root, text="PlayReady", variable=self.playready_var)
        self.playready_checkbox.grid(row=2, column=1, padx=10, pady=10)

        self.fairplay_checkbox = tk.Checkbutton(root, text="FairPlay", variable=self.fairplay_var)
        self.fairplay_checkbox.grid(row=2, column=1, padx=10, pady=10, sticky="e")

        # Widevine Settings
        self.widevine_frame = tk.LabelFrame(root, text="Widevine Settings")
        self.widevine_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.signer_label = tk.Label(self.widevine_frame, text="Signer")
        self.signer_label.grid(row=0, column=0, padx=10, pady=10)

        self.signer_entry = tk.Entry(self.widevine_frame, width=50)
        self.signer_entry.grid(row=0, column=1, padx=10, pady=10)
        self.signer_entry.insert(0, 'widevine_test')

        self.aes_key_label = tk.Label(self.widevine_frame, text="AES Signing Key")
        self.aes_key_label.grid(row=1, column=0, padx=10, pady=10)

        self.aes_key_entry = tk.Entry(self.widevine_frame, width=50)
        self.aes_key_entry.grid(row=1, column=1, padx=10, pady=10)
        # key and iv from https://shaka-project.github.io/shaka-packager/html/tutorials/widevine.html#widevine-test-credential
        self.aes_key_entry.insert(0, '1ae8ccd0e7985cc0b6203a55855a1034afc252980e970ca90e5202689f947ab9')

        self.aes_iv_label = tk.Label(self.widevine_frame, text="AES Signing IV")
        self.aes_iv_label.grid(row=2, column=0, padx=10, pady=10)
        self.aes_iv_label.insert(0, 'd58ce954203b7c9a9a9d467f59839249')

        self.aes_iv_entry = tk.Entry(self.widevine_frame, width=50)
        self.aes_iv_entry.grid(row=2, column=1, padx=10, pady=10)

        self.key_server_url_label = tk.Label(self.widevine_frame, text="Key Server URL")
        self.key_server_url_label.grid(row=3, column=0, padx=10, pady=10)

        self.key_server_url_entry = tk.Entry(self.widevine_frame, width=50)
        self.key_server_url_entry.grid(row=3, column=1, padx=10, pady=10)
        self.key_server_url_entry.insert(0, 'https://license.uat.widevine.com/cenc/getcontentkey/widevine_test')

        # PlayReady Settings
        self.playready_frame = tk.LabelFrame(root, text="PlayReady Settings")
        self.playready_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.playready_key_label = tk.Label(self.playready_frame, text="PlayReady Key")
        self.playready_key_label.grid(row=0, column=0, padx=10, pady=10)

        self.playready_key_entry = tk.Entry(self.playready_frame, width=50)
        self.playready_key_entry.grid(row=0, column=1, padx=10, pady=10)

        self.playready_iv_label = tk.Label(self.playready_frame, text="PlayReady IV")
        self.playready_iv_label.grid(row=1, column=0, padx=10, pady=10)

        self.playready_iv_entry = tk.Entry(self.playready_frame, width=50)
        self.playready_iv_entry.grid(row=1, column=1, padx=10, pady=10)

        # FairPlay Settings
        self.fairplay_frame = tk.LabelFrame(root, text="FairPlay Settings")
        self.fairplay_frame.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.fairplay_key_label = tk.Label(self.fairplay_frame, text="FairPlay Key")
        self.fairplay_key_label.grid(row=0, column=0, padx=10, pady=10)

        self.fairplay_key_entry = tk.Entry(self.fairplay_frame, width=50)
        self.fairplay_key_entry.grid(row=0, column=1, padx=10, pady=10)

        self.fairplay_iv_label = tk.Label(self.fairplay_frame, text="FairPlay IV")
        self.fairplay_iv_label.grid(row=1, column=0, padx=10, pady=10)

        self.fairplay_iv_entry = tk.Entry(self.fairplay_frame, width=50)
        self.fairplay_iv_entry.grid(row=1, column=1, padx=10, pady=10)

        self.fairplay_cert_label = tk.Label(self.fairplay_frame, text="FairPlay Certificate URL")
        self.fairplay_cert_label.grid(row=2, column=0, padx=10, pady=10)

        self.fairplay_cert_entry = tk.Entry(self.fairplay_frame, width=50)
        self.fairplay_cert_entry.grid(row=2, column=1, padx=10, pady=10)

        # Playlist Options
        self.hls_var = BooleanVar(value=False)
        self.dash_var = BooleanVar(value=False)

        self.mbr_mp4 = BooleanVar(value=True)

        self.playlist_label = tk.Label(root, text="Generate Playlists:")
        self.playlist_label.grid(row=6, column=0, padx=10, pady=10)

        self.hls_checkbox = tk.Checkbutton(root, text="HLS Playlist", variable=self.hls_var)
        self.hls_checkbox.grid(row=6, column=1, padx=10, pady=10, sticky="w")

        self.dash_checkbox = tk.Checkbutton(root, text="DASH Playlist", variable=self.dash_var)
        self.dash_checkbox.grid(row=6, column=1, padx=10, pady=10)

        self.mbr_mp4_checkbox = tk.Checkbutton(root, text="Multibitrate MP4", variable=self.mbr_mp4)
        self.mbr_mp4_checkbox.grid(row=6, column=1, padx=10, pady=10, sticky="e")

        # Pack Button
        self.pack_button = tk.Button(root, text="Pack", command=self.run_packager)
        self.pack_button.grid(row=7, column=1, pady=10)

    def browse_input_dir(self):
        input_dir = filedialog.askdirectory()
        if input_dir:
            self.input_dir_entry.insert(0, input_dir)

    def browse_output_dir(self):
        output_dir = filedialog.askdirectory()
        if output_dir:
            self.output_dir_entry.insert(0, output_dir)

    def run_packager(self):
        input_dir = self.input_dir_entry.get()
        output_dir = self.output_dir_entry.get()
        signer = self.signer_entry.get()
        aes_key = self.aes_key_entry.get()
        aes_iv = self.aes_iv_entry.get()
        key_server_url = self.key_server_url_entry.get()
        playready_key = self.playready_key_entry.get()
        playready_iv = self.playready_iv_entry.get()
        fairplay_key = self.fairplay_key_entry.get()
        fairplay_iv = self.fairplay_iv_entry.get()
        fairplay_cert = self.fairplay_cert_entry.get()

        if not input_dir or not output_dir:
            messagebox.showwarning("Warning", "Please fill input and output directories.")
            return

        drm_selected = any([self.widevine_var.get(), self.playready_var.get(), self.fairplay_var.get()])
        if not drm_selected:
            messagebox.showwarning("Warning", "Please select at least one DRM system.")
            return

        for filepath in glob.glob(os.path.join(input_dir, '*.mp4')):
            filename = os.path.basename(filepath)
            name, extension = os.path.splitext(filename)

            tmp_file = os.path.join(output_dir, "recode" + name + ".json")
            command = f"ffprobe -v quiet -print_format json -show_format -show_streams {filepath} > {tmp_file}"
            print(command)
            # Запуск ffprobe
            subprocess.run(command, shell=True, check=True)

            # Загрузка JSON с информацией о потоках
            with open(tmp_file, 'r') as f:
                data = json.load(f)

            count = 0
            vTracks, aTracks, sTracks = [], [], []
            vCount, aCount, sCount = 0, 0, 0

            # Создание команд для разделения потоков
            for stream in data['streams']:
                if stream['codec_type'] == 'video':
                    v_file = f"{output_dir}/{name}_v{vCount}.mp4"
                    v_command = f"ffmpeg -y -i {filepath} -c:v copy -map 0:{count} {v_file}"
                    subprocess.run(v_command, shell=True, check=True)
                    vTracks.append(f"{v_file}")
                    vCount += 1

                elif stream['codec_type'] == 'audio':
                    lang = stream["tags"].get("language", "und")
                    handler_name = stream["tags"].get("handler_name", "audio")
                    a_file = f"{output_dir}/{name}_a{aCount}.mp4"
                    a_command = f"ffmpeg -y -i {filepath} -c:a copy -map 0:{count} {a_file}"
                    subprocess.run(a_command, shell=True, check=True)
                    aTracks.append(f"{a_file}")
                    aCount += 1

                count += 1

            # Генерация уникального content_id
            content_id = ''.join(hex(ord(x))[2:] for x in filename)

            # Создание команды для упаковщика
            packager_command = ["packager"]
            protection_systems = []

            for index, v_file in enumerate(vTracks):
                packager_command.append(f"in={v_file},stream=video,output={name}/p/v{index}.mp4")
            for index, a_file in enumerate(aTracks):
                packager_command.append(f"in={a_file},stream=audio,hls_group_id=audio,hls_name={handler_name},lang={lang},output={name}/p/a{index}.mp4")

            # Обработка потоков (видео и аудио)
            if self.widevine_var.get():
                packager_command += [
                    "--enable_widevine_encryption",
                    f"--key_server_url {key_server_url}",
                    f"--content_id {content_id}",
                    f"--signer {signer}",
                    f"--aes_signing_key {aes_key}",
                    f"--aes_signing_iv {aes_iv}",
                ]
            protection_systems += ['Widevine']

            # Добавление опций для PlayReady
            if self.playready_var.get():
                packager_command += [
                    "--enable_playready_encryption",
                    f"--playready_key_id {content_id}",
                    f"--playready_key {playready_key}",
                    f"--playready_iv {playready_iv}",
                ]
            protection_systems += ['PlayReady']

            # Добавление опций для FairPlay
            if self.fairplay_var.get():
                packager_command += [
                    "--enable_fairplay_encryption",
                    f"--fairplay_key {fairplay_key}",
                    f"--fairplay_iv {fairplay_iv}",
                    f"--fairplay_cert {fairplay_cert}",
                ]
            protection_systems += ['FairPlay']

            protection_systems_as_string = ", ".join(system for system in protection_systems)
            packager_command.append('--protection_systems {protection_systems_as_string}')

            # Генерация HLS и/или DASH плейлистов
            if self.hls_var.get():
                hls_master_playlist_output = os.path.join(output_dir, f"{name}/p/index.m3u8")
                packager_command.append(f"--hls_master_playlist_output {hls_master_playlist_output}")

            if self.dash_var.get():
                dash_output = os.path.join(output_dir, f"{name}/p/index.mpd")
                packager_command.append(f"--mpd_output {dash_output}")
            print(packager_command)
            # Далее команда для упаковки и выполнения
            try:
                subprocess.run(" ".join(packager_command), check=True, shell=True)
                if not self.mbr_mp4.get():
                    messagebox.showinfo("Success", f"File processed successfully: {filename}")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Packaging failed for {filename}: {str(e)}")
            # сборка итогового файла

            if self.mbr_mp4.get():
                try:
                    final_output_file = os.path.join(output_dir, f"{name}_encrypted.mp4")
                    ffmpeg_inputs = " ".join([f"-i {file}" for file in vTracks + aTracks])
                    ffmpeg_maps = " ".join([f"-map {i}:v" for i in range(len(vTracks))] +
                           [f"-map {i+len(vTracks)}:a" for i in range(len(aTracks))])
                    ffmpeg_concat_command = f"ffmpeg -y {ffmpeg_inputs} {ffmpeg_maps} -c copy {final_output_file}"
                    print(ffmpeg_concat_command)
                    subprocess.run(ffmpeg_concat_command, shell=True, check=True)
                    messagebox.showinfo("Success", f"Final encrypted MP4 created for {filename}")
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Packaging failed for {filename}: {str(e)}")



if __name__ == "__main__":
    root = tk.Tk()
    gui = ShakaPackagerGUI(root)
    root.mainloop()
