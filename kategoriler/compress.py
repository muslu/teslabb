import re

from django.utils.html import strip_spaces_between_tags
from django.conf import settings
from django.core.mail import mail_managers




RE_MULTISPACE = re.compile( r"\s{2,}" )
RE_NEWLINE = re.compile( r"\n" )


class MinifyHTMLMiddleware( object ):
	def process_response( self, request, response ):

		if not "admin" in request.path and 'text/html' in response['Content-Type'] and settings.COMPRESS_HTML:

			response.content = strip_spaces_between_tags( response.content.strip( ) )
			response.content = RE_MULTISPACE.sub( " ", response.content )
			response.content = RE_NEWLINE.sub( "", response.content )

		return response


class BrokenLinkEmailsMiddleware( object ):
	def process_response( self, request, response ):
		if response.status_code == 404 and not settings.DEBUG:
			domain = request.get_host( )
			path = request.get_full_path( )
			referer = request.META.get( 'HTTP_REFERER', 'None' )
			is_not_search_engine = '?' not in referer
			is_ignorable = self.is_ignorable_404( path )
			if is_not_search_engine and not is_ignorable:
				ua = request.META.get( 'HTTP_USER_AGENT', '<none>' )
				ip = request.META.get( 'REMOTE_ADDR', '<none>' )
				mail_managers( "Bulunamayan URL %s" % domain, "Yonlendiren: %s\nURL: %s\nUser agent: %s\nIP: %s\n" % (referer, path, ua, ip), fail_silently = True )
		return response



	def is_ignorable_404( self, uri ):
		return any( pattern.search( uri ) for pattern in settings.IGNORABLE_404_URLS )
