#!/usr/bin/env python3
import subprocess
import os
import glob
import json
import tkinter as tk
from tkinter import filedialog, messagebox

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

        # Signer Parameter
        self.signer_label = tk.Label(root, text="Signer")
        self.signer_label.grid(row=2, column=0, padx=10, pady=10)

        self.signer_entry = tk.Entry(root, width=50)
        self.signer_entry.grid(row=2, column=1, padx=10, pady=10)
        self.signer_entry.insert(0, 'widevine_test')

        # AES Signing Key
        self.aes_key_label = tk.Label(root, text="AES Signing Key")
        self.aes_key_label.grid(row=3, column=0, padx=10, pady=10)

        self.aes_key_entry = tk.Entry(root, width=50)
        self.aes_key_entry.grid(row=3, column=1, padx=10, pady=10)
        # self.aes_key_entry.insert(0, '')

        # AES Signing IV
        self.aes_iv_label = tk.Label(root, text="AES Signing IV")
        self.aes_iv_label.grid(row=4, column=0, padx=10, pady=10)

        self.aes_iv_entry = tk.Entry(root, width=50)
        self.aes_iv_entry.grid(row=4, column=1, padx=10, pady=10)
        # self.aes_iv_entry.insert(0, '')

        # Key Server URL
        self.key_server_url_label = tk.Label(root, text="Key Server URL")
        self.key_server_url_label.grid(row=5, column=0, padx=10, pady=10)

        self.key_server_url_entry = tk.Entry(root, width=50)
        self.key_server_url_entry.grid(row=5, column=1, padx=10, pady=10)
        self.key_server_url_entry.insert(0, 'https://license.uat.widevine.com/cenc/getcontentkey/widevine_test')

        # Pack Button
        self.pack_button = tk.Button(root, text="Pack", command=self.run_packager)
        self.pack_button.grid(row=6, column=1, pady=10)

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

        if not input_dir or not output_dir or not signer or not aes_key or not aes_iv or not key_server_url:
            messagebox.showwarning("Warning", "Please fill all fields.")
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
            for index, v_file in enumerate(vTracks):
                packager_command.append(f"in={v_file},stream=video,output={name}/p/v{index}.mp4")
            for index, a_file in enumerate(aTracks):
                packager_command.append(f"in={a_file},stream=audio,hls_group_id=audio,hls_name={handler_name},lang={lang},output={name}/p/a{index}.mp4")

            packager_command += [
                "--enable_widevine_encryption",
                f"--key_server_url {key_server_url}",
                f"--content_id {content_id}",
                f"--signer {signer}",
                "--hls_master_playlist_output " + os.path.join(output_dir, f"{name}/p/index.m3u8"),
                "--mpd_output " + os.path.join(output_dir, f"{name}/p/index.mpd"),
                f"--aes_signing_key {aes_key}",
                f"--aes_signing_iv {aes_iv}",
                "--enable_widevine_encryption"
            ]
            print(packager_command)
            # Запуск packager
            try:
                subprocess.run(" ".join(packager_command), check=True, shell=True)
                #messagebox.showinfo("Success", f"Packaging completed for {filename}")

                # Финальная команда ffmpeg для объединения всех зашифрованных потоков в один файл
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
