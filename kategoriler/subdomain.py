# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.conf import settings

from siteayarlari.models import SubDomainYonlendir


class SubdomainMiddleware:
	def process_request( self, request ):

		domain_parts = request.get_host( ).split( '.' )

		if (len( domain_parts ) > 2):

			subdomain = domain_parts[0]

			if (subdomain.isdigit( )):
				domain = None
				subdomain = None

			else:

				if (subdomain.lower( ) == 'www'):
					subdomain = None
				domain = '.'.join( domain_parts[1:] )

		else:
			subdomain = None
			domain = request.get_host( )

		if subdomain is not None:

			try:

				YonlendirmeOku = SubDomainYonlendir.objects.get( Ne = subdomain )

				return HttpResponseRedirect( str( settings.DOMAIN ) + str( YonlendirmeOku.Nereye ) )

			except:
				return HttpResponseRedirect( "/" )

		request.subdomain = subdomain
		request.domain = domain

