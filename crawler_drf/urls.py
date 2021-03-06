"""crawler_drf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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

from acts import views as acts_view
from executors import views as executors_view
from art_purchase_orgs import views as art_purchase_orgs_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('acts/', acts_view.ActView.as_view()),
    path('executors/', executors_view.ExecutorView.as_view()),
    path('art-purchase-orgs/', art_purchase_orgs_view.ArtPurchaseOrgView.as_view())
]
