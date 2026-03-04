all: build

.PHONY: build install

PASSKEYD_DIR = ${INSTALL_PREFIX}/usr/lib/passkeyd/passkeyd-enroll

build:
ifeq ($(UID), 0)
	$(error Won't build as root)
endif
	cargo build --release

install:
	install -d ${INSTALL_PREFIX}/usr/lib/passkeyd-qt/select/qml/
	install -m644 passkeyd-select/qml/Main.qml   ${INSTALL_PREFIX}/usr/lib/passkeyd-qt/select/qml/Main.qml
	install -m644 passkeyd-select/qml/qmldir     ${INSTALL_PREFIX}/usr/lib/passkeyd-qt/select/qml/qmldir
	install -m755 passkeyd-select/main.py        ${INSTALL_PREFIX}/usr/lib/passkeyd-qt/select/main.py


	install -d ${INSTALL_PREFIX}/usr/lib/passkeyd
	install -m755 target/release/passkeyd-enroll    ${INSTALL_PREFIX}/usr/lib/passkeyd/passkeyd-enroll-qt
	ln -sf ../../lib/passkeyd-qt/select/main.py   ${INSTALL_PREFIX}/usr/lib/passkeyd/passkeyd-select-qt
	install -m755 bin/passkeyd-presence  ${INSTALL_PREFIX}/usr/lib/passkeyd/passkeyd-presence-qt
