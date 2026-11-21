# NVIDIA Parakeet TDT 0.6B v3 model (f16) in whisper.cpp's ggml format, as a noarch RPM.
#
# Companion to whisper-cpp-vulkan.spec. Used by parakeet-cli. Multilingual (25
# European languages incl. German and English), much faster than Whisper.
# One 1.2 GiB file.
#
# Built in Copr reisner/whisper-vulkan; the model is downloaded during
# %%build, so the build needs network access.

%global model       ggml-parakeet-tdt-0.6b-v3-f16.bin
# SHA256 of the Hugging Face LFS object
%global model_sha256  833bffc9513b2cae867ee9e51633cfd11e4d51aaa5597c8ac02159385a2b426f
%global modeldir    %{_datadir}/whisper-cpp/models

# Nothing to strip or to extract debuginfo from
%global debug_package %{nil}
%global __os_install_post %{nil}
# The weights hardly compress; do not burn minutes on it.
%global _binary_payload w1T0.zstdio

Name:           whisper-cpp-model-parakeet-tdt-0.6b-v3
Version:        3
Release:        1
Summary:        NVIDIA Parakeet TDT 0.6B v3 speech recognition model for whisper.cpp (ggml)

License:        CC-BY-4.0
URL:            https://huggingface.co/ggml-org/parakeet-GGUF

BuildArch:      noarch
BuildRequires:  curl

%description
The multilingual NVIDIA Parakeet TDT 0.6B v3 model, converted to the ggml
format used by whisper.cpp's parakeet-cli. Installed as
%{modeldir}/%{model}.

%prep

%build
# The model is too big for the SRPM: fetch it here (needs network access
# during the build, e.g. Copr with "--enable-net on").
curl -fsSL --retry 3 -o %{model} https://huggingface.co/ggml-org/parakeet-GGUF/resolve/main/ggml-parakeet-tdt-0.6b-v3-f16.bin
echo "%{model_sha256}  %{model}" | sha256sum -c -

%install
install -D -p -m 0644 %{model} %{buildroot}%{modeldir}/%{model}

%files
%dir %{_datadir}/whisper-cpp
%dir %{modeldir}
%{modeldir}/%{model}

%changelog
* Sat Nov 21 2026 Philipp Reisner <phil@localhost> - 3-1
- Initial package
