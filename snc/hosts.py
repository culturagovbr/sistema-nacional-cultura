from django_hosts import patterns, host

host_patterns = patterns('',
   host(r'www','snc.urls', name='www'),
   host(r'api', 'api.urls', name='api'),
)

