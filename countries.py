'''
Потрібно реалізувати клас який буде взаємодіяти зі стороннім API:
API (https://restcountries.com) Клас повинен отримувати дані від API та
повертати в консоль в табличній формі, а саме такі дані: назва країни,
назва столиці та посилання на зображення прапору в форматі png.
'''

import os
import requests
from typing import TypedDict
from urllib.parse import urlencode, quote


class CountriesAPI:
    base = 'https://restcountries.com/v3.1'

    class Country(TypedDict):
        name: str
        capital: str | None
        flag: str | None

    def __init__(self):
        endpoints = (
            'name', 'alpha', 'currency', 'demonym', 'lang',
            'capital', 'region', 'subregions', 'translation'
        )
        for name in endpoints:
            def shortcut(argument, **filters):
                return self.endpoint(name, argument, **filters)
            setattr(self, name, shortcut)

    def _parse(self, country: dict) -> Country:
        '''
        Parses a dict representing a country according to the structure:
        gitlab.com/restcountries/restcountries/-/blob/master/FIELDS.md
        '''
        return {
            'name': country.get('name', {}).get('common', 'No common name'),
            'flag': country.get('flags', {}).get('png'),
            'capital': ', '.join(country.get('capital', ''))
        }

    def endpoint(self, name: str, argument: str, **filters) -> list[Country]:
        'General method for accessing API endpoints'

        url = self.base + '/' + name
        if argument:
            url += '/' + quote(argument)
        if filters:
            url += '?' + urlencode(filters, doseq=True)

        result = requests.get(url).json()

        if not isinstance(result, list):
            print(result)
            exit(1)

        return [self._parse(country) for country in result]

    def all(self, **filters) -> list[Country]:
        return self.endpoint('all', '', **filters)

    def full_name(self, country_name: str, **filters) -> list[Country]:
        filters['fullText'] = True
        return self.endpoint('name', country_name, **filters)

    def list_of_codes(self, codes: list[str], **filters) -> list[Country]:
        filters['codes'] = codes
        return self.endpoint('alpha', **filters)


def print_table(countries: list[CountriesAPI.Country]):
    columns, _ = os.get_terminal_size()
    if columns < 80:
        return print('Your terminal is too small to display the table ):')

    template = '{:20.20} | {:20.20} | {:34.34}'
    sep = '-'
    sep = f'\n{sep * 21}+{sep * 22}+{sep * 35}\n'

    legend = template.format('Name', 'Capital', 'Flag')
    rows = (template.format(i['name'], i['capital'], i['flag'])
            for i in countries)

    print(legend, *rows, sep=sep)


if __name__ == '__main__':
    api = CountriesAPI()
    countries = api.all()

    print_table(countries)
