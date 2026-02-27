use std::pin::Pin;
use std::io::Read;
use std::process::ExitCode;
use std::sync::atomic::AtomicBool;
use std::sync::Mutex;
use std::option::Option;

use ctap_types::serde::cbor_deserialize;
use ctap_types::webauthn::PublicKeyCredentialRpEntity;
use ctap_types::webauthn::PublicKeyCredentialUserEntity;

static IS_AUTHORIZED: AtomicBool = AtomicBool::new(false);
static PENDING: Mutex<Option<AuthorizationData>> = Mutex::new(None);

use serde::{Deserialize, Serialize};
#[derive(Serialize, Deserialize, Clone)]
pub struct OtherUI {
    pub user: PublicKeyCredentialUserEntity,
    pub site_icon: Option<bytes::Bytes>,
    pub user_icon: Option<bytes::Bytes>,
}
#[derive(Serialize, Deserialize, Clone)]
pub struct AuthorizationData {
    pub rp: PublicKeyCredentialRpEntity,
    pub other_ui: OtherUI,
}

use cxx_qt_lib::{QGuiApplication, QQmlApplicationEngine, QQuickStyle, QString, QUrl};
use cxx_qt_lib_extras::QApplication;
use std::env;

#[cxx_qt::bridge]
mod ffi {
  unsafe extern "C++" {
      include!("cxx-qt-lib/qstring.h");
      type QString = cxx_qt_lib::QString;
  }
  extern "RustQt" {
    #[qobject]
    #[qml_element]
    #[qproperty(QString, username)]
    #[qproperty(QString, domain)]
    #[qproperty(QString, icon)]
    type MyQObject = super::QRustStruct;

    #[qinvokable]
    fn authorize(self: Pin<&mut MyQObject>);

    #[qinvokable]
    fn load_data(self: Pin<&mut MyQObject>);
  }
}

#[derive(Default)]
pub struct QRustStruct {
  username: QString,
  domain: QString,
  icon: QString,
}

impl ffi::MyQObject {
  fn authorize(self: Pin<&mut Self>) {
    IS_AUTHORIZED.store(true, std::sync::atomic::Ordering::SeqCst);
  }
  fn load_data(mut self: Pin<&mut Self>) {
    if let Some(auth_data) = PENDING.lock().unwrap().take() {
      let username = if let Some(dname) = &auth_data.other_ui.user.display_name {
        dname.as_str()
      } else if let Some(name) = &auth_data.other_ui.user.name {
        name.as_str()
      } else if let Ok(id) = str::from_utf8(&auth_data.other_ui.user.id) {
        id
      } else {
        ""
      };
      let domain = auth_data.rp.id.as_str();
      let icon_str = if let Some(icon) = &auth_data.other_ui.user_icon {
          std::str::from_utf8(icon).unwrap_or("")
      } else {
          ""
      };
      self.as_mut().set_username(QString::from(username));
      self.as_mut().set_domain(QString::from(domain));
      self.as_mut().set_icon(QString::from(icon_str));
    }
  }
}

fn getinput() -> AuthorizationData {
    let mut state_buffer = Vec::with_capacity(size_of::<AuthorizationData>());
    std::io::stdin()
        .read_to_end(&mut state_buffer)
        .expect("Failed to read input");
    cbor_deserialize(&state_buffer).expect("Invalid cbor received")
}

fn main() -> ExitCode {

  let auth_data = getinput();
  *PENDING.lock().unwrap() = Some(auth_data);


  let mut app = QApplication::new();
  let mut engine = QQmlApplicationEngine::new();
  // To associate the executable to the installed desktop file
  QGuiApplication::set_desktop_file_name(&QString::from("passkeyd-select"));
  // To ensure the style is set correctly
  let style = env::var("QT_QUICK_CONTROLS_STYLE");
  if style.is_err() {
      QQuickStyle::set_style(&QString::from("org.kde.desktop"));
  }
  if let Some(engine) = engine.as_mut() {
      engine.load(&QUrl::from("qrc:/qt/qml/project/src/qml/Main.qml"));
  }
  if let Some(app) = app.as_mut() {
      app.exec();
  }
  let is_auth = IS_AUTHORIZED.load(std::sync::atomic::Ordering::SeqCst);
  if is_auth {
    return ExitCode::SUCCESS;
  } else {
    return ExitCode::FAILURE;
  }
}

#[cfg(test)]
mod tests {

    use std::{io::Write, process::Stdio};

    use ctap_types::serde::cbor_serialize;

    use super::*;

    #[test]
    fn test() {
        let mut bufferrrr = [0; 10000];
        let otherui = OtherUI {
            site_icon: None,
            user_icon: None,
            user: ctap_types::webauthn::PublicKeyCredentialUserEntity {
                id: ctap_types::Bytes::from_slice(&[1u8; 64]).expect(""),
                icon: None,
                name: Some("test".into()),
                display_name: Some("Damglador".into()),
            },
        };

        let values = AuthorizationData {
            other_ui: otherui,
            rp: PublicKeyCredentialRpEntity {
                id: "github.com".into(),
                name: Some("GitHub".into()),
                icon: None,
            },
        };
        let x = cbor_serialize(&values, &mut bufferrrr[..]).expect("");

        // debug!("spawning ui");
        let mut command = std::process::Command::new("systemd-run")
            .arg(format!("--machine={}@", 1000))
            .arg("--user")
            .arg("--collect")
            .arg("--wait")
            .arg("--quiet")
            .arg("--pipe")
            // .env("SYSTEMD_LOG_LEVEL", "debug")
            .arg(format!(
                "/home/damglador/kirigami-rust/target/debug/{}",
                "passkeyd-enroll"
            ))
            // .arg("/usr/lib/passkeyd/passkeyd-enroll")
            .stdin(Stdio::piped())
            .spawn()
            .expect("Failed to spawn UI, are you root?");

        {
            let mut stdin = command.stdin.take().expect("Failed to get stdin");
            stdin.write_all(&x).expect("Failed to write into pipe");
        }
        let result = command.wait().expect("failed to collect ui response");
        let g = result.code().unwrap_or(1);
        assert_eq!(g, 0)
    }
}
