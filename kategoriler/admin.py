# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db.models import Sum
from django.forms import *
from django.db import models
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from kategoriler.models import Kategori, OrtaKategori, AltKategori, Marka, Urun, Varyant, BenzerKategoriler, BenzerUrunler, Cinsiyet, MarkaAltKatAciklama, ServisDurumu
from uyeler.models import SepetUrunler


class MarkaAdmin( admin.ModelAdmin ):
	list_display = ('Logoyu_Goster', 'id', 'Adi', 'Aciklama')
	prepopulated_fields = { "Slug": ("Adi",) }


admin.site.register( Marka, MarkaAdmin )


class MarkaAltKatAciklamaAdmin( admin.ModelAdmin ):
	list_display = ('Marka', 'Aciklama',)


admin.site.register( MarkaAltKatAciklama, MarkaAltKatAciklamaAdmin )


class CinsiyetAdmin( admin.ModelAdmin ):
	list_display = ('Adi', 'LogoLink', 'Logoyu_Goster')
	prepopulated_fields = { "Slug": ("Adi",) }


admin.site.register( Cinsiyet, CinsiyetAdmin )


class KategoriAdmin( admin.ModelAdmin ):
	list_display = ('id', 'Cinsiyet', 'Adi', 'MetaAciklama', 'Logoyu_Goster')
	list_filter = ('Cinsiyet', 'Adi')
	prepopulated_fields = { "Slug": ("Adi",) }
	ordering = ['Cinsiyet', 'Adi']


admin.site.register( Kategori, KategoriAdmin )


class OrtaKategoriAdmin( admin.ModelAdmin ):
	list_display = ('id', 'UstKategorisi', 'Adi', 'MetaAciklama', 'MetaEtiket')
	list_filter = ('UstKat__Cinsiyet', 'UstKat__Adi', 'Adi',)
	prepopulated_fields = { "Slug": ("Adi",) }
	search_fields = ['Adi']


admin.site.register( OrtaKategori, OrtaKategoriAdmin )


class AltKategoriAdmin( admin.ModelAdmin ):
	list_display = ('UstKat', 'OrtaKategorisi', 'Adi', 'Aciklama', 'Oncelik', 'Bolge')
	list_filter = ('UstKat', 'OrtaKat', 'Oncelik', 'Bolge')
	prepopulated_fields = { "Slug": ("Adi",) }
	search_fields = ['Adi']
	ordering = ('UstKat', 'OrtaKat')


admin.site.register( AltKategori, AltKategoriAdmin )


class VaryantInline( admin.TabularInline ):
	model = Varyant
	formfield_overrides = { models.CharField: { 'widget': TextInput( ) }, }
	fields = ('id', 'VaryantOlanSubeleriGosteer', 'StokSayisi', 'Renk', 'Beden', 'Kavala', 'Cinsiyet', 'Barkod', 'EkstraFiyat', 'UcBoyutlu', 'Logo1', 'Logo2', 'Logo3', 'Logo4', 'Logo5', 'AltKat', 'Defolu')
	extra = 1
	ordering = ['Renk']
	readonly_fields = ('VaryantOlanSubeleriGosteer', 'id')


def yeniurune_tasi( modeladmin, request, queryset ):
	queryset.update( Yeni = 1 )


yeniurune_tasi.short_description = "Seçili ürünleri Yeni olarak işaretle"


def yeniurunden_kaldir( modeladmin, request, queryset ):
	queryset.update( Yeni = 0 )


yeniurunden_kaldir.short_description = "Seçili ürünleri Yeni Ürünlerden kaldır"


def vitrine_tasi( modeladmin, request, queryset ):
	queryset.update( Vitrin = 1 )


vitrine_tasi.short_description = "Seçili ürünleri Vitrine koy"


def vitrinden_kaldir( modeladmin, request, queryset ):
	queryset.update( Vitrin = 0 )


vitrinden_kaldir.short_description = "Seçili ürünleri Vitrinden kaldır"


def firsata_tasi( modeladmin, request, queryset ):
	queryset.update( Firsat = 1 )


firsata_tasi.short_description = "Seçili ürünleri Fırsat ürünü yap"


def firsattan_kaldir( modeladmin, request, queryset ):
	queryset.update( Firsat = 0 )


firsattan_kaldir.short_description = "Seçili ürünleri Fırsat ürünlerinden kaldır"


def outlete_tasi( modeladmin, request, queryset ):
	queryset.update( Outlet = 1 )


outlete_tasi.short_description = "Seçili ürünleri Outlete taşı"


def outletten_kaldir( modeladmin, request, queryset ):
	queryset.update( Outlet = 0 )


outletten_kaldir.short_description = "Seçili ürünleri Outletten kaldır"


def haftaninurunune_tasi( modeladmin, request, queryset ):
	queryset.update( HaftaninUrunu = 1 )


haftaninurunune_tasi.short_description = "Seçili ürünleri Haftanın ürünü yap"


def defoluurune_tasi( modeladmin, request, queryset ):
	queryset.update( Defolu = 1 )


defoluurune_tasi.short_description = "Seçili ürünleri Defolu ürün yap"


def defoluurunu_kaldir( modeladmin, request, queryset ):
	queryset.update( Defolu = 0 )


defoluurunu_kaldir.short_description = "Seçili ürünleri Defolu üründen kaldır"


def encoksatilana_tasi( modeladmin, request, queryset ):
	queryset.update( EnCokSatan = 1 )


encoksatilana_tasi.short_description = "Seçili ürünleri En Çok Satılanlara ekle"


def varyantlari_altkat_idye_tasi( modeladmin, request, queryset ):
	from django.db import connection




	cursor = connection.cursor( )

	for oo in queryset:

		for ooo in oo.AltKat.all( ):

			for i in Varyant.objects.filter( Urunu_id = oo.id ):

				# ~ print "INSERT INTO Django.dbo.kategoriler_varyant_AltKat (varyant_id, altkategori_id) VALUES('" + str(i.id) + "', '" + str(ooo.id) + "');"

				cursor.execute( "if exists(select * from Django.dbo.kategoriler_varyant_AltKat where varyant_id = '" + str( i.id ) + "' and altkategori_id = '" + str( ooo.id ) + "') DELETE FROM Django.dbo.kategoriler_varyant_AltKat WHERE varyant_id = '" + str( i.id ) + "'; else INSERT INTO Django.dbo.kategoriler_varyant_AltKat (varyant_id, altkategori_id) VALUES('" + str( i.id ) + "', '" + str( ooo.id ) + "');" );



			# ~ Cts 18 Oca 2014 14:10:13 EET  - Muslu YÜKSEKTEPE


varyantlari_altkat_idye_tasi.short_description = "Seçili ürünlerin varyantlarını düzenle"
# ~ 31.12.2013 18:20:58


def haftaninurununden_kaldir( modeladmin, request, queryset ):
	queryset.update( HaftaninUrunu = 0 )


haftaninurununden_kaldir.short_description = "Seçili ürünleri Haftanın üründen kaldır"


def FotoKontrol( dosyayolu ):
	import os
	from django.conf import settings




	return os.path.isfile( str( settings.__getattr__( "BASE_DIR" ) ) + "/media/" + str( dosyayolu ) )


# ##### Ürünler için özel filtreler ######




class StokluUrunlerUrunler( admin.SimpleListFilter ):
	title = (u'Stoklar')
	parameter_name = u'ss'



	def lookups( self, request, model_admin ):
		return (
		('ts', (u'Tükenen')), ('ks', (u'Kritik')), ('ns', (u'Normal')), ('fs', (u'Fazla')), ('hs', (u'Hatalı')),
		)



	def queryset( self, request, queryset ):

		urun_listesiii = ()

		if self.value( ) == 'ns':
			for i in queryset.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = settings.__getattr__( 'NORMAL_STOK' ) ).order_by( '-id' ):
				if FotoKontrol( i.Logo ):
					urun_listesiii += (str( Urun.objects.get( id = i.id ).id ),)

		elif self.value( ) == 'ks':
			for i in queryset.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = settings.__getattr__( 'KRITIK_STOK' ), ToplamStok_Sayisi__lt = settings.__getattr__( 'NORMAL_STOK' ) ).order_by( '-id' ):
				if FotoKontrol( i.Logo ):
					urun_listesiii += (str( Urun.objects.get( id = i.id ).id ),)

		elif self.value( ) == 'fs':
			for i in queryset.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = settings.__getattr__( 'FAZLA_STOK' ) ).order_by( '-id' ):
				if FotoKontrol( i.Logo ):
					urun_listesiii += (str( Urun.objects.get( id = i.id ).id ),)

		elif self.value( ) == 'ts':
			for i in queryset.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi = 0 ).order_by( '-id' ):
				if FotoKontrol( i.Logo ):
					urun_listesiii += (str( Urun.objects.get( id = i.id ).id ),)

		elif self.value( ) == "hs":
			for i in queryset.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi = None ).order_by( '-id' ):
				if FotoKontrol( i.Logo ):
					urun_listesiii += (str( Urun.objects.get( id = i.id ).id ),)

		else:
			for i in queryset.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0 ).order_by( '-id' ):
				urun_listesiii += (str( Urun.objects.get( id = i.id ).id ),)

		return queryset.filter( id__in = urun_listesiii )


class SadeceFotografsizUrunler( admin.SimpleListFilter ):
	title = u'Fotoğrafsızlar'
	parameter_name = u'f'



	def lookups( self, request, model_admin ):
		return (
		('fl', (u'Göster')), ('ry', (u'ResimYok')),
		)



	def queryset( self, request, queryset ):

		if self.value( ) == 'fl':
			urun_listesiii = ()

			for i in queryset:

				if not FotoKontrol( i.Logo ):
					urun_listesiii += (str( Urun.objects.get( id = i.id ).id ),)

			return queryset.filter( id__in = urun_listesiii )

		if self.value( ) == 'ry':
			urun_listesiii = ()

			for i in queryset:
				if i.Logo == "urun_resimleri/ResimYok.jpg":
					urun_listesiii += (str( Urun.objects.get( id = i.id ).id ),)
			return queryset.filter( id__in = urun_listesiii )


class MarkasizUrunler( admin.SimpleListFilter ):
	title = (u'Markasızlar')
	parameter_name = u'm'



	def lookups( self, request, model_admin ):
		return (
		('ml', (u'Göster')),
		)



	def queryset( self, request, queryset ):

		if self.value( ) == 'ml':
			urun_listesiii = ()

			for i in queryset:
				try:
					Markasi = i.Marka.Adi
				except:
					urun_listesiii += (str( Urun.objects.get( id = i.id ).id ),)

			return queryset.filter( id__in = urun_listesiii )


class IndirimlisizUrunler( admin.SimpleListFilter ):
	title = (u'İndirim')
	parameter_name = u'i'



	def lookups( self, request, model_admin ):
		return (
		('ili', (u'İndirimli')), ('isiz', (u'İndirimsiz')),
		)



	def queryset( self, request, queryset ):

		if self.value( ) == 'ili':
			urun_listesiii = ()
			for i in queryset:
				if i.EFiyat > i.Fiyat:
					urun_listesiii += (str( Urun.objects.get( id = i.id ).id ),)
			return queryset.filter( id__in = urun_listesiii )

		if self.value( ) == 'isiz':
			urun_listesiii = ()
			for i in queryset:
				if i.EFiyat <= i.Fiyat:
					urun_listesiii += (str( Urun.objects.get( id = i.id ).id ),)
			return queryset.filter( id__in = urun_listesiii )


# ##### Ürünler iin özel filtreler ######


def export_xls( modeladmin, request, queryset ):
	import xlwt




	response = HttpResponse( mimetype = 'application/ms-excel' )
	response['Content-Disposition'] = 'attachment; filename=GenelRapor.xls'
	wb = xlwt.Workbook( encoding = 'utf-8' )
	ws = wb.add_sheet( "Sayfa" )

	row_num = 0

	columns = [(u"StokKodu", 6000), (u"Marka", 8000), (u"Stok Sayısı", 4000), ]

	font_style = xlwt.XFStyle( )
	font_style.font.bold = True

	for col_num in xrange( len( columns ) ):
		ws.write( row_num, col_num, columns[col_num][0], font_style )
		ws.col( col_num ).width = columns[col_num][1]

	font_style = xlwt.XFStyle( )
	font_style.alignment.wrap = 1

	for obj in queryset:
		row_num += 1
		row = [obj.StokKodu, obj.Marka.Adi, obj.varyant__StokSayisi__sum]
		for col_num in xrange( len( row ) ):
			ws.write( row_num, col_num, row[col_num], font_style )

	wb.save( response )
	return response


export_xls.short_description = u"XLS Çıkart"


def google_merchant( modeladmin, request, queryset ):
	urun_listesi = Urun.objects.values_list( 'id' ).annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( '-id' )

	urlset = Varyant.objects.filter( Urunu__id__in = urun_listesi )

	return render_to_response( 'sitemapD.xml', { 'urlset': urlset, }, context_instance = RequestContext( request ), mimetype = "application/xml" )


google_merchant.short_description = u"Google Merchant"


class UrunAdmin( admin.ModelAdmin ):
	list_display = ('Logoyu_Goster', 'AltKategorisi', 'StokKodu', 'Marka', 'Adi', 'Tarih', 'Fiyat', 'EFiyat', 'Vitrin', 'Defolu', 'Outlet', 'Firsat', 'HaftaninUrunu', 'Yeni', 'Guncelle', 'Varyanttoplam_stok_sayisi', 'SepeteAtilmaSayisi')
	prepopulated_fields = { "Slug": ("Adi",) }
	search_fields = ['StokKodu', 'Marka__Adi', 'Adi']
	list_per_page = 30
	inlines = (VaryantInline,)
	actions = [yeniurune_tasi, vitrine_tasi, firsata_tasi, outlete_tasi, outletten_kaldir, haftaninurunune_tasi, haftaninurununden_kaldir, defoluurune_tasi, defoluurunu_kaldir, encoksatilana_tasi, yeniurunden_kaldir, vitrinden_kaldir, firsattan_kaldir, varyantlari_altkat_idye_tasi, export_xls, google_merchant]
	filter_horizontal = ('AltKat',)
	actions_on_top = True
	ordering = ['-id']

	# list_filter = (StokluUrunlerUrunler, VitrinIcinUrunler, SadeceFotografsizUrunler, MarkasizUrunler, IndirimlisizUrunler, 'UstKat__Adi', 'UstKat__Cinsiyet__Adi', 'Marka',)
	list_filter = (MarkasizUrunler, IndirimlisizUrunler, 'UstKat__Adi', 'UstKat__Cinsiyet__Adi', 'Marka', SadeceFotografsizUrunler)
	# ~ Çrş 15 Oca 2014 15:18:45 EET  - Muslu YÜKSEKTEPE
	# ~ change_list_template = "admin/change_list_filter_sidebar.html"

	class Media:
		js = ('/static/tiny_mce/tiny_mce.js', '/static/textareas.js')


	def queryset( self, request ):
		qs = super( UrunAdmin, self ).queryset( request )
		qss = qs.annotate( models.Sum( 'varyant__StokSayisi' ) )
		return qss



	def Varyanttoplam_stok_sayisi( self, obj ):
		return obj.varyant__StokSayisi__sum



	def SepeteAtilmaSayisi( self, obj ):

		Barkod_Liste = Varyant.objects.values_list( 'id' ).filter( Urunu__id = obj.id )

		ii = 0

		for i in SepetUrunler.objects.filter( VaryantID__in = Barkod_Liste ):
			ii += i.Adet

		return ii



	Varyanttoplam_stok_sayisi.admin_order_field = 'varyant__StokSayisi__sum'
	Varyanttoplam_stok_sayisi.short_description = 'Stok Sayısı'

	SepeteAtilmaSayisi.short_description = 'Sepete Atılma'


admin.site.register( Urun, UrunAdmin )


class BenzerKategorilerAdmin( admin.ModelAdmin ):
	list_display = ('AltKat', 'BenzerKat_Adlari')
	search_fields = ['AltKat__Adi', 'BenzerKat__Adi']
	list_per_page = 50



	def BenzerKat_Adlari( self, obj ):

		altkate = ""

		for ii in [p.id for p in obj.BenzerKat.all( )]:

			altkate += str( AltKategori.objects.get( id = ii ) ) + " ,"

		return altkate


admin.site.register( BenzerKategoriler, BenzerKategorilerAdmin )


class BenzerUrunlerAdmin( admin.ModelAdmin ):
	list_display = ('Urun_Adlari', 'BenzerUrun_Adlari')
	search_fields = ['urun__Adi', ]
	list_per_page = 150
	filter_horizontal = ('eslesenurun',)
	raw_id_fields = ("urun",)



	def formfield_for_foreignkey( self, db_field, request, **kwargs ):

		if db_field.name == "urun":
			kwargs["queryset"] = Urun.objects.filter( AltKat__id__isnull = False, ).order_by( 'Marka', 'StokKodu' )
		return super( self.__class__, self ).formfield_for_foreignkey( db_field, request, **kwargs )



	def formfield_for_manytomany( self, db_field, request, **kwargs ):

		if db_field.name == "eslesenurun":
			kwargs["queryset"] = Urun.objects.filter( AltKat__id__isnull = False ).order_by( 'Marka', 'StokKodu' )
		return super( self.__class__, self ).formfield_for_manytomany( db_field, request, **kwargs )



	def Urun_Adlari( self, obj ):

		esurun = ""

		for ii in [p.id for p in obj.urun.all( )]:

			esurun += str( Urun.objects.get( id = ii ) ) + " ,"

		return esurun



	def BenzerUrun_Adlari( self, obj ):

		esurun = ""

		for ii in [p.id for p in obj.eslesenurun.all( )]:

			esurun += str( Urun.objects.get( id = ii ) ) + " ,"

		return esurun


admin.site.register( BenzerUrunler, BenzerUrunlerAdmin )


class ServisDurumuAdmin( admin.ModelAdmin ):
	list_display = ('Servis', 'Gun', 'IslemTarihi', 'BitisTarihi', 'Calisiyor', 'Tamamlandi', 'IP')
	list_filter = ('Tamamlandi',)
	search_fields = ['Sorgu']
	date_hierarchy = 'IslemTarihi'
	actions_on_top = True


admin.site.register( ServisDurumu, ServisDurumuAdmin )
