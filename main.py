import datetime as dt
import os

# Импорт всех реализаций
from oop_encapsulation_violation import Person as PersonViolation, encode_person as encode_violation, decode_person as decode_violation
from oop_proper_encapsulation import Person as PersonProper, PersonEncoder
from functional_serialization import (
    create_person, add_friend, 
    encode_person_functional, decode_person_functional,
    save_to_file, load_from_file
)

def demonstrate_oop_violation() -> None:
    """Демонстрация ООП подхода с нарушением инкапсуляции."""
    print("=" * 70)
    print("ООП С НАРУШЕНИЕМ ИНКАПСУЛЯЦИИ")
    print("=" * 70)
    
    # Создаем объекты
    p1 = PersonViolation("Иван", dt.datetime(1990, 5, 15))
    p2 = PersonViolation("Мария", dt.datetime(1992, 8, 22))
    p3 = PersonViolation("Петр", dt.datetime(1985, 3, 10))
    
    # Создаем циклические связи
    p1.add_friend(p2)
    p2.add_friend(p3)
    p3.add_friend(p1)  # Цикл!
    
    print(f"До кодирования:")
    print(f"p1: {p1.name}, друзей: {len(p1._friends)}")
    print(f"p2: {p2.name}, друзей: {len(p2._friends)}")
    print(f"p3: {p3.name}, друзей: {len(p3._friends)}")
    
    # Кодируем
    encoded = encode_violation(p1)
    print(f"\nЗакодировано {len(encoded)} байт")
    
    # Декодируем
    decoded_p1 = decode_violation(encoded)
    
    print(f"\nПосле декодирования:")
    print(f"decoded_p1: {decoded_p1.name}, друзей: {len(decoded_p1._friends)}")
    print(f"Друг decoded_p1: {decoded_p1._friends[0].name if decoded_p1._friends else 'нет'}")
    print(f"Друг друга decoded_p1: {decoded_p1._friends[0]._friends[0].name if decoded_p1._friends and decoded_p1._friends[0]._friends else 'нет'}")
    
    # Проверяем цикличность
    print(f"\nПроверка цикличности:")
    print(f"p1 есть в друзьях p2? {decoded_p1 in decoded_p1._friends[0]._friends}")
    print(f"p2 есть в друзьях p3? {decoded_p1._friends[0] in decoded_p1._friends[0]._friends[0]._friends}")
    
    return encoded

def demonstrate_oop_proper() -> None:
    """Демонстрация ООП подхода БЕЗ нарушения инкапсуляции."""
    print("\n" + "=" * 70)
    print("ООП БЕЗ НАРУШЕНИЯ ИНКАПСУЛЯЦИИ")
    print("=" * 70)
    
    p1 = PersonProper("Анна", dt.datetime(1995, 7, 30))
    p2 = PersonProper("Борис", dt.datetime(1993, 2, 14))
    p3 = PersonProper("Светлана", dt.datetime(1988, 11, 5))
    
    p1.add_friend(p2)
    p2.add_friend(p3)
    
    print(f"До кодирования:")
    print(f"p1: {p1.name}, друзей: {len(p1.get_friends())}")
    print(f"p2: {p2.name}, друзей: {len(p2.get_friends())}")
    
    encoded = PersonEncoder.encode(p1)
    print(f"\nЗакодировано {len(encoded)} байт")
    
    decoded_p1 = PersonEncoder.decode(encoded)
    
    print(f"\nПосле декодирования:")
    print(f"decoded_p1: {decoded_p1.name}, друзей: {len(decoded_p1.get_friends())}")
    print(f"Друг decoded_p1: {decoded_p1.get_friends()[0].name if decoded_p1.get_friends() else 'нет'}")
    
    return encoded

def demonstrate_functional() -> None:
    """Демонстрация функционального подхода."""
    print("\n" + "=" * 70)
    print("ФУНКЦИОНАЛЬНЫЙ ПОДХОД")
    print("=" * 70)
    
    # Создаем структуры
    p1 = create_person("Олег", dt.datetime(1991, 4, 18))
    p2 = create_person("Татьяна", dt.datetime(1994, 9, 3))
    p3 = create_person("Дмитрий", dt.datetime(1987, 12, 25))
    
    # Добавляем друзей (возвращаются новые структуры)
    p1, p2 = add_friend(p1, p2)
    p2, p3 = add_friend(p2, p3)
    
    print(f"До кодирования:")
    print(f"p1: {p1.name}, друзей: {len(p1.friends)}")
    print(f"p2: {p2.name}, друзей: {len(p2.friends)}")
    print(f"p3: {p3.name}, друзей: {len(p3.friends)}")
    
    encoded = encode_person_functional(p1)
    print(f"\nЗакодировано {len(encoded)} байт")
    
    # Сохраняем в файл
    save_to_file(encoded, "person_data.json")
    print("Сохранено в файл 'person_data.json'")
    
    # Загружаем из файла
    loaded_data = load_from_file("person_data.json")
    decoded_p1 = decode_person_functional(loaded_data)
    
    print(f"\nПосле декодирования из файла:")
    print(f"decoded_p1: {decoded_p1.name}, друзей: {len(decoded_p1.friends)}")
    print(f"Друг decoded_p1: {decoded_p1.friends[0].name if decoded_p1.friends else 'нет'}")
    
    # Удаляем временный файл
    if os.path.exists("person_data.json"):
        os.remove("person_data.json")
    
    return encoded

def analyze_approaches() -> None:
    """Анализ различных подходов."""
    print("\n" + "=" * 70)
    print("АНАЛИЗ ПОДХОДОВ")
    print("=" * 70)
    
    print("\n1. ООП С НАРУШЕНИЕМ ИНКАПСУЛЯЦИИ:")
    print("   - Плюсы: Простая реализация, прямой доступ ко всем данным")
    print("   - Минусы: Нарушение принципов ООП, уязвимость к изменениям в классе")
    print("   - Проблемы: Зависимость от внутренней реализации, сложность поддержки")
    
    print("\n2. ООП БЕЗ НАРУШЕНИЯ ИНКАПСУЛЯЦИИ:")
    print("   - Плюсы: Сохранение инкапсуляции, стабильный API, легче поддерживать")
    print("   - Минусы: Более сложная реализация, требуется больше кода")
    print("   - Проблемы: Необходимость в дополнительных методах (get_id, get_friend_ids)")
    
    print("\n3. ФУНКЦИОНАЛЬНЫЙ ПОДХОД:")
    print("   - Плюсы: Чистые функции, неизменяемость данных, предсказуемость")
    print("   - Минусы: Может быть менее эффективным по памяти")
    print("   - Проблемы: Необходимость создавать новые структуры при изменении")
    
    print("\n4. ОБРАБОТКА ЦИКЛИЧЕСКИХ ССЫЛОК:")
    print("   - Решение: Использование уникальных ID и кэширования объектов")
    print("   - Двухэтапная реконструкция: 1) создание объектов, 2) установка связей")
    
    print("\n5. СОЗДАНИЕ ОБЪЕКТОВ БЕЗ КОНСТРУКТОРА:")
    print("   - Метод __new__: Позволяет создать экземпляр без вызова __init__")
    print("   - Применение: Для десериализации, когда нужен контроль над инициализацией")
    print("   - Риски: Объект может быть в неконсистентном состоянии")

def main() -> None:
    """Основная функция демонстрации."""
    print("Лабораторная работа 3: Проблемы инкапсуляции при сериализации")
    print("=" * 70)
    
    # Демонстрация всех подходов
    violation_data = demonstrate_oop_violation()
    proper_data = demonstrate_oop_proper()
    functional_data = demonstrate_functional()
    
    # Анализ подходов
    analyze_approaches()
    
    # Сравнение размеров данных
    print("\n" + "=" * 70)
    print("СРАВНЕНИЕ РАЗМЕРОВ ДАННЫХ:")
    print(f"ООП с нарушением инкапсуляции: {len(violation_data)} байт")
    print(f"ООП без нарушения инкапсуляции: {len(proper_data)} байт")
    print(f"Функциональный подход: {len(functional_data)} байт")

if __name__ == "__main__":
    main()