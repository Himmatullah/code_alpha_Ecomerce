from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product
from .models import Cart, CartItem


class CartFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name='Test electronics')
        cls.product = Product.objects.create(
            category=category,
            name='Test product',
            description='Product for checkout-free cart tests',
            price=Decimal('12.50'),
            stock=3,
            is_active=True,
        )

    def test_cart_pages_and_guest_add(self):
        self.assertEqual(self.client.get(reverse('cart_detail')).status_code, 200)
        response = self.client.post(
            reverse('add_to_cart', args=[self.product.pk]),
            {'quantity': '2'},
        )
        self.assertRedirects(response, reverse('cart_detail'))
        self.assertContains(self.client.get(reverse('cart_detail')), '25.00')
        self.assertEqual(CartItem.objects.get().quantity, 2)

    def test_stock_limit_and_remove(self):
        self.client.post(reverse('add_to_cart', args=[self.product.pk]), {'quantity': '2'})
        self.client.post(reverse('add_to_cart', args=[self.product.pk]), {'quantity': '2'})
        item = CartItem.objects.get()
        self.assertEqual(item.quantity, 2)
        self.client.post(reverse('remove_from_cart', args=[item.pk]))
        self.assertFalse(CartItem.objects.exists())

    def test_cart_mutations_require_post(self):
        self.assertEqual(self.client.get(reverse('add_to_cart', args=[self.product.pk])).status_code, 405)

    def test_different_guest_cannot_modify_cart_item(self):
        self.client.post(reverse('add_to_cart', args=[self.product.pk]), {'quantity': '1'})
        item = CartItem.objects.get()
        from django.test import Client
        other = Client()
        response = other.post(reverse('remove_from_cart', args=[item.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CartItem.objects.filter(pk=item.pk).exists())
