# TODO implement from tinydb import TinyDB, Query
from copy import deepcopy
from abc import ABC, abstractmethod

class Item:
    """
    Represents an item on an item list or receipt
    Note: amount is interpreted as units if by_weight is False
    and grams otherwise. Keeping amount as an int enforces
    precision limitations (i.e. fractions of grams are not to
    be considered).
    """
    MAX_NAME_LENGTH = 32
    STANDARD_TAGS = {None, 'reduced'}

    def __init__(self, code, name, price, amount=1, by_weight=False, tag=None):
        self.code = code
        self.name = name
        self.price = price
        self.amount = amount
        self.by_weight = by_weight
        self.tag = tag # TODO maybe this should be a set of tags

    @property
    def code(self):
        return self.__code

    @code.setter
    def code(self, code):
        try:
            assert isinstance(code, str)
            assert int(code) >= 0
            self.__code = code
        except:
            raise ValueError('code must be a string of digits')

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        #if not isinstance(name, str):
        #    raise TypeError('name must be a string')
        self.__name = name[:self.MAX_NAME_LENGTH]

    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, price):
        #if not isinstance(price, int):
        #    raise TypeError('price must be an integer')

        self.__price = price

    @property
    def amount(self):
        return self.__amount

    @amount.setter
    def amount(self, amount):
        #if not isinstance(amount, int):
        #    raise TypeError('amount must be an integer')

        self.__amount = amount

    @property
    def by_weight(self):
        return self.__by_weight

    @by_weight.setter
    def by_weight(self, by_weight):
        #if not isinstance(by_weight, bool):
        #    raise TypeError('by_weight must be a boolean')

        self.__by_weight = by_weight

    @property
    def cost(self):
        cost = self.amount * self.price
        if self.by_weight:
            cost //= 1000  # TODO decide whether this should floor or round

        return cost

    def canceled(self):
        return self.tag == 'canceled'

    def cancel(self):
        self.tag = 'canceled'


class Sale(ABC):
    def __init__(self, code, name, applicable_items):
        self.code = code
        self.name = name
        self.applicable_items = applicable_items

    @abstractmethod
    def apply_sale(self, item_list):
        pass


class XForYSale(Sale):
    def __init__(self):
        pass

    def apply_sale(self, item_list):
        pass


class ItemList:
    def __init__(self):
        self.__items = []

    @property
    def items(self):
        return deepcopy(self.__items)

    def add(self, item):
        #if not isinstance(item, Item):
        #    raise TypeError('item must be an Item')

        self.__items.append(item)

    def find_all(self, code, include_canceled=False, tags=Item.STANDARD_TAGS):
        """
        Finds all items with a given code
        :param code: the code to search for
        :param include_canceled: include canceled items
        :param tags: the tags to search for
        :return: a list containing all items with the given code
        """
        if include_canceled:
            tags += {'canceled'}
        res = []
        for i in self.__items:
            if i.code == code and i.tag in tags:
                res.append(i)

        return res

    def find(self, code, include_canceled=False, tags=Item.STANDARD_TAGS):
        """
        Finds the last item with a given code
        :param code: the code to search for
        :param include_canceled: include canceled items
        :param tags: the tags to search for
        :return: the last item with the given code
        """
        if include_canceled:
            tags += {'canceled'}
        for i in reversed(self.__items):
            if i.code == code and i.tag in tags:
                return i

        return None

    def cancel(self, index=None, code=None, amount=1):
        if amount < 1:
            raise ValueError('amount must be >=1')

        # Look up the item
        if index:
            item = self.__items[index]
        elif code:
            item = self.find(code)
        else:
            raise ValueError('expected either code or index')

        if not item:
            raise ValueError('item is not in list')

        cancelation_item = deepcopy(item)

        if item.by_weight:
            item.cancel()
        else:
            to_cancel = self.find_all(code)
            amount_copy = amount
            for i in reversed(to_cancel):
                if amount_copy >= i.amount:
                    i.cancel()
                    amount_copy -= i.amount
                else:
                    # Split the item
                    item_copy = deepcopy(i)
                    item_copy.amount = amount_copy
                    i.amount -= amount_copy
                    self.add(item_copy)
                    item_copy.cancel()
                    amount_copy = 0

                if amount_copy == 0:
                    break


        cancelation_item.price *= -1
        cancelation_item.amount = amount
        cancelation_item.tag = 'cancelation'
        self.add(cancelation_item)

    def inc_last(self):
        last = None
        for i in reversed(self.__items):
            if i.tag in Item.STANDARD_TAGS and not i.canceled:
                last = i
                break

        if last is None:
            return

        if last.by_weight:
            raise ValueError('cannot increment a weighable item')\

        last.amount += 1

        return last.amount

    def count(self, code):
        return sum(map(lambda i: i.amount, self.find_all(code)))

    @property
    def subtotal(self):
        return sum(map(lambda i: i.cost, self.__items))


    def __len__(self):
        res = 0
        for i in filter(lambda x: x.tag in Item.STANDARD_TAGS, self.__items):
            res += (i.amount if not i.by_weight else 1)

        return res
