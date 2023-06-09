FROM ubuntu:latest as base_image
USER root
ENV TZ=America/Denver
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && apt-get update \
    && apt-get upgrade -y \
    && apt install software-properties-common -y \
    && add-apt-repository ppa:ubuntu-toolchain-r/test \
    && apt-get update \
    && dpkg --add-architecture i386 \
    && apt-get update \
    && apt-get install -y libtinfo6 git wget curl vim software-properties-common gcc-9 g++-9 bash build-essential libssl-dev libffi-dev libgl1-mesa-dev nvidia-cuda-toolkit xclip libjpeg-dev zlib1g-dev libpng-dev \
    && rm -rf /var/lib/apt/lists/ \
    && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 60 --slave /usr/bin/g++ g++ /usr/bin/g++-9

FROM base_image as wine_support
ENV WINEDEBUG=fixme-all
ENV DISPLAY=:0
ENV WINEARCH=win64
ENV WINEPREFIX=/home/.wine-win10
RUN apt-get update \
    && wget -nc https://dl.winehq.org/wine-builds/winehq.key \
    && apt-key add winehq.key \
    && add-apt-repository 'deb https://dl.winehq.org/wine-builds/ubuntu/ focal main' \
    && apt-get update \
    && apt-get install -y coreutils winbind xvfb winehq-stable winetricks x11-apps wine64 wine32 winbind cabextract \
    && winetricks win10

FROM wine_support as winegecko
RUN wget https://dl.winehq.org/wine/wine-gecko/2.47.1/wine-gecko-2.47.1-x86_64.msi \
    && wine64 msiexec /i wine-gecko-2.47.1-x86_64.msi \
    && rm wine-gecko-2.47.1-x86_64.msi

FROM winegecko as install_python
RUN wget https://www.python.org/ftp/python/3.10.8/python-3.10.8-amd64.exe \
    && xvfb-run -e /dev/stdout wine64 python-3.10.8-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 TargetDir=C:\\Python310 \
    && rm python-3.10.8-amd64.exe \
    && rm -rf /tmp/.X99-lock

FROM install_python as install_git
RUN apt-get install -y unzip \
    && wget https://github.com/git-for-windows/git/releases/download/v2.40.0.windows.1/MinGit-2.40.0-64-bit.zip -O MinGit-2.40.0-64-bit.zip \
    && unzip -o MinGit-2.40.0-64-bit.zip \
    && rm MinGit-2.40.0-64-bit.zip

FROM install_git as final
USER root
RUN export PATH="$(winepath -u "C:\Python310\Scripts"):$PATH" \
    && export PATH="$(winepath -u "C:\Python310\site-packages"):$PATH" \
    && export PATH="$(winepath -u "C:\Python310\site-packages\Pillow.libs"):$PATH" \
    && export PATH="$(winepath -u "C:\Python310\site-packages\tokenizers.libs"):$PATH" \
    && export PATH="$(winepath -u "C:\Python310\site-packages\xformers\triton"):$PATH" \
    && export PATH="$(winepath -u "C:\Python310\site-packages\nvidia\cuda_runtime\lib"):$PATH" \
    && export PATH="$(winepath -u "C:\Python310\site-packages\nvidia\cudnn\lib"):$PATH" \
    && export PATH="$(winepath -u "C:\Python310\site-packages\numpy.libs"):$PATH" \
    && export PATH="$(winepath -u "C:\Python310\site-packages\h5py.libs"):$PATH" \
    && export PATH="$(winepath -u "C:\Python310\site-packages\torchaudio\lib"):$PATH" \
    && export PATH="$(winepath -u "C:\Python310\site-packages\torch\lib"):$PATH" \
    && export PATH="$(winepath -u "C:\Python310\site-packages\torch\bin"):$PATH" \
    && export PATH="$(winepath -u "C:\Python310\site-packages\torch\_C"):$PATH" \
    && export PATH="$(winepath -u "C:\Python310\site-packages\torch"):$PATH" \
    && export PATH="$(winepath -u "C:\Python310\site-packages\triton"):$PATH" \
    && export PATH="$(winepath -u "C:\Python310\site-packages\triton/_C"):$PATH"

FROM final as install_apps
WORKDIR /app
USER root
ENV DISPLAY=:0
RUN apt-get install -y mesa-utils \
    && apt-get install -y libgl1-mesa-glx \
    && wine64 C:\\Python310\\python.exe -m pip install --upgrade pyinstaller \
    && wine64 C:\\Python310\\python.exe -m pip install torch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1 --index-url https://download.pytorch.org/whl/cu117 \
    && wine64 reg add "HKEY_CURRENT_USER\Environment" /v PATH /t REG_EXPAND_SZ /d "C:\\;Z:\\app\\lib\\PortableGit\\cmd;C:\\Program Files\\NVIDIA\\CUDNN\\v8.6.0.163\\bin;C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v11.7\\bin;C:\\Python310;C:\\Python310\\site-packages;C:\\Python310\\site-packages\\lib;%PATH%" /f \
    && apt install git \
    && chown root:root /home/.wine-win10 \
    && mkdir -p root:root /home/.wine-win10/drive_c/users/root && chown -R root:root root:root /home/.wine-win10/drive_c/users/root \
    && chown -R root:root /home/.wine-win10/drive_c/users/root \
    && mkdir -p /app/.cache/mesa_shader_cache && chown -R root:root /app/.cache/mesa_shader_cache \
    && mkdir -p /home/.wine-win10/drive_c/users/root/AppData/Roaming && chown -R root:root /home/.wine-win10/drive_c/users/root/AppData/Roaming \
    && mkdir -p /home/.wine-win10/drive_c/users/root/AppData/Local && chown -R root:root /home/.wine-win10/drive_c/users/root/AppData/Local

FROM install_apps as install_upx
RUN wget https://github.com/upx/upx/releases/download/v4.0.2/upx-4.0.2-win64.zip \
    && unzip -o upx-4.0.2-win64.zip \
    && cp upx-4.0.2-win64/upx.exe /home/.wine-win10/drive_c/Python310/Scripts/

FROM install_upx as install_libs
USER root
RUN wine64 C:\\Python310\\python.exe -m pip install torch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1 --index-url https://download.pytorch.org/whl/cu117 \
    && wine64 C:\\Python310\\python.exe -m pip install https://github.com/w4ffl35/diffusers/archive/refs/tags/v0.14.0.ckpt_fix.tar.gz \
    && wine64 C:\\Python310\\python.exe -m pip install https://github.com/w4ffl35/transformers/archive/refs/tags/tensor_fix-v1.0.2.tar.gz \
    && wine64 C:\\Python310\\python.exe -m pip install https://github.com/acpopescu/bitsandbytes/releases/download/v0.37.2-win.0/bitsandbytes-0.37.2-py3-none-any.whl \
    && wine64 C:\\Python310\\python.exe -m pip install aihandlerwindows \
    && wine64 C:\\Python310\\python.exe -m pip install requests \
    && git clone https://github.com/Capsize-Games/chatai.git /app/chatairunner
WORKDIR /app/chatairunner
RUN wine64 C:\\Python310\\python.exe -m pip install -e . --no-deps \
    && wine64 C:\\Python310\\python.exe -c "from accelerate.utils import write_basic_config; write_basic_config(mixed_precision='fp16')"

FROM install_libs as source_files
COPY build.windows.cmd /app/build.windows.cmd
COPY build.windows.py /app/build.windows.py
COPY build.chatairunner.windows.prod.spec /app/build.chatairunner.windows.prod.spec
COPY windows.itch.toml /app/windows.itch.toml
COPY src/chatairunner/v1.yaml /app/v1.yaml
COPY src/chatairunner/v2.yaml /app/v2.yaml
COPY src/chatairunner/src/icons /app/src/chatairunner/src/icons
COPY src/chatairunner/pyqt /app/src/chatairunner/pyqt
COPY setup.py /app/setup.py
COPY version.py /app/version.py
RUN cp /usr/lib/x86_64-linux-gnu/wine/api-ms-win-shcore-scaling-l1-1-1.dll /home/.wine-win10/drive_c/api-ms-win-shcore-scaling-l1-1-1.dll

FROM source_files as install_butler
RUN wget https://broth.itch.ovh/butler/windows-amd64/15.21.0/archive/default -O butler-windows-amd64.zip
RUN unzip butler-windows-amd64.zip -d butler-windows-amd64
RUN mv butler-windows-amd64/butler.exe /home/.wine-win10/drive_c/Python310/Scripts/butler.exe
RUN rm -rf butler-windows-amd64 butler-windows-amd64.zip
