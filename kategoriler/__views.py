# -*- coding: utf-8 -*-


import random
import string
import datetime
import json
import sys
import urllib2
from decimal import Decimal

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.template.defaultfilters import slugify
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db import connection
from django.db.models import F
from django.views.decorators.csrf import csrf_protect

from bankalar.models import Bankalar
from uyeler.models import Kullanicilar





# ~ from django.db.models import Avg, Max, Min





# ~ Aksesuar_Listem              =       ['AKSESUAR', 'ANAHTARLIK', 'ATKI', 'AYAKKABI ÇANTASI', 'BERE', 'BİLEKLİK', 'BONE', 'CÜZDAN', 'ÇANTA', 'ÇORAP', 'ELDİVEN', 'FREE BAG', 'HAVLU', 'KEMER', 'SIRT ÇANTASI', 'ŞAPKA']
# ~ Ayakkabi_Listem              =       ['AYAKKABI', 'BABET', 'BASKETBOL AYKB.', 'BOT', 'HALI SAHA AYAKKABI', 'KOŞU AYKB.', 'KRAMPON', 'SANDALET', 'TENİS AYKB.', 'TRAINING AYKB.']
#~ Tekstil_Listem               =       ['ATLET', 'BİKİNİ', 'CEKET', 'ÇORAP', 'EŞOFMAN ALTI', 'EŞOFMAN TK', 'EŞOFMAN ÜSTÜ', 'ETEK', 'FORMA', 'GÖMLEK', 'KAPRİ', 'MAYO', 'MONT', 'PANTOLON', 'POLO YAKA T-SHIRT', 'SWEAT', 'İPLİK', 'ŞORT MAYO', 'TAYT', 'T-SHIRT', 'YELEK']





# 26.02.2014 16:41:53#      -  Muslu YÜKSEKTEPE



def AnaSayfa( request ):
	#~
	#~ encoksatilan_listesi        =       Urun.objects.filter(EnCokSatan=1, AltKat__id__isnull=False, varyant__AltKat__id__isnull=False).order_by('-id').distinct()[0:20]
	#~ yeni_urun_listesi           =       Urun.objects.filter(Yeni=1, AltKat__id__isnull=False, varyant__AltKat__id__isnull=False).order_by('-id').distinct()[0:20]


	vitrin_urun_listesi = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0, Vitrin = 1, AltKat__id__isnull = False, varyant__AltKat__id__isnull = False ).order_by( 'id' )[0:3]
	vitrin_urun_listesii = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0, Vitrin = 1, AltKat__id__isnull = False, varyant__AltKat__id__isnull = False ).order_by( 'id' )[4:7]
	vitrin_urun_listesiii = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0, Vitrin = 1, AltKat__id__isnull = False, varyant__AltKat__id__isnull = False ).order_by( 'id' )[7:10]

	firsat_urun_listesi = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0, Firsat = 1, AltKat__id__isnull = False, varyant__AltKat__id__isnull = False ).order_by( '-id' )[0:3]
	firsat_urun_listesii = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0, Firsat = 1, AltKat__id__isnull = False, varyant__AltKat__id__isnull = False ).order_by( '-id' )[4:7]
	firsat_urun_listesiii = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0, Firsat = 1, AltKat__id__isnull = False, varyant__AltKat__id__isnull = False ).order_by( '-id' )[7:10]

	response = render_to_response( 'index.html', {

	'firsat_urun_listesi': firsat_urun_listesi, 'firsat_urun_listesii': firsat_urun_listesii, 'firsat_urun_listesiii': firsat_urun_listesiii, 'vitrin_urun_listesi': vitrin_urun_listesi, 'vitrin_urun_listesii': vitrin_urun_listesii, 'vitrin_urun_listesiii': vitrin_urun_listesiii,

	}, context_instance = RequestContext( request ) )

	try:
		if request.user.is_authenticated( ):

			UyeID = Kullanicilar.objects.get( user = request.user ).uyeid

	except:
		response.delete_cookie( 'UyeID' )

	return response


#~ def MarkaListesi(request, urunleri):
#~ marka_listesi               =       Marka.objects.all()
#~ return render_to_response('marka.html', {'marka_listesi':marka_listesi}, context_instance=RequestContext(request))



def MarkaDetayi( request, slug ):
	marka_listesi = Marka.objects.all( )
	marka_detayi = Marka.objects.get( Slug = slug )

	varyant_listesi_BedenNumara = Varyant.objects.filter( Urunu__Marka__Slug = slug ).annotate( ToplamStok_Sayisi = Sum( 'StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0 ).values( 'Beden' ).distinct( ).order_by( 'Beden' )

	BedenNumaraFiltresi = ""
	KavalaFiltresi = ""

	cerezim = request.COOKIES

	if cerezim:

		for i in cerezim:

			if i.startswith( "BN" ) and i != "":
				BedenNumaraFiltresi += cerezim.get( i ) + ","

			if i.startswith( "K" ) and i != "":
				KavalaFiltresi += cerezim.get( i ) + ","

	SecilenBedenler = BedenNumaraFiltresi[0:-1].split( "," )
	SecilenKavala = KavalaFiltresi[0:-1].split( "," )

	VarolanBedenler = ""
	VarolanKavalalar = ""

	for i in varyant_listesi_BedenNumara:
		VarolanBedenler += "BN" + slugify( i.get( 'Beden' ) ) + ","

	if not 'BN' + slugify( BedenNumaraFiltresi[0:-1] ) in VarolanBedenler:
		SecilenBedenler = ""

	if SecilenBedenler != "" and SecilenBedenler[0] != "" and SecilenKavala[0] == "":
		urunlistesi = Urun.objects.filter( Marka__Slug = slug, AltKat__id__isnull = False, varyant__AltKat__id__isnull = False, varyant__Beden = SecilenBedenler[0] ).annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0 ).order_by( '-id', 'Marka' )


	elif SecilenBedenler != "" and SecilenBedenler[0] != "" and SecilenKavala[0] != "":

		if len( SecilenKavala ) == 1:
			urunlistesi = Urun.objects.filter( Marka__Slug = slug, AltKat__id__isnull = False, varyant__AltKat__id__isnull = False, varyant__Beden = SecilenBedenler[0], varyant__Kavala = SecilenKavala[0] ).annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0 ).order_by( '-id', 'Marka' )

		else:
			urunlistesi = Urun.objects.filter( Marka__Slug = slug, AltKat__id__isnull = False, varyant__AltKat__id__isnull = False, varyant__Beden = SecilenBedenler[0], varyant__Kavala__in = SecilenKavala ).annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0 ).order_by( '-id', 'Marka' )

	else:
		urunlistesi = Urun.objects.filter( Marka__Slug = slug, AltKat__id__isnull = False, varyant__AltKat__id__isnull = False ).annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0 ).order_by( '-id', 'Marka' )

	varyant_listesi_Kavala = Varyant.objects.filter( AltKat__id__isnull = False, Urunu__Marka__Slug = slug, Beden__in = SecilenBedenler ).annotate( ToplamStok_Sayisi = Sum( 'StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0 ).values( 'Kavala' ).distinct( ).order_by( 'Kavala' )

	if len( varyant_listesi_Kavala ) == 0:
		varyant_listesi_Kavala = { }

	#~ print urunlistesi.aggregate(Avg('Fiyat'), Max('Fiyat'), Min('Fiyat'))

	paginator = Paginator( urunlistesi, 12 )

	page = request.GET.get( 'sayfa' )
	try:
		urunler = paginator.page( page )
	except PageNotAnInteger:
		urunler = paginator.page( 1 )
	except EmptyPage:
		urunler = paginator.page( paginator.num_pages )

	response = render_to_response( 'marka_detayi.html', { 'urunler': urunler, 'varyant_listesi_BedenNumara': varyant_listesi_BedenNumara, 'varyant_listesi_Kavala': varyant_listesi_Kavala, 'BedenNumaraFiltresi': BedenNumaraFiltresi, 'KavalaFiltresi': KavalaFiltresi, 'urunlistesi': urunlistesi, 'marka_detayi': marka_detayi, 'marka_listesi': marka_listesi

	}, context_instance = RequestContext( request ) )

	for i in varyant_listesi_Kavala:
		VarolanKavalalar += "K" + slugify( i.get( 'Kavala' ) ) + ","

	if not 'BN' + slugify( BedenNumaraFiltresi[0:-1] ) in VarolanBedenler:
		response.delete_cookie( 'BN' + slugify( BedenNumaraFiltresi[0:-1] ) )

	if not 'K' + slugify( KavalaFiltresi[0:-1] ) in VarolanKavalalar:
		response.delete_cookie( 'K' + slugify( KavalaFiltresi[0:-1] ) )

	return response


#~ return render_to_response('marka_detayi.html', {'urunler':urunler, 'marka_detayi':marka_detayi, 'marka_listesi':marka_listesi}, context_instance=RequestContext(request))


def MarkaDetayi_json( request, page, slug ):
	urunlistesi = Urun.objects.filter( Marka__Slug = slug ).order_by( '-id' )

	paginator = Paginator( urunlistesi, 12 )

	try:
		urunler = paginator.page( page )
	except (EmptyPage, InvalidPage):
		urunler = paginator.page( paginator.num_pages )

	template = 'tracks.json'

	return render_to_response( template, { 'urunler': urunler } )


def KategoriListesi( request ):
	kategori_listesi = Kategori.objects.all( )
	return render_to_response( 'kategori.html', { 'kategori_listesi': kategori_listesi }, context_instance = RequestContext( request ) )


def OrtaKategoriListesi( request, slug ):
	#~ try:

	ust_kategori_listesi = Kategori.objects.all( )
	ust_kategori_bilgileri = Kategori.objects.get( Slug = slug )

	orta_kategoriler = OrtaKategori.objects.filter( UstKat__Slug = slug )

	#~ except OrtaKategori.DoesNotExist:
	#~ return render_to_response('404.html')

	return render_to_response( 'ortakategori.html', { 'ust_kategori_bilgileri': ust_kategori_bilgileri, 'Kslug': slug, 'orta_kategoriler': orta_kategoriler, 'ust_kategori_listesi': ust_kategori_listesi }, context_instance = RequestContext( request ) )


def AltKategoriListesi( request, UstKat, slug ):
	try:

		ust_kategori_listesi = Kategori.objects.all( )
		orta_kategori_listesi = OrtaKategori.objects.filter( UstKat__Slug = UstKat )

		orta_kategori_bilgileri = OrtaKategori.objects.get( Slug = slug, UstKat__Slug = UstKat )

		alt_kategoriler = AltKategori.objects.filter( OrtaKat__Slug = slug, OrtaKat__UstKat__Slug = UstKat )


	except AltKategori.DoesNotExist:
		return render_to_response( '404.html' )

	return render_to_response( 'altkategori.html', { 'orta_kategori_bilgileri': orta_kategori_bilgileri, 'KUstKat': UstKat, 'KSlug': slug, 'alt_kategoriler': alt_kategoriler, 'orta_kategori_listesi': orta_kategori_listesi, 'ust_kategori_listesi': ust_kategori_listesi }, context_instance = RequestContext( request ) )


def UrunListesi( request, UstKat, OrtaKat, slug, AltKatid ):
	#~ try:


	ustkat_muslu = request.get_full_path( ).split( '-' )[0].replace( '/', '' )
	ortakat_muslu = request.get_full_path( ).split( '-' )[1]
	slug_muslu = request.get_full_path( ).split( '-' )[2:-3]
	#~ altkatid_muslu              =       request.get_full_path().split('-')[-1].replace('/','')

	slug_musslu = ""

	for i in slug_muslu:
		slug_musslu += i + "-"

	alt_kategori_bilgileri = AltKategori.objects.get( OrtaKat__UstKat__Slug = ustkat_muslu, OrtaKat__Slug = ortakat_muslu, Slug = slug_musslu[0:-1] )

	varyant_listesi_BedenNumara = Varyant.objects.filter( AltKat__id = AltKatid ).annotate( ToplamStok_Sayisi = Sum( 'StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0 ).values( 'Beden' ).distinct( ).order_by( 'Beden' )

	markaliste = Urun.objects.filter( AltKat__id = AltKatid ).values_list( 'Marka__Adi' ).distinct( ).order_by( 'Marka' )

	markalar = ()

	for i in markaliste:
		markalar += i

	BedenNumaraFiltresi = ""
	KavalaFiltresi = ""

	cerezim = request.COOKIES

	if cerezim:

		for i in cerezim:

			if i.startswith( "BN" ) and i != "":
				BedenNumaraFiltresi += cerezim.get( i ) + ","

			if i.startswith( "K" ) and i != "":
				KavalaFiltresi += cerezim.get( i ) + ","

	SecilenBedenler = BedenNumaraFiltresi[0:-1].split( "," )
	SecilenKavala = KavalaFiltresi[0:-1].split( "," )

	VarolanBedenler = ""
	VarolanKavalalar = ""

	for i in varyant_listesi_BedenNumara:
		VarolanBedenler += "BN" + slugify( i.get( 'Beden' ) ) + ","

	if not 'BN' + slugify( BedenNumaraFiltresi[0:-1] ) in VarolanBedenler:
		SecilenBedenler = ""

	if SecilenBedenler != "" and SecilenBedenler[0] != "" and SecilenKavala[0] == "":
		urunlistesi = Urun.objects.filter( AltKat = AltKatid, AltKat__id__isnull = False, varyant__AltKat__id__isnull = False, varyant__Beden = SecilenBedenler[0] ).annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0 ).order_by( '-id', 'Marka' )


	elif SecilenBedenler != "" and SecilenBedenler[0] != "" and SecilenKavala[0] != "":

		if len( SecilenKavala ) == 1:
			urunlistesi = Urun.objects.filter( AltKat = AltKatid, AltKat__id__isnull = False, varyant__AltKat__id__isnull = False, varyant__Beden = SecilenBedenler[0], varyant__Kavala = SecilenKavala[0] ).annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0 ).order_by( '-id', 'Marka' )

		else:
			urunlistesi = Urun.objects.filter( AltKat = AltKatid, AltKat__id__isnull = False, varyant__AltKat__id__isnull = False, varyant__Beden = SecilenBedenler[0], varyant__Kavala__in = SecilenKavala ).annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0 ).order_by( '-id', 'Marka' )

	else:
		urunlistesi = Urun.objects.filter( AltKat = AltKatid, AltKat__id__isnull = False, varyant__AltKat__id__isnull = False ).annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0 ).order_by( '-id', 'Marka' )

	varyant_listesi_Kavala = Varyant.objects.filter( AltKat__id__isnull = False, AltKat__id = AltKatid, Beden__in = SecilenBedenler ).annotate( ToplamStok_Sayisi = Sum( 'StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0 ).values( 'Kavala' ).distinct( ).order_by( 'Kavala' )

	if len( varyant_listesi_Kavala ) == 0:
		varyant_listesi_Kavala = { }

	#~ print urunlistesi.aggregate(Avg('Fiyat'), Max('Fiyat'), Min('Fiyat'))

	paginator = Paginator( urunlistesi, 12 )

	page = request.GET.get( 'sayfa' )
	try:
		urunler = paginator.page( page )
	except PageNotAnInteger:
		urunler = paginator.page( 1 )
	except EmptyPage:
		urunler = paginator.page( paginator.num_pages )

	response = render_to_response( 'urunler.html', { 'urunler': urunler, 'alt_kategori_bilgileri': alt_kategori_bilgileri, 'KUstKat': UstKat, 'KOrtaKat': OrtaKat, 'KSlug': slug, 'varyant_listesi_BedenNumara': varyant_listesi_BedenNumara, 'varyant_listesi_Kavala': varyant_listesi_Kavala, 'BedenNumaraFiltresi': BedenNumaraFiltresi, 'KavalaFiltresi': KavalaFiltresi, 'urunlistesi': urunlistesi, 'markalar': markalar,

	}, context_instance = RequestContext( request ) )

	for i in varyant_listesi_Kavala:
		VarolanKavalalar += "K" + slugify( i.get( 'Kavala' ) ) + ","

	if not 'BN' + slugify( BedenNumaraFiltresi[0:-1] ) in VarolanBedenler:
		response.delete_cookie( 'BN' + slugify( BedenNumaraFiltresi[0:-1] ) )

	if not 'K' + slugify( KavalaFiltresi[0:-1] ) in VarolanKavalalar:
		response.delete_cookie( 'K' + slugify( KavalaFiltresi[0:-1] ) )

	return response


def UrunListesi_json( request, page, uk, slug ):
	urunlistesi = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0, AltKat__OrtaKat__UstKat__Slug = uk, AltKat__Slug = slug ).order_by( '-id' )
	paginator = Paginator( urunlistesi, 12 )

	try:
		urunler = paginator.page( page )
	except (EmptyPage, InvalidPage):
		urunler = paginator.page( paginator.num_pages )

	template = 'tracks.json'

	return render_to_response( template, { 'urunler': urunler } )


def UrunDetayi( request, marka, slug ):
	cerezim = request.COOKIES

	BedenNumaraFiltresi = ""
	KavalaFiltresi = ""

	if cerezim:

		for i in cerezim:

			if i.startswith( "BN" ) and i != "":
				BedenNumaraFiltresi = cerezim.get( i )

			if i.startswith( "K" ) and i != "":
				KavalaFiltresi = cerezim.get( i )

	urun_detayi = Urun.objects.get( Slug = slug )
	#~ siparis_linki            =       ''.join([random.choice(string.digits + string.letters) for i in range(0, 90)])
	#~ ust_kategorisi              =       Kategori.objects.get(id=AltKatid.split('_')[0])
	#~ orta_kategorisi             =       OrtaKategori.objects.get(id=AltKatid.split('_')[1])
	#~ alt_kategorisi              =       AltKategori.objects.get(id=AltKatid.split('_')[2])

	urun_varyant_detayi = Varyant.objects.filter( AltKat__id__isnull = False, Urunu_id = urun_detayi.id )
	toplam_stok_sayisi = urun_varyant_detayi.aggregate( Sum( 'StokSayisi' ) )

	RenkeGoreBeden = ""
	Sayi = 0

	for i in urun_varyant_detayi:
		if i.StokSayisi != 0:
			Sayi += 1
			RenkeGoreBeden += str( i.id ) + "=" + str( i.Beden ) + ", "




		#~ if settings.__getattr__("ALTKATEGORIYE_AIT_URUNLERI_GOSTER"):
		#~ altkat_diger_urunler    =       Urun.objects.annotate(ToplamStok_Sayisi=Sum('varyant__StokSayisi')).filter(ToplamStok_Sayisi__gt=0,  AltKat__id__isnull=False, varyant__AltKat__id__isnull=False).exclude(id=urun_detayi.id).order_by('-id').distinct()[0:6]
		#~ else:
		#~ altkat_diger_urunler    =       {}
		#~
		#~
		#~ if settings.__getattr__("FIYATI_BENZER_URUNLERI_GOSTER"):
		#~ fiyat_diger_urunler     =       Urun.objects.annotate(ToplamStok_Sayisi=Sum('varyant__StokSayisi')).filter(ToplamStok_Sayisi__gt=0,  AltKat__id__isnull=False,  varyant__AltKat__id__isnull=False, Fiyat__gte = (urun_detayi.Fiyat - int(settings.__getattr__("FIYAT_ARALIGI"))), Fiyat__lte = (urun_detayi.Fiyat + int(settings.__getattr__("FIYAT_ARALIGI")))).exclude(id=urun_detayi.id).order_by('-id').distinct()[0:6]  #~ Pzt 20 Oca 2014 11:17:32 EET  - Muslu YÜKSEKTEPE
		#~ else:
		#~ fiyat_diger_urunler     =       {}

	if settings.__getattr__( "MARKAYA_AIT_URUNLERI_GOSTER" ):
		marka_diger_urunler = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0, AltKat__id__isnull = False, varyant__AltKat__id__isnull = False, Marka__Slug = marka ).exclude( id = urun_detayi.id ).order_by( '-id' ).distinct( )[0:6]  #~ Pzt 20 Oca 2014 11:18:04 EET  - Muslu YÜKSEKTEPE
	else:
		marka_diger_urunler = { }

	eslestirilmis_urunlerr = { }

	if settings.__getattr__( "ESLESTIRILMIS_URUNLERI_GOSTER" ):

		eslestirilmis_urunler = BenzerUrunler.objects.filter( Q( urun = urun_detayi.id ) | Q( eslesenurun = urun_detayi.id ), urun__AltKat__id__isnull = False, urun__varyant__AltKat__id__isnull = False ).order_by( 'id' )

		for s in eslestirilmis_urunler:
			eslestirilmis_urunlerr = s.eslesenurun

	else:
		eslestirilmis_urunlerr = { }

	if settings.__getattr__( "ESLESTIRILMIS_KATEGORIURUNLERI_GOSTER" ):
		eslestirilmis_kategori_urunleri = Urun.objects.raw( "SELECT * FROM Django.dbo.kategoriler_urun where id in (SELECT urun_id FROM Django.dbo.kategoriler_urun_AltKat where altkategori_id in (SELECT altkategori_id FROM Django.dbo.kategoriler_benzerkategoriler_BenzerKat where benzerkategoriler_id in (SELECT id FROM Django.dbo.kategoriler_benzerkategoriler where AltKat_id in (SELECT altkategori_id FROM Django.dbo.kategoriler_urun_AltKat where urun_id='" + str( urun_detayi.id ) + "'))));" )
	else:
		eslestirilmis_kategori_urunleri = { }

	if len( list( eslestirilmis_kategori_urunleri ) ) != 0:
		return render_to_response( 'urun_detayi.html', { 'urun_detayi': urun_detayi, 'urun_varyant_detayi': urun_varyant_detayi,  #~ 'altkat_diger_urunler':altkat_diger_urunler,
		                                                 'toplam_stok_sayisi': toplam_stok_sayisi, 'marka_diger_urunler': marka_diger_urunler,  #~ 'fiyat_diger_urunler':fiyat_diger_urunler,

		                                                 'eslestirilmis_kategori_urunleri': eslestirilmis_kategori_urunleri, 'eslestirilmis_urunlerr': eslestirilmis_urunlerr, 'BedenNumaraFiltresi': BedenNumaraFiltresi, 'KavalaFiltresi': KavalaFiltresi, }, context_instance = RequestContext( request ) )
	else:
		return render_to_response( 'urun_detayi.html', { 'urun_detayi': urun_detayi, 'urun_varyant_detayi': urun_varyant_detayi, 'toplam_stok_sayisi': toplam_stok_sayisi, 'marka_diger_urunler': marka_diger_urunler, 'eslestirilmis_urunlerr': eslestirilmis_urunlerr, 'BedenNumaraFiltresi': BedenNumaraFiltresi, 'KavalaFiltresi': KavalaFiltresi, }, context_instance = RequestContext( request ) )


def VaryantGoster( request, muslu, ceylan, VaryantID ):
	#~ try:
	UyeID = Kullanicilar.objects.get( user = request.user ).uyeid

	varyant_detayi = Varyant.objects.get( id = VaryantID.split( '_' )[0] )
	urun_detayi = Urun.objects.get( id = varyant_detayi.Urunu_id )

	VaryantTutari = str( urun_detayi.Fiyat + varyant_detayi.EkstraFiyat ).replace( ',', '.' )  # Islem tutari

	Kargo_Kamp_Fiy_tamamla = { }
	kargo_kamp_urunler = { }
	kargo_kamp_urunleri = { }

	Kargo_Kamp_Fiy = Decimal( settings.__getattr__( "KARGO_KAMPANYA" ) )
	Kargo_Kamp_Ara = Decimal( settings.__getattr__( "KARGO_KAMPANYA_ARALIGI" ) )

	try:

		Sepetteki = SepetUrunler.objects.filter( SepetID = Sepet.objects.get( UyeID = UyeID, Tamamlandi = False ) )
		SepetTutari = 0

		for i in Sepetteki:
			SepetTutari += i.Adet * i.Fiyat

		KampIcinEnAzTutar = (Kargo_Kamp_Fiy - SepetTutari)
		KampIcinEnFazlaTutar = (Kargo_Kamp_Fiy - SepetTutari) + Kargo_Kamp_Ara

		if Decimal( VaryantTutari ) <= SepetTutari and KampIcinEnAzTutar > 0:
			kargo_kamp_urunleri = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0, AltKat__id__isnull = False, Fiyat__gte = KampIcinEnAzTutar, Fiyat__lte = KampIcinEnFazlaTutar ).exclude( id = urun_detayi.id ).order_by( '-id' ).distinct( )[0:9]



	except:

		KampIcinEnAzTutar = Kargo_Kamp_Fiy - Decimal( VaryantTutari )
		KampIcinEnFazlaTutar = (KampIcinEnAzTutar + Kargo_Kamp_Ara)

		if Decimal( VaryantTutari ) <= Kargo_Kamp_Fiy and KampIcinEnAzTutar > 0:
			kargo_kamp_urunleri = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0, AltKat__id__isnull = False, Fiyat__gte = KampIcinEnAzTutar, Fiyat__lte = KampIcinEnFazlaTutar ).exclude( id = urun_detayi.id ).order_by( '-id' ).distinct( )[0:9]

	response = render_to_response( 'varyantgoster.html', { 'urun_detayi': urun_detayi, 'varyant_detayi': varyant_detayi, 'VaryantTutari': VaryantTutari, 'kargo_kamp_urunleri': kargo_kamp_urunleri,

	                                                       'KampIcinEnAzTutar': KampIcinEnAzTutar, 'KampIcinEnFazlaTutar': KampIcinEnFazlaTutar, 'Kargo_Kamp_Fiy': Kargo_Kamp_Fiy, 'UyeID': UyeID, 'Cinsiyet': VaryantID.split( '_' )[1], 'AltKategoriTuru': VaryantID.split( '_' )[3] }, context_instance = RequestContext( request ) )
	return response


#~ except:
#~ return HttpResponseRedirect("/")


def tkug( request ):
	if request.is_ajax( ):

		VaryantTutari = request.GET['YeniTutar']
		VaryantID = request.GET['VaryantID']
		UyeID = Kullanicilar.objects.get( user = request.user ).uyeid

		Kargo_Kamp_Fiy = Decimal( settings.__getattr__( "KARGO_KAMPANYA" ) )
		Kargo_Kamp_Ara = Decimal( settings.__getattr__( "KARGO_KAMPANYA_ARALIGI" ) )

		try:

			Sepetteki = SepetUrunler.objects.filter( SepetID = Sepet.objects.get( UyeID = UyeID, Tamamlandi = False ) )
			SepetTutari = 0

			for i in Sepetteki:
				SepetTutari += i.Adet * i.Fiyat

			KampIcinEnAzTutar = Kargo_Kamp_Fiy - Decimal( SepetTutari )
			KampIcinEnFazlaTutar = (KampIcinEnAzTutar + Kargo_Kamp_Ara)

		except:

			KampIcinEnAzTutar = Kargo_Kamp_Fiy - Decimal( VaryantTutari )
			KampIcinEnFazlaTutar = (KampIcinEnAzTutar + Kargo_Kamp_Ara)

		if Decimal( VaryantTutari ) < Decimal( KampIcinEnAzTutar ):
			kargo_kamp_urunleri = Urun.objects.filter( AltKat__id__isnull = False, varyant__AltKat__id__isnull = False, Fiyat__gte = KampIcinEnAzTutar, Fiyat__lte = KampIcinEnFazlaTutar )[0:9]


		else:
			kargo_kamp_urunleri = { }

		MEsaj = ""

		if len( kargo_kamp_urunleri ) == 0:
			MEsaj = str( KampIcinEnAzTutar ) + " - " + str( KampIcinEnFazlaTutar ) + " TL aralığında uygun ürün bulunamadı"
		else:
			MEsaj = str( KampIcinEnAzTutar ) + " - " + str( KampIcinEnFazlaTutar ) + " TL aralığında ki ürünler"

		return render_to_response( 'adetegorekargo.html', { 'kargo_kamp_urunleri': kargo_kamp_urunleri,

		                                                    'KampIcinEnAzTutar': KampIcinEnAzTutar, 'KampIcinEnFazlaTutar': KampIcinEnFazlaTutar, 'Kargo_Kamp_Fiy': Kargo_Kamp_Fiy, 'VaryantTutari': VaryantTutari, 'MEsaj': MEsaj }, context_instance = RequestContext( request ) )


@login_required
def SepetimeEkle( request ):
	VaryantAdeti = request.POST.get( "VaryantAdeti" )
	VaryantID = request.POST.get( "VaryantID" )
	Cinsiyet = request.POST.get( "Cinsiyet" )
	AltKategoriTuru = request.POST.get( "AltKategoriTuru" )


	#~ #   print VaryantAdeti, VaryantID, Cinsiyet, AltKategoriTuru


	from django.db.models import F




	UyeID = Kullanicilar.objects.get( user = request.user ).uyeid

	varyant_detayi = Varyant.objects.get( id = VaryantID )

	#~ print VaryantAdeti, varyant_detayi.StokSayisi, int(VaryantAdeti) > int(varyant_detayi.StokSayisi)

	if int( VaryantAdeti ) > int( varyant_detayi.StokSayisi ):
		VaryantAdeti = varyant_detayi.StokSayisi

	urun_detayi = Urun.objects.get( id = varyant_detayi.Urunu_id )

	VaryantTutari = str( urun_detayi.Fiyat + varyant_detayi.EkstraFiyat ).replace( ',', '.' )  # Islem tutari

	varolankayit, yenikayit = Sepet.objects.get_or_create( UyeID = UyeID, Tamamlandi = False )

	if yenikayit:

		SepetinID = Sepet.objects.get( UyeID = varolankayit.UyeID, Tamamlandi = False )

		SepetUrunlerEkle = SepetUrunler( SepetID = SepetinID, VaryantID = VaryantID, Adet = VaryantAdeti, Fiyat = VaryantTutari, EFiyat = urun_detayi.EFiyat, StokKodu = urun_detayi.StokKodu, RenkKodu = varyant_detayi.RenkKodu, Renk = varyant_detayi.Renk, Beden = varyant_detayi.Beden, Kavala = varyant_detayi.Kavala, Cinsiyet = Cinsiyet, AltKategoriTuru = AltKategoriTuru )
		SepetUrunlerEkle.save( )

	else:

		SepetinID = Sepet.objects.get( UyeID = UyeID, Tamamlandi = False )

		SepetteUrunVarMi = SepetUrunler.objects.filter( SepetID = SepetinID, VaryantID = VaryantID )

		if SepetteUrunVarMi:

			SepetUrunler.objects.filter( SepetID = SepetinID, VaryantID = VaryantID ).update( Adet = F( 'Adet' ) + VaryantAdeti )

		else:

			SepetUrunlerEkle = SepetUrunler( SepetID = SepetinID, VaryantID = VaryantID, Adet = VaryantAdeti, Fiyat = VaryantTutari, EFiyat = urun_detayi.EFiyat, StokKodu = urun_detayi.StokKodu, RenkKodu = varyant_detayi.RenkKodu, Renk = varyant_detayi.Renk, Beden = varyant_detayi.Beden, Kavala = varyant_detayi.Kavala, Cinsiyet = Cinsiyet, AltKategoriTuru = AltKategoriTuru )
			SepetUrunlerEkle.save( )

	response = render_to_response( 'sepeteekle.html', { 'UyeID': UyeID, }, context_instance = RequestContext( request ) )

	response.set_cookie( 'VaryantID', VaryantID )
	response.set_cookie( 'VaryantAdeti', VaryantAdeti )
	response.set_cookie( 'StokKodu', urun_detayi.StokKodu )

	return response


@login_required
def Sepetim( request ):
	try:

		SepettekiUrunlerim = { }
		BankaListesi = { }
		Sepetim = { }

		UyeBilgileri = Kullanicilar.objects.get( user = request.user )

		Sepetim = Sepet.objects.get( UyeID = UyeBilgileri.uyeid, Tamamlandi = 0 )
		SepettekiUrunlerim = SepetUrunler.objects.filter( SepetID = Sepetim.id )
		BankaListesi = Bankalar.objects.filter( Aktif = 1 ).order_by( 'Adi', )

		response = render_to_response( 'sepetim.html', { 'UyeBilgileri': UyeBilgileri, 'SepettekiUrunlerim': SepettekiUrunlerim, 'BankaListesi': BankaListesi }, context_instance = RequestContext( request ) )

		return response


	except Sepet.DoesNotExist:
		return redirect( "/" )


@login_required
def SepetimUrunSil( request, gVaryantID ):
	SepetUrunler.objects.get( VaryantID = gVaryantID, SepetID = Sepet.objects.get( UyeID = Kullanicilar.objects.get( user = request.user ).uyeid, Tamamlandi = False ) ).delete( )
	return HttpResponseRedirect( "/sepetim/" )


@csrf_protect
@login_required
def Odeme( request ):  #~ Cum 24 Oca 2014 15:21:22 EET  - Muslu YÜKSEKTEPE

	#~ try:

	OdemeYapildiMi = Sepet.objects.get( UyeID = Kullanicilar.objects.get( user = request.user ).uyeid, Tamamlandi = False )

	for i in request.POST.getlist( 'group1' ):
		BankaID = i.split( '_' )[0]
		ToplamTaksit = i.split( '_' )[1]
		Tutar = i.split( '_' )[2]
		EkTaksit = i.split( '_' )[3]
		SirketTaksit = i.split( '_' )[4]

	import base64, hashlib




	oid = ''.join( [random.choice( string.digits + string.letters ) for i in range( 0, 10 )] )
	rnd = ''.join( [random.choice( string.digits + string.letters ) for i in range( 0, 30 )] )

	amount = Tutar  # Islem tutari

	if ToplamTaksit == "0":
		taksit = ""
	else:
		taksit = ToplamTaksit  # taksit sayisi

	BankaBilgileri = Bankalar.objects.get( id = BankaID )

	BankaAdi = BankaBilgileri.Adi

	clientId = BankaBilgileri.MusteriNumarasi
	okUrl = str( settings.__getattr__( "OKURL" ) )
	failUrl = str( settings.__getattr__( "FAILURL" ) )
	islemtipi = str( settings.__getattr__( "ISLEMTIPI" ) )
	storekey = str( settings.__getattr__( "STOREKEY" ) )

	hashstr = clientId + oid + amount + okUrl + failUrl + islemtipi + taksit + rnd + storekey

	hashi = base64.b64encode( hashlib.sha1( hashstr ).digest( ) )

	return render_to_response( 'est.html',

	                           { 'hashi': hashi, 'oid': oid, 'rnd': rnd, 'amount': amount, 'taksit': taksit, 'hashi': hashi, 'clientId': clientId, 'okUrl': okUrl, 'failUrl': failUrl, 'storekey': storekey, 'SirketTaksit': SirketTaksit, 'EkTaksit': EkTaksit, 'BankaAdi': BankaAdi },

	                           context_instance = RequestContext( request ) )


#~ except:
#~ return redirect("/") # zaten ödeme yapıldı ise ana sayfa yönlendir


@csrf_protect
@login_required
def PayOdeme( request ):  #~ Cum 24 Oca 2014 15:40:54 EET  - Muslu YÜKSEKTEPE


	#~ SayfaYuklendiMi  = request.COOKIES.has_key('SayfaYuklendiMi')

	SiparisNosu = ""

	try:

		if request.POST['mdStatus'] == "0":
			Sonuc = "İptal Edildi"
		if request.POST['mdStatus'] == "1":
			Sonuc = "Başarılı"
		if request.POST['mdStatus'] == "2":
			Sonuc = "Kart sahibi banka veya Kart 3D-Secure Üyesi Değil"
		if request.POST['mdStatus'] == "3":
			Sonuc = "Kart prefixi 3D-Secure sisteminde tanımlı değil"
		if request.POST['mdStatus'] == "4":
			Sonuc = "Doğrulama Denemesi"
		if request.POST['mdStatus'] == "5":
			Sonuc = "Sistem ulaşılabilir değil"
		if request.POST['mdStatus'] == "6":
			Sonuc = "3D-Secure Hatası"
		if request.POST['mdStatus'] == "7":
			Sonuc = "Sistem Hatası"
		if request.POST['mdStatus'] == "8":
			Sonuc = "Geçersiz Kart"
		if request.POST['mdStatus'] == "9":
			Sonuc = "Üye İşyeri 3D-Secure sistemine kayıtlı değil"

		if request.POST['mdStatus'] != "1":

			Sonuc = Sonuc + " " + str( request.POST['mdErrorMsg'] )

		else:


			UyeID = Kullanicilar.objects.get( user = request.user ).uyeid

			SiparisNosu = ''.join( [random.choice( string.digits ) for i in range( 0, 10 )] )

			SiparisTamamla = Sepet.objects.get( UyeID = UyeID, Tamamlandi = False )
			SiparisTamamla.Tamamlandi = 1
			SiparisTamamla.save( )

			SiparisKaydet = Siparis( SiparisNo = SiparisNosu, UyeID = UyeID, SepetID = SiparisTamamla.id, ToplamTutar = request.POST["amount"], ToplamTaksit = int( request.POST["taksit"] ), EkTaksit = int( request.POST["ektaksit"] ), SirketTaksit = int( request.POST["sirkettaksit"] ) )
			SiparisKaydet.save( )

			SepetUrunBul = SepetUrunler.objects.filter( SepetID = SiparisTamamla.id )

			for i in SepetUrunBul:

				VaryantAdetAzalt = Varyant.objects.get( id = i.VaryantID )
				VaryantAdetAzalt.StokSayisi = VaryantAdetAzalt.StokSayisi - i.Adet
				VaryantAdetAzalt.save( )

		response = render_to_response( 'estsonuc.html', { 'Sonuc': Sonuc, 'SiparisNosu': SiparisNosu }, context_instance = RequestContext( request ) )

		if request.POST['mdStatus'] == "1":
			response.delete_cookie( 'VaryantID' )
			response.delete_cookie( 'VaryantAdeti' )
			response.delete_cookie( 'StokKodu' )

		return response

	except:
		return redirect( "/" )



	#~ Cum 24 Oca 2014 16:47:46 EET  - Muslu YÜKSEKTEPE


@login_required
def PayOdemei( request, SiparisNo, Sonuc ):
	return render_to_response( 'estsonuc.html', { 'Sonuc': Sonuc, 'SiparisNo': SiparisNo }, context_instance = RequestContext( request ) )


@login_required
def Yazdir( request, sepetID, siparisID ):
	SepetUrunlerBilgileri = SepetUrunler.objects.filter( SepetID = Sepet.objects.get( id = sepetID ) )
	SiparisBilgileri = Siparis.objects.get( id = siparisID )
	KullaniciBilgileri = Kullanicilar.objects.get( uyeid = SiparisBilgileri.UyeID )

	return render_to_response( 'yazdir.html', { 'SepetUrunlerBilgileri': SepetUrunlerBilgileri, 'SiparisBilgileri': SiparisBilgileri, 'KullaniciBilgileri': KullaniciBilgileri }, context_instance = RequestContext( request ) )



#~ Çrş 05 Şub 2014 10:05:20 EET  - Muslu YÜKSEKTEPE
# 18.02.2014 12:13:48#      -  Muslu YÜKSEKTEPE


YasakListesi = ['sikis', 'sikti', 'sikme', 'sokus', 'sokma', 'domal', 'amcik', 'xxx', 'yarak', 'yarrak', 'domal', '31', 'adrianne', 'adult', 'amcik', 'anal', 'analcum', 'animal', 'asshole', 'atesli', 'azdirici', 'azgin', 'bakire', 'baldiz', 'beat', 'biseksuel', 'bitch', 'bok', 'boob', 'bosal', 'buyutucu', 'cenabet', 'ciftles', 'ciplak', 'ciplak', 'citir', 'cock suck', 'crap', 'cukpenis', 'cunub', 'dick', 'domal', 'dump', 'emme', 'ensest', 'erotic', 'erotig', 'erotik', 'esbian', 'escinsel', 'escort', 'eskort', 'etek', 'fantezi', 'fetish', 'fire', 'firikik', 'free', 'fuck', 'gay', 'geciktirici', 'genital', 'gerdek', 'girl', 'gizli', 'gogus', 'got', 'hatun', 'haydar', 'hayvan', 'hentai', 'hikaye', 'homemade', 'homoseksüel', 'hot', 'impud', 'itiraf', 'jigolo', 'kalca', 'kaltak', 'kerhane', 'kinky', 'kizlik', 'kudur', 'kulot', 'lesbian', 'lezbiyen', 'liseli', 'lolita', 'lust', 'mastirbas', 'masturbasyon', 'mature', 'meme', 'mom', 'naughty', 'nefes', 'nubile', 'nude', 'nudist', 'olgun', 'opusme', 'oral', 'orgazm', 'orospu', 'panty', 'partner', 'penis', 'pervert', 'pezevenk', 'popo', 'porn', 'pussy', 'sapik', 'sarisin', 'sehvet', 'seks', 'sevisme', 'sex', 'showgirl', 'sicak', 'sicak', 'sik', 'sisman', 'sok', 'sperm', 'suck', 'surtuk', 'swinger', 'taciz', 'tecavuz', 'teen', 'terbiyesiz', 'travesti', 'tube', 'turbanli', 'vagina', 'vajina', 'virgin', 'vurvur', 'xn', 'xx', 'yala', 'yarak', 'yarak', 'yarrak', 'yasak', 'yerli', 'yetiskin', 'zoo', 'a.p', 'a.q', 'adrianne', 'adult', 'amcik', 'amcık', 'anal', 'analcum', 'asshole', 'ateşli', 'atesli', 'azdırıcı', 'azgın', 'bakire', 'biseksuel', 'bitch', 'bok', 'boob', 'boşalmak', 'bosalmak', 'buyutucu', 'büyütücü', 'cenabet', 'ciftles', 'çiftleş', 'ciplak', 'çıplak', 'citir', 'çıtır', 'cock', 'crap', 'cukpenis', 'cunub', 'cünüp', 'cünup', 'dick', 'daşşak', 'daşşağ', 'domal', 'emme', 'ensest', 'erotic', 'erotig', 'erotik', 'esbian', 'escinsel', 'escort', 'eskort', 'esrar', 'etek', 'fahise', 'fahişe', 'fantezi', 'fantazi', 'fetish', 'fire', 'firikik', 'fuck', 'gay', 'gey', 'geciktirici', 'genital', 'girl', 'gizli', 'gogus', 'göğüs', 'got', 'göt', 'hatun', 'hentai', 'hikaye', 'homoseksuel', 'hot', 'jigolo', 'kalça', 'kalça', 'kaltak', 'kancik', 'kancık', 'kinky', 'kizlik', 'kızlık', 'kudur', 'külot', 'külot', 'lesbian', 'lezbien', 'lezbiyen', 'liseli', 'lolita', 'lust', 'mastirbas', 'mastırbas', 'mastürbasyon', 'mastürbas', 'mature', 'meme', 'naughty', 'nefes', 'nude', 'nudist', 'olgun', 'opusme', 'öpüşme', 'oral', 'orgazm',
                'orospu', 'panty', 'partner', 'penis', 'pervert', 'pic', 'piç', 'pkk', 'popo', 'porn', 'pussy', 'sapik', 'sapık', 'sarisin', 'sarışın', 'sehvet', 'şehvet', 'seks', 'sevişme', 'sevişme', 'sex']


def UrunAra( request ):
	q = request.POST.get( 'q' )

	if not q:
		q = request.GET.get( 'q' )

	if not q.encode( 'utf-8' ) in YasakListesi:

		cursor = connection.cursor( )

		cursor.execute( """
                    if exists ( select * from Django.dbo.kategoriler_aramalar where Aranan = '""" + q.encode( 'utf-8' ) + """')

                        UPDATE Django.dbo.kategoriler_aramalar SET AranmaSayisi = (AranmaSayisi+1) WHERE Aranan = '""" + q.encode( 'utf-8' ) + """'

                    else

                        INSERT INTO Django.dbo.kategoriler_aramalar (Aranan, AranmaSayisi, UyeID, IslemTarihi) VALUES (N'""" + q.encode( 'utf-8' ) + """', 1, N'""" + str( request.user ) + """',  CAST('""" + str( datetime.datetime.now( ) ) + """' AS DATETIME2));
                """ )

		Bulunanlar = Urun.objects.filter( Q( Adi__icontains = q ) | Q( StokKodu__icontains = q ), AltKat__id__isnull = False, varyant__AltKat__id__isnull = False ).order_by( 'id' ).distinct( )

		paginator = Paginator( Bulunanlar, 12 )

		page = request.GET.get( 'sayfa' )
		try:
			urunler = paginator.page( page )
		except PageNotAnInteger:
			urunler = paginator.page( 1 )
		except EmptyPage:
			urunler = paginator.page( paginator.num_pages )

		return render_to_response( 'aramasonucu.html', { 'urunler': urunler, 'q': q }, context_instance = RequestContext( request ) )

	else:

		return HttpResponseRedirect( "/yasakkelime/" )


#~ @login_required(login_url='/accounts/login/')




def goo_shorten_url( url ):
	#~ post_url = 'https://www.googleapis.com/urlshortener/v1/url'
	#~ postdata = {'longUrl':url}
	#~ headers = {'Content-Type':'application/json'}
	#~ req = urllib2.Request(
	#~ post_url,
	#~ json.dumps(postdata),
	#~ headers
	#~ )
	#~ ret = urllib2.urlopen(req).read()

	try:

		post_url = "http://po.st/api/shorten?longUrl=" + url + "&apiKey=1D87B898-BEA2-439E-ACBF-9199338B421C"

		postdata = { 'longUrl': url }
		headers = { 'Content-Type': 'application/json' }
		req = urllib2.Request( post_url, json.dumps( postdata ), headers )
		ret = urllib2.urlopen( req ).read( )

		return json.loads( ret )['short_url']
	except:
		return ""


@login_required
def urunv3( request ):
	#~ try:


	lower_map = { ord( u'I' ): u'I', ord( u'İ' ): u'i',  #~ ord(u'Ş'): u'ş',  #~ ord(u'Ç'): u'Ç',  #~ ord(u'Ö'): u'ö',  #~ ord(u'Ğ'): u'ğ',  #~ ord(u'Ü'): u'ü', }

	              GunSayisi = request.GET.get( 'gun', '1' )
	StokKodu_Sorgu = request.GET.get( 'model', '' )

	StokKodu_SorguVarMi = ""

	if StokKodu_Sorgu != "":
		StokKodu_SorguVarMi = " and ProductCode = '" + StokKodu_Sorgu + "'"

	cursor = connection.cursor( )

	cursor.execute( "CREATE TABLE #TempTable (StokKodu NVARCHAR(255), Marka NVARCHAR(255), Adi NVARCHAR(250), Renk NVARCHAR(255), RenkKodu NVARCHAR(255), Beden NVARCHAR(255), Kavala NVARCHAR(255), Fiyat NVARCHAR(255), EFiyati NVARCHAR(255), StokSayisi NVARCHAR(255), Barkod NVARCHAR(255), UstKat NVARCHAR(255), OrtaKat NVARCHAR(255), AltKat NVARCHAR(255)  COLLATE Latin1_General_CI_AS)" );

	cursor.execute( """INSERT INTO #TempTable (StokKodu, Marka, Adi, Renk, RenkKodu, Beden, Kavala, Fiyat, EFiyati, StokSayisi, Barkod, UstKat, OrtaKat, AltKat)

                            SELECT
                                    ProductCode as StokKodu, --0
                                    replace(ProductHierarchyLevel01, '''', '') as Marka,  --1
                                    replace(ProductDescription, '''', '') as Adi, --2
                                    ColorDescription as Renk, --3
                                    ItemDim1Code as Beden, --4
                                    ItemDim2Code as Kavala, --5
                                    Price1 as Fiyat, --6
                                    Price2 as EFiyati, --7
                                    Warehouse1InventoryQty as StokSayisi, --8
                                    Barcode as Barkod, --9

                                    ProductAtt02Desc as UstKat, --10
                                    ProductHierarchyLevel02 as OrtaKat, --11
                                    ProductHierarchyLevel03 as AltKat, --12
                                    ColorCode as RenkKodu --13

                                    from V3_DOGUKAN.dbo.ProductPriceAndInventory (N'TR', N'6', N'7', N'D01', SPACE(0), 'def', """ + GunSayisi + """) where Barcode != '' """ + StokKodu_SorguVarMi + """ ; """ )

	cursor.execute( "SELECT * FROM #TempTable" )

	Firsat = 0

	reload( sys )
	sys.setdefaultencoding( "latin-1" )

	for row in cursor.fetchall( ):

		StokKodu = Turkcelestir( row[0].strip( ) )

	try:
		Marka = Turkcelestir( row[1].strip( ) ).title( )
	except:
		Marka = "Tanimsiz"
	#~ Pzt 20 Oca 2014 16:00:33 EET  - Muslu YÜKSEKTEPE

	UrunAdi_s = row[2].replace( 'ERK ', 'ERKEK ' ).replace( 'BYN', 'BAYAN' ).replace( 'PNT', 'PANTOLON' ).replace( '_', '' ).replace( 'JJ ', '' ).replace( 'JACK JONES ', '' ).replace( 'İSP. ', 'İSPANYOL ' ).replace( '.', '' ).replace( '-', '' ).replace( 'ÇCK ', 'ÇOCUK ' ).replace( 'EŞF ', 'EŞOFMAN ' ).replace( 'ESF ', 'EŞOFMAN ' ).replace( 'AYKB ', 'AYAKKABI ' ).replace( 'AYK ', 'AYAKKABI ' ).replace( ' TK ', ' TAKIMI ' ).replace( 'BBK ', 'BEBEK ' ).replace( 'EŞFALT', 'EŞOFMAN ALT' ).replace( 'ESFALT', 'EŞOFMAN ALT' ).replace( 'ESFÜST', 'EŞOFMAN ÜST' ).replace( 'ESFUST', 'EŞOFMAN ÜST' ).replace( 'ESFTK', 'EŞOFMAN TAKIMI' ).replace( 'Eşorfman', 'EŞOFMAN' )

	UrunAdi = row[2].encode( 'utf8' ).replace( 'ERK ', 'ERKEK ' ).replace( 'BYN', 'BAYAN' ).replace( 'PNT', 'PANTOLON' ).replace( '_', '' ).replace( 'JJ ', '' ).replace( 'JACK JONES ', '' ).replace( 'İSP. ', 'İSPANYOL ' ).replace( '.', '' ).replace( '-', '' ).replace( 'ÇCK ', 'ÇOCUK ' ).replace( 'EŞF ', 'EŞOFMAN ' ).replace( 'ESF ', 'EŞOFMAN ' ).replace( 'AYKB ', 'AYAKKABI ' ).replace( 'AYK ', 'AYAKKABI ' ).replace( ' TK ', ' TAKIMI ' ).replace( 'BBK ', 'BEBEK ' ).replace( 'EŞFALT', 'EŞOFMAN ALT' ).replace( 'ESFALT', 'EŞOFMAN ALT' ).replace( 'ESFÜST', 'EŞOFMAN ÜST' ).replace( 'ESFUST', 'EŞOFMAN ÜST' ).replace( 'ESFTK', 'EŞOFMAN TAKIMI' ).replace( 'Eşorfman', 'EŞOFMAN' )


	#~ Pzt 13 Oca 2014 19:22:26 EET  - Muslu YÜKSEKTEPE
	#~ Sal 14 Oca 2014 19:12:55 EET  - Muslu YÜKSEKTEPE

	Fiyat = row[6]
	EFiyat = row[7]

	if not Fiyat:
		Fiyat = "0"
	if not EFiyat:
		EFiyat = "0"

	Barkod = row[9].strip( )

	StokSayisi = row[8]

	try:
		Renk = Turkcelestir( row[3].strip( ).encode( 'utf8' ) )
	except:
		Renk = "Tanimsiz"

	RenkKodu = Turkcelestir( row[13].strip( ).encode( 'utf8' ) )

	Beden = Turkcelestir( row[4].strip( ) )
	Kavala = Turkcelestir( row[5].strip( ) )

	UstKati = Turkcelestir( row[10].strip( ) )

	if UstKati == "ERKEK":
		UstKati = "Bay"
	if UstKati == "BEBEK":
		UstKati = "Çocuk"
	if UstKati == "UNISEX":
		UstKati = "Bay"
	if UstKati == "COCUK":
		UstKati = "Çocuk"
	if UstKati == "":
		UstKati = "Kategorisiz"

	OrtaKati = Turkcelestir( row[11].strip( ) )
	AltKati = Turkcelestir( row[12].strip( ) )

	if OrtaKati == "BOT-ÇİZME":
		OrtaKati = "Ayakkabı"
	if OrtaKati == "AYAKKABI":
		OrtaKati = "Ayakkabı"
	if OrtaKati == "TERLİK":
		OrtaKati = "Ayakkabı"
	if OrtaKati == "Terlik":
		OrtaKati = "Ayakkabı"

	if OrtaKati == "AKSESUAR":
		UstKati = "Aksesuar";
		OrtaKati = "Aksesuar"
	if OrtaKati == "SPOR MALZEMESİ":
		UstKati = "Aksesuar";
		OrtaKati = "Ekipman"
	if OrtaKati == "Spor Malzemesi":
		UstKati = "Aksesuar";
		OrtaKati = "Ekipman"
	if OrtaKati == "":
		UstKati = "Kategorisiz";
		OrtaKati = "Kategorisiz"

	if UstKati == "":
		OrtaKati = "Kategorisiz"
	if UstKati == "Kategorisiz":
		OrtaKati = "Kategorisiz";
		AltKati = "Kategorisiz"

	if AltKati == "JEAN PANTOLON":
		AltKatii = "Pantolon-Jean"
	if AltKati == "T-SHIRT":
		AltKatii = "TShirt"
	if AltKati == "SWEAT":
		AltKatii = "Sweatshirt"
	if AltKati == "FERMUARLI SWEAT":
		AltKatii = "Sweatshirt"
	if AltKati == "POLO YAKA T-SHIRT":
		AltKatii = "TShirt"
	if AltKati == "YELEK":
		AltKatii = "Yelek-Hırka"
	if AltKati == "PANTOLON":
		AltKatii = "Pantolon-Jean"
	if AltKati == "MONT":
		AltKatii = "Ceket-Mont"
	if AltKati == "EŞOFMAN ALTI":
		AltKatii = "Eşofman Alt"
	if AltKati == "EŞOFMAN ÜSTÜ":
		AltKatii = "Eşofman Üst"
	if AltKati == "EŞOFMAN TK":
		AltKatii = "Eşofman Takım"
	if AltKati == "GÖMLEK":
		AltKatii = "Gömlek"
	if AltKati == "AYAKKABI":
		AltKatii = "Günlük"
	if AltKati == "KRAMPON":
		AltKatii = "Futbol"
	if AltKati == "KOŞU AYKB.":
		AltKatii = "Koşu"
	if AltKati == "CÜZDAN":
		AltKatii = "Aksesuar";
		UstKati = "Aksesuar";
		OrtaKati = "Aksesuar"
	if AltKati == "ŞAPKA":
		AltKatii = "Aksesuar";
		UstKati = "Aksesuar";
		OrtaKati = "Aksesuar"
	if AltKati == "ÇORAP":
		AltKatii = "Çorap";
		UstKati = "Aksesuar";
		OrtaKati = "Aksesuar"
	if AltKati == "BOXER":
		AltKatii = "Boxer";
		UstKati = "Aksesuar";
		OrtaKati = "Aksesuar"
	if AltKati == "GÜNEŞ GÖZLÜĞÜ":
		AltKatii = "Güneş Gözlüğü";
		UstKati = "Aksesuar";
		OrtaKati = "Aksesuar"
	if AltKati == "GÖMLEK UZUN KOLLU":
		AltKatii = "Gömlek";  #UstKati         =       "Aksesuar";     OrtaKati            =       "Aksesuar"
	if AltKati == "GÖMLEK KISA KOLLU":
		AltKatii = "Gömlek";  #UstKati         =       "Aksesuar";     OrtaKati            =       "Aksesuar"
	if AltKati == "GÖMLEK":
		AltKatii = "Gömlek";  #UstKati         =       "Aksesuar";     OrtaKati            =       "Aksesuar"
	if AltKati == "FORMA":
		AltKatii = "Forma";  #UstKati         =       "Aksesuar";     OrtaKati            =       "Aksesuar"

	if Fiyat < EFiyat:
		Firsat = 1




	#~ if not exists (select * from Django.dbo.kategoriler_urun where StokKodu='00474-0008')
	#~ INSERT INTO Django.dbo.kategoriler_urun(UstKat_id, OrtaKat_id, Marka_id, Logo, Adi, StokKodu, Slug, Fiyat, EFiyat, KdvOrani, Desi, Yeni, Firsat)
	#~ VALUES(
	#~ (select id from Django.dbo.kategoriler_kategori where Adi= N'Bayan'),
	#~ (select id from Django.dbo.kategoriler_ortakategori where Adi= N'Tekstil' and UstKat_id=(select id from Django.dbo.kategoriler_kategori where Adi= N'Bayan')),
	#~
	#~ (select id from Django.dbo.kategoriler_marka where Adi= N'Levis'), N'ResimYok__.png', N'LEVIS BAYAN JEAN PANTOLON ',  N'00474-0008',  N'levis-bayan-jean-pantolon-00474-0008',  '90.30',  '129.00',  0, 0, 1, '0');
	#~ else update Django.dbo.kategoriler_urun set Fiyat='90.30', EFiyat='129.00', Firsat='0' where  StokKodu='00474-0008'
	#~
	#~
	#~
	#~
	#~ INSERT INTO Django.dbo.kategoriler_urun_AltKat
	#~ (urun_id, altkategori_id)
	#~ VALUES
	#~ ((select id from Django.dbo.kategoriler_urun where StokKodu='00474-0008'), (select id from Django.dbo.kategoriler_altkategori where Adi= N'Pantolon-Jean' and  OrtaKat_id=(select id from Django.dbo.kategoriler_ortakategori where Adi= N'Tekstil' and UstKat_id=(select id from Django.dbo.kategoriler_kategori where Adi= N'Bayan'))) );

	try:
		cursor.execute( "if not exists (select * from Django.dbo.kategoriler_marka where Adi='" + Marka + "') insert into Django.dbo.kategoriler_marka (Adi, Slug) Values('" + Marka + "', '" + slugify( Marka ) + "');" )
		#~ #Pzt 20 Oca 2014 15:26:21 EET  - Muslu YÜKSEKTEPE

		sss = "if not exists (select * from Django.dbo.kategoriler_urun where StokKodu='" + StokKodu + "') "

		sss += "INSERT INTO Django.dbo.kategoriler_urun(UstKat_id, OrtaKat_id, Marka_id, Logo, Adi, StokKodu, Slug, Fiyat, EFiyat, KdvOrani, Desi, Yeni, Firsat, KisaURL)"

		sss += "VALUES((select id from Django.dbo.kategoriler_kategori where Adi= N'" + UstKati + "'),  "

		sss += "(select id from Django.dbo.kategoriler_ortakategori where Adi= N'" + OrtaKati.title( ) + "' and UstKat_id=(select id from Django.dbo.kategoriler_kategori where Adi= N'" + UstKati.title( ) + "')), "

		sss += " (select id from Django.dbo.kategoriler_marka where Adi= N'" + Marka.title( ) + "'), "
		sss += " N'ResimYok__.png',"
		sss += " N'" + SezonBilgisiSil( UrunAdi ) + "', "
		sss += " N'" + StokKodu + "', "
		sss += " N'" + slugify( SezonBilgisiSil( UrunAdi_s ) + StokKodu ) + "', "
		sss += " '" + Fiyat + "', "
		sss += " '" + EFiyat + "', "
		sss += " 0, 0, 1,"
		sss += " '" + str( Firsat ) + "', "
		sss += " '" + str( goo_shorten_url( settings.__getattr__( "DOMAIN" ) + "/" + slugify( Marka ) + "/" + slugify( SezonBilgisiSil( UrunAdi_s ) + StokKodu ) + "_u/" ) ) + "');"

		sss += "else update Django.dbo.kategoriler_urun set Fiyat='" + Fiyat + "', EFiyat='" + EFiyat + "', Firsat='" + str( Firsat ) + "' where  StokKodu='" + StokKodu + "'"

		cursor.execute( sss )

	except:

		cursor.execute( "if not exists (select * from Django.dbo.kategoriler_marka where Adi='" + Marka + "') insert into Django.dbo.kategoriler_marka (Adi, Slug) Values('" + Marka + "', '" + slugify( Marka ) + "');" )

		sss = "if not exists (select * from Django.dbo.kategoriler_urun where StokKodu='" + StokKodu + "') "

		sss += "INSERT INTO Django.dbo.kategoriler_urun(UstKat_id, OrtaKat_id, Marka_id, Logo, Adi, StokKodu, Slug, Fiyat, EFiyat, KdvOrani, Desi, Yeni, Firsat, KisaURL)"

		sss += "VALUES((select id from Django.dbo.kategoriler_kategori where Adi= N'Kategorisiz'),  "

		sss += "(select id from Django.dbo.kategoriler_ortakategori where Adi= N'Kategorisiz' and UstKat_id=(select id from Django.dbo.kategoriler_kategori where Adi= N'Kategorisiz')), "

		sss += " (select id from Django.dbo.kategoriler_marka where Adi= N'" + Marka.title( ) + "'), "
		sss += " N'ResimYok__.png',"
		sss += " N'" + SezonBilgisiSil( UrunAdi ) + "', "
		sss += " N'" + StokKodu + "', "
		sss += " N'" + slugify( SezonBilgisiSil( UrunAdi_s ) + StokKodu ) + "', "
		sss += " '" + Fiyat + "', "
		sss += " '" + EFiyat + "', "
		sss += " 0, 0, 1,"
		sss += " '" + str( Firsat ) + "', "
		sss += " '" + str( goo_shorten_url( settings.__getattr__( "DOMAIN" ) + "/" + slugify( Marka ) + "/" + slugify( SezonBilgisiSil( UrunAdi_s ) + StokKodu ) + "_u/" ) ) + "');"

		sss += "else update Django.dbo.kategoriler_urun set Fiyat='" + Fiyat + "', EFiyat='" + EFiyat + "', Firsat='" + str( Firsat ) + "' where  StokKodu='" + StokKodu + "'"

		cursor.execute( sss )
	# 20.03.2014 10:30:49#      -  Muslu YÜKSEKTEPE

	try:

		ssss = "INSERT INTO Django.dbo.kategoriler_urun_AltKat (urun_id, altkategori_id) "

		ssss += "VALUES "

		ssss += "((select id from Django.dbo.kategoriler_urun where StokKodu='" + StokKodu.title( ) + "'),  "

		ssss += "(select id from Django.dbo.kategoriler_altkategori where Adi= N'" + AltKatii + "' and  OrtaKat_id=(select id from Django.dbo.kategoriler_ortakategori where Adi= N'" + OrtaKati.title( ) + "' and UstKat_id=(select id from Django.dbo.kategoriler_kategori where Adi= N'" + UstKati.title( ) + "'))) ); "

		cursor.execute( ssss )

	except:
		pass

	cursor.execute( u"if not exists(select * from Django.dbo.kategoriler_varyant where Barkod='" + Barkod + "')" + "INSERT INTO Django.dbo.kategoriler_varyant(Urunu_id, Renk, RenkKodu, Beden, Kavala, Barkod, StokSayisi, EkstraFiyat)" + " VALUES ((select id from Django.dbo.kategoriler_urun where StokKodu='" + StokKodu + "'), " + "N'" + Renk + "', " + "N'" + RenkKodu + "', " + "N'" + Beden + "', " + "N'" + Kavala + "', " + "N'" + Barkod + "', " + "N'" + StokSayisi + "', 0);" + "else update Django.dbo.kategoriler_varyant set StokSayisi='" + StokSayisi + "'  where Barkod='" + Barkod + "'; " )


#~ except:
#~ pass


def Turkcelestir( Veri ):
	return Veri.replace( "\xc3\x87", 'Ç' ).replace( "\xc7", 'Ç' ).replace( "\xc3\x9c", 'Ü' ).replace( "\xdc", 'Ü' ).replace( u"\xc3\x96", 'Ö' ).replace( "\u0130", 'İ' ).replace( u"\u015e", 'Ş' ).replace( u"\u015f", 'Ş' )


def SezonBilgisiSil( UrunAdi ):
	TemizHali = ""

	for i in UrunAdi.split( ' ' ):

		if not "/" in i and len( i ) > int( settings.__getattr__( "URUNADI_TEMIZLE" ) ):  #~ Pzt 20 Oca 2014 14:49:04 EET  - Muslu YÜKSEKTEPE
			TemizHali += i + " "

	return TemizHali.replace( "\xc3\x87", 'Ç' ).replace( "\xc3\x9c", 'Ü' ).replace( "\xc3\x96", 'Ö' )


#~ Pzt 13 Oca 2014 18:57:05 EET  - Muslu YÜKSEKTEPE






def YeniUrunler( request ):
	yeni_urun_listesi = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0, AltKat__id__isnull = False, Yeni = 1, varyant__AltKat__id__isnull = False ).order_by( '-id' ).distinct( )

	paginator = Paginator( yeni_urun_listesi, 12 )

	page = request.GET.get( 'sayfa' )
	try:
		urunler = paginator.page( page )
	except PageNotAnInteger:
		urunler = paginator.page( 1 )
	except EmptyPage:
		urunler = paginator.page( paginator.num_pages )

	return render_to_response( 'yeni_urunler.html', { 'urunler': urunler, }, context_instance = RequestContext( request ) )


def yeni_urunler_json( request, page ):
	urunlistesi = Urun.objects.filter( Yeni = 1 ).order_by( 'id' )
	paginator = Paginator( urunlistesi, 12 )

	try:
		urunler = paginator.page( page )
	except (EmptyPage, InvalidPage):
		urunler = paginator.page( paginator.num_pages )

	template = 'tracks.json'

	return render_to_response( template, { 'urunler': urunler } )


def urunliste( request ):
	urunlistesi = Urun.objects.order_by( '-id' )
	paginator = Paginator( urunlistesi, 4 )

	try:
		page = int( request.GET.get( 'sayfa', '1' ) )
	except ValueError:
		page = 1

	try:
		urunler = paginator.page( page )
	except (EmptyPage, InvalidPage):
		urunler = paginator.page( paginator.num_pages )

	return render_to_response( "urunler2.html", { 'urunler': urunler }, context_instance = RequestContext( request ) )


def urunler_json( request, page ):
	urunlistesi = Urun.objects.order_by( '-id' )
	paginator = Paginator( urunlistesi, 24 )

	try:
		urunler = paginator.page( page )
	except (EmptyPage, InvalidPage):
		urunler = paginator.page( paginator.num_pages )

	template = 'tracks.json'

	return render_to_response( template, { 'urunler': urunler } )


def FirsatUrunleri( request ):
	firsat_urun_listesi = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0, AltKat__id__isnull = False, Firsat = 1, varyant__AltKat__id__isnull = False ).order_by( '-id' ).distinct( )

	paginator = Paginator( firsat_urun_listesi, 12 )

	page = request.GET.get( 'sayfa' )
	try:
		urunler = paginator.page( page )
	except PageNotAnInteger:
		urunler = paginator.page( 1 )
	except EmptyPage:
		urunler = paginator.page( paginator.num_pages )

	return render_to_response( 'firsat_urunler.html', { 'urunler': urunler, }, context_instance = RequestContext( request ) )


def KampanyaliUrunler( request ):
	kampanyali_urun_listesi = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0, AltKat__id__isnull = False, Fiyat__lt = F( 'EFiyat' ), varyant__AltKat__id__isnull = False ).order_by( '-id' ).distinct( )

	paginator = Paginator( kampanyali_urun_listesi, 12 )

	page = request.GET.get( 'sayfa' )
	try:
		urunler = paginator.page( page )
	except PageNotAnInteger:
		urunler = paginator.page( 1 )
	except EmptyPage:
		urunler = paginator.page( paginator.num_pages )

	return render_to_response( 'kampanya_urunler.html', { 'urunler': urunler, }, context_instance = RequestContext( request ) )


def OutletUrunler( request ):
	outlet_urun_listesi = Urun.objects.annotate( ToplamStok_Sayisi = Sum( 'varyant__StokSayisi' ) ).filter( ToplamStok_Sayisi__gt = 0, Outlet = 1, AltKat__id__isnull = False, Fiyat__lt = F( 'EFiyat' ), varyant__AltKat__id__isnull = False ).order_by( '-id' ).distinct( )

	paginator = Paginator( outlet_urun_listesi, 12 )

	page = request.GET.get( 'sayfa' )
	try:
		urunler = paginator.page( page )
	except PageNotAnInteger:
		urunler = paginator.page( 1 )
	except EmptyPage:
		urunler = paginator.page( paginator.num_pages )

	return render_to_response( 'outlet_urunler.html', { 'urunler': urunler, }, context_instance = RequestContext( request ) )


def EnCokSatanUrunler( request ):
	en_cok_satan_urunler = Urun.objects.filter( EnCokSatan = 1, varyant__AltKat__id__isnull = False )
	return render_to_response( 'en_cok_satan_urunler.html', { 'en_cok_satan_urunler': en_cok_satan_urunler }, context_instance = RequestContext( request ) )


def DefoluUrunler( request ):
	defolu_urunler = Urun.objects.filter( EnCokSatan = 1, varyant__AltKat__id__isnull = False )
	return render_to_response( 'defolu_urunler.html', { 'defolu_urunler': defolu_urunler }, context_instance = RequestContext( request ) )













