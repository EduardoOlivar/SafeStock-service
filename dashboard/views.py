from django.db.models import Sum
from django.shortcuts import render
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework import status
from api.models import *
from rest_framework.response import Response
from datetime import datetime, timedelta

# Create your views here.


class GenericDashBoard(APIView):

    # valida la existencia de la shop
    def get_validate_shop(self, request, *args, return_response=False, **kwargs):
        shop_id = kwargs.get('shop_id')
        try:
            shop = Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            if return_response:
                return Response({'message': 'No se encontro el negocio'}, status.HTTP_404_NOT_FOUND)
        return shop

    def timestamp_to_datetime(self,timestamp):
        return datetime.fromtimestamp(timestamp)


class ReportShopAllItemView(GenericDashBoard):

    def get(self, request, *args, **kwargs):
        shop = self.get_validate_shop(request, *args, return_response=True, **kwargs)
        if isinstance(shop, Response):
            return shop
        start_timestamp = int(request.GET.get('start'))
        end_timestamp = int(request.GET.get('end'))

        start_datetime = self.timestamp_to_datetime(start_timestamp)
        end_datetime = self.timestamp_to_datetime(end_timestamp)

        response_data = self.process_report(shop, start_datetime, end_datetime)

        return Response(response_data)

    def process_report(self, shop, start_datetime, end_datetime):
        days_difference = (end_datetime - start_datetime).days + 1

        report_data = []

        for i in range(days_difference):
            current_date = start_datetime + timedelta(days=i)
            report_entry = {}

            #consulta para obtener los datos de venta por dia
            shop_items = ShopItemSold.objects.filter(shop_id=shop.id, date__date=current_date.date())

            if shop_items:
                #se guarda los datos si existe el item en la shop para el dia
                total_sold = shop_items.aggregate(total_sold=Sum('total_sold'))['total_sold']
            else:
                #si no hay datos de venta para el día, se le asigna 0
                total_sold = 0

            #construcción del objeto de entrada para el informe por dia
            report_entry['date'] = current_date.timestamp()
            report_entry['total_sold'] = total_sold

            report_data.append(report_entry)

        return report_data



class ReportShopItemView(GenericDashBoard):
    def get(self, request, *args, **kwargs):
        shop = self.get_validate_shop(request, *args, return_response=True, **kwargs)
        if isinstance(shop, Response):
            return shop
        item_id = request.GET.get('item_id')
        start_timestamp = int(request.GET.get('start'))
        end_timestamp = int(request.GET.get('end'))

        start_datetime = self.timestamp_to_datetime(start_timestamp)
        end_datetime = self.timestamp_to_datetime(end_timestamp)
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            item = None

        response_data = self.process_report(shop, item, start_datetime, end_datetime)

        return Response(response_data)

    def process_report(self,shop, item, start_datetime, end_datetime):
        days_difference = (end_datetime - start_datetime).days + 1

        report_data = []

        for i in range(days_difference):
            current_date = start_datetime + timedelta(days=i)
            report_entry = {}

            #consulta para obtener los datos de venta por dia
            shop_item = ShopItemSold.objects.filter(shop_id=shop.id, item_id=item.id,
                                                 date__date=current_date.date()).first()

            if shop_item:
                #se guarda los datos si existe el item en la shop para el dia
                total_sold = shop_item.total_sold
                quantity_sold = shop_item.quantity_sold
                weight_sold = shop_item.weight_sold
            else:
                #si no hay datos de venta para el día, se le asigna 0
                total_sold = 0
                quantity_sold = 0
                weight_sold = 0

            #construcción del objeto de entrada para el informe por dia
            current_date_timestamp = current_date.timestamp()
            report_entry[current_date_timestamp] = {
                'sold': total_sold,
                'weight': weight_sold,
                'quantity': quantity_sold
            }
            #se hace push al arreglo
            report_data.append(report_entry)

        response_data = {
            'name_item': item.name if item else None,
            'days': report_data
        }

        return response_data



