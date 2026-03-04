use cxx_qt_build::{CxxQtBuilder, QmlModule};

fn main() {
  CxxQtBuilder::new_qml_module(QmlModule::new("passkeyd_enroll").qml_files(["src/qml/Main.qml"]))
    .files(["src/main.rs"])
    .build();
}
