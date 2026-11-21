# OpenAI Whisper large-v3-turbo model in whisper.cpp's ggml format, as a noarch RPM.
#
# Companion to whisper-cpp-vulkan.spec. large-v3 with the decoder cut from 32 to 4 layers:
# several times faster at nearly the same accuracy; the model of choice
# for live dictation. One 1.5 GiB file.
#
# Built in Copr reisner/whisper-vulkan; the model is downloaded during
# %%build, so the build needs network access.

%global model       ggml-large-v3-turbo.bin
# SHA1 as published in whisper.cpp's models/README.md
%global model_sha1  4af2b29d7ec73d781377bfd1758ca957a807e941
%global modeldir    %{_datadir}/whisper-cpp/models

# Nothing to strip or to extract debuginfo from
%global debug_package %{nil}
%global __os_install_post %{nil}
# The weights hardly compress; do not burn minutes on it.
%global _binary_payload w1T0.zstdio

Name:           whisper-cpp-model-large-v3-turbo
Version:        3
Release:        1
Summary:        Whisper large-v3-turbo speech recognition model for whisper.cpp (ggml)

License:        MIT
URL:            https://huggingface.co/ggerganov/whisper.cpp

BuildArch:      noarch
BuildRequires:  curl

%description
The multilingual OpenAI Whisper large-v3-turbo model, converted to the
ggml format used by whisper.cpp. Installed as %{modeldir}/%{model}.

%prep

%build
# The model is too big for the SRPM: fetch it here (needs network access
# during the build, e.g. Copr with "--enable-net on").
curl -fsSL --retry 3 -o %{model} https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin
echo "%{model_sha1}  %{model}" | sha1sum -c -

%install
install -D -p -m 0644 %{model} %{buildroot}%{modeldir}/%{model}

%files
%dir %{_datadir}/whisper-cpp
%dir %{modeldir}
%{modeldir}/%{model}

%changelog
* Sat Nov 21 2026 Philipp Reisner <phil@localhost> - 3-1
- Initial package
