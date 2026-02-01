# Laravel Bulk Installer - macOS Build Makefile
# Usage:
#   make build          - Build the package
#   make build-signed   - Build and sign the package
#   make clean          - Clean build artifacts
#   make install        - Install the built package
#   make uninstall      - Run the uninstaller
#   make dev            - Run the app directly for development

VERSION ?= 2.0.0
SIGN_IDENTITY ?=
PROJECT_ROOT := $(shell dirname $(CURDIR))
BUILD_DIR := $(CURDIR)/output
PKG_NAME := LaravelInstaller-$(VERSION).pkg

.PHONY: all build build-signed clean install uninstall dev help

all: build

help:
	@echo "Laravel Bulk Installer - Build System"
	@echo ""
	@echo "Targets:"
	@echo "  build         Build unsigned package"
	@echo "  build-signed  Build signed package (set SIGN_IDENTITY)"
	@echo "  clean         Remove build artifacts"
	@echo "  install       Install the built package"
	@echo "  uninstall     Run the uninstaller script"
	@echo "  dev           Run app directly for development"
	@echo ""
	@echo "Variables:"
	@echo "  VERSION=X.Y.Z       Set package version (default: 2.0.0)"
	@echo "  SIGN_IDENTITY=...   Developer ID for signing"
	@echo ""
	@echo "Examples:"
	@echo "  make build VERSION=2.1.0"
	@echo "  make build-signed SIGN_IDENTITY=\"Developer ID Installer: Name (TEAM)\""

build:
	@echo "Building Laravel Installer $(VERSION)..."
	@chmod +x $(CURDIR)/build.sh
	@VERSION=$(VERSION) $(CURDIR)/build.sh

build-signed:
ifndef SIGN_IDENTITY
	$(error SIGN_IDENTITY is required for signed builds)
endif
	@echo "Building signed Laravel Installer $(VERSION)..."
	@chmod +x $(CURDIR)/build.sh
	@VERSION=$(VERSION) $(CURDIR)/build.sh --sign "$(SIGN_IDENTITY)"

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR)
	@rm -rf $(CURDIR)/payload
	@rm -rf $(CURDIR)/pkg-scripts
	@rm -rf $(CURDIR)/pkg-resources
	@echo "Clean complete"

install: build
	@echo "Installing $(PKG_NAME)..."
	@sudo installer -pkg "$(BUILD_DIR)/$(PKG_NAME)" -target /
	@echo "Installation complete"

uninstall:
	@echo "Running uninstaller..."
	@chmod +x $(PROJECT_ROOT)/scripts/uninstall.sh
	@$(PROJECT_ROOT)/scripts/uninstall.sh

dev:
	@echo "Running app in development mode..."
	@python3 $(PROJECT_ROOT)/app.py

# Verify the built package
verify:
	@echo "Verifying package..."
	@pkgutil --check-signature "$(BUILD_DIR)/$(PKG_NAME)" || echo "(unsigned)"
	@echo ""
	@echo "Package contents:"
	@pkgutil --payload-files "$(BUILD_DIR)/$(PKG_NAME)" | head -20

# Create a DMG containing the pkg (optional)
dmg: build
	@echo "Creating DMG..."
	@mkdir -p $(BUILD_DIR)/dmg-contents
	@cp "$(BUILD_DIR)/$(PKG_NAME)" "$(BUILD_DIR)/dmg-contents/"
	@cp "$(PROJECT_ROOT)/scripts/uninstall.sh" "$(BUILD_DIR)/dmg-contents/Uninstall.command"
	@chmod +x "$(BUILD_DIR)/dmg-contents/Uninstall.command"
	@hdiutil create -volname "Laravel Installer $(VERSION)" \
		-srcfolder "$(BUILD_DIR)/dmg-contents" \
		-ov -format UDZO \
		"$(BUILD_DIR)/LaravelInstaller-$(VERSION).dmg"
	@rm -rf "$(BUILD_DIR)/dmg-contents"
	@echo "DMG created: $(BUILD_DIR)/LaravelInstaller-$(VERSION).dmg"
