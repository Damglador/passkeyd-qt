#!/usr/bin/env python

import sys
import signal
import cbor2
from pydantic import BaseModel

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

class InputData(BaseModel):
  description: str
  title: str
  button: str

saved_index: int
saved_data: InputData

def getdata():
  state_buffer = sys.stdin.buffer.read()
  global saved_data
  saved_data = InputData(**cbor2.loads(state_buffer))

def main():
  app = QApplication(sys.argv)
  app.setWindowIcon(QIcon.fromTheme("passkeyd"))

  try:
    getdata()
  except Exception:
    print("Failed to read cbor")

  """Needed to close the app with Ctrl+C"""
  signal.signal(signal.SIGINT, signal.SIG_DFL)

  response = QMessageBox.question(
    None,
    saved_data.title,
    saved_data.description
  )
  if response == QMessageBox.StandardButton.Yes:
    exit(0)
  else:
    exit(1)

if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    exit(1)
  except Exception as err:
    print(err, file=sys.stderr)
