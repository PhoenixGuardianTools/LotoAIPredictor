import uuid
import sys

# Récupérer la version passée en argument
version = sys.argv[1] if len(sys.argv) > 1 else "1.0.0"

upgrade_guid = str(uuid.uuid4())
component_guid = str(uuid.uuid4())
shortcut_guid = str(uuid.uuid4())

with open("wix/LotoAIPredictor_template.wxs", "r", encoding="utf-8") as f:
    template = f.read()

final_wxs = (
    template
    .replace("{VERSION}", version)
    .replace("{UPGRADE_GUID}", upgrade_guid)
    .replace("{COMPONENT_GUID}", component_guid)
    .replace("{SHORTCUT_GUID}", shortcut_guid)
)

with open("wix/LotoAIPredictor.wxs", "w", encoding="utf-8") as f:
    f.write(final_wxs)

print("✅ Fichier .wxs généré avec GUID et version :", version)
