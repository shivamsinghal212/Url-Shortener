from django.urls import path, re_path, include
from basicapp import views
from rest_framework.authtoken import views as vs
from django.contrib.auth.decorators import login_required

# router = DefaultRouter()S
# router.register('create', views.CreateAPI,base_name='create')

urlpatterns=[
        path('',views.shorten,name='shorten'),
        path('home/',views.auth,name='auth'),
        path('verify/',views.verify,name='verify'),
        path('logout/', views.logout_user, name='logout'),
        path('create/',login_required(views.CreateAPI.as_view(),login_url='/home/'),name='create'),
        re_path(r'^(?P<URLid>[0-9a-zA-Z]+)/$',views.target,name='target')
]

urlpatterns += [
    path('api-token-auth/', vs.obtain_auth_token)
]
