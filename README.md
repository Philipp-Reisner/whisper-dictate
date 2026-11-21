# whisper-dictate

Offline voice dictation into any window on Fedora KDE Plasma (Wayland):
press **Meta+Space**, speak (German, English, mixed, …), press **Meta+Space**
again, and the text is typed where the cursor is. Speech recognition runs
locally with [whisper.cpp](https://github.com/ggml-org/whisper.cpp) on the GPU
(Vulkan); no audio leaves the machine.

This repository holds the RPM spec files. The packages are built in Copr:
<https://copr.fedorainfracloud.org/coprs/reisner/whisper-vulkan/>

## Install

```sh
sudo dnf copr enable reisner/whisper-vulkan
sudo dnf install whisper-dictate          # pulls whisper-cpp-vulkan + turbo model
```

Then log out and in again (KDE picks up the Meta+Space shortcut from
`dictate.desktop`). Optionally keep the model loaded from login on:

```sh
systemctl --user enable --now dictate-server.service
```

Otherwise the first Meta+Space starts it, and the model loads while you speak.

Typing goes through `/dev/uinput` (dotool). Your user needs write access:

```sh
getfacl -p /dev/uinput            # a line "user:<you>:rw-" is enough
sudo usermod -aG input $USER      # otherwise; then log out and in
```

## Packages

| Directory | Package | Contents |
|---|---|---|
| `dictate/` | `whisper-dictate` | `/usr/bin/dictate`, Meta+Space shortcut, `dictate-server.service`, `/etc/dictate.conf` |
| `whisper-cpp-vulkan/` | `whisper-cpp-vulkan` | `whisper-cli`, `whisper-server`, `whisper-stream`, `whisper-vad-speech-segments`, `parakeet-cli`; Vulkan backend, private libs in `/usr/lib64/whisper-cpp-vulkan` |
| `models/` | `whisper-cpp-model-large-v3-turbo` | 1.5 GiB, the default model |
| | `whisper-cpp-model-large-v3` | 2.9 GiB, slightly more accurate, slower |
| | `whisper-cpp-model-silero-vad` | voice activity detection (for pause detection) |
| | `whisper-cpp-model-parakeet-tdt-0.6b-v3` | NVIDIA Parakeet, for `parakeet-cli` |

Models land in `/usr/share/whisper-cpp/models/`. The model specs download the
model from Hugging Face during `%build` and verify its checksum, so the
SRPMs stay small; the build needs network access (Copr: `--enable-net on`).

## How dictate works

```
Meta+Space ─► dictate toggle
   1st press: pw-record → $XDG_RUNTIME_DIR/dictate/rec.wav (16 kHz mono);
              starts dictate-server.service if not running
   2nd press: stop recording → POST to whisper-server (127.0.0.1:8178)
              → dotool types the text into the focused window
              (falls back to whisper-cli if the server is not reachable)
```

- **dotool** types via uinput, so it works in every Wayland application
  (`wtype` does not work on KWin). The XKB layout is taken from KDE
  (`~/.config/kxkbrc`) or `localectl`, so umlauts come out right.
- **audio_ctx**: whisper always encodes a 30 s window. For short dictations
  `dictate` shrinks it to about 2.5× the recording length, which roughly
  halves the time. With whisper.cpp 1.9.5's Vulkan backend only multiples
  of 256 give correct results (others produce garbage), so it rounds up.
- **Vocabulary prompt**: names and terms in `DICTATE_PROMPT` are spelled
  correctly much more often ("DRBD" instead of "der BD").

## Configuration

`/etc/dictate.conf` (documented defaults), overridden per user by
`~/.config/dictate.conf`, overridden by environment variables:

```sh
DICTATE_LANG=auto                       # or de, en, ...
DICTATE_PROMPT="DRBD, LINSTOR, LINBIT, Pacemaker, Kubernetes."
DICTATE_OUTPUT=type                     # paste (wl-copy + Ctrl+V), print (stdout)
DICTATE_MODEL=                          # default: turbo, else large-v3
DICTATE_SERVER=http://127.0.0.1:8178    # empty: always whisper-cli
DICTATE_AUDIO_CTX=auto                  # 0: full 30 s window
```

Test without a microphone and without typing anywhere:

```sh
espeak-ng -v de -w /tmp/t.wav "Ein kurzer Test mit DRBD und Pacemaker."
ffmpeg -loglevel error -y -i /tmp/t.wav -ar 16000 -ac 1 -c:a pcm_s16le /tmp/t16.wav
curl -F file=@/tmp/t16.wav -F response_format=text -F language=auto \
     http://127.0.0.1:8178/inference
```

## Troubleshooting

- Log: `$XDG_RUNTIME_DIR/dictate/log`; server: `journalctl --user -u dictate-server`.
- Nothing typed, but no error: check `/dev/uinput` access (see above).
- Wrong characters/umlauts: set `DOTOOL_XKB_LAYOUT` / `DOTOOL_XKB_VARIANT`.
- First characters missing: `DICTATE_OUTPUT=paste` (not in Konsole: Ctrl+Shift+V).
- Meta+Space does nothing: *System Settings → Shortcuts → Dictate*; a
  `~/.local/share/applications/dictate.desktop` overrides the system one.

## Building

Locally (needs network for the model specs):

```sh
spectool -g -R whisper-cpp-vulkan/whisper-cpp-vulkan.spec
sudo dnf builddep whisper-cpp-vulkan/whisper-cpp-vulkan.spec
rpmbuild -bb whisper-cpp-vulkan/whisper-cpp-vulkan.spec
rpmbuild -bb --define "_sourcedir $PWD/dictate" dictate/whisper-dictate.spec
```

In Copr: `copr-cli buildscm reisner/whisper-vulkan --clone-url <this repo> --subdir dictate --spec whisper-dictate.spec`
(likewise for the other directories).

## Ideas

- Type text at each pause while still speaking (Silero VAD, server stays loaded).
- Parakeet TDT v3 as a faster engine.

## License

MIT for the spec files and scripts. The models have their own licenses
(Whisper, Silero: MIT; Parakeet: CC-BY-4.0).
