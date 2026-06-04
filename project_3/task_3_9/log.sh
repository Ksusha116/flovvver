#!/bin/bash

FILE_PATH="./system.log"
ERROR_CODE=1


if [ -f "$FILE_PATH" ]; then
    echo "Лог-файл найден."
else
    echo "Ошибка: файл не существует."
fi

case $ERROR_CODE in
    0)
        echo "Статус: Ошибок нет." ;;
    1)
        echo "Статус: Критическая ошибка!" ;;
    *)
        echo "Статус: Неизвестный код." ;;
esac
