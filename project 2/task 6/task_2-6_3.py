dphenotype = input("Введите фенотип группы крови донора (I, II, III, IV): ").strip().upper()
pphenotype = input("Введите фенотип группы крови пациента (I, II, III, IV): ").strip().upper()
if pphenotype == dphenotype or pphenotype == "I":
    print("всё чётко, можно переливать")
else:
    print("неее, это никуда не пойдёт")