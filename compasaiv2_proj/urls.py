from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect

handler404 = 'compasaiv2_app.views.error_404'  
handler500 = 'compasaiv2_app.views.error_500'  
def redirect_to_google_signup(request):
    return redirect('/accounts/google/login/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('compasaiv2_app.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('accounts/', include('allauth.urls')), 
    path('logout', LogoutView.as_view()) 
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + \
              static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
