#!/usr/bin/env python

import os
import sys
import signal
import cbor2
import pam
import getpass

from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtCore import QAbstractListModel, QByteArray, QLoggingCategory, QObject, Slot
from PySide6.QtQml import QQmlApplicationEngine, QmlElement

QML_IMPORT_NAME = "io.qt.textproperties"
QML_IMPORT_MAJOR_VERSION = 1
os.environ["QT_LOGGING_RULES"] = "qml=false"

saved_index: int
saved_data:  dict
QAbstractListModel.data
class ItemModel(QAbstractListModel):
  UserRole = 0x0100 + 1
  # DomainRole = 0x0100 + 2
  # IconRole = 0x0100 + 3

  def __init__(self, items):
    super().__init__()
    self._items = items or []

  def rowCount(self, parent): # pyright: ignore[ reportIncompatibleMethodOverride]
    return len(self._items)

  def data(self, index, role): # pyright: ignore[ reportIncompatibleMethodOverride]
    if not index.isValid():
      return ""

    item = self._items[index.row()]
    user = item["user"]

    if role == self.UserRole:
      return user["name"] or ""
    return ""

  def roleNames(self) -> dict[int, QByteArray]:
    return {
      self.UserRole: QByteArray(b"user"),
    }

  def setUsers(self, users):
    self.beginResetModel()
    self._users = users
    self.endResetModel()

@QmlElement
class Bridge(QObject):
  def __init__(self):
    super().__init__()
    try:
      self._websiteName = saved_data["rp"]["name"]
    except Exception:
      self._websiteName = ""
    try:
      self._websiteDomain = saved_data["rp"]["id"]
    except Exception:
      self._websiteDomain = ""

  @Slot(result=str)
  def getLabel(self):
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
      write_output(bytearray(password, "utf-8"))
      return True
    else:
      return False

  @Slot(int, result=str)
  def saveIndex(self, index: int):
    global saved_index
    saved_index = index


def write_output(password: bytearray):
  stdout = sys.stdout.buffer

  stdout.write(b'\x02')
  stdout.write(saved_index.to_bytes(8, 'little'))
  stdout.write(password)
  stdout.write(b'\x03')
  stdout.flush()

  for i in range(len(password)):
    password[i] = 0
  QGuiApplication.exit(0)

def getdata():
  state_buffer = sys.stdin.buffer.read()
  data = cbor2.loads(state_buffer)

  # import json
  # print(json.dumps(data, indent=2, default=lambda x: x.hex() if isinstance(x, bytes) else x), file=sys.stderr)

  global saved_data
  saved_data = data


def main():
  app = QGuiApplication(sys.argv)
  app.setWindowIcon(QIcon.fromTheme("passkeyd"))

  QLoggingCategory.setFilterRules("*.debug=false\n"
                                  "*.info=false\n"
                                  "*.warning=false\n"
                                  "*.critical=true")

  engine = QQmlApplicationEngine()

  getdata()

  model = ItemModel(saved_data["other_uis"])
  engine.rootContext().setContextProperty("itemModel", model)

  """Needed to close the app with Ctrl+C"""
  signal.signal(signal.SIGINT, signal.SIG_DFL)

  """Needed to get proper KDE style outside of Plasma"""
  if not os.environ.get("QT_QUICK_CONTROLS_STYLE"):
        os.environ["QT_QUICK_CONTROLS_STYLE"] = "org.kde.desktop"

  scriptdir = os.path.dirname(os.path.realpath(__file__))
  engine.addImportPath(scriptdir)
  engine.loadFromModule("qml", "Main")

  app.exec()

if __name__ == "__main__":
  main()
