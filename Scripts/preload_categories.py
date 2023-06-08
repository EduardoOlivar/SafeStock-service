from api.models import Category

data = [
    ('lacteos', 'Lacteos'),
    ('carniceria', 'Carniceria'),
    ('panaderia', 'Panaderia'),
    ('despensa', 'Despensa'),
    ('botilleria', 'Botilleria'),
    ('frutas_verduras', 'Frutas o Verduras'),
    ('limpieza', 'Limpieza'),
    ('mascotas', 'Mascotas')
]


def create_categories(data):

    for categorie in data:
        category, created = Category.objects.get_or_create(category=categorie[0])
        if created:
            print(f'Categoría "{category.category}" creada.')
        else:
            print(f'Categoría "{category.category}" ya existe.')


create_categories(data)
