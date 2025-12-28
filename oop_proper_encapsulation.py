import json
import datetime as dt
from typing import Dict, List, Any, Optional, Set
import uuid
from abc import ABC, abstractmethod

class Serializable(ABC):
    """Абстрактный базовый класс для сериализуемых объектов."""
    
    @abstractmethod
    def to_serializable_dict(self) -> Dict[str, Any]:
        """Возвращает данные для сериализации в виде словаря."""
        pass
    
    @classmethod
    @abstractmethod
    def from_serializable_dict(cls, data: Dict[str, Any]) -> 'Serializable':
        """Создает объект из словаря."""
        pass

class Person(Serializable):
    def __init__(
        self,
        name: str,
        born_in: dt.datetime,
    ) -> None:
        self._name = name
        self._friends: List['Person'] = []
        self._born_in = born_in
        # Идентификатор для обработки ссылок
        self._id = str(uuid.uuid4())

    def add_friend(self, friend: 'Person') -> None:
        if friend not in self._friends:
            self._friends.append(friend)
            if self not in friend._friends:
                friend._friends.append(self)

    @property
    def name(self) -> str:
        return self._name

    @property
    def born_in(self) -> dt.datetime:
        return self._born_in

    def get_friends(self) -> List['Person']:
        return self._friends.copy()

    # Публичные методы для работы с инкапсулированными данными
    def get_id(self) -> str:
        return self._id

    def get_friend_ids(self) -> List[str]:
        return [friend.get_id() for friend in self._friends]

    def to_serializable_dict(self) -> Dict[str, Any]:
        """Сериализация с использованием публичных методов."""
        return {
            'id': self.get_id(),
            'name': self._name,  # Доступ к _name допустим из самого класса
            'born_in': self._born_in.isoformat(),
            'friend_ids': self.get_friend_ids()
        }

    @classmethod
    def from_serializable_dict(cls, data: Dict[str, Any]) -> 'Person':
        """Создание объекта из словаря с использованием конструктора."""
        # Создаем объект через конструктор
        person = cls(
            name=data['name'],
            born_in=dt.datetime.fromisoformat(data['born_in'])
        )
        
        # Устанавливаем ID (немного нарушаем инкапсуляцию, но это необходимо)
        person._id = data['id']
        
        # Временно сохраняем ID друзей
        person._friend_ids = data.get('friend_ids', [])
        
        return person

class PersonEncoder:
    """Кодировщик объектов Person с поддержкой циклических ссылок."""
    
    @staticmethod
    def encode(person: Person) -> bytes:
        """Кодирование объекта Person в байты."""
        objects_cache: Dict[str, Person] = {}
        serialized_objects: Dict[str, Dict[str, Any]] = {}
        
        def collect_and_serialize(current_person: Person, visited: Set[str]) -> None:
            if current_person.get_id() in visited:
                return
            visited.add(current_person.get_id())
            
            objects_cache[current_person.get_id()] = current_person
            serialized_objects[current_person.get_id()] = current_person.to_serializable_dict()
            
            for friend in current_person.get_friends():
                collect_and_serialize(friend, visited)
        
        collect_and_serialize(person, set())
        
        data = {
            'root_id': person.get_id(),
            'objects': serialized_objects
        }
        
        return json.dumps(data, indent=2).encode('utf-8')
    
    @staticmethod
    def decode(data: bytes) -> Person:
        """Декодирование объекта Person из байтов."""
        decoded = json.loads(data.decode('utf-8'))
        
        objects_cache: Dict[str, Person] = {}
        
        # Сначала создаем все объекты
        for obj_id, obj_data in decoded['objects'].items():
            person = Person.from_serializable_dict(obj_data)
            objects_cache[obj_id] = person
        
        # Затем устанавливаем связи
        for person in objects_cache.values():
            friend_ids = getattr(person, '_friend_ids', [])
            person._friends = [
                objects_cache[friend_id]
                for friend_id in friend_ids
                if friend_id in objects_cache
            ]
            # Удаляем временный атрибут
            if hasattr(person, '_friend_ids'):
                delattr(person, '_friend_ids')
        
        return objects_cache[decoded['root_id']]