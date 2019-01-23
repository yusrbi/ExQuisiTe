from django.conf.urls import  url 
from . import views 
app_name='demo'
urlpatterns=[

	url(r'^$',views.select_input, name='select_input'),
    #url(r'^select_input$', views.select_input, name="select_input"),
    url(r'^text_input$', views.process_plain_text, name="process_plain_text"),
    url(r'^file_input$', views.process_file, name="process_file"),
    url(r'^url_input$', views.process_url, name="process_url"),
]

