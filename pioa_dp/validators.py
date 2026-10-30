from exceptions import ValidationError


def validate_record(schema: dict, record: dict) -> dict:
    if not isinstance(record, dict):
        raise ValidationError("Запись должна быть словарем 'поле': значение")

    result = {}
    for field, field_type in schema.items():
        if field not in record:
            raise ValidationError(f"Поле '{field}' обязательно")

        value = record[field]
        if type(value) is not field_type:
            raise ValidationError(
                f"Поле '{field}': ожидался тип {field_type.__name__}, "
                f"получен {type(value).__name__}"
            )
        result[field] = value
    return result

