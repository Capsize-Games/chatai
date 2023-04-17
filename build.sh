#!/usr/bin/bash
# this should be called from within docker to kick off a build
DISABLE_TELEMETRY=1
cd /app
echo ""
echo "============================================"
echo "Installing dependencies"
echo "============================================"
echo ""
python3 /app/build.py
echo ""
echo "============================================"
echo "Build chatairunner for linux"
echo "============================================"
echo ""
DEV_ENV=0 CHATAIRUNNER_ENVIRONMENT="prod" PYTHONOPTIMIZE=0 python3 -m PyInstaller --log-level=INFO --noconfirm  build.chatai.linux.prod.spec 2>&1 | tee build.log
echo ""
echo "============================================"
echo "Deploying chatairunner to itch.io"
echo "============================================"
echo ""
chown -R 1000:1000 dist
LATEST_TAG=$(grep -oP '(?<=version=).*(?=,)' setup.py | tr -d "'")
echo "Latest tag: $LATEST_TAG"
wget https://dl.itch.ovh/butler/linux-amd64/head/butler && chmod +x butler
./butler push ./dist/chatairunner capsizegames/chat-ai:ubuntu --userversion $LATEST_TAG