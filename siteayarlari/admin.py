# -*- coding: utf-8 -*-

from django.contrib import admin

from siteayarlari.models import SayfayaOzelIcerik, Blog, BlogKategoriler, SubDomainYonlendir, Banner, GeriBildirimler, IndirimBalonu, Aramalar, Yonlendirmeler, GuncelXMLFirma, Sayfa2SMSArsiv, Sayfa2SMS


class GeriBildirimlerAdmin( admin.ModelAdmin ):
	list_display = ('IsimSoyisim', 'Email', 'Mesaj', 'IslemZamani')
	search_fields = ['IsimSoyisim', 'Email']


def kopyala( modeladmin, request, queryset ):
	for object in queryset:
		object.id = None
		object.save( )


kopyala.short_description = "Aynısını tekrar oluştur"


class SayfayaOzelIcerikAdmin( admin.ModelAdmin ):
	list_display = ('URL', 'BaslamaZamani', 'BitirmeZamani')
	search_fields = ['URL']
	search_fields_verbose = ['URL', ]
	actions = [kopyala, ]
# ~ class Media:
# ~ js = [
#~ '/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
#~ '/static/grappelli/tinymce_setup/tinymce_setup.js',
#~ ]


class BlogAdmin( admin.ModelAdmin ):
	list_display = ('Baslik', 'Aciklama', 'Etiket', 'BaslamaZamani', 'BitirmeZamani')
	search_fields = ['Baslik', 'Aciklama', 'Etiket']
	prepopulated_fields = { "Slug": ("Baslik",) }


	class Media:
		js = ['/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js', '/static/grappelli/tinymce_setup/tinymce_setup.js', ]


class BlogKategorilerAdmin( admin.ModelAdmin ):
	list_display = ('Adi', )
	search_fields = ['Adi']
	prepopulated_fields = { "Slug": ("Adi",) }


class SubDomainYonlendirAdmin( admin.ModelAdmin ):
	list_display = ('Ne', 'Nereye')
	search_fields = ['Nere', 'Nereye']


class BannerAdmin( admin.ModelAdmin ):
	list_display = ('ResimGoster', 'Yerlesim', 'Sira', 'Aktif', 'Baslik', 'Link', 'BaslamaZamani', 'BitirmeZamani', )


class IndirimBalonuAdmin( admin.ModelAdmin ):
	list_display = ( 'Baslik', 'Aktif',)
	search_fields = ['Baslik']


	class Media:
		js = ['/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js', '/static/grappelli/tinymce_setup/tinymce_setup.js', ]


class AramalarAdmin( admin.ModelAdmin ):
	list_display = ('Aranan', 'IP', 'Sonuc', 'Cihaz', 'IslemTarihi', 'UyeID')
	search_fields = ['Aranan']


class GuncelXMLFirmaAdmin( admin.ModelAdmin ):
	list_display = ('IP', 'Sorgu', 'Firma', 'IslemTarihi')
	search_fields = ['Firma']


class SosyalGoster( admin.SimpleListFilter ):
	title = (u'Sosyal Ağlar')
	parameter_name = u'sg'



	def lookups( self, request, model_admin ):
		return (
		('fs', (u'Facebook Site')), ('fm', (u'Facebook Mobil')), ('ts', (u'Twitter Site')), ('tm', (u'Twitter Mobil')),
		)



	def queryset( self, request, queryset ):

		if self.value( ) == 'fs':
			return queryset.filter( YonlendirenLink__icontains = 'www.facebook.com' )

		if self.value( ) == 'fm':
			return queryset.filter( YonlendirenLink__icontains = 'm.facebook.com' )

		if self.value( ) == 'ts':
			return queryset.filter( YonlendirenLink__icontains = 'www.twitter.com' )

		if self.value( ) == 'tm':
			return queryset.filter( YonlendirenLink__icontains = 'm.twitter.com' )


class DetayliArama( admin.SimpleListFilter ):
	title = (u'Detaylı Arama')
	parameter_name = u'da'



	def lookups( self, request, model_admin ):
		return (
		('yl', (u'Yönlendiren Link')), ('ys', (u'Yönlendirilen Sayfa')),
		)



	def queryset( self, request, queryset ):

		if self.value( ) == 'ys':
			return queryset.filter( YonlendirilenSayfa__icontains = request.GET.get( 'q', '' ) )

		if self.value( ) == 'yl':
			return queryset.filter( YonlendirenLink__icontains = request.GET.get( 'q', '' ) )


class YonlendirmelerAdmin( admin.ModelAdmin ):
	list_display = ('IslemTarihi', 'IPFiltre', 'UyeID', 'YonlendirenLinkClick', 'YonlendirilenSayfaClick', 'IPClick', 'Aygit', 'Sehir')
	list_filter = (SosyalGoster, DetayliArama, 'Aygit', 'Sehir', 'UyeID', )
	search_fields = ['UyeID', 'YonlendirenLink', 'YonlendirilenSayfa', 'IP']
	ordering = ['-IslemTarihi', ]
	date_hierarchy = 'IslemTarihi'



	def IPFiltre( self, obj ):
		return "<a href='?o=6&q=" + str( obj.IP ) + "'>" + str( obj.IP ) + "</a>"



	def IPClick( self, obj ):
		return "<a href='http://whatismyipaddress.com/ip/" + str( obj.IP ) + "'>" + str( obj.IP ) + "</a>"



	def YonlendirenLinkClick( self, obj ):
		return "<a href='" + obj.YonlendirenLink + "'>" + obj.YonlendirenLink + "</a>"



	def YonlendirilenSayfaClick( self, obj ):
		return "<a href='" + str( obj.YonlendirilenSayfa.encode( 'utf8' ) ) + "'>" + str( obj.YonlendirilenSayfa.encode( 'utf8' ) ) + "</a>"



	# return '<meta http-equiv="refresh" content="1">'

	IPFiltre.allow_tags = True
	IPFiltre.short_description = 'IP Geçmişi'
	IPClick.allow_tags = True
	IPClick.short_description = 'IP Bilgisi'
	YonlendirenLinkClick.allow_tags = True
	YonlendirenLinkClick.short_description = 'Yönlendiren Link'
	YonlendirilenSayfaClick.allow_tags = True
	YonlendirilenSayfaClick.short_description = 'Yönlendirilen Sayfa'


class Sayfa2SMSArsivAdmin( admin.ModelAdmin ):
	list_display = ('UUrl', 'Url', 'Telefon', 'Durum', 'IP', 'IslemTarihi' )
	search_fields = ['Url', 'UUrl', 'Telefon', 'Durum']
	list_filter = ('Durum', 'Url', 'IP')
	ordering = ['-IslemTarihi', ]
	date_hierarchy = 'IslemTarihi'


class Sayfa2SMSAdmin( admin.ModelAdmin ):
	list_display = ('Metin', 'Limit' )
	search_fields = ['Metin']


admin.site.register( Yonlendirmeler, YonlendirmelerAdmin )
admin.site.register( Aramalar, AramalarAdmin )
admin.site.register( Blog, BlogAdmin )
admin.site.register( SubDomainYonlendir, SubDomainYonlendirAdmin )
admin.site.register( BlogKategoriler, BlogKategorilerAdmin )
admin.site.register( SayfayaOzelIcerik, SayfayaOzelIcerikAdmin )
admin.site.register( Banner, BannerAdmin )
admin.site.register( GeriBildirimler, GeriBildirimlerAdmin )
admin.site.register( IndirimBalonu, IndirimBalonuAdmin )
admin.site.register( GuncelXMLFirma, GuncelXMLFirmaAdmin )
admin.site.register( Sayfa2SMSArsiv, Sayfa2SMSArsivAdmin )
admin.site.register( Sayfa2SMS, Sayfa2SMSAdmin )
