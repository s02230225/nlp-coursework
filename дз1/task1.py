if __name__ == "__main__":
    # Вводится строка. Определить, может ли она являться электронным адресом (в комментариях напишите,
    # каким требованиям строка должна удовлетворять, по-вашему мнению)
    # пример etewtw   moodle.cs.msu.ru  moodle@   @ru.com  we3@u  - нет
    # TGratsianova@cs.msu.ru    mama@yandex.ru  - да

    def is_valid_email(email):
        if email.count('@') != 1:
            return False
        local_part, domain_part = email.split('@')
        if local_part == '' or domain_part == '':
            return False
        if '.' not in domain_part:
            return False
        for char in local_part:
            if not (char.isalnum() or char in '.-_'):
                return False
        for char in domain_part:
            if not (char.isalnum() or char in '.-'):
                return False
        if domain_part[0] in '.-' or domain_part[-1] in '.-':
            return False
        if len(local_part) > 64 or len(email) > 254:
            return False
        if '..' in domain_part:
            return False
        return True


    input_string = input("INPUT: ")
    if is_valid_email(input_string):
        print("ANS: YES")
    else:
        print("ANS^ NO")

    # Строка должна содержать ровно одну '@'
    # Локальная и доменная части не пустые
    # Доменная часть должна содержать точку
    # В локальной части содержать цифры, буквы, дефис, тире, точка
    # В доменной части содержать цифры, буквы, дефис, точка
    # Доменная часть не начинаться и не заканчиваться дефисом или точкой
    # Общая длина не больше 254 символов, в длина локальной не больше 64
    # В доменной части нет двух точек подряд
