#!/bin/bash
# Build tarball for mLinux 7 deployment
set -e

APP_NAME="webapi_example"
VERSION="1.0.4"
MLINUX_VERSION="mlinux7"
TARBALL_NAME="${APP_NAME}-${VERSION}-${MLINUX_VERSION}.tar.gz"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Building ${TARBALL_NAME}..."

# Create temporary build directory
BUILD_DIR=$(mktemp -d)
trap "rm -rf $BUILD_DIR" EXIT

# Copy dist files (manifest, Install, Start, status.json, config)
cp -r dist/* "$BUILD_DIR/"

# Copy source code
cp -r src/webapi_example "$BUILD_DIR/"

# Set permissions
chmod +x "$BUILD_DIR/Install"
chmod +x "$BUILD_DIR/Start"
chmod 644 "$BUILD_DIR/manifest.json"
chmod 644 "$BUILD_DIR/status.json"
chmod 644 "$BUILD_DIR/config/config.json"

# Create tarball
cd "$BUILD_DIR"
tar -czf "$SCRIPT_DIR/$TARBALL_NAME" .

echo "Created: $SCRIPT_DIR/$TARBALL_NAME"
echo "Contents:"
tar -tzf "$SCRIPT_DIR/$TARBALL_NAME"
