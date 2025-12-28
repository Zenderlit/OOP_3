import json
import datetime as dt
from typing import Dict, List, Any, Tuple, Set, TypedDict
import uuid
from dataclasses import dataclass, field
from collections import defaultdict

# Определяем типы данных
class PersonData(TypedDict):
    id: str
    name: str
    born_in: str
    friend_ids: List[str]

@dataclass
class PersonStruct:
    """Структура данных для представления человека."""
    name: str
    born_in: dt.datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    friends: List['PersonStruct'] = field(default_factory=list)

# Тип для кэша объектов
PersonCache = Dict[str, PersonStruct]

def create_person(name: str, born_in: dt.datetime) -> PersonStruct:
    """Создание новой структуры человека."""
    return PersonStruct(name=name, born_in=born_in)

def add_friend(person1: PersonStruct, person2: PersonStruct) -> Tuple[PersonStruct, PersonStruct]:
    """Добавление взаимной дружбы между двумя людьми."""
    if person2 not in person1.friends:
        # Создаем копии с обновленными списками друзей
        new_person1 = PersonStruct(
            id=person1.id,
            name=person1.name,
            born_in=person1.born_in,
            friends=person1.friends + [person2]
        )
        
        new_person2 = PersonStruct(
            id=person2.id,
            name=person2.name,
            born_in=person2.born_in,
            friends=person2.friends + [new_person1]
        )
        
        # Заменяем старую ссылку в друзьях первого человека
        new_person1.friends = [
            new_person2 if friend.id == person2.id else friend
            for friend in new_person1.friends
        ]
        
        return new_person1, new_person2
    
    return person1, person2

def person_to_dict(person: PersonStruct) -> PersonData:
    """Преобразование структуры в словарь."""
    return {
        'id': person.id,
        'name': person.name,
        'born_in': person.born_in.isoformat(),
        'friend_ids': [friend.id for friend in person.friends]
    }

def dict_to_person(data: PersonData, cache: PersonCache) -> PersonStruct:
    """Создание структуры из словаря."""
    if data['id'] in cache:
        return cache[data['id']]
    
    person = PersonStruct(
        id=data['id'],
        name=data['name'],
        born_in=dt.datetime.fromisoformat(data['born_in']),
        friends=[]  # Временный пустой список
    )
    
    cache[data['id']] = person
    return person

def encode_person_functional(person: PersonStruct) -> bytes:
    """Кодирование структуры человека в байты (функциональный стиль)."""
    
    def collect_persons(current: PersonStruct, visited: Set[str], 
                        result: Dict[str, PersonData]) -> None:
        """Рекурсивный сбор всех персон в графе."""
        if current.id in visited:
            return
        
        visited.add(current.id)
        result[current.id] = person_to_dict(current)
        
        for friend in current.friends:
            collect_persons(friend, visited, result)
    
    all_persons: Dict[str, PersonData] = {}
    collect_persons(person, set(), all_persons)
    
    data = {
        'root_id': person.id,
        'persons': all_persons
    }
    
    return json.dumps(data, indent=2).encode('utf-8')

def decode_person_functional(data: bytes) -> PersonStruct:
    """Декодирование структуры человека из байтов (функциональный стиль)."""
    decoded = json.loads(data.decode('utf-8'))
    persons_data: Dict[str, PersonData] = decoded['persons']
    
    # Первый проход: создаем все структуры без связей
    cache: PersonCache = {}
    for person_data in persons_data.values():
        dict_to_person(person_data, cache)
    
    # Второй проход: устанавливаем связи
    for person_data in persons_data.values():
        person = cache[person_data['id']]
        person.friends = [
            cache[friend_id]
            for friend_id in person_data['friend_ids']
            if friend_id in cache
        ]
    
    return cache[decoded['root_id']]

def save_to_file(data: bytes, filename: str) -> None:
    """Сохранение данных в файл."""
    with open(filename, 'wb') as f:
        f.write(data)

def load_from_file(filename: str) -> bytes:
    """Загрузка данных из файла."""
    with open(filename, 'rb') as f:
        return f.read()