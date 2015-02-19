# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.db import models

from uyeler.models import Kullanicilar
from kategoriler.models import Marka, Kategori




UruneToplama = (('Urun', 'Ürün Fiyatına'), ('Toplam', 'Toplam Tutara'))
IndirimTurleri = (('TL', 'TL'), ('YUZDE', 'Yüzde'))
IndirimZamani = (('Aninda', 'Anında'), ('Puan', 'Puan'))
FiyatTuru = (('IndirimliFiyati', 'İndirimli Fiyat'), ('IndirimsizFiyati', 'İndirimsiz Fiyati'), ('TumFiyatlar', 'Tüm Fiyatlar'))


class PuanKampanya( models.Model ):
	Aktif = models.BooleanField( u"Aktif", default = True )
	IndirimTuru = models.CharField( u'İndirim Türü', max_length = 5, choices = IndirimTurleri, default = 'YUZDE' )
	TutarOran = models.CharField( u'Tutar/Oran', max_length = 3, default = "10" )
	IndirimFiyatTuru = models.CharField( u'İndirim Fiyat Türü', max_length = 20, choices = FiyatTuru, default = 'IndirimsizFiyati', blank = False, null = False )
	BaslamaZamani = models.DateTimeField( default = datetime.now( ) )
	BitirmeZamani = models.DateTimeField( default = datetime.now( ) + timedelta( days = 360 ) )
	Mesaj = models.TextField( u'Bilgi Mesajı', help_text = "HTML Kod kabul edilmektedir.", blank = True )


	class Meta:
		verbose_name_plural = u"Puan Kampanyası"
		verbose_name = u"Puan Kampanya"


class PuanKampanyaHakEdenler( models.Model ):
	Aktif = models.BooleanField( u"Aktif", default = True )
	UyeID = models.ForeignKey( Kullanicilar, null = False )
	KazanilanPuan = models.FloatField( u'Kazanılan Puan', max_length = 3, default = "0" )
	IslemTarihi = models.DateTimeField( default = datetime.now( ) )



	def __unicode__( self ):
		return "{0}".format( self.UyeID )


	class Meta:
		verbose_name_plural = u"Puan Kampanyası Hak Edenler"


class FaydanilanKampanyalar( models.Model ):
	UyeID = models.ForeignKey( Kullanicilar, null = False )

	SiparisID = models.CharField( u'Sipariş ID', max_length = 250 )
	KampanyaAdi = models.CharField( u'Kampanya', max_length = 250 )

	IndirimTuru = models.CharField( u'İndirim Türü', max_length = 50, )
	TutarOran = models.CharField( u'Tutar/Oran', max_length = 3 )
	IndirimFiyatTuru = models.CharField( u'İndirim Fiyat Türü', max_length = 50 )

	UrunToplamTutar = models.FloatField( u'Ürün Toplamı', max_length = 3, default = "0" )
	IndirimliFiyat = models.FloatField( u'Indirimli Fiyat', max_length = 3, default = "0" )

	Kargo = models.FloatField( u'Kargo', max_length = 3, default = "0" )
	HizmetBedeli = models.FloatField( u'Hizmet Bedeli', max_length = 3, default = "0" )
	KazanilanPuan = models.FloatField( u'Kazanılan Puan', max_length = 3, default = "0" )

	GenelToplam = models.FloatField( u'Genel Toplam', max_length = 3, default = "0" )
	IslemTarihi = models.DateTimeField( default = datetime.now( ) )



	def __unicode__( self ):
		return "{0}".format( self.UyeID )


	class Meta:
		verbose_name_plural = u"Faydanılan Kampanyalar"


class YeniUyeKampanya( models.Model ):
	Aktif = models.BooleanField( u"Aktif", default = True )

	Adi = models.CharField( u'Kampanya Adı', max_length = 200, default = "Yeni üyelerimize özel indirim" )
	# ~ AltKat                      =       models.ManyToManyField(AltKategori, null=True, blank=True)
	# ~ Marka                       =       models.ForeignKey(Marka, null=True, blank=True)

	# ~ IndirimZamani               =       models.CharField(u'İndirim Zamanı', max_length=7, choices=IndirimZamani, default='Sonraki')
	#~ IndirimFiyatTuru            =       models.CharField(u'İndirim Fiyat Türü', max_length=50, choices=FiyatTuru, default='IndirimsizFiyati')

	IndirimTuru = models.CharField( u'İndirim Türü', max_length = 5, choices = IndirimTurleri, default = 'YUZDE' )

	TutarOran = models.CharField( u'Tutar/Oran', max_length = 3, default = "10" )

	BaslamaZamani = models.DateTimeField( default = datetime.now( ) )
	BitirmeZamani = models.DateTimeField( default = datetime.now( ) + timedelta( days = 360 ) )
	Mesaj = models.TextField( u'Bilgi Mesajı', help_text = "HTML Kod kabul edilmektedir.", blank = True )



	def __unicode__( self ):
		return self.Adi


	class Meta:
		verbose_name_plural = u"Yeni Üye Kampanyası"
		verbose_name = u"Kampanya"


class YeniUyeKampanyaHakEdenler( models.Model ):
	Aktif = models.BooleanField( u"Aktif", default = True )
	UyeID = models.ForeignKey( Kullanicilar, null = False )
	IslemTarihi = models.DateTimeField( default = datetime.now( ) )



	def __unicode__( self ):
		return "{0}".format( self.UyeID )


	class Meta:
		verbose_name_plural = u"Yeni Üye Kampanyası Hak Edenler"


class Kampanya( models.Model ):
	Aktif = models.BooleanField( u"Aktif", default = True )
	Adi = models.CharField( u'Kampanya Adı', max_length = 200 )
	# ~ AltKat                      =       models.ManyToManyField(AltKategori, blank=True, null=True)
	Marka = models.ForeignKey( Marka, blank = True, null = True )
	Uyelik = models.BooleanField( u"Üyelik", default = True, help_text = "Üye girişi zorunlu ise seçiniz." )
	TumAlisverisler = models.BooleanField( u"Tüm alışverişlerde geçerli", default = True, help_text = "Marka ve Kategori kısıtlaması yapmadan tüm alışverişlerde geçerli" )
	Ayni2nciUrun = models.BooleanField( u"2.nci Ürüne İndirim", default = False, help_text = "Aynı ürününün 2.ncisine yapılacak indirim" )

	KampanyaKullanimSiniri = models.IntegerField( u'Kampanya Sınırı', max_length = 3, default = "500", help_text = "Kampanyanın sonra ereceği sipariş sayısı" )
	KalanKullanimSiniri = models.IntegerField( u'Kalan Kullanım Hakkı', max_length = 3, default = "500", help_text = "Kampanyanın kalan kullanım sınırı" )
	SiparisSiniri = models.IntegerField( u'Sipariş Sınırı', max_length = 3, default = "10", help_text = "Bir üyeninin yararlanabileceği en fazla sipariş sayısı" )

	UrunToplam = models.CharField( u'Ürün Fiyatı / Toplam Tutar', max_length = 20, choices = UruneToplama, default = 'Toplam', blank = False, null = False, help_text = "Alışveriş en az tutarı ürün bazlı yada ürünlerin toplam tutarı üzerinden mi hesaplanacak? Örn. Toplam 150 TLlik alışveriş yapanlara ise Toplam Tutar seçilmeli." )
	EnAzTutar = models.FloatField( u'En Az Ürün Tutarı', max_length = 3, default = "20", help_text = "Ürün tutarına göre kampanya yapılırsa ürün fiyatı, Toplam ürün tutarlarına ypaılırsa toplam tutar geçerlidir." )
	EnAzAdet = models.IntegerField( u'En Az Ürün Adeti', max_length = 3, default = "1", blank = False, null = False, help_text = "Sepetteki ürünlerin toplam adeti" )

	IndirimFiyatTuru = models.CharField( u'İndirim Fiyat Türü', max_length = 20, choices = FiyatTuru, default = 'IndirimsizFiyati', blank = False, null = False, help_text = "Sadece ürün fiyatına özel kampanya yapıldığında geçerlidir." )
	IndirimZamani = models.CharField( u'İndirim Zamanı', max_length = 7, choices = IndirimZamani, default = 'Aninda', blank = False, null = False )
	IndirimTuru = models.CharField( u'İndirim Türü', max_length = 5, choices = IndirimTurleri, default = 'YUZDE', blank = False, null = False )
	IndirimOrani = models.IntegerField( u'İndirim Oranı', max_length = 3, default = "10" )

	BaslamaZamani = models.DateTimeField( default = datetime.now( ) )
	BitirmeZamani = models.DateTimeField( default = datetime.now( ) + timedelta( days = 365 ) )



	def __unicode__( self ):
		return u"%s" % (self.Adi)


	class Meta:
		verbose_name_plural = u"Genel Kampanyalar"
		verbose_name = u"Kampanya"


class BirAlanaBirBedavaKampanya( models.Model ):
	Aktif = models.BooleanField( u"Aktif", default = True, help_text = "Yalnızca bir kampanya aktif edilmeli." )
	Adi = models.CharField( u'Kampanya Adı', max_length = 200 )
	UstKat = models.ManyToManyField( Kategori )
	Marka = models.ManyToManyField( Marka )
	Uyelik = models.BooleanField( u"Üyelik", default = True, help_text = "Üye girişi zorunlu ise seçiniz." )

	BaslamaZamani = models.DateTimeField( default = datetime.now( ) )
	BitirmeZamani = models.DateTimeField( default = datetime.now( ) + timedelta( days = 365 ) )



	def __unicode__( self ):
		return u"%s" % (self.Adi)


	class Meta:
		verbose_name_plural = u"Bir Alana Bir Bedava Kampanyası"
		verbose_name = u"Kampanya"


class IkinciyeKampanya( models.Model ):
	Aktif = models.BooleanField( u"Aktif", default = True, help_text = "Yalnızca bir kampanya aktif edilmeli." )
	Adi = models.CharField( u'Kampanya Adı', max_length = 200 )
	UstKat = models.ManyToManyField( Kategori )
	Marka = models.ManyToManyField( Marka )
	Uyelik = models.BooleanField( u"Üyelik", default = True, help_text = "Üye girişi zorunlu ise seçiniz." )

	IndirimFiyatTuru = models.CharField( u'İndirim Fiyat Türü', max_length = 20, choices = FiyatTuru, default = 'IndirimsizFiyati', blank = False, null = False, help_text = "Sadece ürün fiyatına özel kampanya yapıldığında geçerlidir." )
	IndirimZamani = models.CharField( u'İndirim Zamanı', max_length = 7, choices = IndirimZamani, default = 'Aninda', blank = False, null = False )
	IndirimTuru = models.CharField( u'İndirim Türü', max_length = 5, choices = IndirimTurleri, default = 'YUZDE', blank = False, null = False )
	IndirimOrani = models.IntegerField( u'İndirim Oranı', max_length = 3, default = "50" )

	BaslamaZamani = models.DateTimeField( default = datetime.now( ) )
	BitirmeZamani = models.DateTimeField( default = datetime.now( ) + timedelta( days = 365 ) )



	def __unicode__( self ):
		return u"%s" % (self.Adi)


	class Meta:
		verbose_name_plural = u"İkinci Ürüne Kampanyası"
		verbose_name = u"Kampanya"


class TutarliGenelToplamKampanya( models.Model ):
	Aktif = models.BooleanField( u"Aktif", default = True, help_text = "Yalnızca bir kampanya aktif edilmeli." )
	Adi = models.CharField( u'Kampanya Adı', max_length = 200 )
	Marka = models.ForeignKey( Marka )
	Uyelik = models.BooleanField( u"Üyelik", default = True, help_text = "Üye girişi zorunlu ise seçiniz." )

	BaslamaZamani = models.DateTimeField( default = datetime.now( ) )
	BitirmeZamani = models.DateTimeField( default = datetime.now( ) + timedelta( days = 365 ) )



	def __unicode__( self ):
		return u"%s" % (self.Adi)


	class Meta:
		verbose_name_plural = u"Aşamalı Anında İndirim Kampanyası"
		verbose_name = u"Kampanya"


class TutarliGenelToplamKampanyaUcretler( models.Model ):
	Kampanyasi = models.ForeignKey( TutarliGenelToplamKampanya )
	Tutar = models.DecimalField( u'Fiyat', max_digits = 10, decimal_places = 2 )
	Tutar2 = models.DecimalField( u'Fiyat', max_digits = 10, decimal_places = 2 )
	Indirim = models.DecimalField( u'İndirim', max_digits = 10, decimal_places = 2 )



	def __unicode__( self ):
		return u"%s" % (self.Tutar)


	class Meta:
		verbose_name_plural = u"Kriterler"
		verbose_name = u"Kriter"


#
#
#
#
#
# class UyeKampanya(models.Model):
#
# UyeID                       =       models.CharField(u'Uye ID', max_length=100, blank = False, null = False)
#
# Adi                         =       models.CharField(u'Kampanya Adı', max_length=200)
#
# IndirimZamani               =       models.CharField(u'İndirim Zamanı', max_length=7, choices=IndirimZamani, default='Aninda')
#     IndirimTuru                 =       models.CharField(u'İndirim Türü', max_length=5, choices=IndirimTurleri, default='TL')
#     IndirimOrani                =       models.IntegerField(u'İndirim Oranı', max_length=3, default="10")
#
#     Kullanildi                  =       models.BooleanField(u"Kullanıldı", default=False)
#
#
#     def __unicode__(self):
#         return u"%s" %(self.UyeID,)
#
#     class Meta:
#         verbose_name_plural     = u"Faydalanılan Kampanyaları"
#         verbose_name            = u"Kampanya"
#
#


#
