# -*- coding: utf-8 -*-


# ## SporMarket



from decimal import Decimal
import logging
import string
import datetime
import base64
import hashlib
import urllib
from random import randint, random
from passlib.hash import hex_sha1
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext, Context
from django.template.defaultfilters import slugify
from django.template.loader import get_template
from django.utils.encoding import smart_unicode
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from validate_email import validate_email

from kategoriler.models import Varyant, Urun
from bankalar.models import Bankalar, Taksitler
from kategoriler.templatetags.HtmlEtiketler import FiyatAdet, OdemeSekli
from uyeler.models import SepetUrunler, Sepet, HediyeKuponu, Kullanicilar, DFOdeme, DFOdemeArsiv, Siparis, SiparisArsiv, SiparisDurumlari, SiparisDurumKategorileri, KKOdemeArsiv, SMSArsiv




os.environ.setdefault( "DJANGO_SETTINGS_MODULE", "settings" )

OZelListe = ["musluyuksektepe@gmail.com", "merve@incir.com"]


def Hesabim( request ):
	# try:
	try:
		UyeID = Kullanicilar.objects.get( user = request.user ).uyeid
		UyeBilgileri = Kullanicilar.objects.get( user = request.user )
	except:
		UyeID = request.COOKIES.get( 'UyeID' )
		UyeBilgileri = { }

	SiparisBilgileri = Siparis.objects.filter( UyeID = UyeID )

	return render_to_response( 'hesabim.html', { 'UyeBilgileri': UyeBilgileri, 'SiparisBilgileri': SiparisBilgileri, }, context_instance = RequestContext( request ) )


# except:
# return redirect("/404/")


@csrf_exempt
def Sepetim( request ):
	# try:
	request.session['SepetiID'] = randint( 10000, 99999 )

	try:
		UyeID = Kullanicilar.objects.get( user = request.user ).uyeid
		UyeBilgileri = Kullanicilar.objects.get( user = request.user )

		emaili = UyeBilgileri.uyemail
		if emaili in OZelListe:
			Vip = "Evet"
		else:
			Vip = "Hayir"

	except:
		UyeID = request.COOKIES.get( 'UyeID' )
		UyeBilgileri = { }
		Vip = "Hayir"

	#~ try:
	x_forwarded_for = request.META.get( 'HTTP_X_FORWARDED_FOR' )
	if x_forwarded_for:
		ip = x_forwarded_for.split( ',' )[0]
	else:
		ip = request.META.get( 'REMOTE_ADDR' )

	try:

		sepet_id = Sepet.objects.get( UyeID = UyeID, Tamamlandi = False, IP = ip )

		sepet_liste = SepetUrunler.objects.filter( SepetID = sepet_id.id ).order_by( 'Adet' )

		EF = 0
		F = 0
		EFF = 0

		for i in sepet_liste:

			Fiyati = Urun.objects.get( varyant__id = i.VaryantID ).Fiyat
			EFiyati = Urun.objects.get( varyant__id = i.VaryantID ).EFiyat

			EF += EFiyati * i.Adet
			try:
				F += FiyatAdet( Fiyati, i.Adet, EFiyati, request.user.email, "" )
			except:
				F += Fiyati * i.Adet

		EFF = EF - F

		idlerim = ()

		for ii in sepet_liste:

			UrunTukendiMi = Varyant.objects.filter( id = ii.VaryantID ).order_by( '-id' )[0]

			if UrunTukendiMi.StokSayisi != 0:

				idlerim += (str( Varyant.objects.get( id = ii.VaryantID ).Urunu.id ),)

		SuAn = datetime.datetime.utcnow( ).replace( tzinfo = utc ) + datetime.timedelta( days = 1 )
		KuponVarMi = HediyeKuponu.objects.filter( Kullanildi = False, Urun__id__in = idlerim, BaslamaZamani__lt = (SuAn.strftime( '%Y-%m-%d %H:%M:%S' )), BitirmeZamani__gt = (SuAn.strftime( '%Y-%m-%d %H:%M:%S' )), ).count( )

		AktifKuponVar = False

		if KuponVarMi >= 1:
			AktifKuponVar = True

		BosSepet = False

	except:
		sepet_liste = { }
		EF = 0
		F = 0
		EFF = 0
		sepet_id = 0
		BosSepet = True
		AktifKuponVar = False

	try:
		SonSiparisi = Siparis.objects.filter( UyeID = UyeID ).order_by( '-id' ).last( )
	except:
		SonSiparisi = { }

	response = render_to_response( 'sepet.html', { 'sepet_liste': sepet_liste, 'EF': EF, 'F': F, 'EFF': EFF, 'AktifKuponVar': AktifKuponVar, 'sepet_id': sepet_id, 'SonSiparisi': SonSiparisi, 'UyeBilgileri': UyeBilgileri, 'BosSepet': BosSepet, 'VIP': Vip, }, context_instance = RequestContext( request ) )
	return response


# except:
#     try:
#         SonSiparisi = Siparis.objects.filter( UyeID = UyeID ).order_by( '-id' ).last( )
#     except:
#         SonSiparisi = { }
#     return render_to_response( 'sepet.html', { 'BosSepet': True, 'SonSiparisi': SonSiparisi, }, context_instance = RequestContext( request ) )


@csrf_exempt
def SiparisTamamla( request ):
	try:
		UyeID = Kullanicilar.objects.get( user = request.user ).uyeid

		emaili = Kullanicilar.objects.get( user = request.user ).uyemail
		if emaili in OZelListe:
			Vip = "Evet"
		else:
			Vip = "Hayir"

	except:
		UyeID = request.COOKIES.get( 'UyeID' )
		Vip = "Hayir"

	GenelTutar = request.POST.get( 'GenelTutar', None )
	SepetID = request.POST.get( 'cEm', None )
	GelenSepetID = SepetID[0:5]

	SonToplam = 0;
	KargoUcreti = 0;
	SMSUcreti = 0;
	OdemeHizmetBedeli = 0

	x_forwarded_for = request.META.get( 'HTTP_X_FORWARDED_FOR' )
	if x_forwarded_for:
		ip = x_forwarded_for.split( ',' )[0]
	else:
		ip = request.META.get( 'REMOTE_ADDR' )

	GerceksepetIDsi = Sepet.objects.get( UyeID = UyeID, Tamamlandi = False, IP = ip )

	sepet_liste = SepetUrunler.objects.filter( SepetID = GerceksepetIDsi.id ).order_by( 'Adet' )

	F = 0;
	EF = 0
	for i in sepet_liste:
		Fiyati = Urun.objects.get( varyant__id = i.VaryantID ).Fiyat
		EFiyati = Urun.objects.get( varyant__id = i.VaryantID ).EFiyat

		EF += EFiyati * i.Adet
		try:
			F += FiyatAdet( Fiyati, i.Adet, EFiyati, request.user.email, "" )
		except:
			F += Fiyati * i.Adet

	GenelTutar = GenelTutar.replace( ',', '.' )

	OdemeNasil = SepetID[5:7] + SepetID[8:11]
	SmsSayisi = SepetID[7]

	if OdemeNasil == "86154":
		OdemeTuru = "KN"
	if OdemeNasil == "35634":
		OdemeTuru = "KTC"
	if OdemeNasil == "25325":
		OdemeTuru = "HA"
	if OdemeNasil == "35764":
		OdemeTuru = "KKTC"
	if OdemeNasil == "87473":
		OdemeTuru = "KKT"
	if OdemeNasil == "35351":
		OdemeTuru = "OP"

	if Decimal( GenelTutar.replace( ',', '.' ) ) < Decimal( settings.__getattr__( 'KARGO_KAMPANYA' ) ):
		KargoUcreti = Decimal( settings.__getattr__( 'KARGO_TUTARI' ) )

	if SmsSayisi != 0:
		SMSUcreti = int( SmsSayisi ) * Decimal( settings.__getattr__( 'SMS_UCRETI' ) )

	if OdemeTuru == "KN" or OdemeTuru == "KTC":
		OdemeHizmetBedeli = Decimal( settings.__getattr__( 'HIZMET_BEDELI' ) )

	if OdemeTuru == "MA":
		KargoUcreti = 0

	if Vip == "Evet":
		KargoUcreti = 0
	else:
		KargoUcreti = KargoUcreti

	SonToplam = Decimal( GenelTutar ) + Decimal( SMSUcreti ) + Decimal( KargoUcreti ) + Decimal( OdemeHizmetBedeli )

	# logging.info(request.POST)


	# ############################## Form Bilgileri ####################################
	UyelikIstendi = request.POST.get( 'uyelik', False )

	TAdSoyad = request.POST.get( 'isimsoyisim', None )
	TIl = request.POST.get( 'sehir', None )
	TAdres = request.POST.get( 'adres', None )

	Telefon = request.POST.get( 'telefon', None )
	Telefon = Telefon[0:4] + " " + Telefon[4:7] + " " + Telefon[7:]

	uyemail = request.POST.get( 'mail', None )

	Not = request.POST.get( 'not', '' )

	Paket = False
	if Not != '':
		Paket = True

	SMS_Ulasilamadi = request.POST.get( 'SMS_Ulasilamadi', False )
	SMS_Hazirlaniyor = request.POST.get( 'SMS_Hazirlaniyor', False )
	SMS_Paketlendi = request.POST.get( 'SMS_Paketlendi', False )
	SMS_KargoyaVerildi = request.POST.get( 'SMS_KargoyaVerildi', False )
	SMS_KaampanyaBilgileri = request.POST.get( 'SMS_KaampanyaBilgileri', False )

	indirimkuponu = request.POST.get( 'indirimkuponu', '' )

	hitap = request.POST.get( 'hitap', '' )
	ohitap = request.POST.get( 'ohitap', '' )
	omesaj = request.POST.get( 'omesaj', '' )
	otelefon = request.POST.get( 'otelefon', '' )
	#++############################## Form Bilgileri ####################################

	x_forwarded_for = request.META.get( 'HTTP_X_FORWARDED_FOR' )
	if x_forwarded_for:
		ip = x_forwarded_for.split( ',' )[0]
	else:
		ip = request.META.get( 'REMOTE_ADDR' )

	if UyelikIstendi == "true":
		Uyelik = True
	else:
		Uyelik = False

	if Uyelik:

		try:
			first_name = TAdSoyad.split( ' ' )[0]
			last_name = TAdSoyad.split( ' ' )[1]
		except:
			first_name = TAdSoyad
			last_name = TAdSoyad

		uyepassword = randint( 1000000, 9999999 )
		user = User.objects.create_user( username = uyemail, email = uyemail, password = uyepassword, first_name = first_name, last_name = last_name )
		user.save( )

		user.backend = 'django.contrib.auth.backends.ModelBackend'
		KullaniciBilgileri = Kullanicilar( user = user, uyeadi = first_name, uyesoyadi = last_name, uyemail = uyemail, uyeid = UyeID, uyetelefon = Telefon, uyepassword = uyepassword, uyeip = ip )
		KullaniciBilgileri.save( )
		login( request, user )

		Mesaj = " Merhaba  " + TAdSoyad + u"; spormarket.com.tr parolanız: " + str( uyepassword ) + u" mail adresiniz: " + str( uyemail )

		Apimiz = u"http://www.pratikbilisim.net/panel/smsgonder.php?kno=12234&kul_ad=905325614848&sifre=539425&gonderen=SPORMARKET&mesaj='" + Mesaj + "'&cepteller=" + Telefon.replace( ' ', '' )
		uo = urllib.urlopen( Apimiz.encode( 'utf-8' ) )

		SMSGittiMi = uo.read( )
		if "Gonderildi" in SMSGittiMi:
			smsekle = SMSArsiv( UyeID = str( UyeID ), Telefon = Telefon.replace( ' ', '' ), Mesaj = Mesaj, Durum = True )
			smsekle.save( )
		else:
			smsekle = SMSArsiv( UyeID = str( UyeID ), Telefon = Telefon.replace( ' ', '' ), Mesaj = Mesaj, Durum = False )
			smsekle.save( )

	GerceksepetIDsi.Tamamlandi = True
	GerceksepetIDsi.save( )

	SiparisNosu = randint( 1000000, 9999999 )

	Ulasilamadi = False;
	Hazirlaniyor = False;
	Paketlendi = False;
	KargoyaVerildi = False;
	KaampanyaBilgileri = False

	if SMS_Ulasilamadi == "true":
		Ulasilamadi = True
	if SMS_Hazirlaniyor == "true":
		Hazirlaniyor = True
	if SMS_Paketlendi == "true":
		Paketlendi = True
	if SMS_KargoyaVerildi == "true":
		KargoyaVerildi = True
	if SMS_KaampanyaBilgileri == "true":
		KaampanyaBilgileri = True

	SiparisKaydet = Siparis( SiparisNo = SiparisNosu, UyeID = UyeID, SepetID = GerceksepetIDsi.id, Mail = uyemail, UrunlerToplamTutar = EF, IndToplamTutar = Decimal( EF - F ), GenelToplam = SonToplam, KargoBedeli = KargoUcreti, HizmetBedeli = OdemeHizmetBedeli, SMSBedeli = SMSUcreti, TAdSoyad = TAdSoyad, TIl = TIl, TAdres = TAdres, Telefon = Telefon, OdemeTuru = OdemeTuru, Not = Not, Paket = Paket, IP = ip, SMS_Ulasilamadi = Ulasilamadi, SMS_Hazirlaniyor = Hazirlaniyor, SMS_Paketlendi = Paketlendi, SMS_KargoyaVerildi = KargoyaVerildi, SMS_KaampanyaBilgileri = KaampanyaBilgileri, Kategori = SiparisDurumKategorileri.objects.get( id = 1 ), Durum = SiparisDurumlari.objects.get( id = 1 ), OdemeYapildi = False )

	SiparisKaydet.save( )

	SiparisArsiv( SiparisNo = SiparisNosu, Durum = SiparisDurumlari.objects.get( id = 1 ).Durum, TAdSoyad = TAdSoyad, Telefon = Telefon, Mail = uyemail, Not = OdemeTuru ).save( )

	SiparisBilgileri = Siparis.objects.get( UyeID = UyeID, OdemeYapildi = False, SiparisNo = SiparisNosu )

	if OdemeTuru == "HA" or OdemeTuru == "KN" or OdemeTuru == "KTC":

		Mesaj = "Merhaba " + slugify( SiparisBilgileri.TAdSoyad ).replace( '-', ' ' ).split( ' ' )[0].title( ) + u"; siparisin tamamlandi. Siparis Numaran: " + str( SiparisBilgileri.SiparisNo ) + " http://spor.la/" + str( SiparisBilgileri.SiparisNo )
		Apimiz = u"http://www.pratikbilisim.net/panel/smsgonder.php?kno=12234&kul_ad=905325614848&sifre=539425&gonderen=SPORMARKET&mesaj='" + Mesaj + "'&cepteller=" + SiparisBilgileri.Telefon.replace( ' ', '' )
		uo = urllib.urlopen( Apimiz )

		SMSGittiMi = uo.read( )
		if "Gonderildi" in SMSGittiMi:
			smsekle = SMSArsiv( UyeID = str( UyeID ), Telefon = SiparisBilgileri.Telefon, Mesaj = Mesaj, Durum = True )
			smsekle.save( )
		else:
			smsekle = SMSArsiv( UyeID = str( UyeID ), Telefon = SiparisBilgileri.Telefon, Mesaj = Mesaj, Durum = False )
			smsekle.save( )

	SepetUrunlerBilgileri = SepetUrunler.objects.filter( SepetID = SiparisBilgileri.SepetID )
	MailMesaj = get_template( 'mail_yazdir.html' ).render( Context( { 'SepetUrunlerBilgileri': SepetUrunlerBilgileri, 'SiparisBilgileri': SiparisBilgileri, } ) )

	try:
		msg = EmailMessage( 'Yeni Siparisiniz', MailMesaj, to = [SiparisBilgileri.Mail, ] )
	except:
		pass

	msg = EmailMessage( smart_unicode( OdemeSekli( OdemeTuru ) ) + " " + str( SiparisBilgileri.GenelToplam ) + " TL", MailMesaj, to = ['siparis@spormarket.com.tr'] )

	urllib.urlretrieve( "http://htmltopdfapi.com/querybuilder/api.php?url=http://www.spormarket.com.tr/yazdir/" + str( SiparisBilgileri.SiparisNo ), "/home/muslu/django/teslabb/media/SiparisPdf/" + str( SiparisBilgileri ) + ".pdf" )

	msg.attach_file( "/home/muslu/django/teslabb/media/SiparisPdf/" + str( SiparisBilgileri ) + ".pdf" )

	msg.content_subtype = "html"
	msg.send( )



	# if OdemeTuru == "OP":
	#
	#     hitabi = hitap
	#     if ohitap != "":
	#         hitabi = ohitap
	#
	#     Mesaj = hitabi + " ben " + TAdSoyad.split( " " )[0] + u"; bana bunu alır mısın? " + "http://spormarket.com.tr/op/" + str( SiparisNosu ) + "/"
	#
	#     Apimiz = u"http://www.pratikbilisim.net/panel/smsgonder.php?kno=12234&kul_ad=905325614848&sifre=539425&gonderen=SPORMARKET&mesaj='" + Mesaj + "'&cepteller=" + otelefon.replace( ' ', '' )
	#     uo = urllib.urlopen( Apimiz.encode( 'utf-8' ) )
	#
	#     SMSGittiMi = uo.read( )
	#     if "Gonderildi" in SMSGittiMi:
	#         smsekle = SMSArsiv( UyeID = str( UyeID ), GonderenTelefon = SiparisKaydet.Telefon, Telefon = otelefon, Mesaj = Mesaj, Durum = True )
	#         smsekle.save( )
	#     else:
	#         smsekle = SMSArsiv( UyeID = str( UyeID ), GonderenTelefon = SiparisKaydet.Telefon, Telefon = otelefon, Mesaj = Mesaj, Durum = False )
	#         smsekle.save( )
	#


	response = HttpResponse( SiparisKaydet.id )
	response.set_cookie( 'SiparisNosu', str( SiparisNosu ) )
	response.set_cookie( 'OdemeTuru', str( OdemeTuru ) )

	logging.info( SiparisNosu )
	return response


@csrf_exempt
def SiparisTamamlandi( request ):
	# try:

	try:
		UyeID = Kullanicilar.objects.get( user = request.user ).uyeid
	except:
		UyeID = request.COOKIES.get( 'UyeID' )

	SiparisNosu = request.COOKIES.get( 'SiparisNosu', None )
	odemeturu = request.COOKIES.get( 'OdemeTuru', None )

	if SiparisNosu:

		SiparisBilgileri = Siparis.objects.get( UyeID = UyeID, OdemeYapildi = False, SiparisNo = SiparisNosu )

		BankaListesi = Bankalar.objects.filter( Aktif = True )

		if odemeturu == "HA" or odemeturu == "KN" or odemeturu == "KTC":
			return render_to_response( 'siparistamamlandi.html', { 'SiparisBilgileri': SiparisBilgileri, 'BankaListesi': BankaListesi }, context_instance = RequestContext( request ) )
		else:
			logging.info( "odemeyap/" + str( SiparisNosu ) )
			return HttpResponseRedirect( "/odemeyap/" + str( SiparisNosu ) + "/" )


	else:
		return redirect( "/" )

	# except:
	# return redirect ("/")


@csrf_exempt
def OdemeYaptir( request, SiparisNosu ):
	BankaListesi = Bankalar.objects.filter( Aktif = True )

	# try:
	SiparisBilgileri = Siparis.objects.get( OdemeYapildi = False, SiparisNo = SiparisNosu )

	SonToplam = (Decimal( SiparisBilgileri.UrunlerToplamTutar ) - Decimal( SiparisBilgileri.IndToplamTutar )) + Decimal( SiparisBilgileri.SMSBedeli ) + Decimal( SiparisBilgileri.KargoBedeli ) + Decimal( SiparisBilgileri.HizmetBedeli )

	SiparisBilgileri.VadeFarki = 0
	SiparisBilgileri.Banka = 0
	SiparisBilgileri.GenelToplam = SonToplam
	SiparisBilgileri.save( )

	response = render_to_response( 'odemeyaptir.html', { 'SiparisBilgileri': SiparisBilgileri, 'BankaListesi': BankaListesi }, context_instance = RequestContext( request ) )
	response.set_cookie( 'SiparisNosu', str( SiparisNosu ) )
	return response


# except:
#     response = render_to_response( 'odemeyiyap.html', { 'BankaListesi': BankaListesi, 'Hata': u"Sipariş Bulunamadı" }, context_instance = RequestContext( request ) )
#     response.set_cookie( 'SiparisNosu', str( SiparisNosu ) )
#     return response


@csrf_exempt
def OP( request, SiparisNosu ):
	BankaListesi = Bankalar.objects.filter( Aktif = True )

	try:
		SiparisBilgileri = Siparis.objects.get( OdemeYapildi = False, SiparisNo = SiparisNosu )
		SepetUrunlerBilgileri = SepetUrunler.objects.filter( SepetID = SiparisBilgileri.SepetID )
		response = render_to_response( 'op.html', { 'SiparisBilgileri': SiparisBilgileri, 'BankaListesi': BankaListesi, 'SepetUrunlerBilgileri': SepetUrunlerBilgileri }, context_instance = RequestContext( request ) )
		response.set_cookie( 'SiparisNosu', str( SiparisNosu ) )
		return response


	except:
		response = render_to_response( 'op.html', { 'BankaListesi': BankaListesi, 'Hata': u"Sipariş Bulunamadı" }, context_instance = RequestContext( request ) )
		return response


@csrf_exempt
def Bankaya( request, BankaID ):
	# try:

	x_forwarded_for = request.META.get( 'HTTP_X_FORWARDED_FOR' )
	if x_forwarded_for:
		ip = x_forwarded_for.split( ',' )[0]
	else:
		ip = request.META.get( 'REMOTE_ADDR' )


	# BankaID = request.POST.get( 'bankaID', None )

	if BankaID:

		SiparisNosu = request.COOKIES.get( 'SiparisNosu', None )

		SiparisBilgileri = Siparis.objects.get( OdemeYapildi = False, SiparisNo = SiparisNosu )

		TaksitBilgileri = Taksitler.objects.get( id = BankaID )

		ToplamTaksit = TaksitBilgileri.Taksit

		SonToplam = (Decimal( SiparisBilgileri.UrunlerToplamTutar ) - Decimal( SiparisBilgileri.IndToplamTutar )) + Decimal( SiparisBilgileri.SMSBedeli ) + Decimal( SiparisBilgileri.KargoBedeli ) + Decimal( SiparisBilgileri.HizmetBedeli )

		SiparisBilgileri.VadeFarki = 0
		SiparisBilgileri.Banka = ToplamTaksit
		SiparisBilgileri.GenelToplam = SonToplam
		SiparisBilgileri.save( )

		SiparisBilgileri = Siparis.objects.get( OdemeYapildi = False, SiparisNo = SiparisNosu )

		VadeFarki = (TaksitBilgileri.FaizOrani * Decimal( SiparisBilgileri.GenelToplam ) ) / 100
		FormatliVadeFarki = '{:0.2f}'.format( Decimal( VadeFarki ), 2 )
		FormatliGenelToplam = '{:0.2f}'.format( Decimal( SiparisBilgileri.GenelToplam ) + Decimal( FormatliVadeFarki ), 2 )

		SiparisBilgileri.VadeFarki = FormatliVadeFarki
		SiparisBilgileri.GenelToplam = FormatliGenelToplam
		SiparisBilgileri.save( )

		EST_OID = randint( 100000000, 9999999999 )
		EST_RND = randint( 100000000, 9999999999 )

		okUrl = "http://spormarket.com.tr/odemetamamlandi/"
		failUrl = "http://spormarket.com.tr/odemetamamlanamadi/"

		hashi = ""

		if TaksitBilgileri.Banka.Adi == "Akbank" or TaksitBilgileri.Banka.Adi == "HalkBank" or TaksitBilgileri.Banka.Adi == u"Finans Bank" or TaksitBilgileri.Banka.Adi == u"İş Bankası":

			clientId = TaksitBilgileri.Banka.MusteriNumarasi
			storekey = TaksitBilgileri.Banka.GuvenlikAnahtari

			if ToplamTaksit == 1:
				hashstr = str( clientId ) + str( EST_OID ) + str( FormatliGenelToplam ) + okUrl + failUrl + "Auth" + str( EST_RND ) + str( storekey )
			else:
				hashstr = str( clientId ) + str( EST_OID ) + str( FormatliGenelToplam ) + okUrl + failUrl + "Auth" + str( ToplamTaksit ) + str( EST_RND ) + str( storekey )

			hashi = base64.b64encode( hashlib.sha1( hashstr ).digest( ) )

		if TaksitBilgileri.Banka.Adi == u"Garanti Bankası":


			okUrl = "http://spormarket.com.tr/odemetamamlandi/"
			failUrl = "http://spormarket.com.tr/odemetamamlanamadi/"

			clientId = "10021997"
			storekey = "73706F726D61726B6574656F726A676F6572677265726765"
			islemtipi = "sales"

			strTerminalID = "10021997"
			strTerminalID_ = "0" + strTerminalID

			FormatliGenelToplam = '{:0.2f}'.format( Decimal( FormatliGenelToplam ), 2 ).replace( '.', '' ).replace( ',', '' )

			SecurityData = hex_sha1.encrypt( "KUTu3535" + strTerminalID_ ).upper( )

			if ToplamTaksit == 1:
				hashstr = strTerminalID + SiparisBilgileri.SiparisNo + str( FormatliGenelToplam ) + okUrl + failUrl + islemtipi + "0" + storekey + str( SecurityData )
			else:
				hashstr = strTerminalID + SiparisBilgileri.SiparisNo + str( FormatliGenelToplam ) + okUrl + failUrl + islemtipi + str( ToplamTaksit ) + storekey + str( SecurityData )

			hashi = hex_sha1.encrypt( hashstr ).upper( )

		return render_to_response( 'bankaform.html', { 'SiparisBilgileri': SiparisBilgileri, 'FormatliGenelToplam': FormatliGenelToplam, 'TaksitBilgileri': TaksitBilgileri, 'ToplamTaksit': ToplamTaksit, 'EST_OID': EST_OID, 'EST_RND': EST_RND, 'hashi': hashi, 'ip': ip, 'okUrl': okUrl, 'failUrl': failUrl, }, context_instance = RequestContext( request ) )




	# except:
	#
	#     return redirect ("/404/")


@csrf_exempt
def OdemeTamamlanamadi( request ):
	# logging.info(request)


	Hata = request.POST.get( 'mdErrorMsg', "" )
	Hataa = request.POST.get( 'ErrMsg', "" )
	Hataaa = request.POST.get( 'errmsg', "" )
	HataYKB = request.GET.get( 'errmsg', "" )

	EXTRAHOSTMSG = request.POST.get( 'EXTRA.HOSTMSG', "" )

	FormatliGenelToplam = request.POST.get( 'amount', "" )
	Taksit = request.POST.get( 'taksiti', "" )
	Bankasi = request.POST.get( 'banka', '' )
	BankaYKB = request.GET.get( 'ykbrefno', '' )

	YKB = "xid=00000000000009505720&returnmessage=Onaylanmad%FD&returncode=0&authcode=&ykbrefno=&amount=119,25&currency=TL&errmsg=Red-Onaylanmadi++++++++++++++++++++0005&errcode=0005/"
	YKB = 'xid=00000000000009389826&returnmessage=Onayland%FD&returncode=1&authcode=588300&ykbrefno=160862950790010151&amount=126,28&currency=TL&errmsg=&errcode=/'

	try:
		UyeID = Kullanicilar.objects.get( user = request.user ).uyeid
	except:
		UyeID = request.COOKIES.get( 'UyeID' )

	x_forwarded_for = request.META.get( 'HTTP_X_FORWARDED_FOR' )
	if x_forwarded_for:
		ip = x_forwarded_for.split( ',' )[0]
	else:
		ip = request.META.get( 'REMOTE_ADDR' )

	SiparisNoG = request.POST.get( 'orderid', "" )
	SiparisNoEST = request.POST.get( 'SiparisNo', "" )
	SiparisNoYKB = request.GET.get( 'xid', "" )

	try:
		SiparisNo = request.COOKIES['SiparisNosu']
	except:
		SiparisNo = SiparisNoG + SiparisNoEST + SiparisNoYKB[-7:]

	KKOdemeArsiv( SiparisNo = SiparisNo, UyeID = UyeID, Hata = Hata + " " + Hataa + " " + Hataaa + " " + HataYKB, EXTRAHOSTMSG = EXTRAHOSTMSG, ip = ip, FormatliGenelToplam = FormatliGenelToplam, Taksit = Taksit, BankaAdi = Bankasi + BankaYKB ).save( )

	SiparisBilgileri = Siparis.objects.get( SiparisNo = SiparisNo )
	SiparisBilgileri.OzelNot = Hata + " " + Hataa + " " + Hataaa + " " + HataYKB
	SiparisBilgileri.OzelNotMusteri = Hata + " " + Hataa + " " + Hataaa + " " + HataYKB
	SiparisBilgileri.save( )

	SiparisArsivBilgileri = SiparisArsiv.objects.filter( SiparisNo = SiparisNo ).last( )
	SiparisArsivBilgileri.OzelNot = Hata + " " + Hataa + " " + Hataaa + " " + HataYKB
	SiparisArsivBilgileri.save( )

	MailMesaj = ""
	MailMesaj += u"<table width='99%' border='0' cellspacing='4' cellpadding='5' bordercolor='#dcdcdc' >"
	MailMesaj += u"<tr><td colspan='3'><b>Hatalı Ödeme </b></td></tr>"
	MailMesaj += u"<tr>"
	MailMesaj += u"<td width='35%'><b>Ad Soyad</b></td>"
	MailMesaj += u"<td width='5%'><b>:</b></td>"
	MailMesaj += u"<td width='60%'>" + SiparisBilgileri.TAdSoyad + "</td>"
	MailMesaj += u"</tr>"
	MailMesaj += u"<tr>"
	MailMesaj += u"<td><b>Sipariş No</b></td>"
	MailMesaj += u"<td><b>:</b></td>"
	MailMesaj += u"<td>" + SiparisBilgileri.SiparisNo + "</td>"
	MailMesaj += u"</tr>"
	MailMesaj += u"<tr>"
	MailMesaj += u"<td><b>Tutar</b></td>"
	MailMesaj += u"<td><b>:</b></td>"
	MailMesaj += u"<td>" + '{:0.2f}'.format( Decimal( SiparisBilgileri.GenelToplam ), 2 ) + " TL</td>"
	MailMesaj += u"</tr>"
	MailMesaj += u"<tr>"
	MailMesaj += u"<td><b>Banka</b></td>"
	MailMesaj += u"<td><b>:</b></td>"
	MailMesaj += u"<td>" + Bankasi + BankaYKB + " " + str( Taksit ) + "</td>"
	MailMesaj += u"</tr>"
	MailMesaj += u"<tr>"
	MailMesaj += u"<td><b>Hata</b></td>"
	MailMesaj += u"<td><b>:</b></td>"
	MailMesaj += u"<td>" + Hata + " " + Hataa + " " + Hataaa + " " + HataYKB + "</td>"
	MailMesaj += u"</tr>"
	MailMesaj += u"<tr>"
	MailMesaj += u"<td><b>IP</b></td>"
	MailMesaj += u"<td><b>:</b></td>"
	MailMesaj += u"<td>" + str( ip ) + "</td>"
	MailMesaj += u"</tr>"
	MailMesaj += u"</table>"

	msg = EmailMessage( 'Hatalı Ödeme', MailMesaj, to = ['siparis@spormarket.com.tr', ] )
	msg.content_subtype = "html"
	msg.send( )

	return render_to_response( 'odemetamamlanamadi.html', { 'SiparisNo': SiparisNo, 'ErrMsg': Hata + " " + Hataa + " " + Hataaa + " " + HataYKB, 'EXTRAHOSTMSG': EXTRAHOSTMSG,

	}, context_instance = RequestContext( request ) )


@csrf_exempt
def OdemeTamamlandi( request ):
	try:
		UyeID = Kullanicilar.objects.get( user = request.user ).uyeid
	except:
		UyeID = ""

	logging.info( request )

	Bankasi = request.POST.get( 'banka', '' )
	ykbrefno = request.GET.get( 'ykbrefno', '' )

	YKBTutar = request.GET.get( 'amount', '' )
	Tutar = request.POST.get( 'amount', '' )

	Taksit = request.POST.get( 'taksiti', "" )

	SiparisNoG = request.POST.get( 'orderid', "" )
	SiparisNoEST = request.POST.get( 'SiparisNo', "" )
	SiparisNoYKB = request.GET.get( 'xid', "" )

	if ykbrefno != "":
		Tutar = YKBTutar
		Bankasi = "YKB"

	try:
		SiparisNosu = request.COOKIES['SiparisNosu']
	except:
		SiparisNosu = SiparisNoG + SiparisNoEST + SiparisNoYKB[-7:]

	SiparisBilgileri = Siparis.objects.get( SiparisNo = SiparisNosu.strip( ) )
	SiparisBilgileri.OdemeYapildi = True
	SiparisBilgileri.BankaGenelToplam = str( Tutar )
	SiparisBilgileri.Banka = SiparisBilgileri.Banka + " " + Bankasi
	SiparisBilgileri.save( )

	Mesaj = "Merhaba " + slugify( SiparisBilgileri.TAdSoyad ).replace( '-', ' ' ).title( ) + u"; odemeniz tamamlanmistir. http://spor.la/" + str( SiparisBilgileri.SiparisNo )
	Apimiz = u"http://www.pratikbilisim.net/panel/smsgonder.php?kno=12234&kul_ad=905325614848&sifre=539425&gonderen=SPORMARKET&mesaj='" + Mesaj + "'&cepteller=" + SiparisBilgileri.Telefon.replace( ' ', '' )
	uo = urllib.urlopen( Apimiz )

	SMSGittiMi = uo.read( )
	if "Gonderildi" in SMSGittiMi:
		smsekle = SMSArsiv( UyeID = SiparisBilgileri.UyeID, Telefon = SiparisBilgileri.Telefon.replace( ' ', '' ), Mesaj = Mesaj, Durum = True )
		smsekle.save( )
	else:
		smsekle = SMSArsiv( UyeID = SiparisBilgileri.UyeID, Telefon = SiparisBilgileri.Telefon.replace( ' ', '' ), Mesaj = Mesaj, Durum = False )
		smsekle.save( )

	SepetUrunlerBilgileri = SepetUrunler.objects.filter( SepetID = SiparisBilgileri.SepetID )
	MailMesaj = get_template( 'mail_yazdir.html' ).render( Context( { 'SepetUrunlerBilgileri': SepetUrunlerBilgileri, 'SiparisBilgileri': SiparisBilgileri, } ) )

	try:
		msg = EmailMessage( u'Yeni Siparisiniz', MailMesaj, to = [SiparisBilgileri.Mail, ] )
	except:
		pass

	msg = EmailMessage( u'Ödeme Tamamlandı' + str( SiparisBilgileri.GenelToplam ) + " TL", MailMesaj, to = ['siparis@spormarket.com.tr'] )

	msg.content_subtype = "html"
	msg.send( )

	response = render_to_response( 'odemetamamlandi.html', { 'SiparisBilgileri': SiparisBilgileri }, context_instance = RequestContext( request ) )

	response.delete_cookie( 'SiparisNosu' )
	response.delete_cookie( 'OdemeTuru' )
	response.delete_cookie( 'VaryantID' )

	return response


@csrf_exempt
def SiparisDetayGoster( request ):
	SiparisNo = request.POST['SiparisNo']

	SiparisBilgileri = Siparis.objects.get( SiparisNo = SiparisNo )
	SepetUrunlerBilgileri = SepetUrunler.objects.filter( SepetID = SiparisBilgileri.SepetID )
	SiparisArsivBilgileri = SiparisArsiv.objects.filter( SiparisNo = SiparisNo ).order_by( '-IslemTarihi' )
	return render_to_response( 'sipdetay.html', { 'SepetUrunlerBilgileri': SepetUrunlerBilgileri, 'SiparisBilgileri': SiparisBilgileri, 'SiparisArsivBilgileri': SiparisArsivBilgileri, }, context_instance = RequestContext( request ) )


def SiparisSesliCevap( request, SiparisNo ):
	idsi = Siparis.objects.get( SiparisNo = SiparisNo )

	return HttpResponse( idsi.Durum.id )


def Yazdir( request, SiparisNo ):
	SiparisBilgileri = Siparis.objects.get( SiparisNo = SiparisNo )
	SepetUrunlerBilgileri = SepetUrunler.objects.filter( SepetID = SiparisBilgileri.SepetID )
	SiparisArsivBilgileri = SiparisArsiv.objects.filter( SiparisNo = SiparisNo ).order_by( '-IslemTarihi' )
	return render_to_response( 'yazdir.html', { 'SepetUrunlerBilgileri': SepetUrunlerBilgileri, 'SiparisBilgileri': SiparisBilgileri, 'SiparisArsivBilgileri': SiparisArsivBilgileri, }, context_instance = RequestContext( request ) )


def SiparisKontrol( request, SiparisNo ):
	# try:
	SiparisBilgileri = Siparis.objects.get( SiparisNo = SiparisNo )
	SepetUrunlerBilgileri = SepetUrunler.objects.filter( SepetID = SiparisBilgileri.SepetID )
	SiparisArsivBilgileri = SiparisArsiv.objects.filter( SiparisNo = SiparisNo ).order_by( '-IslemTarihi' )
	return render_to_response( 'sipariskontrol.html', { 'SepetUrunlerBilgileri': SepetUrunlerBilgileri, 'SiparisBilgileri': SiparisBilgileri, 'SiparisArsivBilgileri': SiparisArsivBilgileri, }, context_instance = RequestContext( request ) )


# except:
#     return redirect("/404/")


def SiparisKontrol2( request, SiparisNo ):
	# try:
	SiparisBilgileri = Siparis.objects.get( SiparisNo = SiparisNo )
	SepetUrunlerBilgileri = SepetUrunler.objects.filter( SepetID = SiparisBilgileri.SepetID )
	SiparisArsivBilgileri = SiparisArsiv.objects.filter( SiparisNo = SiparisNo ).order_by( '-IslemTarihi' )
	return render_to_response( 'sipariskontrol2.html', { 'SepetUrunlerBilgileri': SepetUrunlerBilgileri, 'SiparisBilgileri': SiparisBilgileri, 'SiparisArsivBilgileri': SiparisArsivBilgileri }, context_instance = RequestContext( request ) )


# except:
#     return redirect("/404/")


def SiparisKontrolSporLA( request, SiparisNo ):
	try:
		SiparisBilgileri = Siparis.objects.get( SiparisNo = SiparisNo )
		if not SiparisBilgileri.OzelNotMusteri:
			return HttpResponse( smart_unicode( SiparisBilgileri.Durum ) )
		else:
			return HttpResponse( smart_unicode( SiparisBilgileri.Durum ) + "<br />" + smart_unicode( SiparisBilgileri.OzelNotMusteri ) )
	except:
		return HttpResponse( "Sipariş no bulunamadı!" )


def DFOdemeYap( request ):
	x_forwarded_for = request.META.get( 'HTTP_X_FORWARDED_FOR' )
	if x_forwarded_for:
		ip = x_forwarded_for.split( ',' )[0]
	else:
		ip = request.META.get( 'REMOTE_ADDR' )

	rastgele = randint( 100000000, 9999999999 )

	okUrl = "http://spormarket.com.tr/dftamamlandi/"
	failUrl = "http://spormarket.com.tr/dftamamlanamadi/"

	clientId = "10021997"
	storekey = "73706F726D61726B6574656F726A676F6572677265726765"
	islemtipi = "sales"

	strTerminalID = "10021997"
	strTerminalID_ = "0" + strTerminalID

	FormatliGenelToplamm = str( DFOdeme.objects.last( ).Tutar )

	FormatliGenelToplam = str( FormatliGenelToplamm ).replace( '.', '' ).replace( ',', '' )

	SecurityData = hex_sha1.encrypt( "KUTu3535" + strTerminalID_ ).upper( )

	hashstr = strTerminalID + str( rastgele ) + str( FormatliGenelToplam ) + okUrl + failUrl + islemtipi + "0" + storekey + str( SecurityData )

	hashi = hex_sha1.encrypt( hashstr ).upper( )

	return render_to_response( 'dfodemeyap.html', { 'hashi': hashi, 'FormatliGenelToplamm': FormatliGenelToplamm, 'FormatliGenelToplam': FormatliGenelToplam, 'rastgele': rastgele, 'SiparisNosu': rastgele, 'okUrl': okUrl, 'failUrl': failUrl, 'ip': ip }, context_instance = RequestContext( request ) )


@csrf_exempt
def DFOdemeYapildi( request ):
	x_forwarded_for = request.META.get( 'HTTP_X_FORWARDED_FOR' )
	if x_forwarded_for:
		ip = x_forwarded_for.split( ',' )[0]
	else:
		ip = request.META.get( 'REMOTE_ADDR' )

	AdSoyad = request.POST.get( 'adsoyad', '' )
	SiparisNo = request.POST.get( 'siparisno', '' )
	FormatliGenelToplam = request.POST.get( 'txnamount', '' )

	DFOdemeArsiv( Odeme = True, IP = ip, Tutar = float( FormatliGenelToplam ) / 100, SiparisNo = SiparisNo, AdSoyad = AdSoyad ).save( )

	return render_to_response( 'dftamamlandi.html', { }, context_instance = RequestContext( request ) )


@csrf_exempt
def DFOdemeYapilamadi( request ):
	x_forwarded_for = request.META.get( 'HTTP_X_FORWARDED_FOR' )
	if x_forwarded_for:
		ip = x_forwarded_for.split( ',' )[0]
	else:
		ip = request.META.get( 'REMOTE_ADDR' )

	AdSoyad = request.POST.get( 'adsoyad', '' )
	SiparisNo = request.POST.get( 'siparisno', '' )
	FormatliGenelToplam = request.POST.get( 'txnamount', '' )

	Hata = request.POST.get( 'mdErrorMsg', "" )
	Hataa = request.POST.get( 'ErrMsg', "" )
	Hataaa = request.POST.get( 'errmsg', "" )

	DFOdemeArsiv( Odeme = False, IP = ip, Tutar = float( FormatliGenelToplam ) / 100, SiparisNo = SiparisNo, AdSoyad = AdSoyad, Durum = request ).save( )

	return render_to_response( 'dftamamlanamadi.html', { 'Hata': Hata + " " + Hataa + " " + Hataaa, }, context_instance = RequestContext( request ) )


def SSDegistir( request, gVaryantID, yAdet ):
	try:

		try:
			UyeID = Kullanicilar.objects.get( user = request.user ).uyeid
		except:
			UyeID = request.COOKIES.get( 'UyeID' )
			if not UyeID:
				UyeID = ''.join( [random.choice( string.digits ) for i in range( 0, 8 )] )

		ss = SepetUrunler.objects.get( VaryantID = gVaryantID, SepetID = Sepet.objects.get( UyeID = UyeID, Tamamlandi = False ) )
		ss.Adet = yAdet
		ss.save( )
		return HttpResponseRedirect( "/sepetim/" )
	except:
		return HttpResponseRedirect( "/sepetim/" )


@csrf_exempt
def SepeteUrunEkle( request ):
	IstenilenAdet = request.POST.get( 'VaryantAdeti', None )
	VaryantID = request.POST.get( 'VaryantID', None )

	varyant_detayi = Varyant.objects.get( id = VaryantID )

	if int( IstenilenAdet ) > int( varyant_detayi.StokSayisi ):
		IstenilenAdet = varyant_detayi.StokSayisi

	try:
		UyeID = Kullanicilar.objects.get( user = request.user ).uyeid
	except:
		UyeID = request.COOKIES.get( 'UyeID' )
		if not UyeID:
			UyeID = randint( 1000000, 9999999 )

	x_forwarded_for = request.META.get( 'HTTP_X_FORWARDED_FOR' )
	if x_forwarded_for:
		ip = x_forwarded_for.split( ',' )[0]
	else:
		ip = request.META.get( 'REMOTE_ADDR' )

	varolanSepet, yeniSepet = Sepet.objects.get_or_create( UyeID = UyeID, Tamamlandi = False, IP = ip )

	if yeniSepet:
		SepetinID = Sepet.objects.get( UyeID = varolanSepet.UyeID, Tamamlandi = False, IP = ip )

	else:
		SepetinID = Sepet.objects.filter( UyeID = UyeID, Tamamlandi = False, IP = ip ).order_by( '-id' ).last( )
	# SepetinID = Sepet.objects.get( UyeID = UyeID, Tamamlandi = False )

	try:

		AdetGuncelle = SepetUrunler.objects.get( SepetID = SepetinID, VaryantID = int( VaryantID ) )
		AdetGuncelle.Adet += int( IstenilenAdet )
		AdetGuncelle.save( )
		response = HttpResponse( "Adet güncellendi" )
		response.set_cookie( 'UyeID', UyeID )
		return response

	except:

		SepetUrunlerEkle = SepetUrunler( SepetID = SepetinID, VaryantID = int( VaryantID ), Adet = int( IstenilenAdet ) )
		SepetUrunlerEkle.save( )
		response = HttpResponse( "Eklendi" )
		response.set_cookie( 'UyeID', UyeID )
		return response


@csrf_exempt
def SepettenUrunSil( request, varID ):
	try:
		try:
			UyeID = Kullanicilar.objects.get( user = request.user ).uyeid
		except:
			UyeID = request.COOKIES.get( 'UyeID' )

		SepetUrunler.objects.get( VaryantID = varID, SepetID = Sepet.objects.get( UyeID = UyeID, Tamamlandi = False ).id ).delete( )
		return redirect( "/sepetim/" )
	except:
		return redirect( "/sepetim/" )


def KullaniciOlustur( request ):
	"kubra_mutlu.67@hotmail.com kubra67 Kübra   Mutlu   5353561092"

	Dosya = open( "/home/muslu/django/uyeaktarma/SMuye.txt", 'r' )
	UyeListem = [satir.split( ',' ) for satir in Dosya.readlines( )]

	f = open( '/home/muslu/django/uyeaktarma/eklenenuyeler.txt', 'a' )
	ff = open( '/home/muslu/django/uyeaktarma/eklenmeyenuyeler.txt', 'a' )
	fff = open( '/home/muslu/django/uyeaktarma/hatali.txt', 'a' )

	for i in UyeListem:
		email = i[0].strip( ).lower( )
		password = i[1].strip( ).lower( )
		first_name = i[2].strip( )
		last_name = i[3].strip( ).lower( )
		uyetelefonu = i[4].strip( ).lower( )

		try:
			if validate_email( email, verify = True ):
				userim = User.objects.create_user( username = email, email = email, password = password, first_name = first_name, last_name = last_name )
				kullanicim = Kullanicilar.objects.create( user = userim, uyeid = randint( 1000000, 9999999 ), uyeadi = first_name, uyesoyadi = last_name, uyemail = email, uyepassword = password, uyetelefon = uyetelefonu )
				# logging.info( kullanicim.uyemail )
				f.write( str( email ) + "\n" )
			else:
				# logging.info( "-----------------------------------------------------------------------> Geçersiz Mail: " + str( email ) )
				ff.write( str( email ) + "\n" )
		except:
			# logging.info("-------------------------------------> Hata: " + str(email) )
			fff.write( str( email ) + "\n" )

	f.close( )


def UyeKayitEkle( request ):
	logging.info( request.method )

	try:
		if request.method == 'POST':


			x_forwarded_for = request.META.get( 'HTTP_X_FORWARDED_FOR' )
			if x_forwarded_for:
				ip = x_forwarded_for.split( ',' )[0]
			else:
				ip = request.META.get( 'REMOTE_ADDR' )

			uyeadi = request.POST.get( 'kisim' )
			uyesoyadi = request.POST.get( 'ksoyisim' )
			uyemail = request.POST.get( 'kemail' )
			uyepassword = request.POST.get( 'kparola' )
			uyetelefon = request.POST.get( 'ktelefon' )
			uyeip = ip

			if validate_email( uyemail, verify = True ):
				try:
					user = User.objects.create_user( username = uyemail, email = uyemail, password = uyepassword, first_name = uyeadi, last_name = uyesoyadi )
					user.save( )

					kullanici = Kullanicilar( user = user, uyeadi = uyeadi, uyesoyadi = uyesoyadi, uyemail = uyemail, uyeid = randint( 1000000, 9999999 ), uyetelefon = uyetelefon, uyeip = uyeip, uyepassword = uyepassword )
					kullanici.save( )
					user = authenticate( email = uyemail, password = uyepassword )
					login( request, user )
					return HttpResponse( "OK" )
				except:
					return HttpResponse( "Kullanıcı zaten mevcut!" )

			else:
				return HttpResponse( "Geçerli bir mail adresi giriniz." )
	except:
		return HttpResponse( "Hata oluştu. Lütfen destek@spormarket.com.tr adresine bildiriniz." )


def UyeCikisYap( request ):
	logout( request )
	response = redirect( "/" )
	response.delete_cookie( 'VaryantID' )
	response.delete_cookie( 'VaryantAdeti' )
	response.delete_cookie( 'UyeID' )
	response.delete_cookie( 'StokKodu' )
	return response


def UyeGirisYap( request ):
	# try:

	uye_kadi = request.POST.get( 'email' )
	uye_sifre = request.POST.get( 'parola' )

	logging.info( uye_kadi + " " + uye_sifre )

	user = authenticate( email = uye_kadi, password = uye_sifre )

	if user is not None:
		if user.is_active:
			login( request, user )
			return HttpResponse( "OK" )
		else:
			return HttpResponse( "Üye Aktif Değil!" )
	else:
		return HttpResponse( "Üye Bulunamadı!" )

	# except:
	#     return HttpResponse("Hata")


@csrf_exempt
def UyeKayitliMi_Mail( request ):
	if request.method == 'POST':

		Sorgu = request.POST.get( 'Sorgu' )
		try:
			UyeAdiVarMi = User.objects.get( email = Sorgu )
			return HttpResponse( "1" )

		except:
			return HttpResponse( "0" )

	else:
		return HttpResponse( "WTF!" )

	return ""


