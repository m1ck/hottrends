from django.conf.urls.defaults import *
from app.views import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #important general shit
    (r'^admin/', include(admin.site.urls)),
    (r'media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    #(r'image_handler/(.+)/(.+)/(.+)$', image_handler),

    #standard pages    
    (r'^$', index),    
    (r'^about/$', about),
    (r'^resources/$', resources),
    (r'^tutorial/$', tutorial),
    (r'^guestbook/$', guestbook),
    (r'^django/$', django),
    (r'^nltkshow/$', nltkshow),
    (r'^twitgraph/$', twitgraph),
    (r'^nltksentiment/$', nltksentiment),
    
    
    #guestbook stuff
    #(r'^login/$', login),
    #(r'^signup/$', signup),
    #(r'^loggedin/$', loggedin),
    #(r'^logout/$', logout),
    #(r'^upload/$', upload_files),
    #(r'^img_uploader/$', myFileHandler)
    )
