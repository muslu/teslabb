# -*- coding: utf-8 -*-


import random
import string
from decimal import Decimal

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.conf import settings
from django.template.defaultfilters import slugify
from django.db.models import Sum

from kategoriler.models import Kategori, OrtaKategori, AltKategori, Marka, Urun, Varyant, Sepet, SepetUrunler, Siparis
from bankalar.models import Bankalar





# ~ Aksesuar_Listem              =       ['AKSESUAR', 'ANAHTARLIK', 'ATKI', 'AYAKKABI ÇANTASI', 'BERE', 'BİLEKLİK', 'BONE', 'CÜZDAN', 'ÇANTA', 'ÇORAP', 'ELDİVEN', 'FREE BAG', 'HAVLU', 'KEMER', 'SIRT ÇANTASI', 'ŞAPKA']
# ~ Ayakkabi_Listem              =       ['AYAKKABI', 'BABET', 'BASKETBOL AYKB.', 'BOT', 'HALI SAHA AYAKKABI', 'KOŞU AYKB.', 'KRAMPON', 'SANDALET', 'TENİS AYKB.', 'TRAINING AYKB.']
# ~ Tekstil_Listem               =       ['ATLET', 'BİKİNİ', 'CEKET', 'ÇORAP', 'EŞOFMAN ALTI', 'EŞOFMAN TK', 'EŞOFMAN ÜSTÜ', 'ETEK', 'FORMA', 'GÖMLEK', 'KAPRİ', 'MAYO', 'MONT', 'PANTOLON', 'POLO YAKA T-SHIRT', 'SWEAT', 'İPLİK', 'ŞORT MAYO', 'TAYT', 'T-SHIRT', 'YELEK']



def AnaSayfa( request ):
	encoksatilan_listesi = Urun.objects.filter( EnCokSatan = 1, AltKat__id__isnull = False, varyant__AltKat__id__isnull = False ).order_by( '-id' ).distinct( )
	yeni_urun_listesi = Urun.objects.filter( Yeni = 1, AltKat__id__isnull = False, varyant__AltKat__id__isnull = False ).order_by( '-id' ).distinct( )

	vitrin_urun_listesi = Urun.objects.filter( Vitrin = 1, AltKat__id__isnull = False, varyant__AltKat__id__isnull = False ).order_by( '-id' )[0:4]
	vitrin_urun_listesii = Urun.objects.filter( Vitrin = 1, AltKat__id__isnull = False, varyant__AltKat__id__isnull = False ).order_by( '-id' )[4:8]

	response = render_to_response( 'index.html', { 'yeni_urun_listesi': yeni_urun_listesi, 'vitrin_urun_listesi': vitrin_urun_listesi, 'vitrin_urun_listesii': vitrin_urun_listesii, 'encoksatilan_listesi': encoksatilan_listesi }, context_instance = RequestContext( request ) )
	response.delete_cookie( 'SayfaYuklendiMi' )
	return response


def MarkaListesi( request ):
	marka_listesi = Marka.objects.all( )
	return render_to_response( 'marka.html', { 'marka_listesi': marka_listesi }, context_instance = RequestContext( request ) )


def MarkaDetayi( request, slug ):
	try:
		marka_listesi = Marka.objects.all( )
		marka_detayi = Marka.objects.get( Slug = slug )
		marka_urunler = Urun.objects.filter( AltKat__id__isnull = False, Marka__Slug = slug ).order_by( '-id' ).distinct( )

		#~ detayi = get_object_or_404(Marka, Slug=slug)
		#~ print request.path_info


		paginator = Paginator( marka_urunler, 8 )

		try:
			page = int( request.GET.get( 'sayfa', '1' ) )
		except ValueError:
			page = 1

		try:
			urunler = paginator.page( page )
		except (EmptyPage, InvalidPage):
			urunler = paginator.page( paginator.num_pages )

		BaslangicSayfasi = max( page - 2, 1 )

		if BaslangicSayfasi <= 3:
			BaslangicSayfasi = 1

		BitisSayfasi = page + 2 + 1

		if BitisSayfasi >= paginator.num_pages - 1:
			BitisSayfasi = paginator.num_pages + 1

		SayfaSayisi = [n for n in range( BaslangicSayfasi, BitisSayfasi ) if n > 0 and n <= paginator.num_pages]


	except Marka.DoesNotExist:
		return render_to_response( '404.html' )

	return render_to_response( 'marka_detayi.html', { 'urunler': urunler, 'marka_detayi': marka_detayi, 'marka_listesi': marka_listesi, 'SayfaSayisi': SayfaSayisi }, context_instance = RequestContext( request ) )


def MarkaDetayi_json( request, page, slug ):
	urunlistesi = Urun.objects.filter( Marka__Slug = slug ).order_by( '-id' )

	paginator = Paginator( urunlistesi, 8 )

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

	ust_kategori_listesi = Kategori.objects.all( )
	orta_kategori_listesi = OrtaKategori.objects.filter( UstKat__Slug = UstKat )
	alt_kategori_listesi = AltKategori.objects.filter( OrtaKat__UstKat__Slug = UstKat, OrtaKat__Slug = OrtaKat )

	alt_kategori_bilgileri = AltKategori.objects.get( OrtaKat__UstKat__Slug = UstKat, OrtaKat__Slug = OrtaKat, Slug = slug )

	urunlistesi = Urun.objects.filter( AltKat = AltKatid ).order_by( '-id' )

	#~ urunlistesi              =       Urun.objects.filter(varyant__AltKat__id=AltKatid).order_by('-id')

	paginator = Paginator( urunlistesi, 8 )

	try:
		page = int( request.GET.get( 'sayfa', '1' ) )
	except ValueError:
		page = 1

	try:
		urunler = paginator.page( page )
	except (EmptyPage, InvalidPage):
		urunler = paginator.page( paginator.num_pages )

	#~ except AltKategori.DoesNotExist:
	#~ return render_to_response('404.html')

	return render_to_response( 'urunler.html', { 'urunler': urunler, 'alt_kategori_bilgileri': alt_kategori_bilgileri, 'KUstKat': UstKat, 'KOrtaKat': OrtaKat, 'KSlug': slug, 'alt_kategori_listesi': alt_kategori_listesi, 'orta_kategori_listesi': orta_kategori_listesi, 'ust_kategori_listesi': ust_kategori_listesi }, context_instance = RequestContext( request ) )


def UrunListesi_json( request, page, uk, slug ):
	urunlistesi = Urun.objects.filter( AltKat__OrtaKat__UstKat__Slug = uk, AltKat__Slug = slug ).order_by( '-id' )
	paginator = Paginator( urunlistesi, 8 )

	try:
		urunler = paginator.page( page )
	except (EmptyPage, InvalidPage):
		urunler = paginator.page( paginator.num_pages )

	template = 'tracks.json'

	return render_to_response( template, { 'urunler': urunler } )


def UrunDetayi( request, marka, slug, AltKatid ):
	urun_detayi = Urun.objects.get( Slug = slug )
	#~ siparis_linki            =       ''.join([random.choice(string.digits + string.letters) for i in range(0, 90)])
	ust_kategorisi = Kategori.objects.get( id = AltKatid.split( '_' )[0] )
	orta_kategorisi = OrtaKategori.objects.get( id = AltKatid.split( '_' )[1] )
	alt_kategorisi = AltKategori.objects.get( id = AltKatid.split( '_' )[2] )

	urun_varyant_detayi = Varyant.objects.filter( AltKat__id__isnull = False, AltKat__id = AltKatid.split( '_' )[2], Urunu_id = urun_detayi.id )
	toplam_stok_sayisi = urun_varyant_detayi.aggregate( Sum( 'StokSayisi' ) )

	if settings.__getattr__( "ALTKATEGORIYE_AIT_URUNLERI_GOSTER" ):
		altkat_diger_urunler = Urun.objects.filter( AltKat__id__isnull = False, varyant__AltKat__id__isnull = False, AltKat__id = AltKatid.split( '_' )[2] ).exclude( id = urun_detayi.id ).order_by( '-id' ).distinct( )
	else:
		altkat_diger_urunler = { }

	if settings.__getattr__( "FIYATI_BENZER_URUNLERI_GOSTER" ):
		fiyat_diger_urunler = Urun.objects.filter( AltKat__id__isnull = False, varyant__AltKat__id__isnull = False, Fiyat__gte = (urun_detayi.Fiyat - int( settings.__getattr__( "FIYAT_ARALIGI" ) )), Fiyat__lte = (urun_detayi.Fiyat + int( settings.__getattr__( "FIYAT_ARALIGI" ) )) ).exclude( id = urun_detayi.id ).order_by( '-id' ).distinct( )  #~ Pzt 20 Oca 2014 11:17:32 EET  - Muslu YÜKSEKTEPE

	else:
		fiyat_diger_urunler = { }

	if settings.__getattr__( "MARKAYA_AIT_URUNLERI_GOSTER" ):
		marka_diger_urunler = Urun.objects.filter( AltKat__id__isnull = False, varyant__AltKat__id__isnull = False, Marka__Slug = marka ).exclude( id = urun_detayi.id ).order_by( '-id' ).distinct( )  #~ Pzt 20 Oca 2014 11:18:04 EET  - Muslu YÜKSEKTEPE
	else:
		marka_diger_urunler = { }

	if settings.__getattr__( "ESLESTIRILMIS_URUNLERI_GOSTER" ):
		eslestirilmis_kategori_urunleri = Urun.objects.raw( "SELECT * FROM Django.dbo.kategoriler_urun where id in (SELECT urun_id FROM Django.dbo.kategoriler_urun_AltKat where altkategori_id in (SELECT altkategori_id FROM Django.dbo.kategoriler_benzerkategoriler_BenzerKat where benzerkategoriler_id in (SELECT id FROM Django.dbo.kategoriler_benzerkategoriler where AltKat_id in (SELECT altkategori_id FROM Django.dbo.kategoriler_urun_AltKat where urun_id='" + str( urun_detayi.id ) + "'))));" )
	else:
		eslestirilmis_kategori_urunleri = { }

	if len( list( eslestirilmis_kategori_urunleri ) ) != 0:
		return render_to_response( 'urun_detayi.html', { 'urun_detayi': urun_detayi, 'urun_varyant_detayi': urun_varyant_detayi, 'altkat_diger_urunler': altkat_diger_urunler, 'toplam_stok_sayisi': toplam_stok_sayisi, 'marka_diger_urunler': marka_diger_urunler, 'fiyat_diger_urunler': fiyat_diger_urunler, 'ust_kategorisi': ust_kategorisi, 'orta_kategorisi': orta_kategorisi, 'alt_kategorisi': alt_kategorisi, 'eslestirilmis_kategori_urunleri': eslestirilmis_kategori_urunleri }, context_instance = RequestContext( request ) )
	else:
		return render_to_response( 'urun_detayi.html', { 'urun_detayi': urun_detayi, 'urun_varyant_detayi': urun_varyant_detayi, 'altkat_diger_urunler': altkat_diger_urunler, 'toplam_stok_sayisi': toplam_stok_sayisi, 'marka_diger_urunler': marka_diger_urunler, 'fiyat_diger_urunler': fiyat_diger_urunler, 'ust_kategorisi': ust_kategorisi, 'orta_kategorisi': orta_kategorisi, 'alt_kategorisi': alt_kategorisi }, context_instance = RequestContext( request ) )


def VaryantGoster( request, VaryantID ):
	GeciciUyeID = request.COOKIES.get( 'GeciciUyeID' )

	if not request.COOKIES.get( 'GeciciUyeID' ):
		GeciciUyeID = ''.join( [random.choice( string.digits ) for i in range( 0, 10 )] )

	varyant_detayi = Varyant.objects.get( id = VaryantID )
	urun_detayi = Urun.objects.get( id = varyant_detayi.Urunu_id )

	VaryantTutari = str( urun_detayi.Fiyat + varyant_detayi.EkstraFiyat ).replace( ',', '.' )  # Islem tutari

	Kargo_Kamp_Fiy_tamamla = { }
	kargo_kamp_urunler = { }

	Kargo_Kamp_Fiy = Decimal( settings.__getattr__( "KARGO_KAMPANYA" ) )
	Kargo_Kamp_Ara = Decimal( settings.__getattr__( "KARGO_KAMPANYA_ARALIGI" ) )

	try:

		Sepetteki = SepetUrunler.objects.filter( SepetID = Sepet.objects.get( UyeID = GeciciUyeID ) )
		SepetTutari = 0

		for i in Sepetteki:
			SepetTutari += i.Adet * i.Fiyat

		KampIcinEnAzTutar = (Kargo_Kamp_Fiy - SepetTutari)
		KampIcinEnFazlaTutar = (Kargo_Kamp_Fiy - SepetTutari) + Kargo_Kamp_Ara

		if Decimal( VaryantTutari ) < SepetTutari:
			kargo_kamp_urunler = Urun.objects.filter( AltKat__id__isnull = False, Fiyat__gte = KampIcinEnAzTutar, Fiyat__lte = KampIcinEnFazlaTutar ).exclude( id = urun_detayi.id ).order_by( '-id' ).distinct( )


	except:

		KampIcinEnAzTutar = Kargo_Kamp_Fiy - Decimal( VaryantTutari )
		KampIcinEnFazlaTutar = (KampIcinEnAzTutar + Kargo_Kamp_Ara)

		if Decimal( VaryantTutari ) < Kargo_Kamp_Fiy:
			kargo_kamp_urunler = Urun.objects.filter( AltKat__id__isnull = False, Fiyat__gte = KampIcinEnAzTutar, Fiyat__lte = KampIcinEnFazlaTutar ).exclude( id = urun_detayi.id ).order_by( '-id' ).distinct( )

	response = render_to_response( 'varyantgoster.html', { 'urun_detayi': urun_detayi, 'varyant_detayi': varyant_detayi, 'VaryantTutari': VaryantTutari, 'kargo_kamp_urunler': kargo_kamp_urunler, 'KampIcinEnAzTutar': KampIcinEnAzTutar, 'KampIcinEnFazlaTutar': KampIcinEnFazlaTutar, 'Kargo_Kamp_Fiy': Kargo_Kamp_Fiy, 'GeciciUyeID': GeciciUyeID }, context_instance = RequestContext( request ) )

	response.set_cookie( 'GeciciUyeID', GeciciUyeID )

	return response


def tkug( request ):
	if request.is_ajax( ):

		VaryantTutari = request.GET['YeniTutar']
		VaryantID = request.GET['VaryantID']
		GeciciUyeID = request.COOKIES.get( 'GeciciUyeID' )

		Kargo_Kamp_Fiy = Decimal( settings.__getattr__( "KARGO_KAMPANYA" ) )
		Kargo_Kamp_Ara = Decimal( settings.__getattr__( "KARGO_KAMPANYA_ARALIGI" ) )

		try:

			Sepetteki = SepetUrunler.objects.filter( SepetID = Sepet.objects.get( UyeID = GeciciUyeID ) )
			SepetTutari = 0

			for i in Sepetteki:
				SepetTutari += i.Adet * i.Fiyat

			KampIcinEnAzTutar = Kargo_Kamp_Fiy - Decimal( SepetTutari )
			KampIcinEnFazlaTutar = (KampIcinEnAzTutar + Kargo_Kamp_Ara)

		except:

			KampIcinEnAzTutar = Kargo_Kamp_Fiy - Decimal( VaryantTutari )
			KampIcinEnFazlaTutar = (KampIcinEnAzTutar + Kargo_Kamp_Ara)

		if Decimal( VaryantTutari ) < Decimal( KampIcinEnAzTutar ):
			kargo_kamp_urunler = Urun.objects.filter( AltKat__id__isnull = False, varyant__AltKat__id__isnull = False, Fiyat__gte = KampIcinEnAzTutar, Fiyat__lte = KampIcinEnFazlaTutar )
		else:
			kargo_kamp_urunler = { }

		MEsaj = ""

		if len( kargo_kamp_urunler ) == 0:
			MEsaj = str( KampIcinEnAzTutar ) + " - " + str( KampIcinEnFazlaTutar ) + " TL aralığında uygun ürün bulunamadı"
		else:
			MEsaj = str( KampIcinEnAzTutar ) + " - " + str( KampIcinEnFazlaTutar ) + " TL aralığında ki ürünler"

		return render_to_response( 'adetegorekargo.html', { 'kargo_kamp_urunler': kargo_kamp_urunler, 'KampIcinEnAzTutar': KampIcinEnAzTutar, 'KampIcinEnFazlaTutar': KampIcinEnFazlaTutar, 'Kargo_Kamp_Fiy': Kargo_Kamp_Fiy, 'VaryantTutari': VaryantTutari, 'MEsaj': MEsaj }, context_instance = RequestContext( request ) )


def SepetimeEkle( request ):
	VaryantAdeti = request.POST.get( "VaryantAdeti" )
	VaryantID = request.POST.get( "VaryantID" )

	from django.db.models import F




	GeciciUyeID = request.COOKIES.get( 'GeciciUyeID' )

	if not request.COOKIES.get( 'GeciciUyeID' ):
		GeciciUyeID = ''.join( [random.choice( string.digits ) for i in range( 0, 10 )] )

	varyant_detayi = Varyant.objects.get( id = VaryantID )
	urun_detayi = Urun.objects.get( id = varyant_detayi.Urunu_id )

	VaryantTutari = str( urun_detayi.Fiyat + varyant_detayi.EkstraFiyat ).replace( ',', '.' )  # Islem tutari

	varolankayit, yenikayit = Sepet.objects.get_or_create( UyeID = GeciciUyeID )

	if yenikayit:

		SepetinID = Sepet.objects.get( UyeID = varolankayit.UyeID )

		SepetUrunlerEkle = SepetUrunler( SepetID = SepetinID, VaryantID = VaryantID, Adet = VaryantAdeti, Fiyat = VaryantTutari, StokKodu = urun_detayi.StokKodu )
		SepetUrunlerEkle.save( )

	else:

		SepetinID = Sepet.objects.get( UyeID = GeciciUyeID )

		SepetteUrunVarMi = SepetUrunler.objects.filter( SepetID = SepetinID, VaryantID = VaryantID )

		if SepetteUrunVarMi:

			SepetUrunler.objects.filter( SepetID = SepetinID, VaryantID = VaryantID ).update( Adet = F( 'Adet' ) + VaryantAdeti )

		else:

			SepetUrunlerEkle = SepetUrunler( SepetID = SepetinID, VaryantID = VaryantID, Adet = VaryantAdeti, Fiyat = VaryantTutari, StokKodu = urun_detayi.StokKodu )
			SepetUrunlerEkle.save( )

	response = render_to_response( 'sepeteekle.html', { 'GeciciUyeID': GeciciUyeID, }, context_instance = RequestContext( request ) )

	response.set_cookie( 'VaryantID', VaryantID )
	response.set_cookie( 'VaryantAdeti', VaryantAdeti )
	response.set_cookie( 'GeciciUyeID', GeciciUyeID )
	response.set_cookie( 'StokKodu', urun_detayi.StokKodu )

	return response


def Sepetim( request ):
	try:

		SepettekiUrunlerim = { }
		BankaListesi = { }
		Sepetim = { }

		GeciciUyeID = request.COOKIES.get( 'GeciciUyeID' )

		if request.COOKIES.get( 'GeciciUyeID' ):

			Sepetim = Sepet.objects.get( UyeID = GeciciUyeID, Tamamlandi = 0 )
			SepettekiUrunlerim = SepetUrunler.objects.filter( SepetID = Sepetim.id )
			BankaListesi = Bankalar.objects.filter( Aktif = 1 ).order_by( 'Adi', )

		response = render_to_response( 'sepetim.html', { 'GeciciUyeID': GeciciUyeID, 'SepettekiUrunlerim': SepettekiUrunlerim, 'BankaListesi': BankaListesi }, context_instance = RequestContext( request ) )

		return response

		response.set_cookie( 'SayfaYuklendiMi', True )

	except Sepet.DoesNotExist:
		return redirect( "/" )


def Odeme( request ):  #~ Cum 24 Oca 2014 15:21:22 EET  - Muslu YÜKSEKTEPE

	for i in request.POST.getlist( 'group1' ):
		BankaID = i.split( '_' )[0]
		ToplamTaksit = i.split( '_' )[1]
		Tutar = i.split( '_' )[2]

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

	                           { 'hashi': hashi, 'oid': oid, 'rnd': rnd, 'amount': amount, 'taksit': taksit, 'hashi': hashi, 'clientId': clientId, 'okUrl': okUrl, 'failUrl': failUrl, 'storekey': storekey, 'BankaAdi': BankaAdi },

	                           context_instance = RequestContext( request ) )


def PayOdeme( request ):  #~ Cum 24 Oca 2014 15:40:54 EET  - Muslu YÜKSEKTEPE


	#~ SayfaYuklendiMi  = request.COOKIES.has_key('SayfaYuklendiMi')

	SiparisNosu = ""

	#~ try:

	if request.POST['mdStatus'] == "0":
		Sonuc = "Onaylanmamış"
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


		GeciciUyeID = request.COOKIES.get( 'GeciciUyeID' )

		SiparisNosu = ''.join( [random.choice( string.digits ) for i in range( 0, 10 )] )

		SiparisTamamla = Sepet.objects.get( UyeID = GeciciUyeID )
		SiparisTamamla.Tamamlandi = 1
		SiparisTamamla.save( )

		SiparisKaydet = Siparis( SiparisNo = SiparisNosu, UyeID = GeciciUyeID, SepetID = SiparisTamamla.id, Taksit = request.POST["taksit"], ToplamTutar = request.POST["amount"] )
		SiparisKaydet.save( )

		SepetUrunBul = SepetUrunler.objects.filter( SepetID = SiparisTamamla.id )

		for i in SepetUrunBul:

			VaryantAdetAzalt = Varyant.objects.get( id = i.VaryantID )
			VaryantAdetAzalt.StokSayisi = VaryantAdetAzalt.StokSayisi - i.Adet
			VaryantAdetAzalt.save( )

	response = render_to_response( 'estsonuc.html', { 'Sonuc': Sonuc, 'SiparisNosu': SiparisNosu }, context_instance = RequestContext( request ) )

	response.delete_cookie( 'VaryantID' )
	response.delete_cookie( 'VaryantAdeti' )
	response.delete_cookie( 'GeciciUyeID' )
	response.delete_cookie( 'StokKodu' )

	return response


#~ except:
#~ return redirect("/")



#~ Cum 24 Oca 2014 16:47:46 EET  - Muslu YÜKSEKTEPE


def PayOdemei( request, SiparisNo, Sonuc ):
	return render_to_response( 'estsonuc.html', { 'Sonuc': Sonuc, 'SiparisNo': SiparisNo }, context_instance = RequestContext( request ) )


def Yazdir( request, ID ):
	print ID

	SepetBilgileri = SepetUrunler.objects.filter( SepetID = Sepet.objects.get( id = ID ) )

	for i in SepetBilgileri:
		print i


	#~ return render_to_response('yazdir.html', {'SepetBilgileri':SepetBilgileri,}, context_instance=RequestContext(request))
	#~ Çrş 05 Şub 2014 10:05:20 EET  - Muslu YÜKSEKTEPE


def urunv3( request ):
	#~ try:

	import sys

	from django.db import connection




	lower_map = { ord( u'I' ): u'I', ord( u'İ' ): u'i',  #~ ord(u'Ş'): u'ş',  #~ ord(u'Ç'): u'Ç',  #~ ord(u'Ö'): u'ö',  #~ ord(u'Ğ'): u'ğ',  #~ ord(u'Ü'): u'ü', }

	              GunSayisi = request.GET.get( 'gun', '1' )
	StokKodu_Sorgu = request.GET.get( 'model', '' )

	StokKodu_SorguVarMi = ""

	if StokKodu_Sorgu != "":
		StokKodu_SorguVarMi = " and ProductCode = '" + StokKodu_Sorgu + "'"

	cursor = connection.cursor( )

	cursor.execute( "CREATE TABLE #TempTable (StokKodu NVARCHAR(255), Marka NVARCHAR(255), Adi NVARCHAR(250), Renk NVARCHAR(255), Beden NVARCHAR(255), Kavala NVARCHAR(255), Fiyat NVARCHAR(255), EFiyati NVARCHAR(255), StokSayisi NVARCHAR(255), Barkod NVARCHAR(255), UstKat NVARCHAR(255), OrtaKat NVARCHAR(255), AltKat NVARCHAR(255)  COLLATE Latin1_General_CI_AS)" );

	cursor.execute( """INSERT INTO #TempTable (StokKodu, Marka, Adi, Renk, Beden, Kavala, Fiyat, EFiyati, StokSayisi, Barkod, UstKat, OrtaKat, AltKat)

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
                                    ProductHierarchyLevel03 as AltKat --12

                                    from V3_DOGUKAN.dbo.ProductPriceAndInventory (N'TR', N'6', N'7', N'D01', SPACE(0), 'def', """ + GunSayisi + """) where Barcode != '' """ + StokKodu_SorguVarMi + """; """ )

	cursor.execute( "SELECT * FROM #TempTable" )

	Firsat = 0

	reload( sys )
	sys.setdefaultencoding( "latin-1" )

	for row in cursor.fetchall( ):

		StokKodu = row[0].strip( )

	try:
		Marka = row[1].strip( )
	except:
		Marka = "Tanimsiz"
	#~ Pzt 20 Oca 2014 16:00:33 EET  - Muslu YÜKSEKTEPE

	UrunAdi_s = row[2].replace( 'ERK ', 'ERKEK ' ).replace( 'BYN', 'BAYAN' ).replace( 'PNT', 'PANTOLON' ).replace( '_', '' ).replace( 'JJ ', '' ).replace( 'JACK JONES ', '' ).replace( 'İSP. ', 'İSPANYOL ' ).replace( '.', '' ).replace( '-', '' ).replace( 'ÇCK ', 'ÇOCUK ' ).replace( 'EŞF ', 'EŞOFMAN ' ).replace( 'ESF ', 'EŞOFMAN ' ).replace( 'AYKB ', 'AYAKKABI ' ).replace( 'AYK ', 'AYAKKABI ' ).replace( ' TK ', ' TAKIMI ' ).replace( 'BBK ', 'BEBEK ' ).replace( 'EŞFALT', 'EŞOFMAN ALT' ).replace( 'ESFALT', 'EŞOFMAN ALT' ).replace( 'ESFÜST', 'EŞOFMAN ÜST' ).replace( 'ESFUST', 'EŞOFMAN ÜST' ).replace( 'ESFTK', 'EŞOFMAN TAKIMI' )

	UrunAdi = row[2].encode( 'utf8' ).replace( 'ERK ', 'ERKEK ' ).replace( 'BYN', 'BAYAN' ).replace( 'PNT', 'PANTOLON' ).replace( '_', '' ).replace( 'JJ ', '' ).replace( 'JACK JONES ', '' ).replace( 'İSP. ', 'İSPANYOL ' ).replace( '.', '' ).replace( '-', '' ).replace( 'ÇCK ', 'ÇOCUK ' ).replace( 'EŞF ', 'EŞOFMAN ' ).replace( 'ESF ', 'EŞOFMAN ' ).replace( 'AYKB ', 'AYAKKABI ' ).replace( 'AYK ', 'AYAKKABI ' ).replace( ' TK ', ' TAKIMI ' ).replace( 'BBK ', 'BEBEK ' ).replace( 'EŞFALT', 'EŞOFMAN ALT' ).replace( 'ESFALT', 'EŞOFMAN ALT' ).replace( 'ESFÜST', 'EŞOFMAN ÜST' ).replace( 'ESFUST', 'EŞOFMAN ÜST' ).replace( 'ESFTK', 'EŞOFMAN TAKIMI' )


	#~ Pzt 13 Oca 2014 19:22:26 EET  - Muslu YÜKSEKTEPE
	#~ Sal 14 Oca 2014 19:12:55 EET  - Muslu YÜKSEKTEPE

	Fiyat = row[6]
	EFiyat = row[7]
	Barkod = row[9].strip( )

	StokSayisi = row[8]

	try:
		Renk = row[3].encode( 'utf8' )
	except:
		Renk = "Tanimsiz"

	Beden = row[4].strip( )
	Kavala = row[5].strip( )

	UstKati = row[10].strip( )

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

	try:
		OrtaKati = row[11].encode( 'utf8' )
	except:
		OrtaKati = row[11]

	if OrtaKati == "BOT-ÇİZME":
		OrtaKati = "Ayakkabı"
	if OrtaKati == "TERLİK":
		OrtaKati = "Ayakkabı"
	if OrtaKati == "AKSESUAR":
		UstKati = "Aksesuar";
		OrtaKati = "Aksesuar"
	if OrtaKati == "SPOR MALZEMESİ":
		UstKati = "Aksesuar";
		OrtaKati = "Ekipman"
	if OrtaKati == "":
		UstKati = "Kategorisiz";
		OrtaKati = "Kategorisiz"
	if UstKati == "":
		OrtaKati = "Kategorisiz"

	if Fiyat < EFiyat:
		Firsat = 1

	#~ if UrunAdi.startswith(Marka):    UrunAdi = re.sub(Marka + ' ', '', UrunAdi)






	cursor.execute( "if not exists (select * from Django.dbo.kategoriler_marka where Adi='" + Marka.decode( 'utf-8' ).translate( lower_map ).title( ) + "') insert into Django.dbo.kategoriler_marka (Adi, Slug) Values('" + Marka.decode( 'utf-8' ).translate( lower_map ).title( ) + "', '" + slugify( Marka ) + "');" )
	#~ #Pzt 20 Oca 2014 15:26:21 EET  - Muslu YÜKSEKTEPE

	sss = "if not exists (select * from Django.dbo.kategoriler_urun where StokKodu='" + StokKodu + "') "

	sss += "INSERT INTO Django.dbo.kategoriler_urun(UstKat_id, OrtaKat_id, Marka_id, Logo, Adi, StokKodu, Slug, Fiyat, EFiyat, KdvOrani, Desi, Yeni, Firsat)"

	sss += "VALUES((select id from Django.dbo.kategoriler_kategori where Adi= N'" + UstKati.replace( "\xc3\x87", 'Ç' ).title( ) + "'),  "

	sss += "(select id from Django.dbo.kategoriler_ortakategori where Adi= N'" + OrtaKati.title( ) + "' and UstKat_id=(select id from Django.dbo.kategoriler_kategori where Adi= N'" + UstKati.replace( "\xc3\x87", 'Ç' ).title( ) + "')), "

	sss += " (select id from Django.dbo.kategoriler_marka where Adi= N'" + str( Marka ).decode( 'utf-8' ).title( ) + "'), "
	sss += " N'ResimYok.jpg',"
	sss += " N'" + SezonBilgisiSil( UrunAdi ) + "', "
	sss += " N'" + StokKodu.decode( 'utf-8' ).translate( lower_map ) + "', "
	sss += " N'" + slugify( SezonBilgisiSil( UrunAdi_s.encode( 'utf-8' ) ) + StokKodu ) + "', "
	sss += " '" + Fiyat + "', "
	sss += " '" + EFiyat + "', "
	sss += " 0, 0, 1,"
	sss += " '" + str( Firsat ) + "');"

	sss += "else update Django.dbo.kategoriler_urun set Fiyat='" + Fiyat + "', EFiyat='" + EFiyat + "', Firsat='" + str( Firsat ) + "' where  StokKodu='" + StokKodu + "'"

	cursor.execute( sss )

	try:

		ssss = "INSERT INTO Django.dbo.kategoriler_urun_AltKat (urun_id, altkategori_id) "
		ssss += "VALUES "
		ssss += "((select id from Django.dbo.kategoriler_urun where StokKodu='" + StokKodu.decode( 'utf-8' ).translate( lower_map ).title( ) + "'), (select id from Django.dbo.kategoriler_altkategori where Adi= N'Pantolon-Jean' and  OrtaKat_id=(select id from Django.dbo.kategoriler_ortakategori where Adi= N'" + OrtaKati.title( ) + "' and UstKat_id=(select id from Django.dbo.kategoriler_kategori where Adi= N'" + UstKati.replace( "\xc3\x87", 'Ç' ).title( ) + "'))) );   "

		cursor.execute( ssss )

	except:
		pass

	cursor.execute( "if not exists(select * from Django.dbo.kategoriler_varyant where Barkod='" + Barkod + "')" + "INSERT INTO Django.dbo.kategoriler_varyant(Urunu_id, Renk, Beden, Kavala, Barkod, StokSayisi, EkstraFiyat)" + " VALUES ((select id from Django.dbo.kategoriler_urun where StokKodu='" + StokKodu + "'), " + "N'" + Renk + "', " + "N'" + Beden + "', " + "N'" + Kavala + "', " + "N'" + Barkod + "', " + "N'" + StokSayisi + "', 0);" + "else update Django.dbo.kategoriler_varyant set StokSayisi='" + StokSayisi + "'  where Barkod='" + Barkod + "'; " )


#~ except:
#~ pass  #~









def SezonBilgisiSil( UrunAdi ):
	TemizHali = ""

	for i in UrunAdi.split( ' ' ):

		if not "/" in i and len( i ) > int( settings.__getattr__( "URUNADI_TEMIZLE" ) ):  #~ Pzt 20 Oca 2014 14:49:04 EET  - Muslu YÜKSEKTEPE
			TemizHali += i + " "

	return TemizHali


#~ Pzt 13 Oca 2014 18:57:05 EET  - Muslu YÜKSEKTEPE




def YeniUrunler( request ):
	yeni_urun_listesi = Urun.objects.filter( AltKat__id__isnull = False, Yeni = 1, varyant__AltKat__id__isnull = False ).order_by( 'id' ).distinct( )

	paginator = Paginator( yeni_urun_listesi, 24 )

	try:
		page = int( request.GET.get( 'sayfa', '1' ) )
	except ValueError:
		page = 1

	try:
		urunler = paginator.page( page )
	except (EmptyPage, InvalidPage):
		urunler = paginator.page( paginator.num_pages )

	BaslangicSayfasi = max( page - 2, 1 )

	if BaslangicSayfasi <= 3:
		BaslangicSayfasi = 1
		BitisSayfasi = page + 2 + 1

	if BitisSayfasi >= paginator.num_pages - 1:
		BitisSayfasi = paginator.num_pages + 1

	SayfaSayisi = [n for n in range( BaslangicSayfasi, BitisSayfasi ) if n > 0 and n <= paginator.num_pages]

	return render_to_response( 'yeni_urunler.html', { 'urunler': urunler, 'SayfaSayisi': SayfaSayisi }, context_instance = RequestContext( request ) )


def yeni_urunler_json( request, page ):
	urunlistesi = Urun.objects.filter( Yeni = 1 ).order_by( 'id' )
	paginator = Paginator( urunlistesi, 24 )

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
	paginator = Paginator( urunlistesi, 4 )

	try:
		urunler = paginator.page( page )
	except (EmptyPage, InvalidPage):
		urunler = paginator.page( paginator.num_pages )

	template = 'tracks.json'

	return render_to_response( template, { 'urunler': urunler } )


def FirsatUrunleri( request ):
	firsat_urunleri = Urun.objects.filter( Firsat = 1, varyant__AltKat__id__isnull = False )
	return render_to_response( 'firsat_urunleri.html', { 'firsat_urunleri': firsat_urunleri }, context_instance = RequestContext( request ) )


def EnCokSatanUrunler( request ):
	en_cok_satan_urunler = Urun.objects.filter( EnCokSatan = 1, varyant__AltKat__id__isnull = False )
	return render_to_response( 'en_cok_satan_urunler.html', { 'en_cok_satan_urunler': en_cok_satan_urunler }, context_instance = RequestContext( request ) )


def DefoluUrunler( request ):
	defolu_urunler = Urun.objects.filter( EnCokSatan = 1, varyant__AltKat__id__isnull = False )
	return render_to_response( 'defolu_urunler.html', { 'defolu_urunler': defolu_urunler }, context_instance = RequestContext( request ) )


def KampanyaliUrunler( request ):
	kampanyali_urunler = Urun.objects.filter( EnCokSatan = 1, varyant__AltKat__id__isnull = False )
	return render_to_response( 'kampanyali_urunler.html', { 'kampanyali_urunler': kampanyali_urunler }, context_instance = RequestContext( request ) )
