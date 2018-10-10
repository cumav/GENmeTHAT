"""genme URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
import generator.views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/generate/', generator.views.genName.as_view(), name='generator'),
    path('api/languages/', generator.views.GetLanguages.as_view(), name='languages'),
    path('api/train/', generator.views.trainGenerator.as_view(), name='trainName'),
    path('api/status/', generator.views.GetTrainingStatus.as_view(), name='status'),
    path('api/load_model/', generator.views.LoadModel.as_view(), name='load_model'),
]
