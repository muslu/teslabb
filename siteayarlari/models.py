# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import os

from django.db import models
from django.template.defaultfilters import slugify

from muslu import *




YERLESIM = (
('dikey', 'Dikey'), ('yatay', 'Yatay'), ('anasayfa', 'Ana Sayfa'), ('urun', 'Urun'),
)


class CeM( models.Model ):
	url = models.CharField( u'Url', max_length = 255, unique = True )
	htmldosyasi = models.CharField( u'HTML Dosyası', max_length = 255 )
	icerik = models.TextField( u'İçerik', )



	def __unicode__( self ):
		return u"%s" % (self.url)


	class Meta:
		verbose_name_plural = u"HTML İçerik"
		verbose_name = u"İçerik"


class GeriBildirimler( models.Model ):
	IsimSoyisim = models.CharField( u'İsim Soyisim', max_length = 200 )
	Email = models.CharField( u'Mail', max_length = 200 )
	Mesaj = models.TextField( u'Mesaj', )
	Tarayici = models.TextField( u'Tarayıcı', )
	Aygit = models.TextField( u'Aygit', )
	IslemZamani = models.DateTimeField( default = datetime.now( ) )



	def __unicode__( self ):
		return u"%s" % (self.IsimSoyisim)


	class Meta:
		verbose_name_plural = u"Geri Bildirimler"
		verbose_name = u"geri bildirim"


class SayfayaOzelIcerik( models.Model ):
	URL = models.CharField( u'URL', help_text = "Örn: /levis/levis-erkek-jean-pantolon-00501-0114_u/1_1_54/", max_length = 200, blank = False, null = False )

	KoduUst = models.TextField( u'Üst Kısım', help_text = "Listelemenin üst kısmı", blank = True )
	KoduAlt = models.TextField( u'Alt Kısım', help_text = "Listelemenin alt kısmı", blank = True )

	Stil = models.TextField( u'CSS', blank = True )
	Javascript = models.TextField( u'Javascript', blank = True )

	Aciklama = models.CharField( u'Meta Açıklama', help_text = "150-160 karakter arası", max_length = 160, blank = True )
	Etiket = models.CharField( u'Meta Etiket', help_text = "Artık pek önemli değil. Boşluklar otomatik virgülle ayrılır.", max_length = 200, blank = True )
	Baslik = models.CharField( u'Meta Başlık', help_text = "64 karakter.", max_length = 70, blank = True )

	BaslamaZamani = models.DateTimeField( default = datetime.now( ) )
	BitirmeZamani = models.DateTimeField( default = datetime.now( ) + timedelta( days = 3 ) )
	# ~ Yerlesim            =       models.CharField(max_length=10, choices=YERLESIM, default=0)





	def __unicode__( self ):
		return u"%s" % (self.URL)


	class Meta:
		app_label = app_name_degistir( "siteayarlari", u"Site Ayarları" )
		verbose_name_plural = u"Sayfaya Özel İçerik"
		verbose_name = u"Özel İçerik"


def Yeniden_Isimlendir( instance, filename ):
	f, ext = os.path.splitext( filename )
	return '%s%s%s' % ('blog/', slugify( instance.Baslik ), ext)


def Yeniden_Isimlendir_Banner( instance, filename ):
	f, ext = os.path.splitext( filename )
	return '%s%s%s' % ('banner/', slugify( instance.Baslik ), ext)


class BlogKategoriler( models.Model ):
	Adi = models.CharField( u'Adı', max_length = 200, blank = False, null = False )
	Slug = models.SlugField( u'Link', max_length = 250, unique = True )  # otomatik unique yapar ama version değişirse diye



	def __unicode__( self ):
		return u"%s" % (self.Adi)


	class Meta:
		verbose_name_plural = u"Blog Kategorileri"
		verbose_name = u"Blog Kategorisi"


class Blog( models.Model ):
	Kategori = models.ForeignKey( BlogKategoriler )
	Baslik = models.CharField( u'Başlık', max_length = 200, blank = False, null = False )

	Aciklama = models.TextField( u'Açıklama', blank = True )

	Etiket = models.CharField( u'Özel Etiket', help_text = "Virgül ile ayırın. Örn: 2014 yaz ayakkabıları, 2014 eşofman takımları", max_length = 200, blank = True )
	Resim = models.ImageField( upload_to = Yeniden_Isimlendir, blank = True, null = True )

	BaslamaZamani = models.DateTimeField( u"Yayına başlama tarihi", default = datetime.now( ) )
	BitirmeZamani = models.DateTimeField( u"Yayına bitirme tarihi", default = datetime.now( ) + timedelta( days = 360 ) )
	Slug = models.SlugField( u'Link', max_length = 250, unique = True )  # otomatik unique yapar ama version değişirse diye



	def __unicode__( self ):
		return u"%s" % (self.Baslik)



	def etiket_as_list( self ):
		return self.Etiket.split( ', ' )


	class Meta:
		verbose_name_plural = u"Bloglar"
		verbose_name = u"Blog"


class Banner( models.Model ):
	Baslik = models.CharField( u'Başlık', max_length = 200, blank = False, null = False )
	Link = models.CharField( u'Link', max_length = 200, blank = False, null = False )
	Aktif = models.BooleanField( u"Aktif", default = False )
	Sira = models.IntegerField( u"Sıra", default = 1 )
	Aciklama = models.TextField( u'Açıklama', blank = True )

	Resim = DosyaTuruKontrol( upload_to = Yeniden_Isimlendir_Banner, blank = False, null = False, kabuledilen_dosya_turu = ['image/jpg', 'image/jpeg', 'image/gif'], en_fazla_byte = 1048576 )

	BaslamaZamani = models.DateTimeField( u"Yayına başlama tarihi", default = datetime.now( ) )
	BitirmeZamani = models.DateTimeField( u"Yayına bitirme tarihi", default = datetime.now( ) + timedelta( days = 10 ) )
	Yerlesim = models.CharField( max_length = 30, choices = YERLESIM, default = 2 )
	# ~ Tiklama             =       models.IntegerField(u'Tıklanma', help_text="Linki tıklama sayısı", blank=True, default=0)

	def __unicode__( self ):
		return u"%s" % (self.Baslik)



	def clean( self ):
		super( Banner, self ).save( )

		import os




		os.system( "jpegoptim --max=90 /home/muslu/django/teslabb/media/" + str( self.Resim.name ) )

		if self.Link:

			LinkSonSil = str( self.Link )

			if LinkSonSil.endswith( '/' ):
				LinkSonSil = LinkSonSil[:-1]

			self.Link = LinkSonSil

			super( Banner, self ).save( )



	def ResimGoster( self ):
		if self.Resim:
			return u'<img src="/media/%s" width="250"/>' % self.Resim



	ResimGoster.short_description = 'Resim'
	ResimGoster.allow_tags = True


	class Meta:
		verbose_name_plural = u"Bannerlar"
		verbose_name = u"Banner"


class SubDomainYonlendir( models.Model ):
	Ne = models.CharField( u'Ne', help_text = "Örn: adidas-esofman-takimlari", max_length = 200, blank = False, null = False )
	Nereye = models.CharField( u'Nereye', help_text = " '/' ile başlayıp bitirilmeli!. Örn: /adidas/urunleri/", max_length = 200, blank = False, null = False )



	def __unicode__( self ):
		return u"%s" % (self.Ne)


	class Meta:
		verbose_name_plural = u"Subdomain Yönlendirme"
		verbose_name = u"Subdomain"


class IndirimBalonu( models.Model ):
	Aktif = models.BooleanField( u"Aktif", default = False )
	Baslik = models.CharField( u'Üst Başlık', max_length = 200 )
	Aciklama = models.TextField( u'Açıklama' )



	def __unicode__( self ):
		return u"%s" % (self.Baslik)


	class Meta:
		verbose_name_plural = u"İndirim Balonu"
		verbose_name = u"Kayıt"


class Aramalar( models.Model ):
	Aranan = models.CharField( u'Aranan', max_length = 100, blank = True, null = True )
	AranmaSayisi = models.IntegerField( u'Aranma Sayısı', max_length = 100, blank = True, null = True, default = 0 )
	Sonuc = models.IntegerField( u'Aranma Sonucu', max_length = 100, blank = True, null = True, default = 0 )
	Cihaz = models.CharField( u'Cihaz', max_length = 100, blank = True, null = True )
	Request = models.TextField( u'Request', blank = True, null = True )
	UyeID = models.CharField( u'Üye ID', max_length = 20, blank = True, null = True )
	IslemTarihi = models.DateTimeField( auto_now = True, blank = True )
	IP = models.CharField( u'IP', max_length = 20, blank = False, null = False )



	def __unicode__( self ):
		return u"%s" % (self.Aranan)


	class Meta:
		verbose_name_plural = u"Aramalar"
		verbose_name = u"Arama"


class Yonlendirmeler( models.Model ):
	UyeID = models.CharField( u'Uye ID', max_length = 100, blank = False, null = False )
	Aygit = models.CharField( u'Aygit', max_length = 25, blank = True, null = True )
	Sehir = models.CharField( u'Şehir', max_length = 25, blank = True, null = True )
	YonlendirenSite = models.URLField( u'Yönlendiren Site', max_length = 200 )
	YonlendirenLink = models.URLField( u'Yönlendiren Link', max_length = 200 )
	YonlendirilenSayfa = models.URLField( u'Yönlendirilen Sayfa' )
	IP = models.IPAddressField( u'IP' )
	IslemTarihi = models.DateTimeField( auto_now = True, blank = False )



	def __unicode__( self ):
		return u"%s - %s" % (self.UyeID, self.IP)


	class Meta:
		verbose_name_plural = u"Ziyaretçi Raporları"
		verbose_name = u"Rapor"


class GuncelXMLFirma( models.Model ):
	Firma = models.CharField( u'Firma', max_length = 100, blank = False, null = False )
	Sorgu = models.CharField( u'Sorgu', max_length = 250, blank = True, null = True )
	Request = models.TextField( u'Request', blank = False, null = False )
	IP = models.IPAddressField( u'IP' )
	IslemTarihi = models.DateTimeField( auto_now = True, blank = False )



	def __unicode__( self ):
		return u"%s - %s" % (self.Firma, self.IP)


	class Meta:
		verbose_name_plural = u"Güncel XML Raporları"
		verbose_name = u"Rapor"


class Sayfa2SMS( models.Model ):
	Metin = models.CharField( u'Metin', max_length = 150, blank = False, null = False )
	Limit = models.IntegerField( u'Url', max_length = 3, default = 5, help_text = "IP bazlı SMS gönderim limiti" )



	def __unicode__( self ):
		return self.Metin


	class Meta:
		verbose_name_plural = u"Sayfa2SMS"


class Sayfa2SMSArsiv( models.Model ):
	Telefon = models.CharField( u'Telefon', max_length = 100, blank = False, null = False )
	Url = models.CharField( u'Kısa Url', max_length = 250, blank = True, null = True )
	UUrl = models.CharField( u'Uzun Url', max_length = 250, blank = True, null = True )
	Durum = models.CharField( u'Durum', max_length = 250, blank = True, null = True )
	Request = models.TextField( u'Request', blank = False, null = False )
	IP = models.IPAddressField( u'IP' )
	IslemTarihi = models.DateTimeField( auto_now = True, blank = False )



	def __unicode__( self ):
		return u"%s - %s - %s" % (self.Telefon, self.Url, self.Durum)


	class Meta:
		verbose_name_plural = u"Sayfa2SMS Raporları"
		verbose_name = u"Rapor"

