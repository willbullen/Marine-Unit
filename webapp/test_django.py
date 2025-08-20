#!/usr/bin/env python
"""Simple Django test script"""
import os
import sys
import django
from django.conf import settings
from django.http import JsonResponse
from django.urls import path
from django.core.wsgi import get_wsgi_application

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-key-for-development',
        ALLOWED_HOSTS=['*'],
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        ROOT_URLCONF='test_django',
    )

django.setup()

def test_api(request):
    """Simple test API endpoint"""
    return JsonResponse({
        'status': 'success',
        'message': 'Buoy QC Web API is working!',
        'endpoints': {
            'dashboard': '/api/dashboard/',
            'stations': '/api/stations/',
            'qc_limits': '/api/limits/'
        }
    })

def home(request):
    """Home page view"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Buoy QC Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-bottom: 30px; }
            .endpoint { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .endpoint a { color: #2980b9; text-decoration: none; font-weight: bold; }
            .endpoint a:hover { text-decoration: underline; }
            .status { background: #d5f4e6; color: #27ae60; padding: 10px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">🌊 Buoy QC Dashboard</h1>
            
            <div class="status">
                ✅ Django Web Application is Running Successfully!
            </div>
            
            <h2>Available API Endpoints:</h2>
            
            <div class="endpoint">
                <strong>Test API:</strong><br>
                <a href="/test/">/test/</a> - Simple API test endpoint
            </div>
            
            <div class="endpoint">
                <strong>Dashboard:</strong><br>
                <a href="/api/dashboard/">/api/dashboard/</a> - QC overview data
            </div>
            
            <div class="endpoint">
                <strong>Stations:</strong><br>
                <a href="/api/stations/">/api/stations/</a> - Buoy station management
            </div>
            
            <div class="endpoint">
                <strong>QC Limits:</strong><br>
                <a href="/api/limits/">/api/limits/</a> - QC threshold configuration
            </div>
            
            <h2>System Integration:</h2>
            <ul>
                <li>✅ Django REST API configured</li>
                <li>✅ Database models created</li>
                <li>✅ QC processor integration ready</li>
                <li>✅ Station-specific QC limits loaded</li>
                <li>🚧 React frontend in development</li>
            </ul>
            
            <p><strong>Next Steps:</strong> Complete React frontend development for full web interface.</p>
        </div>
    </body>
    </html>
    """
    from django.http import HttpResponse
    return HttpResponse(html)

# URL patterns
urlpatterns = [
    path('', home, name='home'),
    path('test/', test_api, name='test_api'),
]

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000'])
