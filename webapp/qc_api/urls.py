from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'stations', views.BuoyStationViewSet)
router.register(r'parameters', views.QCParameterViewSet)
router.register(r'limits', views.StationQCLimitViewSet)
router.register(r'results', views.QCResultViewSet)
router.register(r'third-party-sources', views.ThirdPartyDataSourceViewSet)
router.register(r'third-party-data', views.ThirdPartyDataViewSet)
router.register(r'confirmations', views.DataConfirmationViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/dashboard/', views.dashboard_overview, name='dashboard_overview'),
    path('api/update-limits/', views.update_qc_limits, name='update_qc_limits'),
    path('api/run-qc/', views.run_qc_processing, name='run_qc_processing'),
    path('api/stations/<str:station_id>/limits/', views.get_station_qc_limits, name='station_qc_limits'),
    path('api/download/<str:station_id>/<int:year>/<str:file_type>/', views.download_qc_file, name='download_qc_file'),
    path('api/import-third-party/', views.import_third_party_data, name='import_third_party_data'),
    path('api/run-confirmation/', views.run_data_confirmation, name='run_data_confirmation'),
    path('api/stations/<str:station_id>/confirmation-summary/', views.confirmation_summary, name='confirmation_summary'),
]
