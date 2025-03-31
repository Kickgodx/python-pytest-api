def replace_base_model(file_path):
    """
    Добавляет импорт BaseRequestModel и заменяет BaseModel на BaseRequestModel
    только в тех случаях, где BaseModel используется как базовый класс.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    lines = content.splitlines()
    new_lines = []
    for line in lines:
        if "class " in line and "BaseModel" in line:
            line = line.replace("BaseModel", "BaseRequestModel")
        if "from pydantic import" in line and "BaseModel" in line:
            line = line.replace(" BaseModel,", "")
            line = line + "\nfrom models.base_model import BaseRequestModel"
        new_lines.append(line)

    content = "\n".join(new_lines)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def replace_regex(file_path):
    """
    Заменяет regex на pattern и удаляет unique_items.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    content = content.replace("regex", "pattern")
    content = content.replace(" unique_items=True, ", "")
    content = content.replace(" unique_items=True,", "")
    content = content.replace("unique_items=True ", "")
    content = content.replace("unique_items=True", "")
    content = content.replace("const=", "Literal=")
    content = content.replace("update_forward_refs", "model_rebuild")
    content = content.replace("    extra = Extra.forbid\n", "")
    content = content.replace("class Config:",
                              'model_config=ConfigDict(**BaseRequestModel.model_config, extra="forbid")')
    content = content.replace("UUID", "StrictStr")
    content = content.replace("from uuid import StrictStr", "")

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def replace_reserved_names(file_path):
    """
    Заменяет зарезервированные имена полей на альтернативные.
    """
    reserved_names_mapping = {
        "date": "date_",  # Заменяем "date" на "date_"
        "__root__": "root_non_filled"
    }

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    for old_name, new_name in reserved_names_mapping.items():
        content = content.replace(f"{old_name}: ", f"{new_name}: ")
        content = content.replace(f'"{old_name}": ', f'"{new_name}": ')

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
