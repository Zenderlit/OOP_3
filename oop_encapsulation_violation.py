import json
import datetime as dt
from typing import Dict, List, Any, Optional, Set
import uuid

class Person:
    def __init__(
        self,
        name: str,
        born_in: dt.datetime,
    ) -> None:
        self._name = name
        self._friends: List['Person'] = []
        self._born_in = born_in
        # Внутренний идентификатор для обработки циклических ссылок
        self._id = str(uuid.uuid4())

    def add_friend(self, friend: 'Person') -> None:
        if friend not in self._friends:
            self._friends.append(friend)
            # Взаимная дружба
            if self not in friend._friends:
                friend._friends.append(self)

    @property
    def name(self) -> str:
        return self._name

    @property
    def born_in(self) -> dt.datetime:
        return self._born_in

    @property
    def friends(self) -> List['Person']:
        return self._friends.copy()  # Возвращаем копию для инкапсуляции

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование объекта в словарь (с нарушением инкапсуляции - прямой доступ к приватным полям)."""
        return {
            '_id': self._id,
            '_name': self._name,
            '_born_in': self._born_in.isoformat(),
            '_friends': [friend._id for friend in self._friends]  # Нарушение инкапсуляции!
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], objects_cache: Optional[Dict[str, 'Person']] = None) -> 'Person':
        """Создание объекта из словаря."""
        if objects_cache is None:
            objects_cache = {}

        # Проверяем, не создавали ли мы уже этот объект
        if data['_id'] in objects_cache:
            return objects_cache[data['_id']]

        # Создаем объект без использования конструктора __init__
        # (полностью нарушаем инкапсуляцию)
        person = cls.__new__(cls)
        person._id = data['_id']
        person._name = data['_name']
        person._born_in = dt.datetime.fromisoformat(data['_born_in'])
        person._friends = []

        # Сохраняем в кэш перед обработкой друзей
        objects_cache[person._id] = person

        # Временно сохраняем ID друзей
        person._friend_ids = data['_friends']

        return person

def complete_object_reconstruction(objects_cache: Dict[str, Person]) -> None:
    """Завершает восстановление объектов, устанавливая связи между друзьями."""
    for person in objects_cache.values():
        person._friends = [
            objects_cache[friend_id] 
            for friend_id in getattr(person, '_friend_ids', [])
            if friend_id in objects_cache
        ]
        # Удаляем временный атрибут
        if hasattr(person, '_friend_ids'):
            delattr(person, '_friend_ids')

def encode_person(person: Person) -> bytes:
    """Кодирование объекта Person в байты."""
    # Собираем все объекты в графе
    objects_cache: Dict[str, Person] = {}
    
    def collect_objects(current_person: Person, visited: Set[str]) -> None:
        if current_person._id in visited:
            return
        visited.add(current_person._id)
        objects_cache[current_person._id] = current_person
        
        for friend in current_person._friends:
            collect_objects(friend, visited)
    
    collect_objects(person, set())
    
    # Преобразуем все объекты в словари
    data = {
        '_root_id': person._id,
        '_objects': {obj_id: obj.to_dict() for obj_id, obj in objects_cache.items()}
    }
    
    return json.dumps(data, indent=2).encode('utf-8')

def decode_person(data: bytes) -> Person:
    """Декодирование объекта Person из байтов."""
    decoded = json.loads(data.decode('utf-8'))
    
    objects_cache: Dict[str, Person] = {}
    
    # Сначала создаем все объекты без связей
    for obj_id, obj_data in decoded['_objects'].items():
        Person.from_dict(obj_data, objects_cache)
    
    # Затем устанавливаем связи между объектами
    complete_object_reconstruction(objects_cache)
    
    return objects_cache[decoded['_root_id']]