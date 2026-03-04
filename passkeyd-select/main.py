#!/usr/bin/env python

from typing import Optional
from pydantic import BaseModel
import os
import sys
import signal
import cbor2
import pam
import getpass

from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtCore import Property, QAbstractListModel, QByteArray, QLoggingCategory, QObject, Signal, Slot
from PySide6.QtQml import QQmlApplicationEngine, QmlElement

QML_IMPORT_NAME = "passkeyd_select"
QML_IMPORT_MAJOR_VERSION = 1

class PublicKeyCredentialRpEntity(BaseModel):
  id: str | None = None
  name: str | None = None

class PublicKeyCredentialUserEntity(BaseModel):
  id: bytes
  name: str | None = None
  display_name: str | None = None

class Entry(BaseModel):
  user: PublicKeyCredentialUserEntity
  site_icon: Optional[bytes] = None
  user_icon: Optional[bytes] = None

class InputData(BaseModel):
  rp: PublicKeyCredentialRpEntity
  other_uis: list[Entry]

class SelectionResponse(BaseModel):
  index: int
  passphrase: str

saved_index: int
saved_data:  InputData

class ItemModel(QAbstractListModel):
  UserRole = 0x0100 + 1
  # DomainRole = 0x0100 + 2
  # IconRole = 0x0100 + 3

  def __init__(self, items):
    super().__init__()
    self._items = items or []

  def rowCount(self, parent): # pyright: ignore[reportIncompatibleMethodOverride]
    return len(self._items)

  def data(self, index, role): # pyright: ignore[reportIncompatibleMethodOverride]
    if not index.isValid():
      return ""

    user = self._items[index.row()].user

    if role == self.UserRole:
      return user.name or ""
    return ""

  def roleNames(self) -> dict[int, QByteArray]:
    return {
      self.UserRole: QByteArray(b"user"),
    }

@QmlElement
class Bridge(QObject):
  labelTextChanged = Signal()

  def __init__(self):
    super().__init__()
    global saved_data
    self._websiteName   = ""
    self._websiteDomain = ""

  @Property(str, notify=labelTextChanged)
  def labelText(self):
    if self._websiteName != "" and self._websiteDomain != "":
      return f"Select passkey for {self._websiteName} ({self._websiteDomain})"
    elif self._websiteName == "":
      return f"Select passkey for {self._websiteDomain}"
    elif self._websiteDomain == "":
      return f"Select passkey for {self._websiteDomain}"
    else:
      return "Select passkey"

  @Slot(str, result=bool)
  def authorize(self, password: str):
    if pam.authenticate(getpass.getuser(), password):
      write_output(password)
      return True
    else:
      return False

  @Slot(int, result=str)
  def saveIndex(self, index: int):
    global saved_index
    saved_index = index

  @Slot()
  def load_data(self):
    self._websiteName   = saved_data.rp.name if saved_data.rp.name else ""
    self._websiteDomain = saved_data.rp.id   if saved_data.rp.id   else ""
    self.labelTextChanged.emit()

def write_output(password: str):
  stdout = sys.stdout.buffer
  stdout.write(b'\x02')
  global saved_index
  report = cbor2.dumps(
    SelectionResponse(
      index=saved_index,
      passphrase=password
    ).model_dump())
  stdout.write(report)
  stdout.flush()

  password = ""
  QGuiApplication.exit(0)

def getdata():
  state_buffer = sys.stdin.buffer.read()

  # import json
  # print(json.dumps(cbor2.loads(state_buffer), indent=2, default=lambda x: x.hex() if isinstance(x, bytes) else x), file=sys.stderr)

  global saved_data
  saved_data = InputData(**cbor2.loads(state_buffer))

def main():
  app = QGuiApplication(sys.argv)
  app.setWindowIcon(QIcon.fromTheme("passkeyd"))

  QLoggingCategory.setFilterRules("*.debug=false\n"
                                  "*.info=false\n"
                                  "*.warning=false\n"
                                  "*.critical=true")

  engine = QQmlApplicationEngine()

  getdata()

  model = ItemModel(saved_data.other_uis)
  engine.rootContext().setContextProperty("itemModel", model)

  """Needed to close the app with Ctrl+C"""
  signal.signal(signal.SIGINT, signal.SIG_DFL)

  """Needed to get proper KDE style outside of Plasma"""
  if not os.environ.get("QT_QUICK_CONTROLS_STYLE"):
        os.environ["QT_QUICK_CONTROLS_STYLE"] = "org.kde.desktop"

  scriptdir = os.path.dirname(os.path.realpath(__file__))
  engine.addImportPath(scriptdir)
  engine.loadFromModule("qml", "Main")

  sys.exit(app.exec())

if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    exit(1)
  except Exception as err:
    print(err, file=sys.stderr)
