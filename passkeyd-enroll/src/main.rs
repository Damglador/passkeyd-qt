use std::pin::Pin;
use std::io::Read;
use std::process::ExitCode;
use std::sync::atomic::AtomicBool;

use ctap_types::serde::cbor_deserialize;
use ctap_types::webauthn::PublicKeyCredentialRpEntity;

use serde::{Deserialize, Serialize};

static IS_AUTHORIZED: AtomicBool = AtomicBool::new(false);

#[derive(Serialize, Deserialize, Clone)]
pub struct AuthorizationData {
    pub rp: PublicKeyCredentialRpEntity
}

#[cxx_qt::bridge]
mod ffi {
  extern "RustQt" {
    #[qobject]
    #[qml_element]
    type MyQObject = super::QRustStruct;
    #[qinvokable]
    fn authorize(self: Pin<&mut MyQObject>);
  }
}

#[derive(Default)]
pub struct QRustStruct;

impl ffi::MyQObject {
  fn authorize(self: Pin<&mut Self>) {
    IS_AUTHORIZED.store(true, std::sync::atomic::Ordering::SeqCst);
    println!("clicked!");
  }
}

use cxx_qt_lib::{QGuiApplication, QQmlApplicationEngine, QQuickStyle, QString, QUrl};
use cxx_qt_lib_extras::QApplication;
use std::env;

fn getinput() -> AuthorizationData {
    let mut state_buffer = Vec::with_capacity(size_of::<AuthorizationData>());
    std::io::stdin()
        .read_to_end(&mut state_buffer)
        .expect("Failed to read input");
    cbor_deserialize(&state_buffer).expect("Invalid cbor received")
}

fn main() -> ExitCode {
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
