pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import org.kde.kirigami as Kirigami

import io.qt.textproperties 1.0

Kirigami.ApplicationWindow {
  id: root

  width: Kirigami.Units.gridUnit * 26
  height: Kirigami.Units.gridUnit * 8

  // The order matters apparently
  maximumHeight: height
  maximumWidth: width

  minimumHeight: height
  minimumWidth: width

  flags: Qt.WindowStaysOnTopHint
  title: "Passkey Login"

  pageStack.initialPage: selectionPage

  Bridge {
     id: bridge
  }

  Component {
    id: selectionPage
    Kirigami.Page {
      title: bridge.getLabel()
      ColumnLayout {
        id: layout
        anchors.fill: parent
        ScrollView {
          id: optionsView
          implicitWidth: parent.width
          Layout.maximumHeight: Kirigami.Units.gridUnit * 10

          ScrollBar.vertical: ScrollBar {
            id: scrollBar
            policy: ScrollBar.AlwaysOn
            height: parent.height
            anchors.right: parent.right
          }

          ListView {
            id: optionsList

            property int selectedIndex

            clip: true
            anchors.fill: parent

            model: itemModel

            delegate: ItemDelegate {
              id: item
              required property int index
              required property string user
              // required property string domain
              // required property string website_icon

              width: ListView.view.width - scrollBar.width
              height: Kirigami.Units.gridUnit * 2.5

              RowLayout {

                Kirigami.Icon {
                  source: "user-identity" // item.website_icon
                  fallback: "user-identity"
                  Layout.preferredWidth: Kirigami.Units.iconSizes.large
                  Layout.preferredHeight: Kirigami.Units.iconSizes.large
                }

                RowLayout {
                  spacing: Kirigami.Units.smallSpacing

                  Label {
                    text: item.user
                  }
                  // Label {
                  //   text: "at"
                  // }
                  // Label {
                  //   text: item.domain
                  // }
                }//RowLayout
              }//RowLayout
              onClicked: {
                parent.currentIndex = index
                bridge.saveIndex(parent.currentIndex)
                root.pageStack.push(authorizePage)
              }
              Keys.onReturnPressed: clicked()
            }//ItemDelegate

            Component.onCompleted: {
              forceActiveFocus()
              if (count == 1) {
                Qt.callLater(() => {
                  if (currentItem)
                    currentItem.clicked()   // або твій метод активації
                })
              }
            }//Component.onCompleted
          }//ListView

        }//Scrollview
      }//ColumnLayout
      onActiveFocusChanged: {
        if (activeFocus) {
          root.height = Kirigami.Units.gridUnit * 5 +
            optionsView.height
        }
      }
    }//Kirigami.Page
  }//Component


  Component {
    id: authorizePage
    Kirigami.Page {
      onActiveFocusChanged: {
        if (activeFocus) {
          root.height = Kirigami.Units.gridUnit * 10
          passwordField.forceActiveFocus()
        }
      }
      title: "Making sure it's you"
      ColumnLayout {
        anchors.centerIn: parent
        RowLayout {
          id: mainRow
          Kirigami.Icon {
            id: icon
            source: "user-identity"
            implicitWidth: Kirigami.Units.iconSizes.huge
            implicitHeight: Kirigami.Units.iconSizes.huge
          }
          ColumnLayout {
            Label {
              wrapMode: Text.WordWrap
              text: "Enter your password to authorize this passkey request:"
              font.bold: true
            }
            Kirigami.PasswordField {
              id: passwordField
              Layout.fillWidth: true
              onAccepted: {
                let result = bridge.authorize(passwordField.text)
                if (!result) {
                  errorMessage.visible = true
                }
              }
            }
          }//ColumnLayout
        }//RowLayout
        Kirigami.InlineMessage {
          id: errorMessage
          Behavior on implicitHeight {
            enabled: false
          }

          visible: false
          type: Kirigami.MessageType.Error
          text: "Invalid password. Try again."
          showCloseButton: true
          Layout.fillWidth: true
          onVisibleChanged: {
            if (visible) {
              root.height += Kirigami.Units.gridUnit * 2
            } else {
              root.height -= Kirigami.Units.gridUnit * 2
            }
          }
        }//Kirigami.InlineMessage
        DialogButtonBox {
          standardButtons: DialogButtonBox.Ok | DialogButtonBox.Cancel
          onAccepted: {
            let result = bridge.authorize(passwordField.text)
            if (!result) {
              errorMessage.visible = true
            }
          }
          onRejected: {
            Qt.quit()
          }
          Layout.fillWidth: true
        }//DialogButtonBox
      }//ColumnLayout
    }//Kirigami.Page
  }//Component
}
