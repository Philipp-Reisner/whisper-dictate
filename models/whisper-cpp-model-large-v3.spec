# OpenAI Whisper large-v3 model in whisper.cpp's ggml format, as a noarch RPM.
#
# Companion to whisper-cpp-vulkan.spec. The model is one 2.9 GiB file.
#
# Built in Copr reisner/whisper-vulkan; the model is downloaded during
# %%build, so the build needs network access.

%global model       ggml-large-v3.bin
# SHA1 as published in whisper.cpp's models/README.md
%global model_sha1  ad82bf6a9043ceed055076d0fd39f5f186ff8062
%global modeldir    %{_datadir}/whisper-cpp/models

# Nothing to strip or to extract debuginfo from
%global debug_package %{nil}
%global __os_install_post %{nil}
# The weights are float16 and hardly compress; do not burn minutes on it.
%global _binary_payload w1T0.zstdio

Name:           whisper-cpp-model-large-v3
Version:        3
Release:        2
Summary:        Whisper large-v3 speech recognition model for whisper.cpp (ggml)

License:        MIT
URL:            https://huggingface.co/ggerganov/whisper.cpp

BuildArch:      noarch
BuildRequires:  curl

%description
The multilingual OpenAI Whisper large-v3 model, converted to the ggml
format used by whisper.cpp. Installed as %{modeldir}/%{model};
use it with "whisper-cli -m %{modeldir}/%{model}".

%prep

%build
# The model is too big for the SRPM: fetch it here (needs network access
# during the build, e.g. Copr with "--enable-net on").
curl -fsSL --retry 3 -o %{model} https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin
echo "%{model_sha1}  %{model}" | sha1sum -c -

%install
install -D -p -m 0644 %{model} %{buildroot}%{modeldir}/%{model}

%files
%dir %{_datadir}/whisper-cpp
%dir %{modeldir}
%{modeldir}/%{model}

%changelog
* Sat Nov 21 2026 Philipp Reisner <phil@localhost> - 3-2
- Download the model during %%build instead of shipping it in the SRPM

* Fri Nov 13 2026 Philipp Reisner <phil@localhost> - 3-1
- Initial package
