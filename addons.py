from PyQt5 import Qt, QtCore, QtWidgets

from anki.lang import _
from aqt import mw
from aqt.addons import AddonsDialog
from aqt.utils import restoreGeom, showInfo

from .addon_schema import _addonSchema, _schema_exists
from .schema_to_gui.qt_jsonschema_form.form import WidgetBuilder

old_init = AddonsDialog.__init__


def __init__(self, *args, **kwargs):
    old_init(self, *args, **kwargs)
    self.form.gui_config = QtWidgets.QPushButton(self)
    self.form.gui_config.setObjectName(_("Easy Config"))
    self.form.verticalLayout.addWidget(self.form.gui_config)
    self.form.gui_config.clicked.connect(self.on_gui)
    self.form.gui_config.setText(_("Easy Config"))


AddonsDialog.__init__ = __init__

old_onAddonItemSelected = AddonsDialog._onAddonItemSelected


def _onAddonItemSelected(self: AddonsDialog, row_int):
    old_onAddonItemSelected(self, row_int)
    try:
        addon = self.addons[row_int]
    except IndexError:
        return
    if not addon:
        return
    self.form.gui_config.setEnabled(_schema_exists(self.mgr, addon.dir_name))


AddonsDialog._onAddonItemSelected = _onAddonItemSelected


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
