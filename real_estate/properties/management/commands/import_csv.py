import csv
from django.core.management.base import BaseCommand
from properties.models import Property

class Command(BaseCommand):
    help = 'Import properties data from a CSV file'

    def handle(self, *args, **kwargs):
        with open(r'NY-House-Dataset.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Property.objects.create(
                    broker_title=row['BROKERTITLE'],
                    property_type=row['TYPE'],
                    price=row['PRICE'],
                    beds=row['BEDS'],
                    bath=row['BATH'],
                    property_sqft=row['PROPERTYSQFT'],
                    address=row['ADDRESS'],
                    state=row['STATE'],
                    city=row['LOCALITY'],
                    latitude=row['LATITUDE'],
                    longitude=row['LONGITUDE']
                )
        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
