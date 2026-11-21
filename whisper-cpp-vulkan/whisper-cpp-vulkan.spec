# whisper.cpp command line tools with the Vulkan GPU backend.
#
# Fedora's own whisper-cpp package ships only the libraries (no CLI) and
# uses the ROCm/HIP backend. This one has whisper-cli and friends talking
# to the GPU through Vulkan (RADV), so it works on every machine with a
# working Vulkan driver.
#
# Programs: whisper-cli (files), whisper-server (HTTP, model stays loaded),
# whisper-stream (live microphone transcription, SDL2),
# whisper-vad-speech-segments (Silero VAD) and parakeet-cli (NVIDIA
# Parakeet TDT models).
#
# whisper and ggml are built as shared libraries (upstream default), but
# live in a private directory, %{_libdir}/whisper-cpp-vulkan, found via
# RPATH. Fedora's whisper-cpp and llama-cpp packages both put their own
# libggml*.so into %{_libdir}; this package can be installed next to them.
#
# Build (on ryzen9, once per Fedora release / whisper.cpp version):
#
#   sudo dnf builddep whisper-cpp-vulkan.spec
#   spectool -g -R whisper-cpp-vulkan.spec     # or git archive, see below
#   rpmbuild -bb whisper-cpp-vulkan.spec
#   cp ~/rpmbuild/RPMS/x86_64/whisper-cpp-vulkan-*.rpm /data/RPMs/
#
# Without spectool, from a checkout in ~/src/whisper.cpp:
#
#   git -C ~/src/whisper.cpp archive --prefix=whisper.cpp-1.9.5/ v1.9.5 \
#       | gzip > ~/rpmbuild/SOURCES/whisper.cpp-1.9.5.tar.gz

# No debuginfo subpackage
%global debug_package %{nil}

# The private libraries must not show up as Provides (they would satisfy
# other packages' libwhisper/libggml dependencies) nor as Requires.
%global privlibdir %{_libdir}/%{name}
%global __provides_exclude_from ^%{privlibdir}/.*$
%global __requires_exclude ^lib(whisper|parakeet|ggml(-[a-z]+)?)\.so.*$

Name:           whisper-cpp-vulkan
Version:        1.9.5
Release:        2%{?dist}
Summary:        whisper.cpp speech-to-text tools with the Vulkan GPU backend

License:        MIT
URL:            https://github.com/ggml-org/whisper.cpp
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/whisper.cpp-%{version}.tar.gz

ExclusiveArch:  x86_64

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  glslc
BuildRequires:  vulkan-headers
BuildRequires:  vulkan-loader-devel
BuildRequires:  spirv-headers-devel
BuildRequires:  pkgconfig(sdl2)

%description
The whisper-cli, whisper-server, whisper-stream, whisper-vad-speech-segments
and parakeet-cli programs of whisper.cpp, built with the ggml Vulkan backend.
Its whisper/ggml shared libraries are private to this package. The CPU code
path targets AVX2/FMA/F16C/BMI2 (not the build host's CPU), so the same
package runs on any x86-64-v3 machine.

Models are not included.

%prep
%autosetup -n whisper.cpp-%{version}
# Of the SDL2 examples only whisper-stream is wanted. talk-llama would
# also git-clone llama.cpp at configure time (no network/git in mock).
sed -i -E '/add_subdirectory\((command|talk-llama|lsp)\)/d' examples/CMakeLists.txt

%build
# GGML_NATIVE=OFF: do not use -march=native. The instruction sets have to
# be switched on one by one: rpmbuild sets SOURCE_DATE_EPOCH, which makes
# ggml default all of them to OFF (plain SSE2 otherwise).
# Shared libraries go to a private libdir, with a matching RPATH.
%cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_LIBDIR=%{_lib}/%{name} \
    -DCMAKE_INSTALL_RPATH=%{privlibdir} \
    -DGGML_VULKAN=ON \
    -DGGML_NATIVE=OFF \
    -DGGML_SSE42=ON \
    -DGGML_AVX=ON \
    -DGGML_AVX2=ON \
    -DGGML_FMA=ON \
    -DGGML_F16C=ON \
    -DGGML_BMI2=ON \
    -DGGML_CCACHE=OFF \
    -DWHISPER_BUILD_EXAMPLES=ON \
    -DWHISPER_BUILD_TESTS=OFF \
    -DWHISPER_BUILD_SERVER=ON \
    -DWHISPER_SDL2=ON
%cmake_build

%install
%cmake_install
# Keep the programs listed in %%files and the runtime libraries only: no
# other example programs, no headers, no cmake/pkgconfig files, no .so
# dev symlinks.
find %{buildroot}%{_bindir} -type f \
    ! -name whisper-cli ! -name whisper-server ! -name whisper-stream \
    ! -name whisper-vad-speech-segments ! -name parakeet-cli -delete
rm -rf %{buildroot}%{_includedir} \
       %{buildroot}%{privlibdir}/cmake \
       %{buildroot}%{privlibdir}/pkgconfig
rm -f %{buildroot}%{privlibdir}/*.so

%files
%license LICENSE
%doc README.md
%{_bindir}/whisper-cli
%{_bindir}/whisper-server
%{_bindir}/whisper-stream
%{_bindir}/whisper-vad-speech-segments
%{_bindir}/parakeet-cli
%dir %{privlibdir}
%{privlibdir}/*.so.*

%changelog
* Sat Nov 21 2026 Philipp Reisner <phil@localhost> - 1.9.5-2
- Also ship whisper-server, whisper-stream (SDL2), whisper-vad-speech-segments
  and parakeet-cli

* Fri Nov 13 2026 Philipp Reisner <phil@localhost> - 1.9.5-1
- Initial package: whisper-cli with Vulkan backend, private shared libs
