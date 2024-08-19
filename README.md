DRM Packager GUI
================

This is a simple GUI wrapper around ffmpeg and shaka packager

It takes a directory of (multibitrate) video files as a source, and:
- encode files using shaka packages (this is a main task, at least one drm should be used), and produce one-file-per-stream output
- could produce hls and dash playlists for the encoded files
- produce multibitrate single-file result

(c) 2024-... mediatech.dev

Requirements:

* You will need ffmpeg and packager (shaka-packager) in your PATH.
* Python should be compiled with Tk support, on mac: `brew install python-tk`
* You will need your widevine, fairplay or playready credentials
