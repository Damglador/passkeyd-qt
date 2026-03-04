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

QML_IMPORT_NAME = "passkeyd_enroll"
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
  other_ui: Entry

saved_data:  InputData

@QmlElement
class Bridge(QObject):
  textChanged = Signal()
  def __init__(self):
    super().__init__()
    self._username  = "Err"
    self._website   = "Err"
    global saved_data
    if saved_data.other_ui.user.display_name != "":
      self._username = saved_data.other_ui.user.display_name
    elif saved_data.other_ui.user.name != "":
      self._username = saved_data.other_ui.user.name

    if saved_data.rp.name != "":
      self._website = saved_data.rp.name
    elif saved_data.rp.id != "":
      self._website = saved_data.rp.id

  @Property(str, notify=textChanged)
  def website(self):
    return self._website

  @Property(str, notify=textChanged)
  def username(self):
    return self._username

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
