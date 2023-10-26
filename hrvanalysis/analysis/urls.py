from django.urls import path
from . import views

urlpatterns = [
    path('subjects/', views.subject_list, name="subject_list"),
    path('subjects/<str:pk>/samples/', views.subject_sample_list, name="subject_sample_list"),
    path('subjects/<str:pk>/preview-file-upload/', views.preview_file, name="preview_file"),
    path('Samples/<str:pk>/', views.analysis_board, name="analysis_board"),
    path('Samples/<str:pk>/report/', views.result_render_pdf, name="result_render_pdf"),
]