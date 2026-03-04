import os
import subprocess
import cbor2
from typing import Optional, List
from pydantic import BaseModel

from fido2.webauthn import PublicKeyCredentialUserEntity
from fido2.webauthn import PublicKeyCredentialRpEntity

class Entry(BaseModel):
    user: PublicKeyCredentialUserEntity
    site_icon: Optional[bytes] = None
    user_icon: Optional[bytes] = None

class SelectionData(BaseModel):
    rp: PublicKeyCredentialRpEntity
    other_uis: List[Entry]

def test():
    passkeys_list = []
    for idx in range(1):
        user_entity = PublicKeyCredentialUserEntity(
            id=bytes([1]*64),
            name="Github",
            display_name="Damglador",
        )
        passkeys_list.append(Entry(user=user_entity, site_icon=None, user_icon=None))

    authorization_ui = SelectionData(
        rp=PublicKeyCredentialRpEntity(id="github.com", name="Github"),
        other_uis=passkeys_list
    )

    serialized_data = cbor2.dumps(authorization_ui.model_dump())

    passkeyd_enroll_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "main.py")
    passkeyd_enroll_path = os.path.abspath(passkeyd_enroll_path)
    # print(passkeyd_enroll_path)

    cmd = [
        "systemd-run",
        f"--machine={1000}@",
        "--user",
        "--collect",
        "--wait",
        "--quiet",
        "--pipe",
        str(passkeyd_enroll_path)
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    proc.stdin.write(serialized_data) # pyright: ignore[reportOptionalMemberAccess]
    proc.stdin.close()                # pyright: ignore[reportOptionalMemberAccess]
    proc.wait()

if __name__ == "__main__":
    test()
