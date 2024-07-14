'''
Потрібно створити клас який буде збирати дані за посиланням на Ebay
сторінку товару, формат даних в якому повинні повертатись дані json
в тестовому завданні можна просто виводити в консоль, або зберігати
в файл. Обов’язкові дані це назва, посилання на фото, саме посилання
на товар, ціна, продавець, ціна доставки. Авжеж чим більше даних, тим
краще, але в контексті тестового це не важливо.
'''
import bs4
import json
import requests
from pprint import pprint


class EbayProduct:
    name = None
    image_url = None
    price = None
    shipping = None
    seller = None
    seller_url = None

    def __init__(self, url: str):
        self.soup = bs4.BeautifulSoup(requests.get(url).text, 'html.parser')

        img = self.soup.select_one('#PicturePanel .ux-image-carousel-item img')
        price = self.soup.select_one('.x-price-primary')
        seller = self.soup.select_one('.x-sellercard-atf__info__about-seller a')

        self.name = self._value_by_column('Model')
        self.shipping = self._value_by_column('Shipping:')

        if not self.name:
            self.name = getattr(self.soup.find('h1'), 'text', None)
        if img:
            self.image_url = img.get('src')
        if price:
            self.price = price.text
        if seller:
            self.seller = seller.text
            self.seller_url = seller.get('href')

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'image_url': self.image_url,
            'price': self.price,
            'shipping': self.shipping,
            'seller': self.seller,
            'seller_url': self.seller_url,
        }

    def save(self, path: str):
        product = self.to_dict()

        with open(path, 'w') as file:
            json.dump(product, file)

    def _value_by_column(self, column: str) -> str | None:
        label = self.soup.find(
            'span',
            class_=self._contains('ux-textspans'),
            string=column
        )
        if label:
            parent = label.findParent(
                class_=self._contains('ux-labels-values__labels')
            )
            if parent and parent.next_sibling:
                return parent.next_sibling.text

    @staticmethod
    def _contains(value: str):
        def inner(arg):
            return arg == value or isinstance(arg, list) and value in arg
        return inner


if __name__ == '__main__':
    link = input('Please enter link to product: ')
    product = EbayProduct(link)

    pprint(product.to_dict())
