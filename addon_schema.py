import os.path
from aqt.addons import AddonManager
import json

def _schema_exists(self: AddonManager, dir):
    return os.path.exists(_addonSchemaPath(self, dir))        

# in 2.1.21
def _addonSchemaPath(self: AddonManager, dir):
    return os.path.join(self.addonsFolder(dir), "config.schema.json")

# in 2.1.21
def _addonSchema(self: AddonManager, dir):
    path = _addonSchemaPath(self, dir)
    try:
        if not os.path.exists(path):
            # True is a schema accepting everything
            return True
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.decoder.JSONDecodeError as e:
        print("The schema is not valid:")
        print(e)

