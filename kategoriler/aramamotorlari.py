import urlparse
import re


class AramaMotorlariMiddleware( object ):
	"""
	request.search_referrer_engine
	request.search_referrer_domain
	request.search_referrer_term

	Usage example:
	==============
	Show ads only to visitors coming from a searh engine

	{% if request.search_referrer_engine %}
		html for ads...
	{% endif %}
	"""
	SEARCH_PARAMS = { 'AltaVista': 'q', 'Ask': 'q', 'Google': 'q', 'Live': 'q', 'Lycos': 'query', 'MSN': 'q', 'Yahoo': 'p', 'Cuil': 'q', }

	NETWORK_RE = r"""^
        (?P<subdomain>[-.a-z\d]+\.)?
        (?P<engine>%s)
        (?P<top_level>(?:\.[a-z]{2,3}){1,2})
        (?P<port>:\d+)?
        $(?ix)"""



	@classmethod
	def parse_search( cls, url ):
		try:
			parsed = urlparse.urlsplit( url )
			network = parsed[1]
			query = parsed[3]
		except (AttributeError, IndexError):
			return (None, None, None)
		for engine, param in cls.SEARCH_PARAMS.iteritems( ):
			match = re.match( cls.NETWORK_RE % engine, network )
			if match and match.group( 2 ):
				term = urlparse.parse_qs( query ).get( param )
				if term and term[0]:
					term = ' '.join( term[0].split( ) ).lower( )
					return (engine, network, term)
		return (None, network, None)



	def process_request( self, request ):
		referrer = request.META.get( 'HTTP_REFERER' )
		engine, domain, term = self.parse_search( referrer )
		request.search_referrer_engine = engine
		request.search_referrer_domain = domain
		request.search_referrer_term = term
