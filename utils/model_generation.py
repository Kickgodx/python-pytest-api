import os
import subprocess
from pathlib import Path

from postprocessing import replace_regex, replace_reserved_names
from utils_for_gen import convert_to_utf8, get_description_from_yaml, add_description_to_file

# Пути к папкам
SPECS_DIR = "./src/resources/"  # Папка с файлами схем
MODELS_DIR = "./src/models"  # Папка для сохранения сгенерированных моделей

# Команда для datamodel-codegen
GENERATOR_CMD = (
    "datamodel-codegen "
    "--input {input_file} "
    "--output {output_file} "
    "--input-file-type {input_file_type} "
    "--additional-imports src.func.models.BaseRequestModel,pydantic.ConfigDict "
    "--base-class src.func.models.BaseRequestModel "
    "--field-constraints "
    "--use-standard-collections "
    "--use-union-operator "
    "--snake-case-field "
    # "--use-field-description "
    "--use-schema-description "
    # "--output-model-type pydantic_v2.BaseModel "
    "--enable-version-header "
    "--reuse-model "
    "--use-double-quotes "
    "--capitalise-enum-members "
    "--strict-types str bytes int float bool "
    "--target-python-version 3.12 "
    "--use-unique-items-as-set "
    # "--custom-template-dir custom_templates "
    "--encoding utf-8"  # Указываем кодировку вывода
)


def generate_models():
    # Создаем папку models, если она не существует
    Path(MODELS_DIR).mkdir(parents=True, exist_ok=True)

    # Рекурсивно обходим папку specs
    for root, dirs, files in os.walk(SPECS_DIR):
        for file in files:
            if "OpenAPI.yml" in file:
                # Полный путь к файлу схемы
                input_file = os.path.join(root, file)

                # Конвертируем входной файл в utf-8
                convert_to_utf8(input_file)

                # Извлекаем название микросервиса из имени файла
                service_name = file.replace("OpenAPI.yml", "").strip()

                # Создаем корректное имя для выходного файла
                output_filename = f"{service_name}.py"
                output_file = os.path.join(MODELS_DIR, output_filename)

                # Формируем команду для datamodel-codegen
                cmd = GENERATOR_CMD.format(
                    input_file=input_file,
                    output_file=output_file,
                    input_file_type="openapi",
                )

                print(f"Генерация моделей для {input_file} -> {output_file}")
                try:
                    subprocess.run(cmd, shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Ошибка при генерации {output_filename}\n:{e}")
                    continue  # Пропускаем обработку этого файла при ошибке

                try:
                    description = get_description_from_yaml(input_file)
                    add_description_to_file(output_file, description, service_name)
                except Exception as e:
                    print(f"Ошибка при добавлении описания в файл {output_filename}\n:{e}")

                try:
                    replace_reserved_names(output_file)
                except Exception as e:
                    print(f"Ошибка при замене зарезервированных имен в файле {output_filename}\n:{e}")

                try:
                    replace_regex(output_file)
                except Exception as e:
                    print(f"Ошибка при постобработке файла модели {output_filename}\n:{e}")


if __name__ == "__main__":
    generate_models()
