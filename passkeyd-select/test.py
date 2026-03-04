import os
import subprocess
import cbor2
from dataclasses import dataclass
from typing import Optional, List

from fido2.webauthn import PublicKeyCredentialUserEntity
from fido2.webauthn import PublicKeyCredentialRpEntity

@dataclass
class Passkey:
    user: PublicKeyCredentialUserEntity
    site_icon: Optional[bytes] = None
    user_icon: Optional[bytes] = None

@dataclass
class SelectionData:
    rp: PublicKeyCredentialRpEntity
    passkeys: List[Passkey]

def test_passkey_selection_process():
    passkeys_list = []
    for idx in range(1):
        user_entity = PublicKeyCredentialUserEntity(
            id=bytes([1]*64),
            name="Github",
            display_name="Damglador",
        )
        passkeys_list.append(Passkey(user=user_entity, site_icon=None, user_icon=None))

    authorization_ui = SelectionData(
        rp=PublicKeyCredentialRpEntity(id="github.com", name="Github"),
        passkeys=passkeys_list
    )

    serialized_data = cbor2.dumps({
        "rp": {
            "id": authorization_ui.rp.id,
            "name": authorization_ui.rp.name,
            # "icon": authorization_ui.rp.icon
        },
        "other_uis": [
            {
                "user": {
                    "id": o.user.id,
                    "name": o.user.name,
                    "display_name": o.user.display_name
                },
                "site_icon": o.site_icon,
            } for o in authorization_ui.passkeys
        ]
    })

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
    proc.stdin.write(serialized_data)
    proc.stdin.close()
    exit_code = proc.wait()


if __name__ == "__main__":
    test_passkey_selection_process()
