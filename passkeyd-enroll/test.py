import os
import subprocess
import sys
from typing_extensions import Optional
import cbor2
from pydantic.main import BaseModel

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

def test():
  rp = PublicKeyCredentialRpEntity(
    id = "github.com",
    name = "GitHub"
  )
  user = PublicKeyCredentialUserEntity(
    id=bytes([1] * 64),
    name="test",
    display_name="Damglador"
  )
  entry = Entry(
    user=user,
    site_icon=None,
    user_icon=None,
  )
  data = InputData(
    rp=rp,
    other_ui=entry
  )

  serialized_data = cbor2.dumps(data.model_dump())
  passkeyd_enroll_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "main.py")
  passkeyd_enroll_path = os.path.abspath(passkeyd_enroll_path)
  cmd = [
      "systemd-run",
      "--machine=1000@",
      "--user",
      "--collect",
      "--wait",
      "--quiet",
      "--pipe",
      passkeyd_enroll_path,
  ]
  proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
  proc.stdin.write(serialized_data) # pyright: ignore[reportOptionalMemberAccess]
  proc.stdin.close()                # pyright: ignore[reportOptionalMemberAccess]
  proc.wait()

if __name__ == "__main__":
  try:
    test()
  except KeyboardInterrupt:
    exit(1)
  except Exception as err:
    print(err, file=sys.stderr)
