all:
	@echo "Run make install to install the program"

.PHONY: install

PASSKEYD_DIR = ${INSTALL_PREFIX}/usr/lib/passkeyd/
ENROLL_DIR   = ${INSTALL_PREFIX}/usr/lib/passkeyd-qt/enroll/
SELECT_DIR   = ${INSTALL_PREFIX}/usr/lib/passkeyd-qt/select/

install:
	install -d ${ENROLL_DIR}/qml/
	install -m644 passkeyd-select/qml/Main.qml   ${ENROLL_DIR}/qml/Main.qml
	install -m644 passkeyd-select/qml/qmldir     ${ENROLL_DIR}/qml/qmldir
	install -m755 passkeyd-select/main.py        ${ENROLL_DIR}/main.py

	install -d ${SELECT_DIR}/qml/
	install -m644 passkeyd-select/qml/Main.qml   ${SELECT_DIR}/qml/Main.qml
	install -m644 passkeyd-select/qml/qmldir     ${SELECT_DIR}/qml/qmldir
	install -m755 passkeyd-select/main.py        ${SELECT_DIR}/main.py

	install -d ${PASSKEYD_DIR}
	ln -sf ../../lib/passkeyd-qt/enroll/main.py   ${PASSKEYD_DIR}/passkeyd-enroll-qt
	ln -sf ../../lib/passkeyd-qt/select/main.py   ${PASSKEYD_DIR}/passkeyd-select-qt
	install -m755 bin/passkeyd-presence           ${PASSKEYD_DIR}/passkeyd-presence-qt
