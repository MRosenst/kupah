from unittest import TestCase
from kupah.kupah import *


class TestItemList(TestCase):
    @staticmethod
    def create_generic():
        l = ItemList()
        # l.add(Item('7290004645434', 'Fish', 2990, 1200, True))
        l.add(Item('7290000474021', 'Tara Milk 3% 1L Bag', 450, 6, tag='reduced'))
        # l.add(Item('7290000688381', 'Water 1.5L x6', 1090, 2))
        l.add(Item('7290000474021', 'Tara Milk 3% 1L Bag', 450, 3, tag='reduced'))
        return l

    @staticmethod
    def print_debug(l):
        for i in l.items:
            print(i.name)
            print(i.amount)
            print(i.canceled())
            print(i.tag)
            print('-' * 15)

    def test_cancel(self):
        l = self.create_generic()
        l.cancel(code='7290000474021', amount=4)

        assert l.subtotal == 2250

    def test_count(self):
        l = self.create_generic()
        assert l.count('7290000474021') == 9
        l.cancel(code='7290000474021', amount=4)


        assert l.count('7290000474021') == 5


    def test___len__(self):
        l = self.create_generic()
        assert len(l) == 9
        l.cancel(code='7290000474021', amount=2)
        assert len(l) == 7

