all: build

.PHONY: build install

PASSKEYD_DIR = ${INSTALL_PREFIX}/usr/lib/passkeyd/passkeyd-enroll

build:
ifeq ($(UID), 0)
	$(error Won't build as root)
endif
	cargo build --release

install:
	install -Dm755 bin/passkeyd-enroll    ${INSTALL_PREFIX}/usr/lib/passkeyd/passkeyd-enroll-qt
	@echo "passkeyd-select installation is not implemented yet"
	# install -Dm755 bin/passkeyd-select    ${INSTALL_PREFIX}/usr/lib/passkeyd/passkeyd-select-qt
	install -Dm755 bin/passkeyd-presence  ${INSTALL_PREFIX}/usr/lib/passkeyd/passkeyd-presence-qt
