import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import org.kde.kirigami as Kirigami
import passkeyd_enroll

Kirigami.ApplicationWindow {
  id: root

  width: Kirigami.Units.gridUnit * 20
  height: Kirigami.Units.gridUnit * 11

  // The order matters apparently
  maximumHeight: height
  maximumWidth: width

  minimumHeight: height
  minimumWidth: width

  flags: Qt.WindowStaysOnTopHint
  title: "Create Passkey"

  Bridge {
      id: bridge
      Component.onCompleted: load_data()
  }
  ColumnLayout {
    id: mainLayout
    anchors.fill: parent
    anchors.margins: Kirigami.Units.largeSpacing

    Kirigami.SelectableLabel {
      id: descriptionLbl
      Layout.fillWidth: true
      Layout.alignment: Qt.AlignHCenter
      Layout.maximumHeight: Kirigami.Units.gridUnit * 3
      wrapMode: Text.WrapAtWordBoundaryOrAnywhere
      text: bridge.domain + " wants to create a passkey for your user account " + bridge.username + "."
      font.bold: true
    }
    Rectangle {
      id: userCard
      implicitWidth: parent.width - Kirigami.Units.gridUnit * 3
      implicitHeight: cardLayout.height + Kirigami.Units.gridUnit * 1
      Layout.alignment: Qt.AlignHCenter
      radius: 12
      color: Kirigami.Theme.activeBackgroundColor
      border.color: Kirigami.Theme.focusColor
      border.width: 1
      RowLayout {
        anchors {
          left: parent.left
          verticalCenter: parent.verticalCenter
          leftMargin: Kirigami.Units.mediumSpacing
          topMargin: Kirigami.Units.mediumSpacing
        }
        id: cardLayout
        Kirigami.Icon {
          implicitHeight: Kirigami.Units.iconSizes.large
          implicitWidth: Kirigami.Units.iconSizes.large
          // TODO: use the actual website icon
          source: "github"
          fallback: "user-identity"
        }
        ColumnLayout {
          Label {
            id: websitenameLbl
            text: bridge.domain
          }
          Label {
            id: usernameLbl
            text: bridge.username
          }
        }
      }//RowLayout
    }
    DialogButtonBox {
      Layout.margins: -parent.anchors.margins
      Layout.alignment: Qt.AlignBottom
      standardButtons: DialogButtonBox.Ok | DialogButtonBox.Cancel
      onAccepted: {
        // TODO: Register passkey
        bridge.authorize()
        Qt.quit()
      }
      onRejected: {
        Qt.quit()
      }
      Layout.fillWidth: true
    }//DialogButtonBox
  }//ColumnLayout
}//Kirigami.ApplicationWindow
