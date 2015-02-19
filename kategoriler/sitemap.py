# -*- coding: utf-8 -*-


import datetime

from django.contrib.sitemaps import Sitemap


class UrunlerSiteMap( Sitemap ):
	changefreq = "weekly"
	priority = 0.5



	def items( self ):
		return Urun.objects.all( )



	def lastmod( self, obj ):
		return datetime.datetime.now( )
