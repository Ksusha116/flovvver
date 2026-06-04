#!/bin/bash

check_root () {
	if [ $EUID -ne 0 ]; then
		echo "Скрипт должен быть запущен с правами Root-пользователя!"
		return 1
	else
		echo "Всё работает!"
	fi
}


check_root
