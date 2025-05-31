from django.urls import path
from .views import PredictSalaryAPIView

urlpatterns = [
    path('predict/', PredictSalaryAPIView.as_view(), name='predict_salary'),
]