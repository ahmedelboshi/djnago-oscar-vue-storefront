from rest_framework import serializers
from oscarapi.serializers import product
from oscar.core.loading import get_class,get_model
from oscarapi.utils.loading import get_api_classes, get_api_class
from django.shortcuts import reverse
StockRecord = get_model("partner", "StockRecord")
ProductReview = get_model('reviews', 'ProductReview')

PriceSerializer = get_api_class("serializers.checkout", "PriceSerializer")



Selector = get_class("partner.strategy", "Selector")
(

    ProductStockRecordSerializer,
    AvailabilitySerializer,
) = get_api_classes(
    "serializers.product",
    [
        "ProductStockRecordSerializer",
        "AvailabilitySerializer",
    ],
)

class ProductReviewSerializer(serializers.ModelSerializer):
    # user = ser
    class Meta:
        model = ProductReview
        exclude =['status']


class ProductReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        exclude = ['product','user','score','name','email','homepage','status','total_votes','delta_votes','date_created']




class ChildProductSerializer(product.ChildProductSerializer):
    price = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()

    def get_price(self, obj):
        request = self.context['request']
        strategy = Selector().strategy(request=request, user=request.user)
        return PriceSerializer(strategy.fetch_for_product(obj).price,context={"request": request}).data

    def get_availability(self,obj):
    	request = self.context['request']
    	strategy = Selector().strategy(request=request, user=request.user)
    	return AvailabilitySerializer(
            strategy.fetch_for_product(obj).availability,
            context={"request": request},
        ).data


class ProductSerializer(product.ProductSerializer):
    price = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()
    stockrecords = serializers.SerializerMethodField()
    review_link = serializers.SerializerMethodField()
    children = ChildProductSerializer(many=True, required=False)

    # reviews 
    class Meta(product.ProductSerializer.Meta):
        fields=(
                "url",
                "upc",
                "id",
                "title",
                "description",
                "structure",
                "date_created",
                "date_updated",
                "recommended_products",
                "attributes",
                "categories",
                "product_class",
                "images",
                "price",
                "availability",
                "stockrecords",
                "review_link",
                "options",
                "children",
            )


    def get_price(self, obj):
        request = self.context['request']
        strategy = Selector().strategy(request=request, user=request.user)
        return PriceSerializer(strategy.fetch_for_product(obj).price,context={"request": request}).data

    def get_availability(self,obj):
    	request = self.context['request']
    	strategy = Selector().strategy(request=request, user=request.user)
    	return AvailabilitySerializer(
            strategy.fetch_for_product(obj).availability,
            context={"request": request},
        ).data

    def get_stockrecords(self,obj):
    	stock_records = StockRecord.objects.filter(product_id=obj.pk)
    	return ProductStockRecordSerializer(stock_records,many=True,context={'request':self.context['request']}).data


    def get_review_link(self,obj):
        return self.context['request'].build_absolute_uri(reverse('prodcut-review-list',kwargs={'product_pk':obj.pk}))

