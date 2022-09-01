from django.urls import include, path
from django.contrib import admin
from .views.product import ProductReviewList,ProductReviewCreate

urlpatterns = [
	path('products/<int:product_pk>/review/',ProductReviewList.as_view(),name='prodcut-review-list'),
	path('products/<int:product_pk>/review/create',ProductReviewCreate.as_view(),name='prodcut-review-create'),

]