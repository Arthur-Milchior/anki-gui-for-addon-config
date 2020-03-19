from PyQt5 import Qt, QtCore, QtWidgets

from anki.lang import _
from aqt import gui_hooks, mw
from aqt.addons import AddonsDialog
from aqt.utils import restoreGeom, showInfo

from .addon_schema import _addonSchema, _schema_exists
from .schema_to_gui.qt_jsonschema_form.form import WidgetBuilder


def init(self):
    self.form.gui_config = QtWidgets.QPushButton(self)
    self.form.gui_config.setObjectName(_("Easy Config"))
    self.form.verticalLayout.addWidget(self.form.gui_config)
    self.form.gui_config.clicked.connect(self.on_gui)
    self.form.gui_config.setText(_("Easy Config"))


gui_hooks.addons_dialog_will_show.append(init)


def _onAddonItemSelected(self: AddonsDialog, addon):
    if not addon:
        return
    self.form.gui_config.setEnabled(_schema_exists(self.mgr, addon.dir_name))


gui_hooks.addons_dialog_did_change_selected_addon.append(_onAddonItemSelected)


def on_gui(self):
    addon = self.onlyOneSelected()
    if not addon:
        return

    # does add-on manage its own config?
    act = self.mgr.configAction(addon)
    if act:
        ret = act()
        if ret is not False:
            return

    schema = _addonSchema(mw.addonManager, addon)
    if schema is None:
        return
    conf = self.mgr.getConfig(addon)
    if conf is None:
        showInfo(_("Add-on has no configuration."))
        return

    builder = WidgetBuilder()
    form = builder.create_form(schema, palette=mw.palette())
    form.widget.state = conf

    restoreGeom(form, "gui_window")
    form.buttonBox = QtWidgets.QDialogButtonBox(form)
    form.buttonBox.setOrientation(QtCore.Qt.Horizontal)
    form.buttonBox.setStandardButtons(
        QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
    form.buttonBox.setObjectName("buttonBox")
    form.buttonBox.accepted.connect(form.accept)
    form.buttonBox.rejected.connect(form.reject)
    form.layout.addWidget(form.buttonBox)
    res = form.exec()
    if res == QtWidgets.QDialog.Accepted:
        self.mgr.writeConfig(addon, form.widget.state)


AddonsDialog.on_gui = on_gui
