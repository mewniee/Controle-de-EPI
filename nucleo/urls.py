"""
URL configuration for epi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from nucleo import views

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('equipamentos/', views.equipamentos, name='equipamentos'),
    path('colaboradores/', views.colaboradores, name='colaboradores'),
    path('controle/', views.controle, name='controle'),
    path('relatorios/', views.relatorios, name='relatorios'),
    path('excluir-colaborador/<int:id>/', views.excluir_colaborador, name='excluir_colaborador'),
    path('excluir-epi/<int:id>/', views.excluir_epi, name='excluir_epi'),
    path('excluir-emprestimo/<int:id>/', views.excluir_emprestimo, name='excluir_emprestimo'),
]
