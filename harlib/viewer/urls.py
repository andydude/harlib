from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    'harlib.viewer.views',
    url(r'^$', 'index'),
)
