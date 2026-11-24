# dictate: press Meta+Space, speak, press Meta+Space again: the text is typed
# into the focused window. Offline speech recognition with whisper.cpp
# (Vulkan GPU backend), typing via dotool (uinput), KDE Plasma on Wayland.
#
# Sources are the files next to this spec. Built in Copr
# reisner/whisper-vulkan from the git repository (subdir dictate/).

Name:           whisper-dictate
Version:        1.0
Release:        3%{?dist}
Summary:        Offline voice dictation into any window with whisper.cpp

License:        MIT
URL:            https://github.com/Philipp-Reisner/whisper-dictate
Source0:        dictate
Source1:        dictate.conf
Source2:        dictate.desktop
Source3:        dictate-server.service

BuildArch:      noarch
BuildRequires:  systemd-rpm-macros

# whisper-server came with 1.9.5-2
Requires:       whisper-cpp-vulkan >= 1.9.5-2
Requires:       (whisper-cpp-model-large-v3-turbo or whisper-cpp-model-large-v3)
Recommends:     whisper-cpp-model-large-v3-turbo
Requires:       dotool
Requires:       kdotool
Requires:       util-linux-core
Requires:       gawk
Requires:       grep
Requires:       pipewire-utils
Requires:       wl-clipboard
Requires:       libnotify
Requires:       curl
Requires:       glib2
Requires:       systemd

%description
dictate records from the microphone while toggled with Meta+Space and types
the transcribed text into the focused window. Speech recognition runs
locally with whisper.cpp; a systemd user service keeps the model loaded
(whisper-server), so the text appears about a second after you stop.

The user needs write access to /dev/uinput for typing: be in group "input"
(dotool's udev rule) or have a uaccess ACL on it.

%prep

%build

%install
install -D -p -m 0755 %{SOURCE0} %{buildroot}%{_bindir}/dictate
install -D -p -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/dictate.conf
install -D -p -m 0644 %{SOURCE2} %{buildroot}%{_datadir}/applications/dictate.desktop
install -D -p -m 0644 %{SOURCE3} %{buildroot}%{_userunitdir}/dictate-server.service

%post
%systemd_user_post dictate-server.service

%preun
%systemd_user_preun dictate-server.service

%files
%{_bindir}/dictate
%config(noreplace) %{_sysconfdir}/dictate.conf
%{_datadir}/applications/dictate.desktop
%{_userunitdir}/dictate-server.service

%changelog
* Tue Nov 24 2026 Philipp Reisner <phil@localhost> - 1.0-3
- Block global shortcuts and release modifiers while typing: with Meta
  still held the text triggered shortcuts and every space re-toggled dictate
- Type only into the window focused when the recording stopped, not into
  the desktop, panel or lock screen; otherwise copy to the clipboard
- Drop typical whisper hallucinations (subtitle credits, Cyrillic
  "Спасибо", non-Latin script, a word looping)
- One toggle at a time (flock), ignore toggles 1 s after a dictation

* Sat Nov 21 2026 Philipp Reisner <phil@localhost> - 1.0-2
- Do not re-declare all shell variables when no DICTATE_* variable is set
  in the environment

* Sat Nov 21 2026 Philipp Reisner <phil@localhost> - 1.0-1
- Initial package: dictate toggle script, whisper-server user service,
  Meta+Space shortcut
