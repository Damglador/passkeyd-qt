import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import org.kde.kirigami as Kirigami
import project

Kirigami.ApplicationWindow {
  id: root

  width: Kirigami.Units.gridUnit * 20
  height: Kirigami.Units.gridUnit * 10

  // The order matters apparently
  maximumHeight: height
  maximumWidth: width

  minimumHeight: height
  minimumWidth: width

  flags: Qt.WindowStaysOnTopHint
  title: "Create Passkey"

  MyQObject {
      id: myQObject
  }
  onBeforeRendering: {
    myQObject.load_data()
  }
  pageStack.initialPage: Kirigami.Page {
    id: mainPage
    width: parent.width
    height: parent.height
    globalToolBarStyle: Kirigami.ApplicationHeaderStyle.None
    ColumnLayout {
      Layout.margins: Kirigami.Units.largeSpacing
      width: parent.width
      height: parent.height
      Label {
        id: descriptionLbl
        Layout.maximumWidth: parent.width
        wrapMode: Text.WrapAtWordBoundaryOrAnywhere
        text: myQObject.domain + " wants to create a passkey for your user account " + myQObject.username
        font.bold: true
      }
      Rectangle {
        id: userCard
        Layout.fillWidth: true
        Layout.alignment: Qt.AlignHCenter
        implicitWidth:  cardLayout.width  + Kirigami.Units.gridUnit * 5
        implicitHeight: cardLayout.height + Kirigami.Units.gridUnit * 1
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
              text: myQObject.domain
            }
            Label {
              id: usernameLbl
              text: myQObject.username
            }
          }
        }//RowLayout
      }

      DialogButtonBox {
        standardButtons: DialogButtonBox.Ok | DialogButtonBox.Cancel
        onAccepted: {
          // TODO: Register passkey
          myQObject.authorize()
          Qt.quit()
        }
        onRejected: {
          Qt.quit()
        }
        Layout.fillWidth: true
      }//DialogButtonBox
    }//ColumnLayout
  }//Kirigami.Page
}//Kirigami.ApplicationWindow
