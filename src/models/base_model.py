import json
import uuid

from dicttoxml import dicttoxml
from pydantic import BaseModel, ConfigDict


class BaseRequestModel(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
        # Позволяет использовать значения перечислений вместо их индексов. Пример: "type": "INTERNAL"
        populate_by_name=True,  # Позволяет использовать ключи, отличающиеся от Python-имён. Пример: "from_": "from"
        arbitrary_types_allowed=True  # Позволяет использовать любые типы данных
    )

    def serialize_payload(self) -> str:
        """
        Сериализует модель в JSON-строку, исключая поля с None.
        :return: JSON-строка.
        """
        return json.dumps(self.model_dump(exclude_none=True), ensure_ascii=False)

    def serialize_payload_by_alias(self) -> str:
        """
        Сериализует модель в JSON-строку, исключая поля с None.
        :return: JSON-строка.
        """
        return json.dumps(self.model_dump(exclude_none=True, by_alias=True), ensure_ascii=False,
                          default=self.custom_serializer)

    @staticmethod
    def custom_serializer(obj):
        """
        Кастомный сериализатор для объектов, которые не могут быть сериализованы стандартным json.dumps.
        """
        if isinstance(obj, uuid.UUID):
            return str(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def to_xml(self, root_tag: str = None) -> str:
        """
        Преобразует модель в XML-строку.
        :param root_tag: Название корневого элемента XML.
        :return: Строка в формате XML.
        """
        # Получаем словарь без полей с None
        data_dict = self.model_dump(exclude_none=True)

        # Конвертируем словарь в XML
        if root_tag:
            xml_bytes = dicttoxml(data_dict, custom_root=root_tag, attr_type=False)
        else:
            xml_bytes = dicttoxml(data_dict, attr_type=False)

        # Декодируем из bytes в строку
        return xml_bytes.decode("utf-8")

    def to_dict(self) -> dict:
        """
        Преобразует модель в словарь.
        :return: Словарь.
        """
        return self.model_dump(exclude_none=True)

    @classmethod
    def from_json(cls, json_str: str):
        """
        Создаёт экземпляр модели из JSON-строки.
        :param json_str: JSON-строка.
        :return: Экземпляр модели.
        """
        data = json.loads(json_str)
        return cls(**data)

    # Сериализовать в JSON строку массив с объектами
    @staticmethod
    def serialize_array_by_alias(data: list):
        """
        Сериализует массив объектов в JSON-строку.
        :param data: Массив объектов.
        :return: JSON-строка.
        """
        return json.dumps([item.model_dump(exclude_none=True, by_alias=True) for item in data], ensure_ascii=False)
