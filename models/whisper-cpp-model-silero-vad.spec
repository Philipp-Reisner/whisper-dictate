# Silero voice activity detection (VAD) model v6.2.0 in whisper.cpp's ggml format, as a noarch RPM.
#
# Companion to whisper-cpp-vulkan.spec. Used by whisper-cli/whisper-server --vad
# and whisper-vad-speech-segments to find speech and pauses. Tiny (865 KiB).
#
# Built in Copr reisner/whisper-vulkan; the model is downloaded during
# %%build, so the build needs network access.

%global model       ggml-silero-v6.2.0.bin
# SHA256 of the Hugging Face LFS object
%global model_sha256  2aa269b785eeb53a82983a20501ddf7c1d9c48e33ab63a41391ac6c9f7fb6987
%global modeldir    %{_datadir}/whisper-cpp/models

# Nothing to strip or to extract debuginfo from
%global debug_package %{nil}
%global __os_install_post %{nil}
# The weights hardly compress; do not burn minutes on it.
%global _binary_payload w1T0.zstdio

Name:           whisper-cpp-model-silero-vad
Version:        6.2.0
Release:        1
Summary:        Silero voice activity detection model for whisper.cpp (ggml)

License:        MIT
URL:            https://huggingface.co/ggml-org/whisper-vad

BuildArch:      noarch
BuildRequires:  curl

%description
The Silero VAD v6.2.0 model in ggml format, for the --vad options of
whisper.cpp. Installed as %{modeldir}/%{model}.

%prep

%build
# The model is too big for the SRPM: fetch it here (needs network access
# during the build, e.g. Copr with "--enable-net on").
curl -fsSL --retry 3 -o %{model} https://huggingface.co/ggml-org/whisper-vad/resolve/main/ggml-silero-v6.2.0.bin
echo "%{model_sha256}  %{model}" | sha256sum -c -

%install
install -D -p -m 0644 %{model} %{buildroot}%{modeldir}/%{model}

%files
%dir %{_datadir}/whisper-cpp
%dir %{modeldir}
%{modeldir}/%{model}

%changelog
* Sat Nov 21 2026 Philipp Reisner <phil@localhost> - 6.2.0-1
- Initial package
