#!/bin/bash

sed -E 's|/var/lib/mysql/data|/mnt/ssd/mysql|g' settings.php
