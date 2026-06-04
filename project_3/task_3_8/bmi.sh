read -p 'Введите массу тела, кг: ' WEIGHT
read -p 'Введите рост, м: ' HEIGHT

BMI=$(echo "scale=0; $WEIGHT / ($HEIGHT * $HEIGHT)" | bc)

echo "ИМТ: $BMI"
