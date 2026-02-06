#!/bin/bash
# mac2win-zip Finder 통합 제거 스크립트

WORKFLOW_NAME="mac2win-compress.workflow"
SERVICES_DIR="$HOME/Library/Services"

echo ""
echo "🗑️  mac2win-zip Finder 통합을 제거합니다..."
echo ""

# Quick Action 제거
if [ -d "$SERVICES_DIR/$WORKFLOW_NAME" ]; then
    rm -rf "$SERVICES_DIR/$WORKFLOW_NAME"
    echo "✅ Quick Action이 제거되었습니다."
else
    echo "ℹ️  Quick Action이 이미 제거되어 있습니다."
fi

# CLI 제거 여부 확인
# curl | bash로 실행 시 stdin이 파이프이므로 interactive가 아님
if [ -t 0 ]; then
    echo ""
    read -p "mac2win-zip CLI도 제거하시겠습니까? (y/N): " REMOVE_CLI
    if [[ "$REMOVE_CLI" =~ ^[Yy]$ ]]; then
        if command -v uv &>/dev/null; then
            uv tool uninstall mac2win-zip 2>/dev/null && echo "✅ CLI가 제거되었습니다." || echo "⚠️  uv를 통한 CLI 제거 실패. 수동으로 제거해주세요."
        elif command -v pipx &>/dev/null; then
            pipx uninstall mac2win-zip 2>/dev/null && echo "✅ CLI가 제거되었습니다." || echo "⚠️  pipx를 통한 CLI 제거 실패. 수동으로 제거해주세요."
        elif command -v pip3 &>/dev/null; then
            pip3 uninstall -y mac2win-zip 2>/dev/null && echo "✅ CLI가 제거되었습니다." || echo "⚠️  pip3를 통한 CLI 제거 실패. 수동으로 제거해주세요."
        else
            echo "⚠️  패키지 매니저를 찾을 수 없습니다. CLI를 수동으로 제거해주세요."
        fi
    fi
fi

echo ""
echo "👋 제거가 완료되었습니다."
echo ""
