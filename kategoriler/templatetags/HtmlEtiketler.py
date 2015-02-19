# -*- coding: utf-8 -*-

from decimal import Decimal
import logging
import os
from datetime import datetime, timedelta

from django import template
from django.conf import settings
from django.utils.encoding import smart_str
from django.utils.timezone import utc
from django.db.models import Sum
from django.template.defaultfilters import slugify
import pygeoip
import requests
from requests.exceptions import HTTPError

from kategoriler.models import Kategori, OrtaKategori, AltKategori, Marka, Urun, Varyant, Cinsiyet
from uyeler.models import Kullanicilar, Sepet, SepetUrunler, Siparis
from siteayarlari.models import Banner
from bankalar.models import Taksitler




register = template.Library( )

rawdata = pygeoip.GeoIP( '/home/muslu/GeoLiteCity.dat' )


@register.filter
def Degistir( ne, neyineyle ):
	arg_list = [arg for arg in neyineyle.split( '/' )]

	return str( ne ).replace( arg_list[0], arg_list[1] )


@register.filter
def OzelDurumVarMi( SiparisNo ):
	try:
		OdemeBilgileri = Siparis.objects.filter( SiparisNo = SiparisNo ).last( )

		if OdemeBilgileri.OzelNotMusteri:
			return OdemeBilgileri.OzelNotMusteri
		else:
			return ""
	except:
		return ""


@register.filter
def Resim50Boy( ResimYolu ):
	try:
		return ResimYolu.url.replace( 'urun_resimleri', 'urun_resimleri_50' ).replace( '/media/', '/' )
	except:
		return ResimYolu.replace( 'urun_resimleri', 'urun_resimleri_50' ).replace( '/media/', '/' )


@register.filter
def Markasi( value ):
	try:
		markasi = Marka.objects.get( id = value )
		return markasi.Logo
	except:
		return ""


@register.simple_tag
def Menuler( request ):
	menuler = Cinsiyet.objects.order_by( 'Adi' )

	menuolustur = ''

	for i in menuler:

		if i.Adi != "UNISEX" and i.Adi != "BEBEK":

			menuolustur += ''

			menuolustur += '<li class="level0 first parent dropdown">\n'

			if str( i.Adi ) == u"COCUK":
				menuolustur += u'<a href="/bul/?q=' + i.Adi + '" title="' + i.Adi + u'"> <span style="font-size:15px;"><b>ÇOCUK</b></span> </a>\n'
			else:
				menuolustur += u'<a href="/bul/?q=' + i.Adi + '" title="' + i.Adi + '"> <span style="font-size:15px;"><b>' + i.Adi + '</b></span> </a>\n'

			menuolustur += '<ul class="level0 shown-sub">\n'
			menuolustur += '    <ul class="shadow">\n'
			menuolustur += u'        <li class="row_top"><span class="inside"><i class="icon-heart"></i><a href="/yeni-sezon-indirimli-' + i.Slug + u'-urunleri/">Yeni Ürünler</a>\n'
			menuolustur += u'        <i class=" icon-down-2"></i><a href="/firsat-outlet-indirimli-' + i.Slug + u'-urunleri/">Fırsat Ürünleri</a></span></li>\n'
			menuolustur += '        <li class="row_middle shown-sub">\n'
			menuolustur += '            <ul class="rows_outer">\n'
			menuolustur += '                <li>\n'
			menuolustur += '                    <ul class="menu_row">\n'

			k = 0
			kk = 0
			for ii in Kategori.objects.filter( Cinsiyet = i.id ).order_by( 'Adi' ):

				menuolustur += '                        <li class="col">\n'
				menuolustur += '                            <ul>\n'

				k += 1

				if k == 1:
					menuolustur += '                                <li class="level1 first parent title"> <a> ' + ii.Adi.title( ) + ' </a> </li>\n'
					menuolustur += '                                    <li class="level2 first parent">\n'
				else:
					menuolustur += '                                <li class="level1 parent title"> <a> ' + ii.Adi.title( ) + ' </a> </li>\n'
					menuolustur += '                                    <li class="level2 first">\n'

				for iii in OrtaKategori.objects.filter( UstKat__id = ii.id ).order_by( 'Adi' ):

					if request.mobile:
						menuolustur += u'                                                   <li class="level2">' + iii.Adi.title( ) + ' '
					else:
						menuolustur += u'                                                   <li class="level2"> <a href="/' + slugify( i.Adi ) + '--' + slugify( iii.Adi ) + '-urunleri/' + str( iii.id ) + '/ "> ' + iii.Adi.title( ) + ' </a>\n'

					menuolustur += u'                                                           <ul>\n'
					for iiii in AltKategori.objects.filter( OrtaKat__id = iii.id ).order_by( 'Adi' ):
						menuolustur += u'                                                           <li class="level3"><a href="/online-' + slugify( i.Adi ) + '--' + slugify( iiii.Adi ) + '-satis-modelleri/' + str( iiii.id ) + '/ "><span>' + iiii.Adi.title( ) + '</span></a></li>\n'
					menuolustur += u'                                                           </ul>\n'
					menuolustur += u'                                                       </li>\n'

				menuolustur += '                            </ul>\n'
				menuolustur += '                        </li>\n'

			menuolustur += '                    </ul>\n'
			menuolustur += '                </li>\n'
			menuolustur += '            </ul>\n'
			menuolustur += '            <div class="custom">\n'

			if not i.LogoLink:
				LogoLinki = "/"
			else:
				LogoLinki = i.LogoLink

			if i.Logo:
				menuolustur += u'                <p class="custom_category_menu_text"><a href="' + str( LogoLinki ) + u'"><img data-retina="true" style="width:300px;" src="http://cdn.spormarket.com.tr/media/' + str( i.Logo ) + '" alt=" ' + str( i.Adi ) + ' "></a> </p>\n'
			# if i.Logo: menuolustur += u'                <p class="custom_category_menu_text"><a class="custom_category_link" href="/"></a> </p>\n'
			menuolustur += '            </div>\n'
			menuolustur += '        </li>\n'
			menuolustur += '    </ul>\n'
			menuolustur += '</ul>\n'
			menuolustur += '</li>\n'

	return menuolustur


@register.filter
def VaryantFotoKontrol( StokKodu, Sira ):
	if os.path.isfile( "/home/muslu/django/teslabb/media/urun_resimleri/" + smart_str( StokKodu ) + "_" + str( Sira ) + ".jpg" ):
		return "urun_resimleri/" + smart_str( StokKodu ) + "_" + str( Sira ) + ".jpg"


@register.filter
def id2StokSayisi( StokID ):
	from django.db.models import Sum




	toplam_stok_sayisi = Varyant.objects.filter( Urunu_id = StokID, AltKat__id__isnull = False, StokSayisi__gt = 0 ).aggregate( Sum( 'StokSayisi' ) )
	return str( toplam_stok_sayisi['StokSayisi__sum'] )


@register.filter
def StokID2VaryantBilgileri( StokID ):
	VBilgileri = Varyant.objects.filter( Urunu_id = StokID, AltKat__id__isnull = False, StokSayisi__gt = 0 )
	return VBilgileri


@register.filter
def FotoKontrol( dosyayolu ):
	return os.path.isfile( "/home/muslu/django/teslabb/media/" + str( dosyayolu ) )


@register.filter
def SepetUrunAdeti( request ):
	try:
		UyeID = Kullanicilar.objects.get( user = request.user ).uyeid
	except:
		UyeID = request.COOKIES.get( 'UyeID' )

	try:
		toplam_adet = SepetUrunler.objects.filter( SepetID__id = Sepet.objects.get( UyeID = UyeID, Tamamlandi = False ).id ).aggregate( Sum( 'Adet' ) )

		if toplam_adet['Adet__sum']:
			return '%s' % (toplam_adet['Adet__sum'])
		else:
			return "0"
	except:
		return "0"


@register.filter
def VaryantToplamStokSayisi( id ):
	return range( Varyant.objects.get( id = id ).StokSayisi + 1 )


@register.filter
def UrlKontrol( url ):
	logging.info( url )
	try:
		r = requests.get( url )
		logging.info( r.raise_for_status( ) )
	except HTTPError:
		return False
	else:
		return True


@register.filter
def DonBabaDonelim( kackere ):
	return range( kackere )


@register.simple_tag
def FiyatAdet( Fiyat, Adet, EFiyat, email, Istek ):
	# OZelListe = ["merve@incir.com" ]
	OZelListe = ["musluyuksektepe@gmail.com", "merve@incir.com"]

	SonFiyat = Fiyat * Adet

	if email in OZelListe:

		logging.info( email )
		if EFiyat <= Fiyat:
			SonFiyat = ((Fiyat * Adet) * 80) / 100

	if Istek == "Indirim":
		return (EFiyat * Adet) - SonFiyat

	if Istek == "IndirimOrani":
		return int( (((EFiyat * Adet) - SonFiyat) / (EFiyat * Adet)) * 100 )

	return SonFiyat


@register.filter
def VaryantHangiSubede( Barkod, Istek ):
	try:
		from django.db import connections




		cursor = connections["V3"].cursor( )

		try:
			VaryantBilgisi = Varyant.objects.get( Barkod = Barkod )
		except:
			VaryantBilgisi = Varyant.objects.get( id = Barkod )

		strr = """

        SELECT
            V3_DOGUKAN.dbo.MSEnvanterDepo.M01 AS 'Buca',
            V3_DOGUKAN.dbo.MSEnvanterDepo.S01 AS 'Sirinyer',
            V3_DOGUKAN.dbo.MSEnvanterDepo.OPT AS 'Optimum',
            V3_DOGUKAN.dbo.MSEnvanterDepo.ANADEPO AS 'AnaDepo',
            V3_DOGUKAN.dbo.MSEnvanterDepo.INT AS 'Internet',
            V3_DOGUKAN.dbo.MSEnvanterDepo.TOPL AS 'Toplam'


            FROM V3_DOGUKAN.dbo.MSEnvanterDepo


            WHERE (MSEnvanterDepo.ItemCode = '""" + VaryantBilgisi.Urunu.StokKodu + """' and
             MSEnvanterDepo.ColorCode = '""" + VaryantBilgisi.RenkKodu + """' and
             MSEnvanterDepo.ItemDim1Code = '""" + VaryantBilgisi.Beden + """' and
             MSEnvanterDepo.ItemDim2Code = '""" + VaryantBilgisi.Kavala + """')  """

		cursor.execute( strr )

		# #   print strr


		Donus = ""

		for row in cursor.fetchall( ):

			if Istek == "Olanlar":
				if int( row[0] ) != 0:
					Donus += "b" + str( int( row[0] ) )
				if int( row[1] ) != 0:
					Donus += " s" + str( int( row[1] ) )
				if int( row[2] ) != 0:
					Donus += " o" + str( int( row[2] ) )
				if int( row[3] ) != 0:
					Donus += " d" + str( int( row[3] ) )
				if int( row[4] ) != 0:
					Donus += " i" + str( int( row[4] ) )
			else:
				Donus = "b" + str( int( row[0] ) ), " s" + str( int( row[1] ) ), " o" + str( int( row[2] ) ), " d" + str( int( row[3] ) ), " i" + str( int( row[4] ) )

		return str( ''.join( Donus ).upper( ) )

	except:
		return "Tükendi"


@register.simple_tag
def OdemeSekli( OdemeTuru ):
	if OdemeTuru == "KN":
		return "Kapıda Nakit"
	if OdemeTuru == "KTC":
		return "Kapıda Tek Çekim"
	if OdemeTuru == "HA":
		return "Havale"
	if OdemeTuru == "KKTC":
		return "Kredi Kartı Tek Çekim"
	if OdemeTuru == "KKT":
		return "Kredi Kartı Taksitli"
	if OdemeTuru == "MA":
		return "Mağazadan Ödeme"
	if OdemeTuru == "OP":
		return "Ödemeyi Paylaş"


@register.filter( )
def VaryantID2UrunBilgileri( varID, Istek ):
	UrunBilgileri = Urun.objects.get( varyant__id = varID )
	VaryantBilgileri = Varyant.objects.get( id = varID )

	if Istek == "UrunAdi":
		return UrunBilgileri.Adi
	if Istek == "StokKodu":
		return UrunBilgileri.StokKodu
	if Istek == "Barkod":
		return VaryantBilgileri.Barkod
	if Istek == "EFiyat":
		return UrunBilgileri.EFiyat

	if Istek == "Fiyat":
		return UrunBilgileri.Fiyat

	if Istek == "Logo":
		return UrunBilgileri.Logo
	if Istek == "Indirim":
		return (UrunBilgileri.EFiyat - UrunBilgileri.Fiyat)
	if Istek == "RenkBedenKavala":
		return VaryantBilgileri.Renk + " " + VaryantBilgileri.Beden + " " + VaryantBilgileri.Kavala
	if Istek == "Renk":
		return VaryantBilgileri.Renk
	if Istek == "Kavala":
		return VaryantBilgileri.Kavala
	if Istek == "Beden":
		return VaryantBilgileri.Beden


# /media{{ i.VaryantID|VaryantID2UrunBilgileri:"Logo"|Resim50Boy }}


@register.filter
def SepetUrunlerDiv( request ):
	try:

		try:
			UyeID = Kullanicilar.objects.get( user = request.user ).uyeid
		except:
			UyeID = request.COOKIES.get( 'UyeID' )

		SepettekiUrunlerListesi = SepetUrunler.objects.filter( SepetID__id = Sepet.objects.get( UyeID = UyeID, Tamamlandi = False ).id )

		if len( SepettekiUrunlerListesi ) != 0:

			html = ''

			for i in SepettekiUrunlerListesi:

				VBilgi = Varyant.objects.get( id = i.VaryantID )

				html += ' <div class="item">'

				if VBilgi.Urunu.Logo:
					html += ' <a href="/vd/' + str( i.VaryantID ) + '/" class="product-image"><img style="height:50px; width:50px;" src="http://cdn.spormarket.com.tr/media/' + str( VBilgi.Urunu.Logo ) + '" title="' + VBilgi.Urunu.Adi + '" alt="' + VBilgi.Urunu.Adi + '"></a>'

				html += '       <div class="product-detailes" style="width:200px;">'
				html += '           <a href="/vd/' + i.VaryantID + '/" class="product-name">' + VBilgi.Urunu.Adi + '</a>'

				html += '           <div class="product-price">' + VBilgi.Renk + '</div>'

				if VBilgi.Beden:
					html += '           <div class="product-price">' + VBilgi.Beden + '</div>'
				if VBilgi.Kavala:
					html += '           <div class="product-price">' + VBilgi.Kavala + '</div>'

				html += '           <div class="product-price">' + str( i.Adet ) + ' x ' + str( VBilgi.Urunu.Fiyat ) + ' TL</div>'

				html += '       </div>'
				html += '       <div class="alignright"><a href="/urunsil/' + str( i.VaryantID ) + '/"><i class="icon-trash-3"></i></a> </div>'
				html += ' </div><div class="line-1"></div>'

			html += u'<div class="wrapper"> <a href="/sepetim/" class="button">SİPARİŞİMİ TAMAMLA</a></div>'
			return html

		else:
			return u"Sepetiniz Boş!"


	except:
		return u"Sepetiniz Boş!"


@register.simple_tag
def TatilMi( ):
	Tatil = ""

	import datetime, locale




	locale.setlocale( locale.LC_ALL, 'tr_TR.UTF-8' )

	now = datetime.datetime.now( )
	TahminiTeslimat = now + datetime.timedelta( days = 2 )

	if str( now.strftime( "%A" ) ) == "Cumartesi" and now.hour > 12:
		TahminiTeslimat = now + datetime.timedelta( days = 4 )
		Tatil = "<b style='color: red;'>Kargo firması mesai dışında olduğundan; kargonuz Pazartesi günü gönderilecek.</b>"

	if str( now.strftime( "%A" ) ) == "Pazar":
		TahminiTeslimat = now + datetime.timedelta( days = 3 )
		Tatil = "<b style='color: red;'>Kargo firması mesai dışında olduğundan; kargonuz yarın gönderilecek.</b>"

	if now.hour > 14:
		TahminiTeslimat = now + datetime.timedelta( days = 3 )
		Tatil = "<b style='color: red;'>Kargo firmasının alım saati dolmuştur. Kargonuz yarın gönderilecek.</b> "

	if now.hour > 14 and now.strftime( "%A" ) == "Perşembe":
		TahminiTeslimat = now + datetime.timedelta( days = 4 )
		Tatil = "<b style='color: red;'>Kargo firmasının alım saati dolmuştur. Kargonuz yarın gönderilecek.</b> "

	if now.strftime( "%A" ) == "Cuma":
		TahminiTeslimat = now + datetime.timedelta( days = 3 )

	if now.hour > 14 and now.strftime( "%A" ) == "Cuma":
		TahminiTeslimat = now + datetime.timedelta( days = 3 )
		Tatil = "<b style='color: red;'>Kargo firmasının alım saati dolmuştur. Kargonuz yarın gönderilecek.</b> "

	Tatil += "<br /><b>Tahmini teslimat günü:</b><br /> " + str( TahminiTeslimat.strftime( '%d %B %Y (%A)' ) )

	if TahminiTeslimat.strftime( '%A' ) == "Cumartesi" or now.strftime( "%A" ) == "Cumartesi":
		Tatil += "<br />NOT:<b>Kargo firması Cumartesi günleri yarım gün mesai yapmaktadır.</b>"

	if now.hour > 14 and (now.strftime( "%A" ) == "Perşembe" or now.strftime( "%A" ) == "Cuma"):
		Tatil += "<br />NOT:<b>Kargo firması Cumartesi günleri yarım gün mesai yapmaktadır.</b>"

	Son = '<div class="blockquote style2"><span class="quote"><img src="/media/img/icon_quotes.png" width="41" height="31" alt=""></span><div><p>' + Tatil + '</p> </div></div>'

	return Son


@register.simple_tag
def SiteBilgileri( Istek ):
	return str( settings.__getattr__( Istek ) )


@register.filter
def UyeBilgileri( request ):
	try:
		Bilgiler = Kullanicilar.objects.get( user = request.user.id )
		return Bilgiler.uyeadi + " " + Bilgiler.uyesoyadi
	except:
		return ""


@register.filter
def IndirimdeMi( id ):
	UrunFiyati = Urun.objects.get( id = id )

	IndirimOrani = 100 - ((UrunFiyati.Fiyat / UrunFiyati.EFiyat) * 100)

	if IndirimOrani >= 0:
		return str( int( IndirimOrani ) )


Kargo_Kamp_Fiy = Decimal( settings.__getattr__( "KARGO_KAMPANYA" ) )


@register.filter
def KargoBedavaMi( Tutar ):
	if Tutar > Kargo_Kamp_Fiy:
		KargoBedava = True
	else:
		KargoBedava = False
	return KargoBedava


@register.filter
def Reklamlar( Yerlesim ):
	SuAn = datetime.utcnow( ).replace( tzinfo = utc ) + timedelta( days = 1 )
	banner_liste = Banner.objects.values_list( 'Link', 'Resim', 'Aciklama', 'Baslik' ).filter( BaslamaZamani__lt = (SuAn.strftime( '%Y-%m-%d %H:%M:%S' )), BitirmeZamani__gt = (SuAn.strftime( '%Y-%m-%d %H:%M:%S' )), Aktif = True, Yerlesim = Yerlesim ).order_by( "-Sira" )[0:6]
	return banner_liste


@register.simple_tag
def KK_TaksitHesapla( tid, geneltoplam, Istek ):
	# logging.info("kktaksithesapla tid: " + str(tid) + " gt: " + str(geneltoplam) + " istek: " + str(Istek))

	TaksitBilgileri = Taksitler.objects.get( id = tid )
	VadeFarkSonuc = (TaksitBilgileri.FaizOrani * Decimal( geneltoplam )) / 100
	TaksitTutariSonuc = (((TaksitBilgileri.FaizOrani * Decimal( geneltoplam )) / 100) + Decimal( geneltoplam )) / (TaksitBilgileri.Taksit + TaksitBilgileri.EkTaksit)

	if Istek == "VadeFarki":
		return '{:0.2f}'.format( round( VadeFarkSonuc, 2 ) )

	if Istek == "TaksitTutari":
		return '{:0.2f}'.format( round( TaksitTutariSonuc, 2 ) )

	if Istek == "TaksitTutariKargo":

		if geneltoplam < Kargo_Kamp_Fiy:
			return '{:0.2f}'.format( round( TaksitTutariSonuc + Decimal( settings.__getattr__( "KARGO_TUTARI" ) ), 2 ) )
		else:
			return '{:0.2f}'.format( round( TaksitTutariSonuc, 2 ) )

	if Istek == "VadeliToplamTutar":
		return '{:0.2f}'.format( round( Decimal( geneltoplam ) + VadeFarkSonuc, 2 ) )

	if Istek == "VadeliToplamTutarKargo":
		if geneltoplam < Kargo_Kamp_Fiy:
			return '{:0.2f}'.format( round( Decimal( geneltoplam + Decimal( settings.__getattr__( "KARGO_TUTARI" ) ) ) + VadeFarkSonuc, 2 ) )
		else:
			return '{:0.2f}'.format( round( Decimal( geneltoplam ) + VadeFarkSonuc, 2 ) )











