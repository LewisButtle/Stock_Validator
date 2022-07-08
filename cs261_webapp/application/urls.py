from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create_trade/', views.CreateTradeView, name='create_trade'),
    path('edit_trade/', views.EditTradeView, name='edit_trade'),
    path('delete_trade/', views.DeleteTradeView, name='delete_trade'),
    path('daily_report/', views.DailyReportView, name='daily_report'),
    path('csv_upload/', views.UploadCSV, name='csv_upload'),
    path('main/', views.MainView, name='main'),
]
