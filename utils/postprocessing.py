def replace_base_model(file_path):
    """Добавляет импорт BaseRequestModel и заменяет BaseModel на BaseRequestModel
    только в тех случаях, где BaseModel используется как базовый класс.

    @param file_path: Путь к файлу, в котором нужно произвести замену.
    """
    with open(file_path, encoding="utf-8") as file:
        content = file.read()

    lines = content.splitlines()
    new_lines = []
    for line in lines:
        modified_line = line
        if "class " in line and "BaseModel" in line:
            modified_line = line.replace("BaseModel", "BaseRequestModel")
        if "from pydantic import" in line and "BaseModel" in line:
            modified_line = line.replace(" BaseModel,", "")
            modified_line = modified_line + "\nfrom models.base_model import BaseRequestModel"
        new_lines.append(modified_line)

    content = "\n".join(new_lines)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def replace_regex(file_path):
    """Заменяет regex на pattern и удаляет unique_items.

    @param file_path: Путь к файлу, в котором нужно произвести замену.
    """
    with open(file_path, encoding="utf-8") as file:
        content = file.read()

    content = content.replace("regex", "pattern")
    content = content.replace(" unique_items=True, ", "")
    content = content.replace(" unique_items=True,", "")
    content = content.replace("unique_items=True ", "")
    content = content.replace("unique_items=True", "")
    content = content.replace("const=", "Literal=")
    content = content.replace("update_forward_refs", "model_rebuild")
    content = content.replace("    extra = Extra.forbid\n", "")
    content = content.replace("class Config:", 'model_config=ConfigDict(**BaseRequestModel.model_config, extra="forbid")')
    content = content.replace("UUID", "StrictStr")
    content = content.replace("from uuid import StrictStr", "")

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def replace_reserved_names(file_path):
    """Заменяет зарезервированные имена полей на альтернативные.

    @param file_path: Путь к файлу, в котором нужно произвести замену.
    """
    reserved_names_mapping = {"date": "date_", "__root__": "root_non_filled"}  # Заменяем "date" на "date_"

    with open(file_path, encoding="utf-8") as file:
        content = file.read()

    for old_name, new_name in reserved_names_mapping.items():
        content = content.replace(f"{old_name}: ", f"{new_name}: ")
        content = content.replace(f'"{old_name}": ', f'"{new_name}": ')

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
