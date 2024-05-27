import os
import re
from datetime import datetime


def sanitize_name(name):
    now = datetime.now()
    file_name, ext = os.path.splitext(name)
    file_name = f"{file_name}_{now.strftime('%Y-%m-%d')}"
    # Eliminar caracteres especiales y espacios del nombre de archivo
    file_name = re.sub(r"[^\w\s-]", "", file_name).strip().replace(" ", "_")
    # Unir el nombre del archivo saneado con la extensión original
    return f"{file_name}{ext}"
