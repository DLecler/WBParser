
# "prod=9835&xsubject=764&param=faction",
# "prod=9835&xsubject=764&param=fnds",
# "prod=9835&xsubject=764&param=frating",
# "prod=9835&xsubject=764&param=foriginal",
# "prod=9835&xsubject=764&param=fpremium",
# "prod=9835&xsubject=764&param=ffeedbackpoints",
# "prod=9835&xsubject=764&param=fpremiumuser",
# "prod=9835&xsubject=764&param=fdlvr&value=2-4 часа",
# "prod=9835&xsubject=764&param=fdlvr&value=завтра",
# "prod=9835&xsubject=1889&param=faction",
# "prod=9835&xsubject=1889&param=fnds",
# "prod=9835&xsubject=1889&param=fdlvr&value=завтра",
# "prod=9835&xsubject=1889&param=fdlvr&value=до 5 дней",
# "prod=9835&xsubject=1889&param=frating",
# "prod=9835&xsubject=1889&param=foriginal",
# "prod=9835&xsubject=1889&param=fpremium",
# "prod=9835&xsubject=1889&param=ffeedbackpoints",
# "prod=9835&xsubject=1889&param=fpremiumuser",
# "prod=9835&xsubject=1889&param=f11461&value=22528",
# "prod=9835&xsubject=1889&param=f11461&value=22533",
# "prod=9835&xsubject=1889&param=f14081&value=643600725",
# "prod=9835&xsubject=1889&param=f14081&value=102252956",
# "prod=9835&xsubject=1889&param=f15002656&value=-29856",
# "prod=9835&xsubject=1889&param=f15002656&value=-29855",
# "prod=9835&xsubject=1889&param=f746&value=9564676",
# "prod=9835&xsubject=1889&param=f746&value=10326",
# "prod=9835&xsubject=1889&param=f355315&value=371772",
# "prod=9835&xsubject=1889&param=f355315&value=371771",
# "prod=9835&xsubject=1889&param=f5023&value=214366",
# "prod=9835&xsubject=1889&param=f5023&value=85146",
# "prod=9835&param=fbrand&value=194905231",
# "prod=9835&param=fbrand&value=311378557",
# "prod=9835&param=fsupplier&value=3942301",
# "prod=9835&param=fsupplier&value=206677",
# "prod=9835&xsubject=764&priceU=100%3B200",
# "prod=9835&xsubject=1889&priceU=500%3B600"




# 2) удаляем "param=" и "&value", удаляем строки с "fdlvr=Любой" + замена:
# "fdlvr=2-4 часа" на "fdlvr=4"
# "fdlvr=Сегодня" на "fdlvr=12"
# "fdlvr=Завтра" на "fdlvr=24"
# "fdlvr=Послезавтра" на "fdlvr=48"
# "fdlvr=До 3 дней" на "fdlvr=72"
# "fdlvr=До 5 дней" на "fdlvr=120"

# "prod=9835&xsubject=764&faction",
# "prod=9835&xsubject=764&fnds",
# "prod=9835&xsubject=764&frating",
# "prod=9835&xsubject=764&foriginal",
# "prod=9835&xsubject=764&fpremium",
# "prod=9835&xsubject=764&ffeedbackpoints",
# "prod=9835&xsubject=764&fpremiumuser",
# "prod=9835&xsubject=764&fdlvr=4",
# "prod=9835&xsubject=764&fdlvr=24",
# "prod=9835&xsubject=1889&faction",
# "prod=9835&xsubject=1889&fnds",
# "prod=9835&xsubject=1889&fdlvr=24",
# "prod=9835&xsubject=1889&fdlvr=120",
# "prod=9835&xsubject=1889&frating",
# "prod=9835&xsubject=1889&foriginal",
# "prod=9835&xsubject=1889&fpremium",
# "prod=9835&xsubject=1889&ffeedbackpoints",
# "prod=9835&xsubject=1889&fpremiumuser",
# "prod=9835&xsubject=1889&f11461=22528",
# "prod=9835&xsubject=1889&f11461=22533",
# "prod=9835&xsubject=1889&f14081=643600725",
# "prod=9835&xsubject=1889&f14081=102252956",
# "prod=9835&xsubject=1889&f15002656=-29856",
# "prod=9835&xsubject=1889&f15002656=-29855",
# "prod=9835&xsubject=1889&f746=9564676",
# "prod=9835&xsubject=1889&f746=10326",
# "prod=9835&xsubject=1889&f355315=371772",
# "prod=9835&xsubject=1889&f355315=371771",
# "prod=9835&xsubject=1889&f5023=214366",
# "prod=9835&xsubject=1889&f5023=85146",
# "prod=9835&fbrand=194905231",
# "prod=9835&fbrand=311378557",
# "prod=9835&fsupplier=3942301",
# "prod=9835&fsupplier=206677",
# "prod=9835&xsubject=764&priceU=100%3B200",
# "prod=9835&xsubject=1889&priceU=500%3B600"


    # 3) рядом с параметрами faction, fnds, frating, foriginal, fpremium, ffeedbackpoints, fpremiumuser добавляем "=1"
    # объединяем значения равных параметров строк, содержащих одинаковые значения prod и xsubject (кроме строк с параметрами fdlvr) (между значениями параметров СТРОГО ставится "%3B")
    # в случае, если строка содержит только prod и любой параметр кроме fdlvr - объединяем строки с одинаковыми значениями параметра prod и названием параметра -
    # пример таких строк: "prod=9835&fbrand=194905231" и "prod=9835&fbrand=311378557"

# "prod=9835&xsubject=764&fdlvr=4",
# "prod=9835&xsubject=764&fdlvr=24",
# "prod=9835&xsubject=764&faction=1",
# "prod=9835&xsubject=764&fnds=1",
# "prod=9835&xsubject=764&frating=1",
# "prod=9835&xsubject=764&foriginal=1",
# "prod=9835&xsubject=764&fpremium=1",
# "prod=9835&xsubject=764&ffeedbackpoints=1",
# "prod=9835&xsubject=764&fpremiumuser=1",
# "prod=9835&xsubject=1889&fdlvr=24",
# "prod=9835&xsubject=1889&fdlvr=120",
# "prod=9835&xsubject=1889&faction=1",
# "prod=9835&xsubject=1889&fnds=1",
# "prod=9835&xsubject=1889&frating=1",
# "prod=9835&xsubject=1889&foriginal=1",
# "prod=9835&xsubject=1889&fpremium=1",
# "prod=9835&xsubject=1889&ffeedbackpoints=1",
# "prod=9835&xsubject=1889&fpremiumuser=1",
# "prod=9835&xsubject=1889&f11461=22528%3B22533",
# "prod=9835&xsubject=1889&f14081=643600725%3B102252956",
# "prod=9835&xsubject=1889&f15002656=-29856%3B-29855",
# "prod=9835&xsubject=1889&f746=9564676%3B10326",
# "prod=9835&xsubject=1889&f355315=371772%3B371771",
# "prod=9835&xsubject=1889&f5023=214366%3B85146",
# "prod=9835&fbrand=194905231%3B311378557",
# "prod=9835&fsupplier=3942301%3B206677",
# "prod=9835&xsubject=764&priceU=100%3B200",
# "prod=9835&xsubject=1889&priceU=500%3B600"






# 4) объединяем параметры строк, содержащих одинаковые значения prod и xsubject (кроме строк с параметрами fdlvr) (между значениями параметров ставим "&")
# строки с параметрами fbrand и fsupplier с одинаковыми значениями prod объединяем вместе
# если в строке нет параметра xsubject, то по равным значениям prod

# "prod=9835&xsubject=764&fdlvr=4",
# "prod=9835&xsubject=764&fdlvr=24",
# "prod=9835&xsubject=764&faction=1&fnds=1&frating=1&foriginal=1&fpremium=1&ffeedbackpoints=1&fpremiumuser=1&priceU=100%3B200",
# "prod=9835&xsubject=1889&fdlvr=24",
# "prod=9835&xsubject=1889&fdlvr=120",
# "prod=9835&xsubject=1889&faction=1&fnds=1&frating=1&foriginal=1&fpremium=1&ffeedbackpoints=1&fpremiumuser=1&f11461=22528%3B22533&f14081=643600725%3B102252956&f15002656=-29856%3B-29855&f746=9564676%3B10326&f355315=371772%3B371771&f5023=214366%3B85146&priceU=500%3B600",
# "prod=9835&fbrand=194905231%3B311378557&fsupplier=3942301%3B206677"

# 5) добавляем строки содержащие и/или параметры fbrand и fsupplier к каждой строке с соответствующими значениями параметра prod (не содержащей параметр fdlvr):
# "prod=9835&xsubject=764&fdlvr=4",
# "prod=9835&xsubject=764&fdlvr=24",
# "prod=9835&xsubject=764&faction=1&fnds=1&frating=1&foriginal=1&fpremium=1&ffeedbackpoints=1&fpremiumuser=1&priceU=100%3B200&fbrand=194905231%3B311378557&fsupplier=3942301%3B206677",
# "prod=9835&xsubject=1889&fdlvr=24",
# "prod=9835&xsubject=1889&fdlvr=120",
# "prod=9835&xsubject=1889&faction=1&fnds=1&frating=1&foriginal=1&fpremium=1&ffeedbackpoints=1&fpremiumuser=1&f11461=22528%3B22533&f14081=643600725%3B102252956&f15002656=-29856%3B-29855&f746=9564676%3B10326&f355315=371772%3B371771&f5023=214366%3B85146&priceU=500%3B600&fbrand=194905231%3B311378557&fsupplier=3942301%3B206677",

# 6) теперь собираем все варианты строк, содержащие одинаковые prod, но с неповторяющимися значениями параметра fdlvr:


# "prod=9835&xsubject=764&faction=1&fnds=1&frating=1&foriginal=1&fpremium=1&ffeedbackpoints=1&fpremiumuser=1&priceU=100%3B200&fbrand=194905231%3B311378557&fsupplier=3942301%3B206677&fdlvr=4",
# "prod=9835&xsubject=764&faction=1&fnds=1&frating=1&foriginal=1&fpremium=1&ffeedbackpoints=1&fpremiumuser=1&priceU=100%3B200&fbrand=194905231%3B311378557&fsupplier=3942301%3B206677&fdlvr=24",
# "prod=9835&xsubject=1889&faction=1&fnds=1&frating=1&foriginal=1&fpremium=1&ffeedbackpoints=1&fpremiumuser=1&f11461=22528%3B22533&f14081=643600725%3B102252956&f15002656=-29856%3B-29855&f746=9564676%3B10326&f355315=371772%3B371771&f5023=214366%3B85146&priceU=500%3B600&fbrand=194905231%3B311378557&fsupplier=3942301%3B206677&fdlvr=24",
# "prod=9835&xsubject=1889&faction=1&fnds=1&frating=1&foriginal=1&fpremium=1&ffeedbackpoints=1&fpremiumuser=1&f11461=22528%3B22533&f14081=643600725%3B102252956&f15002656=-29856%3B-29855&f746=9564676%3B10326&f355315=371772%3B371771&f5023=214366%3B85146&priceU=500%3B600&fbrand=194905231%3B311378557&fsupplier=3942301%3B206677&fdlvr=120",




# Итог
# "prod=4830",
# "prod=15692",
# "prod=9835&xsubname=FM-трансмиттер&xsubject=764&fpremium=1&fpremiumuser=1&fdlvr=72&priceU=100%3B2000000",
# "prod=9835&xsubname=Автомобильное зарядное устройство&xsubject=1889&fbrand=27920%3B9546&fpremiumuser=1&fsupplier=33762&f11461=22528%3B22533",
# "prod=9835&xsubname=Видеорегистратор автомобильный&xsubject=600"




















'prod=9835&xsubname=FM-трансмиттер&xsubject=764',
'prod=9835&xsubname=Автомобильное зарядное устройство&xsubject=1889&faction=1&fnds=1&fdlvr=24&frating=1&foriginal=1&fpremium=1&ffeedbackpoints=1&fpremiumuser=1&f11461=22528&f14081=63147&f15002656=-29856%3B-29857&f746=10326%3B3658649%3B3698306&f355315=371772&f5023=109520&priceU=50000%3B100000',
'prod=15692'


'prod=9835&xsubject=1889&faction=1',
'prod=9835&xsubject=1889&fnds=1',
'prod=9835&xsubject=1889&fdlvr=24',
'prod=9835&xsubject=1889&frating=1',
'prod=9835&xsubject=1889&foriginal=1',
'prod=9835&xsubject=1889&fpremium=1',
'prod=9835&xsubject=1889&ffeedbackpoints=1',
'prod=9835&xsubject=1889&fpremiumuser)=1',
'prod=9835&xsubject=764&xsubname=FM-трансмиттер',
'prod=9835&xsubject=1889&xsubname=Автомобильное зарядное устройство',
'prod=9835&xsubject=1889&f11461=22528',
'prod=9835&xsubject=1889&f14081=63147',
'prod=9835&xsubject=1889&f15002656=-29856%3B-29857',
'prod=9835&xsubject=1889&f746=10326%3B3658649%3B3698306',
'prod=9835&xsubject=1889&f355315=371772',
'prod=9835&xsubject=1889&f5023=109520',
'prod=9835&xsubject=1889&priceU=50000%3B100000'