NAME       := Nikoru
VERSION    := 0.0.1
PYTHON     := python3

PREFIX     ?= /usr/local
BINDIR     := $(DESTDIR)$(PREFIX)/bin
SHARE_BASE := $(DESTDIR)$(PREFIX)/share/$(NAME)


MAIN_FILE  := Code/Niradock/Nikoru-DockPanel.py

DEPS = PySide6:PySide6 NLUtils:https://github.com/Niritech-Labs/Niritech-Labs-Utils/releases/download/v0.0.1/nlutils-0.0.1-py3-none-any.whl

	

WAYLAND_DIR := $(shell pkg-config --variable=pkgdatadir wayland-client)
WAYLAND_PROTOCOLS_DIR := $(shell pkg-config --variable=pkgdatadir wayland-protocols)

PY_MODULES := PySide6 

.PHONY: all check build install uninstall clean install-subfolder 

stub:
	@echo "Do not run $(MAKE) directly without any arguments."
	
all: 
	$(MAKE) build

check:
	@echo "--- Checking dependencies ---"

	@for dep in $(DEPS); do \
		module=$${dep%%:*}; \
		target=$${dep#*:}; \
		python3 -c "import $$module" 2>/dev/null || (echo "Installing $$target..."; pip install $$target); \
		done

build: check
	@echo "--- Build wayland protocols ---"
#$(PYTHON) -m pywayland.scanner -i $(WAYLAND_DIR)/wayland.xml src/code/Protocols/wlr-layer-shell-unstable-v1.xml $(WAYLAND_PROTOCOLS_DIR)/stable/xdg-shell/xdg-shell.xml -o src/code/Protocols/

install:
	@echo "--- Installing $(NAME) ---"
 
	@$(MAKE) install-subfolder SOURCE_DIR=src/code TARGET_DIR=$(SHARE_BASE)/Code
	@$(MAKE) install-subfolder SOURCE_DIR=src/other TARGET_DIR=$(SHARE_BASE)/Other
 
	@echo "--- Setting correct permissions ---"
	@find "$(SHARE_BASE)" -type d -exec chmod 755 {} +
 
	@find "$(SHARE_BASE)" -type f -exec chmod 644 {} +
 
	@chmod 755 "$(SHARE_BASE)/$(MAIN_FILE)"

	@echo "--- Creating binary link ---"
	@install -d "$(BINDIR)"
	@ln -sf "$(PREFIX)/share/$(NAME)/$(MAIN_FILE)" "$(BINDIR)/nikoru-dock"
 
	@echo "--- Byte-compiling ---"
	@$(PYTHON) -m compileall -q "$(SHARE_BASE)"
	@echo "[OK] Installation finished."

install-subfolder:
	@echo "Processing $(SOURCE_DIR) -> $(TARGET_DIR)"
	@install -d "$(TARGET_DIR)"
	@cd $(SOURCE_DIR) && cp -Pr . "$(TARGET_DIR)/"
	@find "$(TARGET_DIR)" -name "__pycache__" -type d -exec rm -rf {} +

uninstall:
	rm -rf "$(SHARE_BASE)"
	rm -f "$(BINDIR)/$(NAME)"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
