from peewee import *
import sqlite3
from datetime import datetime, timedelta
from random import randint, choice

conn = SqliteDatabase("cafeclass.sqlite")

# Модели базы данных
class BaseModel(Model):
    class Meta:
        database = conn

class Dishes(BaseModel):
    dishes_id = AutoField(column_name='DishesId')
    name = TextField()

    class Meta:
        table_name = 'Dishes'

class Orders(BaseModel):    
    orders_id = AutoField(column_name='OrdersId')
    dishes = ForeignKeyField(column_name='DishesId', field='dishes_id', model=Dishes)
    cook_time = TextField()
    order_time = TextField()

    class Meta:
        table_name = 'Orders'
    
    @property
    def order_datetime(self):
        return datetime.strptime(self.order_time, '%Y-%m-%d %H:%M:%S')
    
    @order_datetime.setter
    def order_datetime(self, dt):
        self.order_time = dt.strftime('%Y-%m-%d %H:%M:%S')
    
    @property
    def cook_datetime(self):
        return datetime.strptime(self.cook_time, '%Y-%m-%d %H:%M:%S')
    
    @cook_datetime.setter
    def cook_datetime(self, dt):
        self.cook_time = dt.strftime('%Y-%m-%d %H:%M:%S')

class Reviews(BaseModel):
    reviews_id = AutoField(column_name='ReviewsId')
    orders = ForeignKeyField(column_name='OrdersId', field='orders_id', model=Orders)
    review = TextField()

    class Meta:
        table_name = 'Reviews'

class OrderDetails(BaseModel):
    orders_id = IntegerField(column_name='OrdersId')
    dish_name = TextField()
    order_time = TextField()
    cook_time = TextField()
    review = TextField(null=True)
    
    class Meta:
        table_name = 'OrderDetails'
        primary_key = False

    @property
    def order_datetime(self):
        return datetime.strptime(self.order_time, '%Y-%m-%d %H:%M:%S')
    
    @order_datetime.setter
    def order_datetime(self, dt):
        self.order_time = dt.strftime('%Y-%m-%d %H:%M:%S')
    
    @property
    def cook_datetime(self):
        return datetime.strptime(self.cook_time, '%Y-%m-%d %H:%M:%S')
    
    @cook_datetime.setter
    def cook_datetime(self, dt):
        self.cook_time = dt.strftime('%Y-%m-%d %H:%M:%S')

# Базовый класс для коллекции
class BaseCollection:
    # Инициализация коллекции
    def __init__(self, data=None):
        self._data = data or []
    # Поддержка итерации по коллекции
    def __iter__(self):
        return iter(self._data)
    # Поддержка индексированного доступа
    def __getitem__(self, index):
        return self._data[index]
    # Строковое представление объекта
    def __repr__(self):
        return f"{self.__class__.__name__}({self._data})"
    # Поддержка функции len()
    def __len__(self):
        return len(self._data)
    # Контроль над установкой атрибутов
    def __setattr__(self, name, value):
        if name != '_data' and hasattr(self, '_data'):
            raise AttributeError("Установка атрибутов напрямую запрещена")
        super().__setattr__(name, value)
    # Добавление нового элемента в коллекцию
    def add(self, item):
        self._data.append(item)

# Класс для работы с OrderDetails
class OrderDetailsCollection(BaseCollection):
    @staticmethod
    def get_all_sorted_by_dish_name():
        query = OrderDetails.select().order_by(OrderDetails.dish_name)
        return OrderDetailsCollection(list(query))

    def get_all_sorted_by_orders_id():
        query = OrderDetails.select().order_by(OrderDetails.orders_id)
        return OrderDetailsCollection(list(query))
    
    @staticmethod
    def get_by_orders_id(orders_id):
        query = OrderDetails.select().where(OrderDetails.orders_id == orders_id)
        return OrderDetailsCollection(list(query))
    
    @staticmethod
    def get_fast_orders(max_minutes=15):
        query = OrderDetails.select()
        result = []
        for order in query:
            delta = order.cook_datetime - order.order_datetime
            if delta < timedelta(minutes=max_minutes):
                result.append(order)
        return OrderDetailsCollection(result)
    
    def print_all(self):
        for item in self._data:
            print(f"Order ID: {item.orders_id}, Dish: {item.dish_name}, "
                  f"Order Time: {item.order_time}, Cook Time: {item.cook_time}, "
                  f"Review: {item.review}")

# Класс для добавления новых данных
class DataAdder:
    @staticmethod
    def add_dish(name):
        dish = Dishes(name=name)
        dish.save()
        return dish
    
    @staticmethod
    def add_order(dish_id, order_time, cook_time):
        order = Orders(dishes=dish_id, order_time=order_time, cook_time=cook_time)
        order.save()
        return order
    
    @staticmethod
    def add_review(order_id, review_text):
        review = Reviews(orders=order_id, review=review_text)
        review.save()
        return review
    
    @staticmethod
    def generate_full_order():
        """Генерирует полный тестовый заказ со всеми связанными данными"""
        dish = DataAdder.add_dish(f"Тестовое блюдо {randint(1, 100)}")
        order_time = datetime.now() - timedelta(minutes=randint(0, 60))
        cook_time = order_time + timedelta(minutes=randint(5, 30))
    
        order = DataAdder.add_order(
            dish_id=dish.dishes_id,
            order_time=order_time.strftime('%Y-%m-%d %H:%M:%S'),
            cook_time=cook_time.strftime('%Y-%m-%d %H:%M:%S')
        )
    
        review = DataAdder.add_review(
            order_id=order.orders_id,
            review_text=choice(["Отлично", "Хорошо", "Удовлетворительно", "Плохо"])
        )
    
        return {
            'dish': dish,
            'order': order,
            'review': review
        }

# Пример использования
def main():
    conn.connect()
    try:
        while True:
            print ("\nВведите цифру от 0 до 5:\n0 - Завершение программы\n1 - Вывести информацию по конкретному заказу")
            print("2 - Содержимое базы данных с сортировкой по наименованию блюда\n3 - Содержимое базы данных с сортировкой по номеру блюда")
            print("4 - Содержимое базы данных с фильтрацией по времени выдачи\n5 - Ввод новых записей в базу данных")
            c = input()
            match c:
                case "0":
                    print ("\nВыполнение программы остановлено")
                    break
                case "1":
                    print ("\nВывести информацию по конкретному заказу:")
                    print ("Введите номер заказа:")
                    try:
                        order_id = int(input())
                        order_by_id = OrderDetailsCollection.get_by_orders_id(order_id)
                        order_by_id.print_all()
                    except ValueError:
                        print("Ошибка: номер заказа должен быть целым числом")
                case "2":
                    print ("\nСодержимое базы данных с сортировкой по наименованию блюда:")
                    orders_sorted_by_dish_name = OrderDetailsCollection.get_all_sorted_by_dish_name()
                    orders_sorted_by_dish_name.print_all()
                case "3":
                    print("\nСодержимое базы данных с сортировкой по номеру заказа:")
                    orders_sorted_by_orders_id = OrderDetailsCollection.get_all_sorted_by_orders_id()
                    orders_sorted_by_orders_id.print_all()
                case "4":
                    print("\nСодержимое базы данных с фильтрацией по времени выдачи:")
                    fast_orders = OrderDetailsCollection.get_fast_orders()
                    fast_orders.print_all()
                case "5":

                    order_data = DataAdder.generate_full_order()
                    
                    # Выводим информацию о созданных данных
                    print("\nДобавлены тестовые данные:")
                    print(f"Блюдо: {order_data['dish'].name} (ID: {order_data['dish'].dishes_id})")
                    print(f"Заказ: ID {order_data['order'].orders_id}")
                    print(f"Время заказа: {order_data['order'].order_time}")
                    print(f"Время готовности: {order_data['order'].cook_time}")
                    print(f"Отзыв: '{order_data['review'].review}'")                

    finally:
        conn.close()

if __name__ == "__main__":
    main()  # Вызов основной функции программы