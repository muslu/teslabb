# -*- coding: utf-8 -*-



# ## SporMarket

from decimal import Decimal
import datetime
import json
import operator
import os
import urllib2
import sys
from dircache import listdir
from math import floor
from random import randint

from django.conf import settings
from django.db import connections
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import F, Q, Sum
from django.template.defaultfilters import slugify
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import resolve
from django.core.mail import EmailMultiAlternatives

from kategoriler.models import OrtaKategori, AltKategori, Marka, Urun, Varyant, Cinsiyet, ServisDurumu, BenzerUrunler
from kategoriler.templatetags.HtmlEtiketler import FotoKontrol
from siteayarlari.models import Banner, Aramalar, GuncelXMLFirma
from bankalar.models import Bankalar
from uyeler.models import SepetUrunler, Sepet, Kullanicilar



# 25.12.2014 09:48:19#      -  Muslu YÜKSEKTEPE



def AnaSayfa( request ):
	# encoksatilan_listesi        =       Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0, Firsat=1, AltKat__id__isnull=False, varyant__AltKat__id__isnull=False).exclude(Defolu = True, Logo="urun_resimleri/ResimYok.jpg" ).order_by('?')[0:15]

	try:
		UyeID = Kullanicilar.objects.get( user = request.user ).uyeid
	except:
		UyeID = request.COOKIES.get( 'UyeID' )
		if not UyeID:
			UyeID = randint( 1000000, 9999999 )

	indirimli_urun_listesii = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 2, Fiyat__lt = F( 'EFiyat' ) ).exclude( Defolu = 1 ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( 'Fiyat' )[0:8]
	BulunanIDler = ()

	for i in indirimli_urun_listesii:
		if FotoKontrol( i.Logo ):
			BulunanIDler += (str( Urun.objects.get( id = i.id ).id ),)

	indirimli_urun_listesi = Urun.objects.values_list( 'id', 'Adi', 'StokKodu', 'Logo', 'Logo2', 'Logo3', 'Logo4', 'Logo5', 'Slug', 'Yeni', 'Firsat', 'Fiyat', 'EFiyat', 'Marka__Adi', 'Marka_id' ).filter( id__in = BulunanIDler )

	yeni_urun_listesii = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 1 ).exclude( Defolu = 1 ).exclude( Vitrin = 1 ).exclude( Fiyat__lt = F( 'EFiyat' ) ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( '-id' )[0:90]
	BulunanIDler = ()

	for i in yeni_urun_listesii:
		if FotoKontrol( i.Logo ):
			BulunanIDler += (str( Urun.objects.get( id = i.id ).id ),)

	yeni_urun_listesi = Urun.objects.values_list( 'id', 'Adi', 'StokKodu', 'Logo', 'Logo2', 'Logo3', 'Logo4', 'Logo5', 'Slug', 'Yeni', 'Firsat', 'Fiyat', 'EFiyat', 'Marka__Adi', 'Marka_id' ).filter( id__in = BulunanIDler ).order_by( '-id' )[0:90]

	outlet_urun_listesii = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__lte = 2, ToplamStok_Sayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( '-id' )[0:30]
	BulunanIDler = ()

	for i in outlet_urun_listesii:
		if FotoKontrol( i.Logo ):
			BulunanIDler += (str( Urun.objects.get( id = i.id ).id ),)

	outlet_urun_listesi = Urun.objects.values_list( 'id', 'Adi', 'StokKodu', 'Logo', 'Logo2', 'Logo3', 'Logo4', 'Logo5', 'Slug', 'Yeni', 'Firsat', 'Fiyat', 'EFiyat', 'Marka__Adi', 'Marka_id' ).filter( id__in = BulunanIDler )

	vitrin_urun_listesii = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0, Vitrin = 1 ).exclude( Defolu = 1 ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( '-id' )[0:6]
	BulunanIDler = ()

	for i in vitrin_urun_listesii:
		if FotoKontrol( i.Logo ):
			BulunanIDler += (str( Urun.objects.get( id = i.id ).id ),)

	vitrin_urun_listesi = Urun.objects.values_list( 'id', 'Adi', 'StokKodu', 'Logo', 'Logo2', 'Logo3', 'Logo4', 'Logo5', 'Slug', 'Yeni', 'Firsat', 'Fiyat', 'EFiyat', 'Marka__Adi', 'Marka_id' ).filter( id__in = BulunanIDler )

	SuAn = datetime.datetime.utcnow( ).replace( tzinfo = utc ) + datetime.timedelta( days = 1 )
	banner_liste = Banner.objects.values_list( 'Link', 'Resim', 'Aciklama' ).filter( BaslamaZamani__lt = (SuAn.strftime( '%Y-%m-%d %H:%M:%S' )), BitirmeZamani__gt = (SuAn.strftime( '%Y-%m-%d %H:%M:%S' )), Aktif = True, Yerlesim = 'Ana Sayfa' ).order_by( "-Sira" )[0:6]

	response = render_to_response( 'index.html', { 'banner_liste': banner_liste, 'indirimli_urun_listesi': indirimli_urun_listesi, 'yeni_urun_listesi': yeni_urun_listesi, 'outlet_urun_listesi': outlet_urun_listesi, 'vitrin_urun_listesi': vitrin_urun_listesi }, context_instance = RequestContext( request ) )

	# try:
	# UyeID = Kullanicilar.objects.get( user = request.user ).uyeid
	# except:
	# UyeID = request.COOKIES.get( 'UyeID' )
	#
	response.set_cookie( 'UyeID', UyeID )
	return response


def UrunListesi( request, CinsiyetAdi, KatAdi, Katid ):
	GelenUrl = resolve( request.path_info ).url_name

	# logging.info(GelenUrl)


	try:
		CinsiyetAdi = Cinsiyet.objects.get( Slug = CinsiyetAdi ).Adi.title( )
	except:
		CinsiyetAdi = False

	TemelFiltre = Urun.objects.values_list( 'id', 'Adi', 'StokKodu', 'Logo', 'Logo2', 'Logo3', 'Logo4', 'Logo5', 'Slug', 'Yeni', 'Firsat', 'Fiyat', 'EFiyat', 'Marka__Adi', 'Marka_id' )

	if GelenUrl == "UrunListesiOrtaKat":

		Bulunanlarr = Urun.objects.filter( OrtaKat__id = Katid, varyant__StokSayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( '-id' )

		BulunanIDler = ()

		for i in Bulunanlarr:
			if FotoKontrol( i.Logo ):
				BulunanIDler += (str( Urun.objects.get( id = i.id ).id ),)

		Bulunanlar = TemelFiltre.filter( id__in = BulunanIDler ).distinct( ).order_by( '-id' )

		OrtaKategoriBilgileri = OrtaKategori.objects.get( id = Katid )

		MarkaAdiListesi = []

		for i in Bulunanlar:

			MarkaAdi = i[13]

			if MarkaAdi != None:
				if not MarkaAdi.title( ) in MarkaAdiListesi:
					MarkaAdiListesi.append( MarkaAdi.title( ) )

		MarkaAdiListesi.sort( )

		SayfaBaslik = OrtaKategoriBilgileri.Adi.title( ) + " " + CinsiyetAdi + " " + ', '.join( MarkaAdiListesi[0:7] )
		SayfaAciklama = OrtaKategoriBilgileri.Adi.title( ) + " " + CinsiyetAdi + " " + str( ', ' ).join( MarkaAdiListesi )

		GoogleLink1 = CinsiyetAdi
		GoogleLink2 = OrtaKategoriBilgileri.Adi.title( )
		GoogleLink3 = False
		GoogleLink4 = False

	if GelenUrl == "UrunListesiAltKat":

		Bulunanlarr = Urun.objects.filter( AltKat__id = Katid, varyant__StokSayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( '-id' )

		BulunanIDler = ()

		for i in Bulunanlarr:
			if FotoKontrol( i.Logo ):
				BulunanIDler += (str( Urun.objects.get( id = i.id ).id ),)

		Bulunanlar = TemelFiltre.filter( id__in = BulunanIDler ).distinct( ).order_by( '-id' )

		AltKategoriBilgileri = AltKategori.objects.get( id = Katid )

		MarkaAdiListesi = []

		for i in Bulunanlar:

			MarkaAdi = i[13]

			if MarkaAdi != None:
				if not MarkaAdi.title( ) in MarkaAdiListesi:
					MarkaAdiListesi.append( MarkaAdi.title( ) )

		MarkaAdiListesi.sort( )

		SayfaBaslik = AltKategoriBilgileri.Adi.title( ) + " " + CinsiyetAdi + " " + ', '.join( MarkaAdiListesi[0:7] )
		SayfaAciklama = AltKategoriBilgileri.Adi.title( ) + " " + CinsiyetAdi + " " + str( ', ' ).join( MarkaAdiListesi )

		GoogleLink1 = CinsiyetAdi
		GoogleLink2 = AltKategoriBilgileri.OrtaKat.Adi.title( )
		GoogleLink3 = AltKategoriBilgileri.Adi.title( )
		GoogleLink4 = False

	if GelenUrl == "UrunListesiMarka":

		Bulunanlarr = Urun.objects.filter( Marka__id = Katid, varyant__StokSayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( '-id' )

		BulunanIDler = ()

		for i in Bulunanlarr:
			if FotoKontrol( i.Logo ):
				BulunanIDler += (str( Urun.objects.get( id = i.id ).id ),)

		Bulunanlar = TemelFiltre.filter( id__in = BulunanIDler ).distinct( ).order_by( '-id' )

		Markas = Marka.objects.get( id = Katid )
		Markasi = Markas.Adi
		MarkaSlug = Markas.Slug

		Bulunanlar = Bulunanlar.filter( Marka__Slug = MarkaSlug )

		AltKatBulunanlar = Urun.objects.values_list( 'AltKat__Adi' ).filter( Marka__id = Katid ).exclude( Defolu = 1 ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( )

		AltKategor = []

		for i in AltKatBulunanlar:

			AltKatAdi = i[0]

			if AltKatAdi != None:

				if not AltKatAdi.title( ) in AltKategor:
					AltKategor.append( AltKatAdi.title( ) )

		AltKategor.sort( )

		SayfaBaslik = Markasi.title( ) + " " + ', '.join( AltKategor[0:4] ) + " " + Markasi.upper( )
		SayfaAciklama = Markasi.title( ) + " " + str( ', ' + Markasi.title( ) + ' ' ).join( AltKategor )

		GoogleLink1 = Markasi.title( )

		GoogleLink2 = False
		GoogleLink3 = False
		GoogleLink4 = False

		if Markasi.title( ) == "Adidas":
			GoogleLink2 = "Ayakkabı"
			GoogleLink3 = "Eşofman"
			GoogleLink4 = "Krampon"

		if Markasi.title( ) == "Nike":
			GoogleLink2 = "Ayakkabı"
			GoogleLink3 = "Eşofman"
			GoogleLink4 = "Krampon"

		if Markasi.title( ) == "Levis":
			GoogleLink2 = "Jean Pantolon"
			GoogleLink3 = "Gömlek"
			GoogleLink4 = "Bot"

		if Markasi.title( ) == "Hummel":
			GoogleLink2 = "Ayakkabı"
			GoogleLink3 = "Eşofman"
			GoogleLink4 = "Sweat"

	if GelenUrl == "UrunListesiOutlet":

		Bulunanlarr = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0, ToplamStok_Sayisi__lte = 1 ).exclude( Defolu = 1 ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( '-id' )

		BulunanIDler = ()

		for i in Bulunanlarr:
			if FotoKontrol( i.Logo ):
				BulunanIDler += (str( Urun.objects.get( id = i.id ).id ),)

		Bulunanlar = TemelFiltre.filter( id__in = BulunanIDler ).distinct( ).order_by( '-id' )

		MarkaAdiListesi = []

		for i in Bulunanlar:

			MarkaAdi = i[13]

			if MarkaAdi != None:
				if not MarkaAdi.title( ) in MarkaAdiListesi:
					MarkaAdiListesi.append( MarkaAdi.title( ) )

		MarkaAdiListesi.sort( )

		SayfaBaslik = u"Outlet " + ', '.join( MarkaAdiListesi[0:9] ) + u" Bay Bayan Çocuk Ürünler"
		SayfaAciklama = str( ', ' ).join( MarkaAdiListesi )

		GoogleLink1 = CinsiyetAdi
		GoogleLink2 = "Adidas"
		GoogleLink3 = "Nike"
		GoogleLink4 = "Hummel"

	if GelenUrl == "UrunListesiYeni":

		Bulunanlarr = Urun.objects.filter( varyant__StokSayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( '-id' )

		BulunanIDler = ()

		for i in Bulunanlarr:
			if FotoKontrol( i.Logo ):
				BulunanIDler += (str( Urun.objects.get( id = i.id ).id ),)

		Bulunanlar = TemelFiltre.filter( id__in = BulunanIDler ).distinct( ).order_by( '-id' )

		MarkaAdiListesi = []

		for i in Bulunanlar:

			MarkaAdi = i[13]

			if MarkaAdi != None:
				if not MarkaAdi.title( ) in MarkaAdiListesi:
					MarkaAdiListesi.append( MarkaAdi.title( ) )

		MarkaAdiListesi.sort( )

		SayfaBaslik = u"Yeni Sezon " + ', '.join( MarkaAdiListesi[0:9] ) + u" Bay Bayan Çocuk indirimli yeni sezon ürünler"
		SayfaAciklama = str( ', ' ).join( MarkaAdiListesi )

		GoogleLink1 = CinsiyetAdi
		GoogleLink2 = "Adidas"
		GoogleLink3 = "Nike"
		GoogleLink4 = "Hummel"

	if GelenUrl == "UrunListesiFirsat":

		Bulunanlarr = Urun.objects.filter( Fiyat__lt = F( 'EFiyat' ), varyant__StokSayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( 'Fiyat' )

		BulunanIDler = ()

		for i in Bulunanlarr:
			if FotoKontrol( i.Logo ):
				BulunanIDler += (str( Urun.objects.get( id = i.id ).id ),)

		Bulunanlar = TemelFiltre.filter( id__in = BulunanIDler ).distinct( ).order_by( '-id' )

		MarkaAdiListesi = []

		for i in Bulunanlar:

			MarkaAdi = i[13]

			if MarkaAdi != None:
				if not MarkaAdi.title( ) in MarkaAdiListesi:
					MarkaAdiListesi.append( MarkaAdi.title( ) )

		MarkaAdiListesi.sort( )

		SayfaBaslik = ', '.join( MarkaAdiListesi[0:7] ) + u" Bay Bayan Çocuk Outlet Fırsat Ürünleri."
		SayfaAciklama = str( ', ' ).join( MarkaAdiListesi )

		GoogleLink1 = CinsiyetAdi
		GoogleLink2 = "Adidas"
		GoogleLink3 = "Nike"
		GoogleLink4 = "Hummel"

	if GelenUrl == "UrunListesiHaftaninUrunu":

		Bulunanlarr = Urun.objects.filter( HaftaninUrunu = 1, varyant__StokSayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( 'Fiyat' )

		BulunanIDler = ()

		for i in Bulunanlarr:
			if FotoKontrol( i.Logo ):
				BulunanIDler += (str( Urun.objects.get( id = i.id ).id ),)

		Bulunanlar = TemelFiltre.filter( id__in = BulunanIDler ).distinct( ).order_by( '-id' )

		MarkaAdiListesi = []

		for i in Bulunanlar:

			MarkaAdi = i[13]

			if MarkaAdi != None:
				if not MarkaAdi.title( ) in MarkaAdiListesi:
					MarkaAdiListesi.append( MarkaAdi.title( ) )

		MarkaAdiListesi.sort( )

		SayfaBaslik = ', '.join( MarkaAdiListesi[0:7] ) + u" Haftanın Ürünleri"
		SayfaAciklama = str( ', ' ).join( MarkaAdiListesi )

		GoogleLink1 = "Sevgililer"
		GoogleLink2 = "Günü"
		GoogleLink3 = "Özel"
		GoogleLink4 = "Ürünler"

	if GelenUrl == "UrunListesiYeniCinsiyet":

		Bulunanlarr = Urun.objects.filter( UstKat__Cinsiyet__Slug = Katid, varyant__StokSayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( '-id' )

		BulunanIDler = ()

		for i in Bulunanlarr:
			if FotoKontrol( i.Logo ):
				BulunanIDler += (str( Urun.objects.get( id = i.id ).id ),)

		Bulunanlar = TemelFiltre.filter( id__in = BulunanIDler ).distinct( ).order_by( '-id' )

		MarkaAdiListesi = []

		for i in Bulunanlar:

			MarkaAdi = i[13]

			if MarkaAdi != None:
				if not MarkaAdi.title( ) in MarkaAdiListesi:
					MarkaAdiListesi.append( MarkaAdi.title( ) )

		MarkaAdiListesi.sort( )

		SayfaBaslik = u"Yeni Sezon " + ', '.join( MarkaAdiListesi[0:9] ) + u" indirimli ürünleri"
		SayfaAciklama = str( ', ' ).join( MarkaAdiListesi )

		GoogleLink1 = CinsiyetAdi
		GoogleLink2 = "Adidas"
		GoogleLink3 = "Nike"
		GoogleLink4 = "Hummel"

	if GelenUrl == "UrunListesiFirsatCinsiyet":

		Bulunanlarr = Urun.objects.filter( Fiyat__lt = F( 'EFiyat' ), UstKat__Cinsiyet__Slug = Katid, varyant__StokSayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( 'Fiyat' )

		BulunanIDler = ()

		for i in Bulunanlarr:
			if FotoKontrol( i.Logo ):
				BulunanIDler += (str( Urun.objects.get( id = i.id ).id ),)

		Bulunanlar = TemelFiltre.filter( id__in = BulunanIDler ).distinct( ).order_by( '-id' )

		MarkaAdiListesi = []

		for i in Bulunanlar:

			MarkaAdi = i[13]

			if MarkaAdi != None:
				if not MarkaAdi.title( ) in MarkaAdiListesi:
					MarkaAdiListesi.append( MarkaAdi.title( ) )

		MarkaAdiListesi.sort( )

		SayfaBaslik = ', '.join( MarkaAdiListesi[0:7] ) + u" Bay Bayan Çocuk Outlet Fırsat Ürünleri."
		SayfaAciklama = str( ', ' ).join( MarkaAdiListesi )

		GoogleLink1 = CinsiyetAdi
		GoogleLink2 = False
		GoogleLink3 = False
		GoogleLink4 = False

	bedensecimi = request.GET.get( 'be', None )
	numarasecimi = request.GET.get( 'nu', None )  # numara ve beden aynı sadece filtre detaylandırma ve arkplan rengi için ayırıyoruz
	kavalasecimi = request.GET.get( 'kv', None )
	cinsiyetsecimi = request.GET.get( 'ci', None )
	ortakatsecimi = request.GET.get( 'ok', None )
	markasecimi = request.GET.get( 'marka', None )

	if GelenUrl == "UrunListesiMarka":
		MarkaSlug = Marka.objects.get( id = Katid ).Slug
		cinsiyetliste = Urun.objects.values_list( 'id', 'Adi', 'StokKodu', 'Logo', 'Logo2', 'Logo3', 'Logo4', 'Logo5', 'Slug', 'Yeni', 'Firsat', 'Fiyat', 'EFiyat', 'Marka__Adi', 'Marka_id' ).filter( Marka__Slug = MarkaSlug ).values_list( 'UstKat__Cinsiyet__Adi', flat = True ).exclude( UstKat__Cinsiyet__Adi = 'UNISEX' ).exclude( UstKat__Cinsiyet__Adi = 'BEBEK' ).distinct( ).order_by( 'UstKat__Cinsiyet__Adi' )
	else:
		cinsiyetliste = Urun.objects.values_list( 'id', 'Adi', 'StokKodu', 'Logo', 'Logo2', 'Logo3', 'Logo4', 'Logo5', 'Slug', 'Yeni', 'Firsat', 'Fiyat', 'EFiyat', 'Marka__Adi', 'Marka_id' ).values_list( 'UstKat__Cinsiyet__Adi', flat = True ).exclude( UstKat__Cinsiyet__Adi = 'UNISEX' ).exclude( UstKat__Cinsiyet__Adi = 'BEBEK' ).distinct( ).order_by( 'UstKat__Cinsiyet__Adi' )

	if cinsiyetsecimi:
		Bulunanlar = Bulunanlar.filter( UstKat__Cinsiyet__Slug = cinsiyetsecimi, varyant__StokSayisi__gt = 0 )

	ortakatliste = Bulunanlar.values_list( 'OrtaKat__Adi', flat = True ).distinct( ).order_by( 'OrtaKat__Adi' )
	if ortakatsecimi:
		Bulunanlar = Bulunanlar.filter( OrtaKat__Slug = ortakatsecimi, varyant__StokSayisi__gt = 0 )  # Bulunanlar.filter( OrtaKat__Slug = ortakatsecimi )



	#
	# if cinsiyetsecimi:
	# Bulunanlar = Bulunanlar.filter( UstKat__Cinsiyet__Slug = cinsiyetsecimi )
	# ortakatliste = Bulunanlar.values_list( 'OrtaKat__Adi', flat = True ).distinct( ).order_by( 'OrtaKat__Adi' )
	#
	#    if ortakatsecimi:
	#     Bulunanlar = Bulunanlar.filter( UstKat__Cinsiyet__Slug = cinsiyetsecimi, OrtaKat__Slug = ortakatsecimi ) #Bulunanlar.filter( OrtaKat__Slug = ortakatsecimi )
	# else:
	#    ortakatliste = Bulunanlar.values_list( 'OrtaKat__Adi', flat = True ).distinct( ).order_by( 'OrtaKat__Adi' )
	#




	if GelenUrl != "UrunListesiMarka":

		altmarka = request.GET.get( 'q', None )

		# logging.info( altmarka )


		markaliste = Bulunanlar.values_list( 'Marka__Adi', flat = True ).exclude( Marka__Adi = '' ).distinct( ).order_by( 'Marka__Adi' )
	else:
		markaliste = { }

	if markasecimi and GelenUrl != "UrunListesiMarka":
		Bulunanlar = Bulunanlar.filter( Marka__Slug = markasecimi )

	RenkKlasoru = "/home/muslu/django/teslabb/media/renkler/"
	RenkFiltreResimleri = [f for f in listdir( RenkKlasoru )]

	renkliste = Bulunanlar.values_list( 'varyant__Renk', flat = True ).distinct( ).order_by( 'varyant__Renk' )

	tumrenkler = ()

	for i in RenkFiltreResimleri:
		b = i.replace( '.png', '' )
		if b in list( renkliste ):
			tumrenkler += (str( b ),)

	renksectimi = request.GET.get( 'renk', None )

	if renksectimi:
		Bulunanlar = Bulunanlar.filter( varyant__Renk__icontains = renksectimi )

	bedenliste = Bulunanlar.filter( UstKat__Adi__icontains = "TEKSTİL" ).values_list( 'varyant__Beden', flat = True ).distinct( ).order_by( 'varyant__Beden' )
	numaraliste = Bulunanlar.filter( UstKat__Adi__icontains = "AYAKKABI" ).values_list( 'varyant__Beden', flat = True ).distinct( ).order_by( 'varyant__Beden' )

	kavalaliste = Bulunanlar.values_list( 'varyant__Kavala', flat = True ).exclude( varyant__Kavala = '' ).distinct( ).order_by( 'varyant__Kavala' )

	if bedensecimi:
		Bulunanlar = Bulunanlar.filter( varyant__Beden = bedensecimi, varyant__StokSayisi__gt = 0 )
		kavalaliste = Bulunanlar.values_list( 'varyant__Kavala', flat = True ).exclude( varyant__Kavala = '' ).distinct( ).order_by( 'varyant__Kavala' )

	if numarasecimi:
		Bulunanlar = Bulunanlar.filter( varyant__Beden = numarasecimi, varyant__StokSayisi__gt = 0 )
		kavalaliste = Bulunanlar.values_list( 'varyant__Kavala', flat = True ).exclude( varyant__Kavala = '' ).distinct( ).order_by( 'varyant__Kavala' )

	if kavalasecimi:
		Bulunanlar = Bulunanlar.filter( varyant__Beden = bedensecimi, varyant__Kavala = kavalasecimi, varyant__StokSayisi__gt = 0 )

	try:
		enYuksekFiyat = int( round( Bulunanlar.values_list( 'Fiyat', flat = True ).distinct( ).order_by( '-Fiyat' )[0:1][0] ) )
		enDusukFiyat = int( floor( Bulunanlar.values_list( 'Fiyat', flat = True ).distinct( ).order_by( 'Fiyat' )[0:1][0] ) )
	except:
		enYuksekFiyat = 0
		enDusukFiyat = 0

	fiyatlar = []

	for i in Bulunanlar.values_list( 'Fiyat', flat = True ).distinct( ).order_by( 'Fiyat' ):
		if not floor( i ) in fiyatlar and floor( i ) != int( enDusukFiyat ):
			fiyatlar += (int( i ),)

	siralama = request.GET.get( 'sirala', None )

	if siralama == "up":
		Bulunanlar = Bulunanlar.order_by( 'Fiyat' )
	if siralama == "pu":
		Bulunanlar = Bulunanlar.order_by( '-Fiyat' )
	if siralama == "ye":
		Bulunanlar = Bulunanlar.order_by( '-id' )
	if siralama == "ey":
		Bulunanlar = Bulunanlar.order_by( 'id' )
	if siralama == "si":
		Bulunanlar = Bulunanlar.filter( Fiyat__lt = F( 'EFiyat' ) )
	if siralama == "isiz":
		Bulunanlar = Bulunanlar.filter( EFiyat__lte = F( 'Fiyat' ) )

	endusukfiyatsecimi = request.GET.get( 'ed', enDusukFiyat )
	enyuksekfiyatsecimi = request.GET.get( 'ey', enYuksekFiyat )

	if endusukfiyatsecimi:
		Bulunanlar = Bulunanlar.filter( Fiyat__gte = endusukfiyatsecimi, Fiyat__lte = int( enyuksekfiyatsecimi ) + 1, varyant__StokSayisi__gt = 0 )

	if GelenUrl == "UrunListesiYeni" or GelenUrl == "UrunListesiYeniCinsiyet":
		Bulunanlar = Bulunanlar[0:50]

	if GelenUrl == "UrunListesiFirsat" or GelenUrl == "UrunListesiFirsatCinsiyet":
		Bulunanlar = Bulunanlar[0:100]

	if GelenUrl == "UrunListesiAltKat" or GelenUrl == "UrunListesiOrtaKat":
		cinsiyetliste = { }
		ortakatliste = { }

	paginator = Paginator( Bulunanlar, 30 )
	page = request.GET.get( 'sayfa', None )

	try:
		urunler = paginator.page( page )
	except PageNotAnInteger:
		urunler = paginator.page( 1 )
	except EmptyPage:
		urunler = paginator.page( paginator.num_pages )

	return render_to_response( 'listing_usual.html', { 'urunler': urunler, 'Bulunanlar': Bulunanlar, 'SayfaBaslik': SayfaBaslik, 'SayfaAciklama': SayfaAciklama, 'GoogleLink1': GoogleLink1, 'GoogleLink2': GoogleLink2, 'GoogleLink3': GoogleLink3, 'GoogleLink4': GoogleLink4, 'Renkler': tumrenkler, 'fiyatlar': fiyatlar, 'enYuksekFiyat': enYuksekFiyat, 'enDusukFiyat': enDusukFiyat, 'bedenliste': bedenliste, 'numaraliste': numaraliste, 'kavalaliste': kavalaliste, 'cinsiyetliste': cinsiyetliste, 'markaliste': markaliste, 'ortakatliste': ortakatliste,

	}, context_instance = RequestContext( request ) )


def UrunDetayii( request, MarkaAdi, Slug, UrunID ):
	try:
		UyeID = Kullanicilar.objects.get( user = request.user ).uyeid
	except:
		UyeID = request.COOKIES.get( 'UyeID' )
		if not UyeID:
			UyeID = randint( 1000000, 9999999 )

	urun_detayi = Urun.objects.get( id = UrunID )

	urun_varyant_detayi = Varyant.objects.filter( Urunu_id = urun_detayi.id, StokSayisi__gt = 0 ).distinct( ).order_by( 'Renk', 'Beden', 'Kavala' )

	toplam_stok_sayisi = urun_varyant_detayi.aggregate( Sum( 'StokSayisi' ) )

	KesilecekYer = ""
	kodu_benzer_urunler = { }

	EslesenUrunlerListesi = ["U410", "M360", "M373", "W373", "M554", "U420", "ML574", "U395", "M400", "KL574", "KV574", "K200", "K2013", "KE410", "KV500", "KV395", "KV373", "U430", "KE420", "KE410"]

	for s in EslesenUrunlerListesi:

		if urun_detayi.StokKodu.startswith( s ):
			KesilecekYer = s

	if KesilecekYer != "":
		kodu_benzer_urunlerr = Urun.objects.filter( StokKodu__icontains = KesilecekYer, varyant__StokSayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( id = UrunID ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( 'Fiyat' )

		BulunanIDler = ()

		for i in kodu_benzer_urunlerr:
			if FotoKontrol( i.Logo ):
				BulunanIDler += (str( Urun.objects.get( id = i.id ).id ),)

		kodu_benzer_urunler = Urun.objects.values_list( 'id', 'Adi', 'StokKodu', 'Logo', 'Logo2', 'Logo3', 'Logo4', 'Logo5', 'Slug', 'Yeni', 'Firsat', 'Fiyat', 'EFiyat', 'Marka__Adi', 'Marka_id' ).filter( id__in = BulunanIDler )

	if urun_detayi.Marka.Adi.lower( ) == "hummel" or urun_detayi.Marka.Adi.lower( ) == "levis" or urun_detayi.Marka.Adi.lower( ) == "superga" or urun_detayi.Marka.Adi.lower( ) == "adidas" or urun_detayi.Marka.Adi.lower( ) == "asics":


		if urun_detayi.Marka.Adi.lower( ) == "hummel" or urun_detayi.Marka.Adi.lower( ) == "levis" or urun_detayi.Marka.Adi.lower( ) == "asics":
			KesilecekYer = urun_detayi.StokKodu.split( '-' )[0]

		if urun_detayi.Marka.Adi.lower( ) == "superga":
			KesilecekYer = urun_detayi.StokKodu.split( '-' )[1]

			kodu_benzer_urunlerr = Urun.objects.filter( StokKodu__icontains = KesilecekYer, varyant__StokSayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( id = UrunID ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( 'Fiyat' )

			BulunanIDler = ()

			for i in kodu_benzer_urunlerr:
				if FotoKontrol( i.Logo ):
					BulunanIDler += (str( Urun.objects.get( id = i.id ).id ),)

			kodu_benzer_urunler = Urun.objects.values_list( 'id', 'Adi', 'StokKodu', 'Logo', 'Logo2', 'Logo3', 'Logo4', 'Logo5', 'Slug', 'Yeni', 'Firsat', 'Fiyat', 'EFiyat', 'Marka__Adi', 'Marka_id' ).filter( id__in = BulunanIDler )

		if urun_detayi.Marka.Adi.lower( ) == "adidas":
			KesilecekYer = urun_detayi.Adi

			kodu_benzer_urunlerr = Urun.objects.filter( Adi__icontains = KesilecekYer, varyant__StokSayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( id = UrunID ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( 'Fiyat' )
			BulunanIDler = ()

			for i in kodu_benzer_urunlerr:
				if FotoKontrol( i.Logo ):
					BulunanIDler += (str( Urun.objects.get( id = i.id ).id ),)

			kodu_benzer_urunler = Urun.objects.values_list( 'id', 'Adi', 'StokKodu', 'Logo', 'Logo2', 'Logo3', 'Logo4', 'Logo5', 'Slug', 'Yeni', 'Firsat', 'Fiyat', 'EFiyat', 'Marka__Adi', 'Marka_id' ).filter( id__in = BulunanIDler )

	sonrakiurun = False
	oncekiurun = False

	try:
		sonrakiurun = kodu_benzer_urunler[0:1]
		oncekiurun = kodu_benzer_urunler[1:2]
	except:
		sonrakiurun = False
		oncekiurun = False

	eslestirilmis_urunler = { }
	eslestirilmis_urunlerrr = { }

	eslestirilmis_urunlerrrr = BenzerUrunler.objects.filter( Q( urun = urun_detayi.id ) | Q( eslesenurun = urun_detayi.id ), urun__AltKat__id__isnull = False, urun__varyant__AltKat__id__isnull = False )

	for s in eslestirilmis_urunlerrrr:

		eslestirilmis_urunlerrr = s.eslesenurun.filter( varyant__StokSayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( id = UrunID ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( 'Fiyat' )

	eslestirilmis_urunlerr = ()

	if eslestirilmis_urunlerrr:

		for i in eslestirilmis_urunlerrr.all( ):

			if FotoKontrol( i.Logo ) and i.id != urun_detayi.id:

				eslestirilmis_urunlerr += (str( Urun.objects.get( id = i.id ).id ),)

		eslestirilmis_urunler = Urun.objects.values_list( 'id', 'Adi', 'StokKodu', 'Logo', 'Logo2', 'Logo3', 'Logo4', 'Logo5', 'Slug', 'Yeni', 'Firsat', 'Fiyat', 'EFiyat', 'Marka__Adi', 'Marka_id' ).filter( id__in = eslestirilmis_urunlerr ).order_by( '?' ).distinct( )[0:12]


	else:
		eslestirilmis_urunler = { }

	BankaListesi = Bankalar.objects.filter( Aktif = True )

	response = render_to_response( 'product_related.html', {

	'urun_detayi': urun_detayi, 'toplam_stok_sayisi': toplam_stok_sayisi, 'urun_varyant_detayi': urun_varyant_detayi, 'kodu_benzer_urunler': kodu_benzer_urunler, 'sonrakiurun': sonrakiurun, 'oncekiurun': oncekiurun, 'eslestirilmis_urunler': eslestirilmis_urunler, 'BankaListesi': BankaListesi,


	}, context_instance = RequestContext( request ) )

	response.set_cookie( 'UyeID', UyeID )
	response.delete_cookie( 'SiparisNosu' )
	response.delete_cookie( 'OdemeTuru' )
	response.delete_cookie( 'VaryantID' )

	return response


def VarID( request, VaryID ):
	urun_detayi = Urun.objects.get( varyant__id = VaryID )

	urun_varyant_detayi = Varyant.objects.filter( id = VaryID, StokSayisi__gt = 0 ).distinct( ).order_by( 'Renk', 'Beden', 'Kavala' )

	toplam_stok_sayisi = urun_varyant_detayi.aggregate( Sum( 'StokSayisi' ) )

	KesilecekYer = ""
	kodu_benzer_urunler = { }

	EslesenUrunlerListesi = ["U410", "M360", "M373", "W373", "M554", "U420", "ML574", "U395", "M400", "KL574", "KV574", "K200", "K2013", "KE410", "KV500", "KV395", "KV373", "U430", "KE420", "KE410"]

	for s in EslesenUrunlerListesi:

		if urun_detayi.StokKodu.startswith( s ):
			KesilecekYer = s

	if KesilecekYer != "":
		kodu_benzer_urunler = Urun.objects.values_list( 'id', 'Adi', 'StokKodu', 'Logo', 'Logo2', 'Logo3', 'Logo4', 'Logo5', 'Slug', 'Yeni', 'Firsat', 'Fiyat', 'EFiyat', 'Marka__Adi', 'Marka_id' ).filter( StokKodu__icontains = KesilecekYer, varyant__StokSayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( varyant__id = VaryID ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( 'Fiyat' )

	if urun_detayi.Marka.Adi.lower( ) == "hummel" or urun_detayi.Marka.Adi.lower( ) == "levis" or urun_detayi.Marka.Adi.lower( ) == "superga" or urun_detayi.Marka.Adi.lower( ) == "adidas" or urun_detayi.Marka.Adi.lower( ) == "asics":


		if urun_detayi.Marka.Adi.lower( ) == "hummel" or urun_detayi.Marka.Adi.lower( ) == "levis" or urun_detayi.Marka.Adi.lower( ) == "asics":
			KesilecekYer = urun_detayi.StokKodu.split( '-' )[0]

		if urun_detayi.Marka.Adi.lower( ) == "superga":
			KesilecekYer = urun_detayi.StokKodu.split( '-' )[1]

		if urun_detayi.Marka.Adi.lower( ) == "adidas":
			KesilecekYer = urun_detayi.Adi

		kodu_benzer_urunler = Urun.objects.values_list( 'id', 'Adi', 'StokKodu', 'Logo', 'Logo2', 'Logo3', 'Logo4', 'Logo5', 'Slug', 'Yeni', 'Firsat', 'Fiyat', 'EFiyat', 'Marka__Adi', 'Marka_id' ).filter( StokKodu__icontains = KesilecekYer, varyant__StokSayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( varyant__id = VaryID ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( 'Fiyat' )

	sonrakiurun = False
	oncekiurun = False

	try:
		sonrakiurun = kodu_benzer_urunler[0:1]
		oncekiurun = kodu_benzer_urunler[1:2]
	except:
		sonrakiurun = False
		oncekiurun = False

	eslestirilmis_urunler = { }
	eslestirilmis_urunlerrr = { }

	eslestirilmis_urunlerrrr = BenzerUrunler.objects.filter( Q( urun = urun_detayi.id ) | Q( eslesenurun = urun_detayi.id ), urun__AltKat__id__isnull = False, urun__varyant__AltKat__id__isnull = False )

	for s in eslestirilmis_urunlerrrr:

		eslestirilmis_urunlerrr = s.eslesenurun.filter( varyant__StokSayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( id = UrunID ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( 'Fiyat' )

	eslestirilmis_urunlerr = ()

	if eslestirilmis_urunlerrr:

		for i in eslestirilmis_urunlerrr.all( ):

			if FotoKontrol( i.Logo ) and i.id != urun_detayi.id:

				eslestirilmis_urunlerr += (str( Urun.objects.get( id = i.id ).id ),)

		eslestirilmis_urunler = Urun.objects.values_list( 'id', 'Adi', 'StokKodu', 'Logo', 'Logo2', 'Logo3', 'Logo4', 'Logo5', 'Slug', 'Yeni', 'Firsat', 'Fiyat', 'EFiyat', 'Marka__Adi', 'Marka_id' ).filter( id__in = eslestirilmis_urunlerr ).order_by( '?' ).distinct( )[0:12]


	else:
		eslestirilmis_urunler = { }

	BankaListesi = Bankalar.objects.filter( Aktif = True )

	return render_to_response( 'product_related.html', {

	'urun_detayi': urun_detayi, 'toplam_stok_sayisi': toplam_stok_sayisi, 'urun_varyant_detayi': urun_varyant_detayi, 'kodu_benzer_urunler': kodu_benzer_urunler, 'sonrakiurun': sonrakiurun, 'oncekiurun': oncekiurun, 'eslestirilmis_urunler': eslestirilmis_urunler, 'BankaListesi': BankaListesi,

	}, context_instance = RequestContext( request ) )


def UrunVaryantSecimi( request, UrunID ):
	rengi = request.GET.get( 'rengi', None )
	bedeni = request.GET.get( 'bedeni', None )
	kavalasi = request.GET.get( 'kavalasi', None )

	try:
		UyeID = Kullanicilar.objects.get( user = request.user ).uyeid
	except:
		UyeID = request.COOKIES.get( 'UyeID' )

	if rengi and bedeni and kavalasi:

		varyant_stoksayisi_listesi = Varyant.objects.get( Urunu_id = UrunID, StokSayisi__gt = 0, Renk = rengi.encode( 'utf-8' ), Beden = bedeni.encode( 'utf-8' ), Kavala = kavalasi.encode( 'utf-8' ) )

		try:

			SepettekiStok = SepetUrunler.objects.get( SepetID = Sepet.objects.get( UyeID = UyeID, Tamamlandi = False ).id, VaryantID = varyant_stoksayisi_listesi.id )

			html = '<option value="0">Adet</option>'
			for i in range( varyant_stoksayisi_listesi.StokSayisi - SepettekiStok.Adet ):
				html += '<option value="' + str( i + 1 ) + "|" + str( varyant_stoksayisi_listesi.id ) + '">' + str( i + 1 ) + '</option>'
			return HttpResponse( html )

		except:

			html = '<option value="0">Adet</option>'
			for i in range( varyant_stoksayisi_listesi.StokSayisi ):
				html += '<option value="' + str( i + 1 ) + "|" + str( varyant_stoksayisi_listesi.id ) + '">' + str( i + 1 ) + '</option>'
			return HttpResponse( html )


	elif rengi and bedeni:
		varyant_kavala_or_stoksayisi_listesi = Varyant.objects.filter( Urunu_id = UrunID, StokSayisi__gt = 0, Renk = rengi.encode( 'utf-8' ), Beden = bedeni.encode( 'utf-8' ) ).values( 'Kavala' ).last( )

		if bool( varyant_kavala_or_stoksayisi_listesi["Kavala"] ):

			varyant_kavala_listesi = Varyant.objects.filter( Urunu_id = UrunID, StokSayisi__gt = 0, Renk = rengi.encode( 'utf-8' ), Beden = bedeni.encode( 'utf-8' ) ).values( 'Kavala' ).distinct( ).order_by( 'Kavala' )

			html = '<option value="1">Boy</option>'
			for i in varyant_kavala_listesi:
				html += '<option>' + str( i['Kavala'] ) + '</option>'
			return HttpResponse( html )


		else:

			varyant_stoksayisi_listesi = Varyant.objects.get( Urunu_id = UrunID, StokSayisi__gt = 0, Renk = rengi.encode( 'utf-8' ), Beden = bedeni.encode( 'utf-8' ) )

			try:

				SepettekiStok = SepetUrunler.objects.get( SepetID = Sepet.objects.get( UyeID = UyeID, Tamamlandi = False ).id, VaryantID = varyant_stoksayisi_listesi.id )

				html = '<option value="0">Adet</option>'
				for i in range( varyant_stoksayisi_listesi.StokSayisi - SepettekiStok.Adet ):
					html += '<option value="' + str( i + 1 ) + "|" + str( varyant_stoksayisi_listesi.id ) + '">' + str( i + 1 ) + '</option>'
				return HttpResponse( html )

			except:
				html = '<option value="0">Adet</option>'
				for i in range( varyant_stoksayisi_listesi.StokSayisi ):
					html += '<option value="' + str( i + 1 ) + "|" + str( varyant_stoksayisi_listesi.id ) + '">' + str( i + 1 ) + '</option>'
				return HttpResponse( html )





	elif rengi:

		try:

			varyant_stoksayisi_listesi = Varyant.objects.get( Urunu_id = UrunID, StokSayisi__gt = 0, Renk = rengi.encode( 'utf-8' ) )

			# logging.info(varyant_stoksayisi_listesi.Beden)

			if not varyant_stoksayisi_listesi.Beden:

				try:

					SepettekiStok = SepetUrunler.objects.get( SepetID = Sepet.objects.get( UyeID = UyeID, Tamamlandi = False ).id, VaryantID = varyant_stoksayisi_listesi.id )

					html = '<option value="1">Adet</option>'
					for i in range( varyant_stoksayisi_listesi.StokSayisi - SepettekiStok.Adet ):
						html += '<option value="' + str( i + 1 ) + "|" + str( varyant_stoksayisi_listesi.id ) + '">' + str( i + 1 ) + '</option>'
					return HttpResponse( html )

				except:
					html = '<option value="1">Adet</option>'
					for i in range( varyant_stoksayisi_listesi.StokSayisi ):
						html += '<option value="' + str( i + 1 ) + "|" + str( varyant_stoksayisi_listesi.id ) + '">' + str( i + 1 ) + '</option>'
					return HttpResponse( html )

			else:

				varyant_beden_listesi = Varyant.objects.filter( Urunu_id = UrunID, StokSayisi__gt = 0, Renk = rengi.encode( 'utf-8' ) ).values( 'Beden' ).distinct( ).order_by( 'Beden' )

				if u"TEKSTİL" in Urun.objects.get( id = UrunID ).UstKat.Adi:
					html = '<option value="1">Beden</option>'
				else:
					html = '<option value="1">Numara</option>'
				for i in varyant_beden_listesi:
					html += '<option>' + str( i['Beden'] ) + '</option>'
				return HttpResponse( html )

		except:

			varyant_beden_listesi = Varyant.objects.filter( Urunu_id = UrunID, StokSayisi__gt = 0, Renk = rengi.encode( 'utf-8' ) ).values( 'Beden' ).distinct( ).order_by( 'Beden' )

			if u"TEKSTİL" in Urun.objects.get( id = UrunID ).UstKat.Adi:
				html = '<option value="1">Beden</option>'
			else:
				html = '<option value="1">Numara</option>'
			for i in varyant_beden_listesi:
				html += '<option>' + str( i['Beden'] ) + '</option>'
			return HttpResponse( html )


@csrf_protect
def Bul( request ):
	request.encoding = 'utf-8'
	q = request.GET['q']

	if not q:
		q = "sporthink"

	ArananKelimeler = q.split( )

	qset1 = reduce( operator.__and__, [Q( Adi__icontains = query ) | Q( StokKodu__icontains = query ) for query in ArananKelimeler] )

	Bulunanlarr = Urun.objects.filter( qset1, varyant__StokSayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( 'Fiyat' )

	BulunanIDler = ()

	for i in Bulunanlarr:
		if FotoKontrol( i.Logo ):
			BulunanIDler += (str( Urun.objects.get( id = i.id ).id ),)

	Bulunanlar = Urun.objects.values_list( 'id', 'Adi', 'StokKodu', 'Logo', 'Logo2', 'Logo3', 'Logo4', 'Logo5', 'Slug', 'Yeni', 'Firsat', 'Fiyat', 'EFiyat', 'Marka__Adi', 'Marka_id' ).filter( id__in = BulunanIDler ).distinct( ).order_by( '-id' )

	MarkaAdiListesi = []

	for i in Bulunanlar:

		MarkaAdi = i[13]

		if MarkaAdi != None:
			if not MarkaAdi.title( ) in MarkaAdiListesi:
				MarkaAdiListesi.append( MarkaAdi.title( ) )

	MarkaAdiListesi.sort( )

	AltKatBulunanlar = Urun.objects.values_list( 'AltKat__Adi' ).filter( qset1, varyant__StokSayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( )

	AltKategor = []

	for i in AltKatBulunanlar:

		AltKatAdi = i[0]

		if AltKatAdi != None:

			if not AltKatAdi.title( ) in AltKategor:
				AltKategor.append( AltKatAdi.title( ) )

	AltKategor.sort( )

	SayfaBaslik = q + " " + str( ', ' ).join( AltKategor ) + ", " + ', '.join( MarkaAdiListesi[0:7] )
	SayfaAciklama = q + " " + str( ', ' ).join( AltKategor ) + ", " + ', '.join( MarkaAdiListesi )

	bedensecimi = request.GET.get( 'be', None )
	numarasecimi = request.GET.get( 'nu', None )  # numara ve beden aynı sadece filtre detaylandırma ve arkplan rengi için ayırıyoruz
	kavalasecimi = request.GET.get( 'kv', None )
	cinsiyetsecimi = request.GET.get( 'ci', None )
	ortakatsecimi = request.GET.get( 'ok', None )
	markasecimi = request.GET.get( 'marka', None )

	cinsiyetliste = Bulunanlar.values_list( 'UstKat__Cinsiyet__Adi', flat = True ).exclude( UstKat__Cinsiyet__Adi = 'UNISEX' ).exclude( UstKat__Cinsiyet__Adi = 'BEBEK' ).distinct( ).order_by( 'UstKat__Cinsiyet__Adi' )

	if cinsiyetsecimi:
		Bulunanlar = Bulunanlar.filter( UstKat__Cinsiyet__Slug = cinsiyetsecimi, varyant__StokSayisi__gt = 0 )

	ortakatliste = Bulunanlar.values_list( 'OrtaKat__Adi', flat = True ).distinct( ).order_by( 'OrtaKat__Adi' )
	if ortakatsecimi:
		Bulunanlar = Bulunanlar.filter( OrtaKat__Slug = ortakatsecimi, varyant__StokSayisi__gt = 0 )  # Bulunanlar.filter( OrtaKat__Slug = ortakatsecimi )

	markaliste = Bulunanlar.values_list( 'Marka__Adi', flat = True ).exclude( Marka__Adi = '' ).distinct( ).order_by( 'Marka__Adi' )

	if markasecimi:
		Bulunanlar = Bulunanlar.filter( Marka__Slug = markasecimi )

	RenkKlasoru = "/home/muslu/django/teslabb/media/renkler/"
	RenkFiltreResimleri = [f for f in listdir( RenkKlasoru )]

	renkliste = Bulunanlar.values_list( 'varyant__Renk', flat = True ).distinct( ).order_by( 'varyant__Renk' )

	tumrenkler = ()

	for i in RenkFiltreResimleri:
		b = i.replace( '.png', '' )
		if b in list( renkliste ):
			tumrenkler += (str( b ),)

	renksectimi = request.GET.get( 'renk', None )

	if renksectimi:
		Bulunanlar = Bulunanlar.filter( varyant__Renk__icontains = renksectimi )

	bedenliste = Bulunanlar.filter( UstKat__Adi__icontains = "TEKSTİL" ).values_list( 'varyant__Beden', flat = True ).distinct( ).order_by( 'varyant__Beden' )
	numaraliste = Bulunanlar.filter( UstKat__Adi__icontains = "AYAKKABI" ).values_list( 'varyant__Beden', flat = True ).distinct( ).order_by( 'varyant__Beden' )

	kavalaliste = Bulunanlar.values_list( 'varyant__Kavala', flat = True ).exclude( varyant__Kavala = '' ).distinct( ).order_by( 'varyant__Kavala' )

	if bedensecimi:
		Bulunanlar = Bulunanlar.filter( varyant__Beden = bedensecimi, varyant__StokSayisi__gt = 0 )
		kavalaliste = Bulunanlar.values_list( 'varyant__Kavala', flat = True ).exclude( varyant__Kavala = '' ).distinct( ).order_by( 'varyant__Kavala' )

	if numarasecimi:
		Bulunanlar = Bulunanlar.filter( varyant__Beden = numarasecimi, varyant__StokSayisi__gt = 0 )
		kavalaliste = Bulunanlar.values_list( 'varyant__Kavala', flat = True ).exclude( varyant__Kavala = '' ).distinct( ).order_by( 'varyant__Kavala' )

	if kavalasecimi:
		Bulunanlar = Bulunanlar.filter( varyant__Beden = bedensecimi, varyant__Kavala = kavalasecimi, varyant__StokSayisi__gt = 0 )

	try:
		enYuksekFiyat = int( round( Bulunanlar.values_list( 'Fiyat', flat = True ).distinct( ).order_by( '-Fiyat' )[0:1][0] ) )
		enDusukFiyat = int( floor( Bulunanlar.values_list( 'Fiyat', flat = True ).distinct( ).order_by( 'Fiyat' )[0:1][0] ) )
	except:
		enYuksekFiyat = 0
		enDusukFiyat = 0

	fiyatlar = []

	for i in Bulunanlar.values_list( 'Fiyat', flat = True ).distinct( ).order_by( 'Fiyat' ):
		if not floor( i ) in fiyatlar and floor( i ) != int( enDusukFiyat ):
			fiyatlar += (int( i ),)

	siralama = request.GET.get( 'sirala', None )

	if siralama == "up":
		Bulunanlar = Bulunanlar.order_by( 'Fiyat' )
	if siralama == "pu":
		Bulunanlar = Bulunanlar.order_by( '-Fiyat' )
	if siralama == "ye":
		Bulunanlar = Bulunanlar.order_by( '-id' )
	if siralama == "ey":
		Bulunanlar = Bulunanlar.order_by( 'id' )
	if siralama == "si":
		Bulunanlar = Bulunanlar.filter( Fiyat__lt = F( 'EFiyat' ) )
	if siralama == "isiz":
		Bulunanlar = Bulunanlar.filter( EFiyat__lte = F( 'Fiyat' ) )

	endusukfiyatsecimi = request.GET.get( 'ed', enDusukFiyat )
	enyuksekfiyatsecimi = request.GET.get( 'ey', enYuksekFiyat )

	if endusukfiyatsecimi:
		Bulunanlar = Bulunanlar.filter( Fiyat__gte = endusukfiyatsecimi, Fiyat__lte = int( enyuksekfiyatsecimi ) + 1, varyant__StokSayisi__gt = 0 )

	x_forwarded_for = request.META.get( 'HTTP_X_FORWARDED_FOR' )
	if x_forwarded_for:
		ip = x_forwarded_for.split( ',' )[0]
	else:
		ip = request.META.get( 'REMOTE_ADDR' )

	Cihaz = "Çözümlenemedi"
	Aramalar( Aranan = q, IP = ip, UyeID = request.COOKIES.get( 'UyeID' ), Sonuc = len( Bulunanlar ), Request = request, Cihaz = Cihaz ).save( )

	paginator = Paginator( Bulunanlar, 48 )
	page = request.GET.get( 'sayfa', None )

	try:
		urunler = paginator.page( page )
	except PageNotAnInteger:
		urunler = paginator.page( 1 )
	except EmptyPage:
		urunler = paginator.page( paginator.num_pages )

	return render_to_response( 'listing_usual.html', { 'urunler': urunler, 'Bulunanlar': Bulunanlar, 'SayfaBaslik': SayfaBaslik, 'SayfaAciklama': SayfaAciklama, 'Renkler': tumrenkler, 'fiyatlar': fiyatlar, 'enYuksekFiyat': enYuksekFiyat, 'enDusukFiyat': enDusukFiyat, 'bedenliste': bedenliste, 'numaraliste': numaraliste, 'kavalaliste': kavalaliste, 'ortakatliste': ortakatliste, 'markaliste': markaliste, 'cinsiyetliste': cinsiyetliste,

	}, context_instance = RequestContext( request ) )


@csrf_protect
def UrunAraXML( request ):
	request.encoding = 'utf-8'
	q = request.GET.get( 'q', "muslu" )

	Bulunanlar = ()

	x_forwarded_for = request.META.get( 'HTTP_X_FORWARDED_FOR' )
	if x_forwarded_for:
		ip = x_forwarded_for.split( ',' )[0]
	else:
		ip = request.META.get( 'REMOTE_ADDR' )

	if len( q ) > 3:

		ArananKelimeler = q.split( )

		qset1 = reduce( operator.__and__, [Q( Adi__icontains = query ) | Q( StokKodu__icontains = query ) for query in ArananKelimeler] )

		Bulunanlarr = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( qset1, ToplamStok_Sayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( Logo = "urun_resimleri/ResimYok.jpg" ).distinct( ).order_by( '-id' )[0:16]

		BulunanIDler = ()

		for i in Bulunanlarr:
			if FotoKontrol( i.Logo ):
				BulunanIDler += (str( Urun.objects.get( id = i.id ).id ),)

		Bulunanlar = Urun.objects.values_list( 'id', 'Adi', 'StokKodu', 'Logo', 'Slug', 'Fiyat', 'Marka' ).filter( id__in = BulunanIDler ).distinct( ).order_by( '-id' )


	# Cihaz = "Çözümlenemedi"

	# Aramalar( Aranan = q, IP = ip, UyeID = request.COOKIES.get( 'UyeID' ), Sonuc = len( Bulunanlar ), Request = request, Cihaz = Cihaz ).save( )

	return render_to_response( 'oto.xml', { 'Bulunanlar': Bulunanlar }, context_instance = RequestContext( request ), content_type = "text/xml; charset=utf-8" )


@csrf_protect
def GoogleMerchantXML( request ):
	limit = request.GET.get( 'limit', 1000 )
	marka = request.GET.get( 'marka', '' )
	outlet = request.GET.get( 'outlet', None )
	indirimli = request.GET.get( 'indirimli', None )
	cinsiyet = request.GET.get( 'cinsiyet', '' )

	Bulunanlarr = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( Logo = "urun_resimleri/ResimYok.jpg" )

	BulunanIDler = ()

	for i in Bulunanlarr:
		if FotoKontrol( i.Logo ):
			BulunanIDler += (str( Urun.objects.get( id = i.id ).id ),)

	Bulunanlar = Urun.objects.values_list( 'Adi', 'StokKodu', 'Logo', 'Slug', 'Fiyat', 'Marka', 'UstKat__Adi', 'OrtaKat__Adi', 'AltKat__Adi', 'Marka__Adi', 'id', 'UstKat__Cinsiyet__Adi' ).filter( id__in = BulunanIDler ).distinct( ).order_by( '-id' )

	if outlet == "evet":
		Bulunanlar = Bulunanlar.filter( ToplamStok_Sayisi__lte = 2 )

	if indirimli == "evet":
		Bulunanlar = Bulunanlar.filter( Fiyat__lt = F( 'EFiyat' ) )

	if marka != "":
		Bulunanlar = Bulunanlar.filter( Marka__Adi = marka )

	if cinsiyet != "":
		Bulunanlar = Bulunanlar.filter( UstKat__Cinsiyet__Adi = cinsiyet )

	Bulunanlar = Bulunanlar.distinct( ).order_by( '-id' )

	return render_to_response( 'googlemerchant.xml', { 'Bulunanlar': Bulunanlar }, context_instance = RequestContext( request ), content_type = "text/xml; charset=utf-8" )


@csrf_protect
def GoogleSitemapXML( request ):
	Bulunanlar = Urun.objects.values_list( 'Marka__Slug', 'Slug', 'id' ).annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( Logo = "urun_resimleri/ResimYok.jpg" )

	return render_to_response( 'googlesitemap.xml', { 'Bulunanlar': Bulunanlar }, context_instance = RequestContext( request ), content_type = "text/xml; charset=utf-8" )


@csrf_protect
def GenelXML( request ):
	XML_IP = ['212.175.17.196', '46.165.204.241', '88.250.159.71']

	limit = request.GET.get( 'limit', 300 )
	marka = request.GET.get( 'marka', '' )
	outlet = request.GET.get( 'outlet', None )
	indirimli = request.GET.get( 'indirimli', None )
	cinsiyet = request.GET.get( 'cinsiyet', '' )
	firma = request.GET.get( 'firma', '' )

	x_forwarded_for = request.META.get( 'HTTP_X_FORWARDED_FOR' )
	if x_forwarded_for:
		ip = x_forwarded_for.split( ',' )[0]
	else:
		ip = request.META.get( 'REMOTE_ADDR' )

	if ip in XML_IP:

		if firma != '':

			Bulunanlarr = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0 ).exclude( Defolu = 1 ).exclude( Logo = "urun_resimleri/ResimYok.jpg" )

			BulunanIDler = ()

			for i in Bulunanlarr:
				if FotoKontrol( i.Logo ):
					BulunanIDler += (str( Urun.objects.get( id = i.id ).id ),)

			Bulunanlar = Urun.objects.filter( id__in = BulunanIDler ).distinct( )

			if outlet == "evet":
				Bulunanlar = Bulunanlar.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__lte = 2 )

			if indirimli == "evet":
				Bulunanlar = Bulunanlar.filter( Fiyat__lt = F( 'EFiyat' ) )

			if marka != "":
				Bulunanlar = Bulunanlar.filter( Marka__Adi = marka )

			if cinsiyet != "":
				Bulunanlar = Bulunanlar.filter( UstKat__Cinsiyet__Adi = cinsiyet )

			Bulunanlar = Bulunanlar.values_list( 'Adi', 'StokKodu', 'Logo', 'Slug', 'Fiyat', 'Marka', 'UstKat__Adi', 'OrtaKat__Adi', 'AltKat__Adi', 'Marka__Adi', 'id', 'UstKat__Cinsiyet__Adi', 'EFiyat' ).order_by( '-id' )[0:int( limit )]

			GuncelXMLFirma( IP = ip, Request = str( request ), Firma = firma, Sorgu = request.META['REQUEST_URI'] ).save( )
			return render_to_response( 'genelXML.xml', { 'Bulunanlar': Bulunanlar, 'ip': ip, 'firma': firma }, context_instance = RequestContext( request ), content_type = "text/xml; charset=utf-8" )

		else:
			GuncelXMLFirma( IP = ip, Request = "FİRMA ADI TANIMLI DEĞİL" + str( request ), Firma = firma, Sorgu = request.META['REQUEST_URI'] ).save( )
			return HttpResponse( "<?xml version='1.0' encoding='UTF-8'?><Hata>Lütfen firma adı belirtiniz. Örn: ?firma=sporthink </Hata>", content_type = "text/xml; charset=utf-8" )


	else:
		GuncelXMLFirma( IP = ip, Request = "IP TANIMLI DEĞİL  " + str( request ), Firma = firma, Sorgu = request.META['REQUEST_URI'] ).save( )
		return HttpResponse( "<?xml version='1.0' encoding='UTF-8'?><Ooops>IP adresi tanımlı değil. </Ooops>", content_type = "text/xml; charset=utf-8" )


def urunv3( request ):
	# try:

	reload( sys )
	sys.setdefaultencoding( "utf-8" )
	os.environ['TDSVER'] = '8.0'

	Calistiran = request.GET.get( 'calistiran', 'manuel' )

	GunSayisi = request.GET.get( 'gun', '1' )
	StokKodu_Sorgu = request.GET.get( 'model', '' )
	Marka_Sorgu = request.GET.get( 'marka', '' )

	StokKodu_SorguVarMi = ""
	Marka_SorguVarMi = ""

	if StokKodu_Sorgu != "":
		StokKodu_SorguVarMi = " and ProductCode = '" + StokKodu_Sorgu + "'"
	if Marka_Sorgu != "":
		Marka_SorguVarMi = " and ProductAtt03 = '" + Marka_Sorgu + "'"

	cursor = connections["default"].cursor( )
	cursorV3 = connections["V3"].cursor( )

	cursorV3.execute( "CREATE TABLE #TempTableSpormarket (StokKodu NVARCHAR(MAX), Marka NVARCHAR(MAX), Adi NVARCHAR(MAX), Renk NVARCHAR(MAX), Beden NVARCHAR(MAX), Kavala NVARCHAR(MAX), Fiyat NVARCHAR(MAX), EFiyati NVARCHAR(MAX), StokSayisi NVARCHAR(MAX), Barkod NVARCHAR(MAX), Cinsiyet NVARCHAR(MAX),  UstKat NVARCHAR(MAX), OrtaKat NVARCHAR(MAX), AltKat NVARCHAR(MAX), RenkKodu NVARCHAR(MAX), ToplamStokSayisi NVARCHAR(MAX)  COLLATE Turkish_CS_AS)" );


	# eksorgu = "case when ROUND(100-( (Price1/Price2)*100 ),0) = 25 and ProductAtt03 = 'ADIDAS' then Price2 else Price1 end as Price1,"


	sorgumm = """ SET TEXTSIZE 2147483647  INSERT INTO #TempTableSpormarket (StokKodu, Marka, Adi, Renk, Beden, Kavala, Fiyat, EFiyati, StokSayisi, Barkod, Cinsiyet, UstKat, OrtaKat, AltKat, RenkKodu, ToplamStokSayisi)

                        SELECT
                            ProductCode as StokKodu,
                            ProductAtt03 as Marka,
                            LTRIM(RTRIM(ProductDescription)) as Adi,
                            LTRIM(RTRIM(ColorDescription)) as Renk,
                            ItemDim1Code as Beden,
                            ItemDim2Code as Kavala,
                            Price1 as Fiyati,
                            Price2 as EFiyati,
                            Warehouse1InventoryQty as StokSayisi,
                            LTRIM(RTRIM(Barcode)) as Barkod,
                            LTRIM(RTRIM(ProductAtt02Desc)) as Cinsiyet,
                            LTRIM(RTRIM(ProductHierarchyLevel01)) as UstKat,
                            LTRIM(RTRIM(ProductHierarchyLevel02)) as OrtaKat,
                            LTRIM(RTRIM(ProductHierarchyLevel03)) as AltKat,
                            ColorCode as RenkKodu,
                            Warehouse1InventoryQtySUM as ToplamStokSayisi

                from V3_DOGUKAN.dbo.ProductPriceAndInventory3 (N'TR', N'6', N'7', N'D01', 'def', """ + GunSayisi + """)
            where

                LTRIM(RTRIM(Barcode)) != '' AND Barcode IS NOT NULL
                and LTRIM(RTRIM(ProductDescription)) != '' AND ProductDescription IS NOT NULL
                and LTRIM(RTRIM(ColorDescription)) != '' AND ColorDescription IS NOT NULL
                and LTRIM(RTRIM(ProductAtt02Desc)) != '' AND ProductAtt02Desc IS NOT NULL
                and LTRIM(RTRIM(ProductHierarchyLevel01)) != '' AND ProductHierarchyLevel01 IS NOT NULL
                and LTRIM(RTRIM(ProductHierarchyLevel02)) != '' AND ProductHierarchyLevel02 IS NOT NULL
                and LTRIM(RTRIM(ProductHierarchyLevel03)) != '' AND ProductHierarchyLevel03 IS NOT NULL
                and LTRIM(RTRIM(ProductAtt03)) != '' AND ProductAtt03 IS NOT NULL AND ProductAtt03 not in ('CAT', 'CUBE', 'ENDER SPOR', 'FARELL', 'LACOSTE',  'DOGUKAN', 'BOAONDA', 'GD', 'JAGHS', 'NORTHERN REBEL', 'PROTEST', 'REEF', 'VODEN', 'WIPEOUT', 'ZEUS', 'MOLTEN', 'BYOS',  'WILSON', 'NONE', 'HAS', 'HITECH', 'HITEC', 'PINK STEP', 'DOCKERS-G', 'ONEILL')

              """ + StokKodu_SorguVarMi + Marka_SorguVarMi

	# logging.info(sorgumm)

	ServisKaydet = ServisDurumu( Gun = GunSayisi, Sorgu = sorgumm, IP = request.ipadres, Servis = Calistiran )
	ServisKaydet.save( )

	cursorV3.execute( sorgumm )
	cursorV3.execute( "SELECT * FROM #TempTableSpormarket" )




	# yenilerikaldir = "update kategoriler_urun set Yeni = 0"
	# cursor.execute( yenilerikaldir )

	islemgorenler = ""

	for row in cursorV3.fetchall( ):

		StokKodu = row[0].strip( )

		Marka = Turkcelestir( row[1].strip( ).encode( 'utf8' ) )

		UrunAdi_s = row[2].replace( "'", "" ).replace( 'ERK ', 'ERKEK ' ).replace( 'BYN', 'BAYAN' ).replace( 'PNT', 'PANTOLON' ).replace( '_', '' ).replace( 'JJ ', 'JACK JONES ' ).replace( 'JACK&JONES ', 'JACK JONES ' ).replace( 'İSP. ', 'İSPANYOL ' ).replace( '.', '' ).replace( '-', '' ).replace( 'ÇCK ', 'ÇOCUK ' ).replace( 'EŞF ', 'EŞOFMAN ' ).replace( 'ESF ', 'EŞOFMAN ' ).replace( 'AYKB ', 'AYAKKABI ' ).replace( 'AYK ', 'AYAKKABI ' ).replace( ' TK ', ' TAKIMI ' ).replace( 'BBK ', 'BEBEK ' ).replace( 'EŞFALT', 'EŞOFMAN ALT' ).replace( 'ESFALT', 'EŞOFMAN ALT' ).replace( 'ESFÜST', 'EŞOFMAN ÜST' ).replace( 'ESFUST', 'EŞOFMAN ÜST' ).replace( 'ESFTK', 'EŞOFMAN TAKIMI' ).replace( 'Eşorfman', 'EŞOFMAN' ).replace( 'USX', 'UNISEX' )

		UrunAdi = row[2].encode( 'utf8' ).replace( "'", "" ).replace( 'ERK ', 'ERKEK ' ).replace( 'BYN', 'BAYAN' ).replace( 'PNT', 'PANTOLON' ).replace( '_', '' ).replace( 'JJ ', 'JACK JONES ' ).replace( 'JACK&JONES ', 'JACK JONES ' ).replace( 'İSP. ', 'İSPANYOL ' ).replace( '.', '' ).replace( '-', '' ).replace( 'ÇCK ', 'ÇOCUK ' ).replace( 'EŞF ', 'EŞOFMAN ' ).replace( 'ESF ', 'EŞOFMAN ' ).replace( 'AYKB ', 'AYAKKABI ' ).replace( 'AYK ', 'AYAKKABI ' ).replace( ' TK ', ' TAKIMI ' ).replace( 'BBK ', 'BEBEK ' ).replace( 'EŞFALT', 'EŞOFMAN ALT' ).replace( 'ESFALT', 'EŞOFMAN ALT' ).replace( 'ESFÜST', 'EŞOFMAN ÜST' ).replace( 'ESFUST', 'EŞOFMAN ÜST' ).replace( 'ESFTK', 'EŞOFMAN TAKIMI' ).replace( 'Eşorfman', 'EŞOFMAN' ).replace( 'USX', 'UNISEX' )

		Renk = Turkcelestir( row[3].strip( ).encode( 'utf8' ) )
		Beden = Turkcelestir( row[4].strip( ).encode( 'utf8' ) )
		Kavala = Turkcelestir( row[5].strip( ).encode( 'utf8' ) )

		VaryantStokSayisi = row[8]
		Barkod = row[9].strip( )

		Cinsiyeti = Turkcelestir( row[10].strip( ).encode( 'utf8' ) )

		UstKati = Turkcelestir( row[11].strip( ).replace( '/', '-' ).encode( 'utf8' ) )
		OrtaKati = Turkcelestir( row[12].strip( ).replace( '/', '-' ).encode( 'utf8' ) )
		AltKati = Turkcelestir( row[13].strip( ).replace( '/', '-' ).encode( 'utf8' ) )

		RenkKodu = Turkcelestir( row[14].strip( ).encode( 'utf8' ) )

		try:
			Fiyat = row[6]
			EFiyat = row[7]

			if Decimal( EFiyat ) > Decimal( Fiyat ):
				Firsat = 1
			else:
				Firsat = 0
		except:
			Fiyat = 99999
			EFiyat = 99999
			Firsat = 0

		ServisCalisiyorKaydet = ServisDurumu.objects.get( id = ServisKaydet.id )
		ServisCalisiyorKaydet.Calisiyor = True
		ServisCalisiyorKaydet.save( )

		urunkontrolet = "select id from kategoriler_urun where StokKodu = '" + StokKodu + "'"
		cursor.execute( urunkontrolet )

		if cursor.rowcount == 0:

			sss = "INSERT INTO kategoriler_urun(UstKat_id, OrtaKat_id, Marka_id, Logo, Adi, StokKodu, Slug, Fiyat, EFiyat, KdvOrani, Desi, Yeni, Firsat, KisaURL, URL, URLdenYukle)"

			sss += " VALUES((select id from kategoriler_kategori where Adi='" + UstKati + "' and Cinsiyet_id=(select id from kategoriler_cinsiyet where Adi='" + Cinsiyeti + "')),  "

			sss += " (select id from kategoriler_ortakategori where Adi='" + OrtaKati + "' and UstKat_id=(select id from kategoriler_kategori where Adi='" + UstKati + "' and Cinsiyet_id=(select id from kategoriler_cinsiyet where Adi='" + Cinsiyeti + "'))), "

			sss += " (select id from kategoriler_marka where Adi= '" + Marka + "'), "
			sss += " 'urun_resimleri/" + str( StokKodu ) + ".jpg',"
			sss += " '" + SezonBilgisiSil( UrunAdi ) + "', '" + StokKodu + "', "
			sss += " '" + slugify( SezonBilgisiSil( UrunAdi_s ) + StokKodu ) + "', "  # 18.06.2014 15:21:14#      -  Muslu YÜKSEKTEPE
			sss += " '" + str( Fiyat ) + "', '" + str( EFiyat ) + "', 0, 2, 1, '" + str( Firsat ) + "', "
			sss += " '', '', 0);"

			cursor.execute( sss )

			# logging.info(sss)

			ssss = "INSERT INTO kategoriler_urun_AltKat (urun_id, altkategori_id) "
			ssss += "VALUES "
			ssss += "((select id from kategoriler_urun where StokKodu='" + StokKodu + "'),  "
			ssss += "(SELECT id FROM kategoriler_altkategori where Adi='" + AltKati + "' and  UstKat_id=(SELECT id FROM kategoriler_kategori WHERE Adi= '" + UstKati + "' AND Cinsiyet_id=(SELECT id FROM kategoriler_cinsiyet WHERE Adi='" + Cinsiyeti + "'))  and  OrtaKat_id in(SELECT id FROM kategoriler_ortakategori WHERE Adi= '" + OrtaKati + "'))); "

			cursor.execute( ssss )

			cursor.close( )
			cursor = connections["default"].cursor( )

		else:

			urunguncelle = "UPDATE kategoriler_urun SET Tarih='" + str( datetime.datetime.now( ) ) + "',  Firsat='" + str( Firsat ) + "', Fiyat = '" + str( Fiyat ) + "', EFiyat = '" + str( EFiyat ) + "', Adi = '" + SezonBilgisiSil( UrunAdi ) + "' WHERE StokKodu = '" + StokKodu + "';"
			cursor.execute( urunguncelle )

			urunaltkatkontrolet = "select id from kategoriler_urun_AltKat where urun_id = (select id from kategoriler_urun where StokKodu='" + StokKodu + "');"

			cursor.execute( urunaltkatkontrolet )

			if cursor.rowcount == 0:

				ssss = "INSERT INTO kategoriler_urun_AltKat (urun_id, altkategori_id) "
				ssss += "VALUES "
				ssss += "((select id from kategoriler_urun where StokKodu='" + StokKodu + "'),  "
				ssss += "(SELECT id FROM kategoriler_altkategori where Adi='" + AltKati + "' and  UstKat_id=(SELECT id FROM kategoriler_kategori WHERE Adi= '" + UstKati + "' AND Cinsiyet_id=(SELECT id FROM kategoriler_cinsiyet WHERE Adi='" + Cinsiyeti + "'))  and  OrtaKat_id in(SELECT id FROM kategoriler_ortakategori WHERE Adi= '" + OrtaKati + "'))); "


				# # logging.info(str(ssss))
				cursor.execute( ssss )

		islem = "YOK "

		cursor.execute( "SELECT MAX(ID)+1 FROM kategoriler_varyant" )
		varyantSonIDsi = cursor.fetchone( )[0]

		cursor.execute( "SELECT MAX(ID)+1 FROM kategoriler_varyant_AltKat" )
		varyantAltKatSonIDsi = cursor.fetchone( )[0]

		varyantkontrolet = "select id from kategoriler_varyant where Barkod = '" + Barkod + "'"
		cursor.execute( varyantkontrolet )

		if cursor.rowcount == 0:
			# try:
			sssss = u"INSERT INTO kategoriler_varyant(Cinsiyet_id, Urunu_id, Renk, RenkKodu, Beden, Kavala, Barkod, StokSayisi, EkstraFiyat)"
			sssss += " VALUES ("
			sssss += "(SELECT id FROM kategoriler_cinsiyet WHERE Adi='" + Cinsiyeti + "'), "
			sssss += "(select id from kategoriler_urun where StokKodu='" + StokKodu + "'), "
			sssss += "'" + Renk + "', "
			sssss += "'" + RenkKodu + "', "
			sssss += "'" + Beden + "', "
			sssss += "'" + Kavala + "', "
			sssss += "'" + Barkod + "', "
			sssss += "'" + VaryantStokSayisi + "', 0);"

			# logging.info( str( sssss ) )

			cursor.execute( sssss )

			ssssss = "INSERT INTO kategoriler_varyant_AltKat (varyant_id, altkategori_id) "
			ssssss += "VALUES ("
			ssssss += "'" + str( varyantSonIDsi ) + "',  "
			ssssss += "(SELECT id FROM kategoriler_altkategori where Adi='" + AltKati + "' and  UstKat_id=(SELECT id FROM kategoriler_kategori WHERE Adi= '" + UstKati + "' AND Cinsiyet_id=(SELECT id FROM kategoriler_cinsiyet WHERE Adi='" + Cinsiyeti + "'))  and  OrtaKat_id in(SELECT id FROM kategoriler_ortakategori WHERE Adi= '" + OrtaKati + "'))); "

			# # logging.info( "" )
			# # logging.info( "" )
			# logging.info( str( ssssss ) )

			cursor.execute( ssssss )
			islem = "Eklendi"
		# except:
		# pass
		else:
			varyantguncelle = "UPDATE kategoriler_varyant SET StokSayisi = '" + VaryantStokSayisi + "' WHERE Barkod = '" + Barkod + "';"
			cursor.execute( varyantguncelle )
			islem = "Güncellendi"

		islemgorenler += islem + " StokKodu: " + StokKodu + " Renk: " + Renk + " " + " Beden: " + Beden + " Kavala: " + Kavala + " " + SezonBilgisiSil( UrunAdi ) + " Barkod: " + Barkod + " Stok Sayısı: " + VaryantStokSayisi + " - " + str( datetime.datetime.now( ) ) + "<br />"

	now = datetime.datetime.now( )

	ServisTamamlandiKaydet = ServisDurumu.objects.get( id = ServisKaydet.id )
	ServisTamamlandiKaydet.Calisiyor = False
	ServisTamamlandiKaydet.Tamamlandi = True
	ServisTamamlandiKaydet.BitisTarihi = now
	ServisTamamlandiKaydet.save( )

	html = "<html><body>%s.<br />%s </body></html>" % ( now, islemgorenler)
	return HttpResponse( html )


# except:
# ServisKaydet = ServisDurumu( Gun = GunSayisi, Sorgu = sorgumm, Tamamlandi = False )
# ServisKaydet.save( )


def urunv3KategoriEkle( request ):
	cursor = connections["default"].cursor( )
	cursorV3 = connections["V3"].cursor( )

	reload( sys )
	sys.setdefaultencoding( "utf-8" )

	cursorV3.execute( "CREATE TABLE #MarkaEkle (Marka NVARCHAR(MAX) COLLATE Latin1_General_CI_AS)" );

	SQL_MarkaEkle = """INSERT INTO #MarkaEkle (Marka) SELECT distinct ProductAtt03 as Marka from V3_DOGUKAN.dbo.ProductPriceAndInventory3 (N'TR', N'6', N'7', N'D01', 'def', 100)

    where       LTRIM(RTRIM(Barcode)) != '' AND Barcode IS NOT NULL
                and LTRIM(RTRIM(ProductDescription)) != '' AND ProductDescription IS NOT NULL
                and LTRIM(RTRIM(ColorDescription)) != '' AND ColorDescription IS NOT NULL
                and LTRIM(RTRIM(ProductAtt02Desc)) != '' AND ProductAtt02Desc IS NOT NULL
                and LTRIM(RTRIM(ProductHierarchyLevel01)) != '' AND ProductHierarchyLevel01 IS NOT NULL
                and LTRIM(RTRIM(ProductHierarchyLevel02)) != '' AND ProductHierarchyLevel02 IS NOT NULL
                and LTRIM(RTRIM(ProductHierarchyLevel03)) != '' AND ProductHierarchyLevel03 IS NOT NULL
                and LTRIM(RTRIM(ProductAtt03)) != '' AND ProductAtt03 IS NOT NULL AND ProductAtt03 not in ('ARENA', 'CAT', 'CUBE', 'ENDER SPOR', 'FARELL', 'LACOSTE',  'DOGUKAN', 'BOAONDA', 'GD', 'JAGHS', 'NORTHERN REBEL', 'PROTEST', 'REEF', 'VODEN', 'WIPEOUT', 'ZEUS', 'MOLTEN', 'BYOS',  'WILSON', 'NONE', 'HAS', 'HITECH', 'HITEC', 'PINK STEP', 'DOCKERS-G', 'ONEILL')"""

	# # logging.info(sorgumm)



	cursorV3.execute( SQL_MarkaEkle )
	cursorV3.execute( "SELECT * FROM #MarkaEkle" )

	html = "<h1>İşlem Gören Markalar:</h1><br />"

	for row in cursorV3.fetchall( ):

		MarkaAdi = Turkcelestir( row[0].strip( ).encode( 'utf8' ) )
		cursor.execute( "INSERT IGNORE INTO SporMarketDB.kategoriler_marka SET Adi = '" + MarkaAdi + "', Slug = '" + slugify( MarkaAdi ) + "'" )

		html += MarkaAdi + "<br />"

	cursorV3.execute( "CREATE TABLE #kategoriEkle (Cinsiyet NVARCHAR(MAX),  UstKat NVARCHAR(MAX), OrtaKat NVARCHAR(MAX), AltKat NVARCHAR(MAX) COLLATE Latin1_General_CI_AS)" );

	SQL_Gecici_Tablo = "INSERT INTO #kategoriEkle (Cinsiyet, UstKat, OrtaKat, AltKat)"
	SQL_Gecici_Tablo += " SELECT "
	SQL_Gecici_Tablo += " distinct"
	SQL_Gecici_Tablo += " ProductAtt02Desc as Cinsiyet,"
	SQL_Gecici_Tablo += " ProductHierarchyLevel01 as UstKat,"
	SQL_Gecici_Tablo += " ProductHierarchyLevel02 as OrtaKat,"
	SQL_Gecici_Tablo += " ProductHierarchyLevel03 as AltKat"
	SQL_Gecici_Tablo += " from V3_DOGUKAN.dbo.ProductPriceAndInventory3 (N'TR', N'6', N'7', N'D01', 'def', 300) where Barcode != '' and ProductHierarchyLevel01 != '' and ProductHierarchyLevel02 != '' and ProductHierarchyLevel03 != '' and ProductAtt02Desc != '' and ProductAtt03 != '' "

	# # logging.info( SQL_Gecici_Tablo)


	cursorV3.execute( SQL_Gecici_Tablo )
	cursorV3.execute( "SELECT * FROM #kategoriEkle" )

	html += "<br /><br /><h1>İşlem Gören Kategoriler:</h1><br />"

	for row in cursorV3.fetchall( ):

		Cinsiyeti = Turkcelestir( row[0].strip( ).encode( 'utf8' ) )

		UstKati = Turkcelestir( row[1].strip( ).replace( '/', '-' ).encode( 'utf8' ) )
		OrtaKati = Turkcelestir( row[2].strip( ).replace( '/', '-' ).encode( 'utf8' ) )
		AltKati = Turkcelestir( row[3].strip( ).replace( '/', '-' ).encode( 'utf8' ) )

		cursor.execute( "INSERT IGNORE INTO SporMarketDB.kategoriler_cinsiyet SET Adi = '" + Cinsiyeti + "', Slug = '" + slugify( Cinsiyeti ) + "'" )

		SQL_KatEkle = "  INSERT INTO SporMarketDB.kategoriler_kategori (Cinsiyet_id, Adi, Slug) "
		SQL_KatEkle += "  SELECT a.Cinsiyet_id, a.Adi, a.Slug"
		SQL_KatEkle += "  FROM"
		SQL_KatEkle += "  (SELECT (select id from SporMarketDB.kategoriler_cinsiyet where Adi='" + str( Cinsiyeti ) + "') Cinsiyet_id, '" + str( UstKati ) + "' Adi,'" + slugify( UstKati ) + "' Slug) a "
		SQL_KatEkle += "  WHERE NOT EXISTS (SELECT 1 FROM SporMarketDB.kategoriler_kategori WHERE Cinsiyet_id=(select id from SporMarketDB.kategoriler_cinsiyet where Adi='" + str( Cinsiyeti ) + "') and Adi = '" + str( UstKati ) + "' and Slug = '" + slugify( UstKati ) + "')"

		cursor.execute( SQL_KatEkle )

		SQL_OrtaKatEkle = "  INSERT INTO SporMarketDB.kategoriler_ortakategori (UstKat_id, Adi, Slug) "
		SQL_OrtaKatEkle += "  SELECT a.UstKat_id, a.Adi, a.Slug"
		SQL_OrtaKatEkle += "  FROM"
		SQL_OrtaKatEkle += "  (SELECT (select id from SporMarketDB.kategoriler_kategori where Cinsiyet_id=(select id from SporMarketDB.kategoriler_cinsiyet where Adi='" + str( Cinsiyeti ) + "') and Adi='" + str( UstKati ) + "') UstKat_id, '" + str( OrtaKati ) + "' Adi,'" + slugify( OrtaKati ) + "' Slug) a "
		SQL_OrtaKatEkle += "  WHERE NOT EXISTS (SELECT 1 FROM SporMarketDB.kategoriler_ortakategori WHERE UstKat_id=(select id from SporMarketDB.kategoriler_kategori where Cinsiyet_id=(select id from SporMarketDB.kategoriler_cinsiyet where Adi='" + str( Cinsiyeti ) + "') and Adi='" + str( UstKati ) + "') and Adi = '" + str( OrtaKati ) + "' and Slug = '" + slugify( OrtaKati ) + "')"

		cursor.execute( SQL_OrtaKatEkle )

		SQL_AltKatEkle = "  INSERT INTO SporMarketDB.kategoriler_altkategori (UstKat_id, OrtaKat_id, Adi, Slug) "
		SQL_AltKatEkle += "  SELECT a.UstKat_id, a.OrtaKat_id, a.Adi, a.Slug"
		SQL_AltKatEkle += "  FROM"
		SQL_AltKatEkle += "  (SELECT (select id from SporMarketDB.kategoriler_kategori where Cinsiyet_id=(select id from SporMarketDB.kategoriler_cinsiyet where Adi='" + str( Cinsiyeti ) + "') and Adi='" + str( UstKati ) + "') UstKat_id, (select id from SporMarketDB.kategoriler_ortakategori where  UstKat_id=(select id from SporMarketDB.kategoriler_kategori where Cinsiyet_id=(select id from SporMarketDB.kategoriler_cinsiyet where Adi='" + str( Cinsiyeti ) + "') and  Adi='" + str( UstKati ) + "') and  Adi='" + str( OrtaKati ) + "') OrtaKat_id, '" + str( AltKati ) + "' Adi,'" + slugify( AltKati ) + "' Slug) a "
		SQL_AltKatEkle += "  WHERE NOT EXISTS (SELECT 1 FROM SporMarketDB.kategoriler_altkategori WHERE UstKat_id=(select id from SporMarketDB.kategoriler_kategori where Cinsiyet_id=(select id from SporMarketDB.kategoriler_cinsiyet where Adi='" + str( Cinsiyeti ) + "') and Adi='" + str( UstKati ) + "') and OrtaKat_id= (select id from SporMarketDB.kategoriler_ortakategori where UstKat_id=(select id from SporMarketDB.kategoriler_kategori where Cinsiyet_id=(select id from SporMarketDB.kategoriler_cinsiyet where Adi='" + str( Cinsiyeti ) + "') and  Adi='" + str( UstKati ) + "') and Adi='" + str( OrtaKati ) + "') and Adi = '" + str( AltKati ) + "' and Slug = '" + slugify( AltKati ) + "')"

		cursor.execute( SQL_AltKatEkle )

		html += Cinsiyeti + " >>> " + UstKati + " >> " + OrtaKati + " > " + AltKati + "<br />"

	return HttpResponse( html )


def bilgi( request ):
	if request.method == 'POST':

		isimsoyisim = request.POST['isimsoyisim']
		telefon = request.POST['telefon']
		soru = request.POST['soru']
		stokkodu = request.POST['stokkodu']
		try:
			UyeID = Kullanicilar.objects.get( user = request.user ).uyeid
		except:
			UyeID = request.COOKIES.get( 'UyeID' )

		Mail = u'<h1>Bilgi Talebi</h1><br />'
		Mail += u'İsim Soyisim: ' + UyeID + ' ' + isimsoyisim + '<br />'
		Mail += u'Telefon: ' + telefon + '<br />'
		Mail += u'StokKodu: ' + stokkodu + '<br />'
		Mail += u'Soru: ' + soru + '<br />'

		msg = EmailMultiAlternatives( 'Spor Market Bilgi Talebi', Mail, 'bilgi@spormarket.com.tr', ['bilgi@spormarket.com.tr'] )
		msg.content_subtype = "html"
		msg.send( )

		return HttpResponse( "Mesajınız gönderildi!\n\nLütfen telefonunuzu açık tutunuz." )

	else:
		return HttpResponse( "Hata oluştu!" )


@csrf_protect
def iletisimform( request ):
	if request.method == 'POST':

		isimsoyisim = request.POST['isimsoyisim']
		telefon = request.POST['telefon']
		soru = request.POST['soru']
		email = request.POST['email']
		try:
			UyeID = Kullanicilar.objects.get( user = request.user ).uyeid
		except:
			UyeID = request.COOKIES.get( 'UyeID' )

		from django.core.mail import EmailMultiAlternatives




		Mail = u'<h1>İletişim Formu</h1><br />'
		Mail += u'İsim Soyisim: ' + UyeID + ' ' + isimsoyisim + '<br />'
		Mail += u'Telefon: ' + telefon + '<br />'
		Mail += u'Soru: ' + soru + '<br />'

		msg = EmailMultiAlternatives( 'Spor Market İletişim Formu', Mail, email, ['destek@spormarket.com.tr', email] )
		msg.content_subtype = "html"
		msg.send( )

		return HttpResponse( "Mesajınız gönderildi!\n\nLütfen telefonunuzu açık tutunuz." )

	else:
		return HttpResponse( "Hata oluştu!" )


def goo_shorten_url( url ):
	try:

		post_url = "http://po.st/api/shorten?longUrl=" + url + "&apiKey=1D87B898-BEA2-439E-ACBF-9199338B421C"

		postdata = { 'longUrl': url }
		headers = { 'Content-Type': 'application/json' }
		req = urllib2.Request( post_url, json.dumps( postdata ), headers )
		ret = urllib2.urlopen( req ).read( )

		return json.loads( ret )['short_url']
	except:
		return ""


def Turkcelestir( Veri ):
	return str( Veri ).replace( "\xc3\x87", 'Ç' ).replace( "\xc7", 'Ç' ).replace( "\xc3\x9c", 'Ü' ).replace( "\xdc", 'Ü' ).replace( u"\xc3\x96", 'Ö' ).replace( "\u0130", 'İ' ).replace( u"\u015e", 'Ş' ).replace( u"\u015f", 'Ş' )


def SezonBilgisiSil( UrunAdi ):
	TemizHali = ""

	for i in UrunAdi.split( ' ' ):

		if not "/" in i and len( i ) > int( settings.__getattr__( "URUNADI_TEMIZLE" ) ):  #~ Pzt 20 Oca 2014 14:49:04 EET  - Muslu YÜKSEKTEPE
			TemizHali += i + " "

	return TemizHali.replace( "\xc3\x87", 'Ç' ).replace( "\xc3\x9c", 'Ü' ).replace( "\xc3\x96", 'Ö' )

