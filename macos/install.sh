#!/bin/bash
set -e

REPO_URL="https://raw.githubusercontent.com/Wordbe/mac2win-zip/main"
WORKFLOW_NAME="mac2win-compress.workflow"
SERVICES_DIR="$HOME/Library/Services"

echo ""
echo "🚀 mac2win-zip Finder 통합을 설치합니다..."
echo ""

# --- Python 3.8+ 확인 ---

check_python() {
    if command -v python3 &>/dev/null; then
        PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
            echo "✅ Python $PY_VERSION 감지됨"
            return 0
        fi
    fi
    echo "❌ Python 3.8 이상이 필요합니다."
    echo "   brew install python3 또는 https://python.org 에서 설치하세요."
    exit 1
}

# --- CLI 설치 ---

install_cli() {
    export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

    if command -v mac2win-zip &>/dev/null; then
        echo "✅ mac2win-zip이 이미 설치되어 있습니다."
        return 0
    fi

    echo "📦 mac2win-zip CLI를 설치합니다..."

    if command -v uv &>/dev/null; then
        echo "   uv를 사용하여 설치 중..."
        uv tool install mac2win-zip
    elif command -v pipx &>/dev/null; then
        echo "   pipx를 사용하여 설치 중..."
        pipx install mac2win-zip
    elif command -v pip3 &>/dev/null; then
        echo "   pip3를 사용하여 설치 중..."
        pip3 install --user mac2win-zip
    else
        echo "❌ uv, pipx 또는 pip3가 필요합니다."
        echo ""
        echo "   uv 설치: curl -LsSf https://astral.sh/uv/install.sh | sh"
        echo "   또는 pip3: brew install python3"
        exit 1
    fi

    echo "✅ mac2win-zip CLI 설치 완료"
}

# --- Quick Action 설치 ---

install_workflow() {
    echo "📁 Quick Action을 설치합니다..."

    mkdir -p "$SERVICES_DIR"

    SCRIPT_DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"

    if [ -d "$SCRIPT_DIR/$WORKFLOW_NAME" ]; then
        cp -R "$SCRIPT_DIR/$WORKFLOW_NAME" "$SERVICES_DIR/"
    else
        TEMP_DIR=$(mktemp -d)
        trap "rm -rf \"$TEMP_DIR\"" EXIT

        mkdir -p "$TEMP_DIR/$WORKFLOW_NAME/Contents"
        curl -fsSL "$REPO_URL/macos/$WORKFLOW_NAME/Contents/Info.plist" \
            -o "$TEMP_DIR/$WORKFLOW_NAME/Contents/Info.plist"
        curl -fsSL "$REPO_URL/macos/$WORKFLOW_NAME/Contents/document.wflow" \
            -o "$TEMP_DIR/$WORKFLOW_NAME/Contents/document.wflow"

        cp -R "$TEMP_DIR/$WORKFLOW_NAME" "$SERVICES_DIR/"
    fi

    echo "✅ Quick Action 설치 완료"
}

# --- 실행 ---

check_python
install_cli
install_workflow

echo ""
echo "🎉 설치가 완료되었습니다!"
echo ""
echo "사용 방법:"
echo "  1. Finder에서 파일이나 폴더를 선택합니다"
echo "  2. 우클릭 → 빠른 동작 → 'mac2win 압축' 클릭"
echo "  3. Windows 호환 ZIP 파일이 생성됩니다"
echo ""
echo "제거하려면:"
echo "  curl -fsSL $REPO_URL/macos/uninstall.sh | bash"
echo ""
