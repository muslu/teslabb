# -*- coding: utf-8 -*-

import random
import urllib
from datetime import datetime, timedelta

from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.conf import settings

from muslu import *
from smart_selects.db_fields import ChainedForeignKey
from kategoriler.models import Urun, Varyant




ODEME_SEKILLERI = (
('KN', 'Kapıda Nakit'), ('KKK', 'Kapıda Kredi Kartı'), ('HVL', 'Havale'), ('KK', 'Kredi Kartı'), ('TEK', 'Kredi Kartı TEK'),
)

KARGO_DURUMU = (
('OnB', 'Onay Bekliyor'), ('OdB', 'Ödeme Bekliyor'), ('H', 'Hazırlanıyor'), ('O', 'Onaylandı'), ('KV', 'Kargoya Verildi'), ('IpE', 'İptal Edildi'), ('IaE', 'İade Edildi'),
)


class VIPMusteri( models.Model ):
	Kullanici = models.ForeignKey( User )
	Oran = models.IntegerField( verbose_name = "İndirim Oranı", default = 20, help_text = "İndirimsiz ürünlerde uygulanacak indirim oranı" )
	IslemTarihi = models.DateTimeField( default = datetime.now, blank = True )



	def __unicode__( self ):
		return str( self.Oran )


	class Meta:
		verbose_name_plural = u"VIP Müşteri"
		verbose_name = u"Müşteri"


def FotoKontrol( dosyayolu ):
	import os




	return os.path.isfile( str( settings.__getattr__( "BASE_DIR" ) ) + "/media/" + str( dosyayolu ) )


class FacebookProfil( models.Model ):
	user = models.ForeignKey( User )
	facebook_id = models.BigIntegerField( )
	access_token = models.TextField( )



	def __unicode__( self ):
		return "{0}".format( self.user )


	class Meta:
		verbose_name_plural = u"Facebook Profilleri"
		verbose_name = u"Profil"


class Kullanicilar( models.Model ):
	user = models.ForeignKey( User )
	uyeid = models.CharField( u"Üye ID", max_length = 150, blank = False, null = False, unique = True )
	uyeadi = models.CharField( u"Üye Adı", max_length = 150, blank = False, null = False )
	# ~ uyeadi2             =       models.CharField(u"Üye Adı2", max_length=150, blank=True, null=True)
	uyesoyadi = models.CharField( u"Üye Soyadı", max_length = 150, blank = True, null = False )
	uyemail = models.EmailField( u"Üye Mail", max_length = 150, blank = False, null = False, unique = True )
	uyepassword = models.CharField( u"Üye Parola", max_length = 150, blank = True, null = False )
	uyetelefon = models.CharField( u"Üye Telefon", max_length = 150, blank = False, null = False )
	uyetc = models.CharField( u"Üye Vergi No", max_length = 25, blank = True, null = True )
	uyeip = models.CharField( u"Üye IP", max_length = 25, blank = True, null = True )
	IslemTarihi = models.DateTimeField( default = datetime.now, blank = True )



	def __unicode__( self ):
		return "{0}".format( self.user )


	class Meta:
		app_label = app_name_degistir( "uyeler", u"Üyelerimiz" )
		verbose_name_plural = u"Kullanıcılar"
		verbose_name = u"Kullanıcı"


	def GezintiGecmisi( self ):
		return u'<a href="https://www.sporthink.com.tr/admin/siteayarlari/yonlendirmeler/?q=%s" target="_blank">Göster</a>' % (self.uyeip)



	GezintiGecmisi.allow_tags = True
	GezintiGecmisi.short_description = u'Gezinti'


class Sepet( models.Model ):
	UyeID = models.CharField( u'Uye ID', max_length = 100, blank = False, null = False )
	OzelNot = models.CharField( u'Özel Not', max_length = 200, blank = True, null = True )
	Tamamlandi = models.BooleanField( u'Tamamlandı?', default = False )
	IslemTarihi = models.DateTimeField( default = datetime.now, blank = True )
	IP = models.CharField( u'IP', max_length = 20, blank = False, null = False )



	def __unicode__( self ):
		return u"%s" % (self.UyeID)



	def SepettekiUrunlerinToplamAdeti( self ):
		toplam_adet = SepetUrunler.objects.filter( SepetID__id = self.id ).aggregate( Sum( 'Adet' ) )
		return '%s' % (toplam_adet['Adet__sum'])



	SepettekiUrunlerinToplamAdeti.short_description = 'Toplam Adet'


	class Meta:
		verbose_name_plural = u"Sepet"
		verbose_name = u"Sepet"


	def GezintiGecmisi( self ):
		uyeadine = Kullanicilar.objects.get( uyeid = self.UyeID )
		return u'<a href="https://www.sporthink.com.tr/admin/siteayarlari/yonlendirmeler/?q=&UyeID=%s" target="_blank">Göster</a>' % (uyeadine.uyemail)



	GezintiGecmisi.allow_tags = True
	GezintiGecmisi.short_description = u'Gezinti'



	def GezintiGecmisiIP( self ):
		if self.IP:
			return u'<a href="https://www.sporthink.com.tr/admin/siteayarlari/yonlendirmeler/?q=%s" target="_blank">Göster</a>' % (self.IP)



	GezintiGecmisiIP.allow_tags = True
	GezintiGecmisiIP.short_description = u'IP Gezinti'


class SepetUrunler( models.Model ):
	SepetID = models.ForeignKey( Sepet )
	VaryantID = models.CharField( u'Varyant ID', max_length = 100, blank = False, null = False )
	Adet = models.IntegerField( u'Adet', blank = True, null = False )



	def __unicode__( self ):
		return u"%s %s %s" % (self.SepetID, self.VaryantID, self.Adet)


	class Meta:
		verbose_name_plural = u"Sepetteki Ürünler"
		verbose_name = u"Ürün"


	def VaryantBarkodGoster( self ):
		return Varyant.objects.get( id = self.VaryantID ).Barkod



	VaryantBarkodGoster.allow_tags = True
	VaryantBarkodGoster.short_description = 'Barkod'



	def VaryantResimGoster( self ):
		Resim = Varyant.objects.get( id = self.VaryantID )
		if Resim.Logo1 and FotoKontrol( str( Resim.Logo1 ) ):
			return u'<a target="_blank" href="/vd/' + self.VaryantID + '/"><img src="/media/%s" width="50px" /></a>' % (Resim.Logo1)
		else:
			Resim = Urun.objects.get( varyant = self.VaryantID )
			if Resim.Logo and FotoKontrol( str( Resim.Logo ) ):
				return u'<a target="_blank" href="/vd/' + self.VaryantID + '/"><img src="/media/%s" width="50px" />' % (Resim.Logo)
			else:
				return u'<a target="_blank" href="/vd/' + self.VaryantID + '/"><img src="/media/%s" width="50px" />' % ("ResimYok.jpg")



	VaryantResimGoster.allow_tags = True
	VaryantResimGoster.short_description = 'Fotoğraf'



	def VaryantOlanSubeleriGoster( self ):

		from django.db import connections




		cursor = connections["V3"].cursor( )

		VaryantBilgisi = Varyant.objects.get( id = self.VaryantID )

		strr = """

            SELECT
                V3_DOGUKAN.dbo.MSEnvanterDepo.M01 AS 'Buca',
                V3_DOGUKAN.dbo.MSEnvanterDepo.S01 AS 'Sirinyer',
                V3_DOGUKAN.dbo.MSEnvanterDepo.OPT AS 'Optimum',
                V3_DOGUKAN.dbo.MSEnvanterDepo.ANADEPO AS 'AnaDepo',
                V3_DOGUKAN.dbo.MSEnvanterDepo.INT AS 'Internet',
                V3_DOGUKAN.dbo.MSEnvanterDepo.TOPL AS 'Toplam'


                FROM V3_DOGUKAN.dbo.MSEnvanterDepo


                WHERE (MSEnvanterDepo.ItemCode='""" + VaryantBilgisi.Urunu.StokKodu + """' and
                 MSEnvanterDepo.ColorCode='""" + VaryantBilgisi.RenkKodu + """' and
                 MSEnvanterDepo.ItemDim1Code='""" + VaryantBilgisi.Beden + """' and
                 MSEnvanterDepo.ItemDim2Code='""" + VaryantBilgisi.Kavala + """')  """

		cursor.execute( strr )

		Buca = ""
		Sirinyer = ""
		Optimum = ""
		AnaDepo = ""
		Internet = ""

		Donus = ""
		for row in cursor.fetchall( ):

			Buca = "Buca:" + str( int( row[0] ) )
			Sirinyer = "<br/>Sirinyer:" + str( int( row[1] ) )
			Optimum = "<br/>Optimum:" + str( int( row[2] ) )
			AnaDepo = "<br/>AnaDepo:" + str( int( row[3] ) )
			Internet = "<br/>Internet:" + str( int( row[4] ) )

			Donus = Buca, Sirinyer, Optimum, AnaDepo, Internet

		return str( Donus ).replace( '(', '' ).replace( ')', '' ).replace( "'", "" ).replace( ',', '' )



	VaryantOlanSubeleriGoster.allow_tags = True
	VaryantOlanSubeleriGoster.short_description = 'Şubeler'


class SiparisDurumKategorileri( models.Model ):
	Adi = models.CharField( u'Kategori Adı', max_length = 100, blank = False, null = False )



	def __unicode__( self ):
		return self.Adi


	class Meta:
		verbose_name_plural = u"Sipariş Durum Kategorileri"


class SiparisDurumlari( models.Model ):
	Kategori = models.ForeignKey( SiparisDurumKategorileri )
	Durum = models.CharField( u'Durum', max_length = 100, blank = False, null = False )



	def __unicode__( self ):
		return self.Durum


	class Meta:
		verbose_name_plural = u"Sipariş Durumu"


class Siparis( models.Model ):
	OzelNot = models.CharField( u'Özel Not', max_length = 200, blank = True, null = True )
	OzelNotMusteri = models.CharField( u'Özel Not - Müşteri', max_length = 255, blank = True, null = True )
	SiparisNo = models.CharField( u'Sipariş No', max_length = 100, blank = False, null = False )
	OdemeYapildi = models.BooleanField( u"Ödeme", default = False )
	# OdemeSekli          =      models.CharField(u'Ödeme Şekli', max_length=20, choices=ODEME_SEKILLERI, default='KN')

	Kategori = models.ForeignKey( SiparisDurumKategorileri )
	Durum = ChainedForeignKey( SiparisDurumlari, chained_field = "Kategori", chained_model_field = "Kategori", show_all = False, auto_choose = True )

	TakipNo = models.CharField( u'Takip No', max_length = 20, blank = True, null = True )

	UyeID = models.CharField( u'Üye ID', max_length = 20, blank = False, null = False )
	OdemeTuru = models.CharField( u'Odeme Türü', max_length = 20, blank = False, null = False )
	Banka = models.CharField( u'Banka', max_length = 20, blank = True, null = True )

	Telefon = models.CharField( u'Telefon', max_length = 100, blank = False, null = False )
	Mail = models.CharField( u'Mail', max_length = 100, blank = True, null = True )

	Paket = models.BooleanField( u'Hediye Paketi', default = False )
	Not = models.CharField( u'Not', max_length = 200, blank = True, null = True )

	IslemTarihi = models.DateTimeField( default = datetime.now, blank = False )

	UrunlerToplamTutar = models.FloatField( u'Ürünler', blank = False, null = False )
	IndToplamTutar = models.FloatField( u'İndirim', blank = True, null = True )

	KargoBedeli = models.FloatField( u'Kargo Bedeli', blank = True, null = True )
	HizmetBedeli = models.FloatField( u'Hizmet Bedeli', blank = True, null = True )
	VadeFarki = models.FloatField( u'Vade Farkı', blank = True, null = True )
	SMSBedeli = models.FloatField( u'SMS Bedeli', blank = True, null = True )

	GenelToplam = models.FloatField( u'Genel Toplam', blank = False, null = False )
	BankaGenelToplam = models.CharField( u'Bankadan Dönen Genel Toplam', max_length = 200, blank = True, null = True )

	# YeniUyeKampanyaYararlandiMi     =       models.BooleanField(u"Yeni Üye Kampanyası" ,default=False)



	TAdSoyad = models.CharField( u'Teslimat Ad Soyad', max_length = 100, blank = False, null = False )
	TIl = models.CharField( u'Teslimat İl', max_length = 100, blank = False, null = False )
	# TIlce               =       models.CharField(u'Teslimat İlçe', max_length=100, blank=False, null=False)
	TAdres = models.CharField( u'Teslimat Adres', max_length = 200, blank = False, null = False )


	# ~ FSirketAdi          =       models.CharField(u'Şirket', max_length=100, blank=True, null=True)
	# ~ FAdSoyad            =       models.CharField(u'Fatura Ad Soyad', max_length=100, blank=False, null=False)
	#~ FIl                 =       models.CharField(u'Fatura Il', max_length=100, blank=False, null=False)
	#~ FIlce               =       models.CharField(u'Fatura İlçe', max_length=100, blank=False, null=False)
	#~ FAdres              =       models.CharField(u'Fatura Adres', max_length=200, blank=False, null=False)

	FVergiDairesi = models.CharField( u'Vergi Dairesi', max_length = 100, blank = True, null = True )
	FTC_VergiNo = models.CharField( u'Vergi/TC No', max_length = 100, blank = True, null = True )

	SMS_Ulasilamadi = models.BooleanField( u"SMS_Ulasilamadi", default = False )
	SMS_Hazirlaniyor = models.BooleanField( u"SMS_Hazirlaniyor", default = False )
	SMS_Paketlendi = models.BooleanField( u"SMS_Paketlendi", default = False )
	SMS_KargoyaVerildi = models.BooleanField( u"SMS_KargoyaVerildi", default = False )
	SMS_KaampanyaBilgileri = models.BooleanField( u"SMS_KaampanyaBilgileri", default = False )

	ToplamTaksit = models.CharField( u'Toplam Taksit', max_length = 3, blank = True, null = True )
	EkTaksit = models.CharField( u'Ek Taksit', max_length = 3, blank = True, null = True )
	SirketTaksit = models.CharField( u'Taksit', max_length = 3, blank = True, null = True )
	IP = models.CharField( u'IP', max_length = 20, blank = False, null = False )
	SepetID = models.CharField( u'Sepet ID', max_length = 20, blank = False, null = False )



	def __unicode__( self ):
		return u"%s" % (self.SiparisNo)


	class Meta:
		verbose_name_plural = u"Siparişler"
		verbose_name = u"Sipariş"


	# 10.07.2014 10:53:26#      -  Muslu YÜKSEKTEPE


	def clean( self ):

		super( Siparis, self ).save( )

		SiparisArsiv( SiparisNo = self.SiparisNo, OzelNot = self.OzelNot, Durum = self.Durum.Durum, TAdSoyad = self.TAdSoyad, Telefon = self.Telefon, Mail = self.Mail, SiparisTarihi = self.IslemTarihi, Not = self.OdemeTuru ).save( )

		from django.utils.encoding import smart_str




		if self.SMS_Ulasilamadi and self.Durum.id == 28:
			Mesaj = "Merhaba " + (self.TAdSoyad).title( ) + "; " + self.SiparisNo + " no ve " + str( self.IslemTarihi.strftime( '%d.%m.%Y %H:%M' ) ) + " tarihli siparisinizin durumu: Ulasilamadi. 0232 320 0 333 numarali telefonu arayabilirsiniz.."

		if self.SMS_Hazirlaniyor and self.Durum.id == 2:
			Mesaj = "Merhaba " + (self.TAdSoyad).title( ) + "; " + self.SiparisNo + " no ve " + str( self.IslemTarihi.strftime( '%d.%m.%Y %H:%M' ) ) + " tarihli siparisinizin durumu: Urunler hazirlaniyor. http://spor.la/" + str( self.SiparisNo )

		if self.SMS_Paketlendi and self.Durum.id == 8:
			Mesaj = "Merhaba " + (self.TAdSoyad).title( ) + "; " + self.SiparisNo + " no ve " + str( self.IslemTarihi.strftime( '%d.%m.%Y %H:%M' ) ) + " tarihli siparisiniz paketlendi. Siparisiniz mesai saatleri icerisinde kargo firmasina teslim edilecek. http://spor.la/" + str( self.SiparisNo )

		if self.SMS_KargoyaVerildi and self.Durum.id == 9:
			Mesaj = "Merhaba " + (self.TAdSoyad).title( ) + "; " + self.SiparisNo + " no ve " + str( self.IslemTarihi.strftime( '%d.%m.%Y %H:%M' ) ) + " tarihli siparisiniz kargoya verildi. http://spor.la/" + str( self.TakipNo )

		if (self.SMS_Ulasilamadi and self.Durum.id == 28) or (self.SMS_Hazirlaniyor and self.Durum.id == 2) or (self.SMS_Paketlendi and self.Durum.id == 8) or (self.SMS_KargoyaVerildi and self.Durum.id == 9):

			Apimiz = "http://www.pratikbilisim.net/panel/smsgonder.php?kno=12234&kul_ad=905325614848&sifre=539425&gonderen=SPORMARKET&mesaj='" + smart_str( Mesaj ) + "'&cepteller=" + str( self.Telefon ).replace( ' ', '' )
			uo = urllib.urlopen( Apimiz )
			SMSGittiMi = uo.read( )

			if "Gonderildi" in SMSGittiMi:
				smsekle = SMSArsiv( UyeID = str( self.UyeID ), Mesaj = Mesaj, Durum = True )
				smsekle.save( )
				raise forms.ValidationError( "SMS Gönderildi" )
			else:
				smsekle = SMSArsiv( UyeID = str( self.UyeID ), Mesaj = Mesaj, Durum = False )
				smsekle.save( )
				raise forms.ValidationError( "SMS Gönderilemedi!" )

			super( Siparis, self ).save( )

		if str( self.Durum ) == "Ücret İadesi Yapıldı":

			Mesaj = "Merhaba " + (self.TAdSoyad).title( ) + "; " + self.SiparisNo + " no ve " + str( self.IslemTarihi.strftime( '%d.%m.%Y %H:%M' ) ) + " tarihli siparisinizin ucret iadesi gerceklestirilmistir."
			Apimiz = "http://www.pratikbilisim.net/panel/smsgonder.php?kno=12234&kul_ad=905325614848&sifre=539425&gonderen=SPORMARKET&mesaj='" + smart_str( Mesaj ) + "'&cepteller=" + str( self.Telefon ).replace( ' ', '' )
			uo = urllib.urlopen( Apimiz )
			SMSGittiMi = uo.read( )

			if "Gonderildi" in SMSGittiMi:
				smsekle = SMSArsiv( UyeID = str( self.UyeID ), Mesaj = Mesaj, Durum = True )
				smsekle.save( )
				raise forms.ValidationError( "SMS Gönderildi" )
			else:
				smsekle = SMSArsiv( UyeID = str( self.UyeID ), Mesaj = Mesaj, Durum = False )
				smsekle.save( )
				raise forms.ValidationError( "SMS Gönderilemedi!" )

			super( Siparis, self ).save( )



	def SepetiGoster( self ):
		return u'<a href="/admin/uyeler/sepet/%s/">Göster</a>' % (self.SepetID)



	SepetiGoster.allow_tags = True
	SepetiGoster.short_description = 'Sepeti Göster'



	def Yazdir( self ):
		return u'<a href="/yazdir/%s/" target="_blank">Yazdır</a>' % (self.SiparisNo)



	Yazdir.allow_tags = True
	Yazdir.short_description = 'Yazdır'



	def GezintiGecmisi( self ):
		return u'<a href="http://www.spormarket.com.tr/admin/siteayarlari/yonlendirmeler/?q=%s" target="_blank">Göster</a>' % (self.IP)



	GezintiGecmisi.allow_tags = True
	GezintiGecmisi.short_description = u'Gezinti'


class SiparisArsiv( models.Model ):
	SiparisNo = models.CharField( u'Sipariş No', max_length = 100, blank = False, null = False )
	TAdSoyad = models.CharField( u'Teslimat Ad Soyad', max_length = 100, blank = False, null = False )
	OzelNot = models.CharField( u'Özel Not', max_length = 200, blank = True, null = True )
	Durum = models.CharField( u'Sipariş Durum', max_length = 100, blank = False, null = False )
	Not = models.CharField( u'Not', max_length = 200, blank = True, null = True )

	Telefon = models.CharField( u'Telefon', max_length = 100, blank = False, null = False )
	Mail = models.CharField( u'Mail', max_length = 100, blank = False, null = False )
	SiparisTarihi = models.DateTimeField( default = datetime.now, blank = False )

	IslemYapan = models.CharField( u'Islem Yapan', max_length = 100, blank = True, null = True )
	IslemTarihi = models.DateTimeField( default = datetime.now, blank = False )



	def __unicode__( self ):
		return u"%s" % (self.SiparisNo)


	class Meta:
		verbose_name_plural = u"Sipariş Arşivi"


class KKOdemeArsiv( models.Model ):
	SiparisNo = models.CharField( u'Sipariş No', max_length = 100, blank = False, null = False )
	UyeID = models.CharField( u'UyeID', max_length = 100, blank = True, null = True )
	Hata = models.TextField( u'Hata', blank = True, null = True )
	EXTRAHOSTMSG = models.CharField( u'EXTRAHOSTMSG', max_length = 100, blank = True, null = True )
	ip = models.CharField( u'ip', max_length = 100, blank = True, null = True )
	FormatliGenelToplam = models.CharField( u'FormatliGenelToplam', max_length = 100 )
	Taksit = models.CharField( u'Taksit', max_length = 100, blank = True, null = True )
	BankaAdi = models.CharField( u'BankaAdi', max_length = 100, blank = True, null = True )
	IslemTarihi = models.DateTimeField( default = datetime.now, blank = False )



	def __unicode__( self ):
		return u"%s" % (self.SiparisNo)


	class Meta:
		verbose_name_plural = u"Kredi Kartı Hataları"


def RastgeleKupon( ):
	YeniKod = str( random.randint( 10000, 99999 ) )

	try:
		HediyeKuponu.objects.get( Kod = YeniKod )
		return RastgeleKupon( )
	except HediyeKuponu.DoesNotExist:
		return "ST" + YeniKod


IndirimTurleri = (('TL', 'TL'), ('YUZDE', 'Yüzde'))
UyelikZorunluMu = (('E', 'Evet'), ('H', 'Hayır'))
# IndirimZamani           = (('Aninda', 'Anında'), ('Puan', 'Puan'))
FiyatTuru = (('IndirimliFiyati', 'İndirimli Fiyat'), ('IndirimsizFiyati', 'İndirimsiz Fiyati'), ('TumFiyatlar', 'Tüm Fiyatlar'))


class HediyeKuponu( models.Model ):
	Kod = models.CharField( u'Kod', max_length = 100, blank = False, null = False, unique = True, default = RastgeleKupon )
	UyelikZorunlu = models.CharField( u'Üyelik Zorunlu', max_length = 5, choices = UyelikZorunluMu, default = 'H' )

	Urun = models.ManyToManyField( Urun, blank = True, null = True )

	IndirimTuru = models.CharField( u'İndirim Türü', max_length = 5, choices = IndirimTurleri, default = 'YUZDE' )
	TutarOran = models.CharField( u'Tutar/Oran', max_length = 3, default = "5" )

	Kullanildi = models.BooleanField( u"Kullanıldı", default = False )
	Kullanan = models.CharField( u'Kullanan', max_length = 100, blank = True, null = True )

	IslemTarihi = models.DateTimeField( default = datetime.now, blank = False )
	BaslamaZamani = models.DateTimeField( default = datetime.now( ) )
	BitirmeZamani = models.DateTimeField( default = datetime.now( ) + timedelta( days = 7 ) )



	def __unicode__( self ):
		return u"%s" % (self.Kod)


	class Meta:
		verbose_name_plural = u"Hediye Kuponu"


class DFOdeme( models.Model ):
	Tutar = models.DecimalField( u'Çekilecek Tutar', max_digits = 8, decimal_places = 2, default = 0, blank = False, null = False )
	IslemTarihi = models.DateTimeField( default = datetime.now, blank = True )



	def __unicode__( self ):
		return str( self.Tutar )


	class Meta:
		verbose_name_plural = u"Değişim Farkı"
		verbose_name = u"Fark"


class DFOdemeArsiv( models.Model ):
	AdSoyad = models.CharField( u'Ad Soyad', max_length = 100 )
	SiparisNo = models.CharField( u'Sipariş No', max_length = 100 )
	Durum = models.TextField( u'Durum', max_length = 255 )
	IP = models.CharField( u'IP', max_length = 20 )
	UyeID = models.CharField( u'Uye ID', max_length = 20 )
	Tutar = models.DecimalField( u'Tutar', max_digits = 8, decimal_places = 2, default = 0, blank = False, null = False )
	IslemTarihi = models.DateTimeField( default = datetime.now, blank = True )
	Odeme = models.BooleanField( u'Tamamlandı?', default = False )



	def __unicode__( self ):
		return str( self.Tutar )


	class Meta:
		verbose_name_plural = u"Değişim Farkı Arşiv"
		verbose_name = u"Arşiv"


class GunlukSiparisArsivi( models.Model ):
	geneltutar_toplami = models.DecimalField( u'Genel Toplam', max_digits = 8, decimal_places = 2, default = 0 )
	geneltutar_ortalamasi = models.DecimalField( u'Sipariş Ortalaması', max_digits = 8, decimal_places = 2, default = 0 )
	teslimedilen_toplami = models.DecimalField( u'Teslim Edilen Ürün', max_digits = 8, decimal_places = 2, default = 0 )
	teslimedilmeyen_toplami = models.DecimalField( u'Teslim Edilmeyen Ürün', max_digits = 8, decimal_places = 2, default = 0 )
	teslimedilenindirim_toplami = models.DecimalField( u'Teslim Edilen İndirim', max_digits = 8, decimal_places = 2, default = 0 )
	teslimedilmeyenindirim_toplami = models.DecimalField( u'Teslim Edilmeyen İndirim', max_digits = 8, decimal_places = 2, default = 0 )
	yenisiparis_toplami = models.DecimalField( u'Yeni Sipariş', max_digits = 8, decimal_places = 2, default = 0 )
	ucretiadesiistendi_toplami = models.DecimalField( u'Ücret İadesi İstendi', max_digits = 8, decimal_places = 2, default = 0 )
	ucretiadesiyapildi_toplami = models.DecimalField( u'Ücret İadesi Yapıldı', max_digits = 8, decimal_places = 2, default = 0 )
	iptalodemeyapilmadi_toplami = models.DecimalField( u'Ödeme Yapılmayan', max_digits = 8, decimal_places = 2, default = 0 )
	smsucreti_toplami = models.DecimalField( u'SMS Ücreti', max_digits = 8, decimal_places = 2, default = 0 )
	hizmetbedeli_toplami = models.DecimalField( u'Hizmet Bedeli', max_digits = 8, decimal_places = 2, default = 0 )
	kargoucreti_toplami = models.DecimalField( u'Kargo Ücreti', max_digits = 8, decimal_places = 2, default = 0 )
	urun_ortalama_tutar = models.DecimalField( u'Ortalama Ürün Tutarı', max_digits = 8, decimal_places = 2, default = 0 )
	urun_adeti = models.IntegerField( u'Ürün Adeti', default = 0 )

	IslemTarihi = models.DateField( auto_now = True, auto_now_add = True, null = False )



	def __unicode__( self ):
		return str( self.geneltutar_toplami )


	class Meta:
		verbose_name_plural = u"Günlük Sipariş Arşivi"
		verbose_name = u"Arşiv"


class SMSArsiv( models.Model ):
	UyeID = models.CharField( u'UyeID', max_length = 100, blank = True, null = True )
	Telefon = models.CharField( u'Telefon', max_length = 25, blank = True, null = True )
	GonderenTelefon = models.CharField( u'Gönderen Telefon', max_length = 25, blank = True, null = True )
	Durum = models.BooleanField( u"Durum", default = False )
	Mesaj = models.TextField( u'Mesaj', blank = True, null = True )
	IslemTarihi = models.DateTimeField( default = datetime.now, blank = False )



	def __unicode__( self ):
		return u"%s" % (self.UyeID)


	class Meta:
		verbose_name_plural = u"SMS Arşivi"





