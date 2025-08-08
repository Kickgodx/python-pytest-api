from pathlib import Path


def replace_base_model(file_path: str | Path):
    """Добавляет импорт BaseRequestModel и заменяет BaseModel на BaseRequestModel
    только в тех случаях, где BaseModel используется как базовый класс.

    @param file_path: Путь к файлу, в котором нужно произвести замену.
    """
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")

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

    path.write_text(content, encoding="utf-8")


def replace_regex(file_path: str | Path):
    """Заменяет regex на pattern и удаляет unique_items.

    @param file_path: Путь к файлу, в котором нужно произвести замену.
    """
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")

    content = content.replace("regex", "pattern")
    content = content.replace(" unique_items=True, ", "")
    content = content.replace(" unique_items=True,", "")
    content = content.replace("unique_items=True ", "")
    content = content.replace("unique_items=True", "")
    content = content.replace("const=", "Literal=")
    content = content.replace("update_forward_refs", "model_rebuild")
    content = content.replace("    extra = Extra.forbid\n", "")
    content = content.replace(
        "class Config:", 'model_config=ConfigDict(**BaseRequestModel.model_config, extra="forbid")'
    )
    content = content.replace("UUID", "StrictStr")
    content = content.replace("from uuid import StrictStr", "")

    path.write_text(content, encoding="utf-8")


def replace_reserved_names(file_path: str | Path):
    """Заменяет зарезервированные имена полей на альтернативные.

    @param file_path: Путь к файлу, в котором нужно произвести замену.
    """
    path = Path(file_path)
    reserved_names_mapping = {
        "date": "date_",
        "__root__": "root_non_filled",
    }  # Заменяем "date" на "date_"

    content = path.read_text(encoding="utf-8")

    for old_name, new_name in reserved_names_mapping.items():
        content = content.replace(f"{old_name}: ", f"{new_name}: ")
        content = content.replace(f'"{old_name}": ', f'"{new_name}": ')

    path.write_text(content, encoding="utf-8")
