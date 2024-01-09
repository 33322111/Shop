from _decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from shop.models import Product, Payment, OrderItem, Order


class TestDataBase(TestCase):
    fixtures = [
        "shop/fixtures/mydata.json"
    ]

    def setUp(self):
        self.user = User.objects.get(username='root')
        self.pr = Product.objects.all().first()

    def test_user_exists(self):
        users = User.objects.all()
        users_number = users.count()
        user = users.first()
        self.assertEqual(users_number, 4)
        self.assertEqual(user.username, 'root')
        self.assertTrue(user.is_superuser)

    def test_user_check_password(self):
        self.assertTrue(self.user.check_password('12345'))

    def test_all_data(self):
        self.assertGreater(Product.objects.all().count(), 0)
        self.assertGreater(Order.objects.all().count(), -1)
        self.assertGreater(OrderItem.objects.all().count(), -1)
        self.assertGreater(Payment.objects.all().count(), -1)

    def find_cart_number(self):
        cart_number = Order.objects.filter(user=self.user, status=Order.STATUS_CART).count()
        return cart_number

    def test_function_get_cart(self):
        """
        Check carts number
        1. No carts
        2. Create cart
        3. Get created cart
        Add @staticmethod Order.get_cart(user)
        """
        # 1. No carts
        self.assertEqual(self.find_cart_number(), 0)

        # 2. Create cart
        Order.get_cart(self.user)
        self.assertEqual(self.find_cart_number(), 1)

        # 3. Get created cart
        Order.get_cart(self.user)
        self.assertEqual(self.find_cart_number(), 1)

    def test_recalculate_order_amount_after_changing_orderitem(self):
        """
        Checking cart amount
        1. Get order amount before any changing
        2. Get order amount after adding an item
        3. Get order amount after deleting an item

        Add amount to OrderItem s @property
        Add Order.get_amount(user)
        """
        # 1. Get order amount before any changing
        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(0))

        # 2. Get order amount after adding an item
        it = OrderItem.objects.create(order=cart, product=self.pr, price=2, quantity=10)
        it = OrderItem.objects.create(order=cart, product=self.pr, price=3, quantity=10)
        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(50))

        # 3. Get order amount after deleting an item
        it.delete()
        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(20))

    def test_cart_status_hanging_after_applying_make_order(self):
        """
        Check cart status change after Order.make_order()
        1. Attemp to change the status for an empty cart
        2. Attemp to change the status for a non-empty cart

        Add Order.make_order()
        """
        # 1. Attemp to change the status for an empty cart
        cart = Order.get_cart(self.user)
        cart.make_order()
        self.assertEqual(cart.status, Order.STATUS_CART)

        # 2. Attemp to change the status for a non-empty cart
        OrderItem.objects.create(order=cart, product=self.pr, price=2, quantity=10)
        cart.make_order()
        self.assertEqual(cart.status, Order.STATUS_WAITING_FOR_PAYMENT)
