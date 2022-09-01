from oscar.core.loading import get_model, get_class
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from api.serializers import product
from oscar.apps.catalogue.reviews.signals import review_added
from django.shortcuts import Http404

Product = get_model('catalogue', 'product')
ProductReview = get_model('reviews', 'ProductReview')
# ProductReviewSerializer 


class ProductReviewList(generics.ListAPIView):
    queryset = ProductReview.objects.all()
    serializer_class = product.ProductReviewSerializer

    def get_queryset(self):
        # get product reviwes
        qs = ProductReview.objects.filter(product__pk=self.kwargs['product_pk'])
        # check if user is authenticated
        if self.request.user.is_authenticated:
            # if user authenticated check if he has none approved reviews if has show with approved reviews
            return qs.filter(Q(user=self.request.user) | Q(status=1))
            # Note product review status 1 mean approved
        return qs.filter(status=1)

        # add this reviews

class ProductReviewCreate(generics.CreateAPIView):
    # copy from oscar.reviews  CreateProductReview
    serializer_class = product.ProductReviewCreateSerializer
    permission_classes=[IsAuthenticated]
    view_signal = review_added
    product_model = Product

    def dispatch(self, request, *args, **kwargs):
        try:
            self.product= self.product_model.objects.filter( ~Q(structure='child')).get(pk=kwargs['product_pk'], is_public=True)
        except self.product_model.DoesNotExist:
            raise Http404()
        # check permission to leave review
        if not self.product.is_review_permitted(request.user):
            if self.product.has_review_by(request.user):
                raise PermissionDenied("You have already reviewed this product!")
            else:
                raise PermissionDenied("You can't leave a review for this product.")

        return super().dispatch(
            request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context

    def perform_create(self, serializer):
        review = serializer.save(user=self.request.user,product=self.product,score=0)
        self.send_signal(request=self.request,review=review)
    def send_signal(self, request, review):
        self.view_signal.send(sender=self, review=review, user=request.user,
                              request=request)

# import django_filters.rest_framework
# from oscarapi.views import product
# from oscar.utils.loading import get_model

# Category = get_model("catalogue","Category")

# class ProductListAPIView(product.ProductList):
# 	def get_queryset(self):
# 		qs = super().get_queryset()

# 		# first step is get categorey
# 		# categorey
# 		# attribute

# 		return qs
