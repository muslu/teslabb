# -*- coding: utf-8 -*-


import os
import re
import urllib2
import cStringIO
import copy
from math import floor
from PIL import Image

from django.db import models
from django.template.defaultfilters import slugify
from django.conf import settings

from smart_selects.db_fields import ChainedForeignKey


def FotoKontrol( dosyayolu ):
	import os




	return os.path.isfile( str( settings.__getattr__( "BASE_DIR" ) ) + "/media/" + str( dosyayolu ) )


def Logoyu_Yeniden_Isimlendir_Marka( instance, filename ):
	f, ext = os.path.splitext( filename )
	return '%s%s%s' % ('marka_logolar/50x50/', slugify( instance.Adi ), ext)


def Logoyu_Yeniden_Isimlendir_Cinsiyet( instance, filename ):
	f, ext = os.path.splitext( filename )
	return '%s%s%s' % ('cinsiyet_logolar/', slugify( instance.Adi ), ext)


def Logoyu_Yeniden_Isimlendir_Kategori( instance, filename ):
	f, ext = os.path.splitext( filename )
	return '%s%s%s' % ('kategori_logolar/', slugify( instance.Adi ), ext)


def Logoyu_Yeniden_Isimlendir_OrtaKategori( instance, filename ):
	f, ext = os.path.splitext( filename )
	return '%s%s%s' % ('ortakategori_logolar/', slugify( instance.Adi ), ext)


def Logoyu_Yeniden_Isimlendir_AltKategori( instance, filename ):
	f, ext = os.path.splitext( filename )
	return '%s%s%s' % ('altkategori_logolar/', slugify( instance.Adi ), ext)


def Logoyu_Yeniden_Isimlendir_Urun( instance, filename ):
	f, ext = os.path.splitext( filename )
	return '%s%s%s' % ('urun_resimleri/', instance.StokKodu, ext)


def Logoyu_Yeniden_Isimlendir_Urun_Varyant( instance, filename ):
	f, ext = os.path.splitext( filename )
	return '%s%s%s' % ('urun_resimleri/' + unicode( instance.Urunu.StokKodu ) + '/', instance.Barkod, ext)


def FotografBoyutlandir( F_IN ):
	from PIL import Image, ImageDraw




	size = (600, 600)

	image = Image.open( F_IN )
	image.thumbnail( size, Image.ANTIALIAS )

	img_w, img_h = image.size
	background = Image.new( 'RGBA', (600, 600), (255, 255, 255, 255) )
	bg_w, bg_h = background.size
	offset = ((bg_w - img_w) / 2, (bg_h - img_h) / 2)

	background.paste( image, offset )

	draw = ImageDraw.Draw( background )
	# font=ImageFont.truetype("/usr/share/fonts/truetype/tlwg/TlwgTypo-Oblique.ttf", 12)
	# draw.text((350, 400), "www.sporthink.com.tr", (255,255,0), font=font)

	background.save( F_IN.path, quality = 60 )


class Marka( models.Model ):
	# ~ id = models.AutoField( primary_key = True, unique = True )
	Adi = models.CharField( u'Ünvanı', max_length = 150, unique = True )
	Logo = models.ImageField( upload_to = Logoyu_Yeniden_Isimlendir_Marka, null = True, blank = True )
	Aciklama = models.TextField( u'Detaylı Açıklama', help_text = 'Marka hakkında detaylı bilgi girilebilir.', blank = True, null = True )
	Slug = models.SlugField( u'Link' )

	# ~ def get_absolute_url( self ):
	# ~ return reverse( 'MarkaDetayi', kwargs = { 'Adi': self.Adi } )


	def __unicode__( self ):
		return u"%s" % self.Adi



	def related_label( self ):
		return u"%s (%s)" % (self.Adi, self.id)



	def Logoyu_Goster( self ):
		if self.Logo:
			return u'<img src="/media/%s" width="100px" />' % self.Logo



	Logoyu_Goster.short_description = 'Logo'
	Logoyu_Goster.allow_tags = True


	class Meta:
		verbose_name_plural = u"Marka"
		ordering = ('Adi',)


	@classmethod
	def get_posts( self, limit = None ):
		if limit:
			return Marka.objects.filter( ).order_by( 'Adi' )[0:limit]
		else:
			return Marka.objects.filter( ).order_by( 'Adi' )


class Cinsiyet( models.Model ):  # Bay Bayan Çocuk
	# ~ id = models.AutoField( primary_key = True, unique=True )
	Adi = models.CharField( u'Cinsiyet', max_length = 150, unique = True )
	Logo = models.ImageField( upload_to = Logoyu_Yeniden_Isimlendir_Cinsiyet, blank = True, null = True )
	LogoLink = models.CharField( u'Logo Linki', blank = True, null = True, max_length = 250 )
	MetaAciklama = models.CharField( u'Meta Açıklama', help_text = u'Kategori hakkında detaylı bilgi girilebilir. Max: 150 Karakter', blank = True, null = True, max_length = 150 )
	MetaEtiket = models.CharField( u'Meta Etiket', help_text = u'Yazılacak tüm kelimelerin arasına virgül ile ayırmanız gerekir. Max: 10 Kelime', blank = True, null = True, max_length = 150 )
	Slug = models.SlugField( u'Link' )



	def __unicode__( self ):
		return u"%s" % self.Adi



	def related_label( self ):
		return u"%s (%s)" % (self.Adi, self.id)



	def Logoyu_Goster( self ):
		if self.Logo:
			return u'<img src="/media/%s" />' % self.Logo



	Logoyu_Goster.short_description = 'Logo'
	Logoyu_Goster.allow_tags = True


	class Meta:
		verbose_name_plural = u"1 - Cinsiyet"
		ordering = ('Adi',)


class Kategori( models.Model ):  # Aksesuar, Ayakkabı Grubu, Spor Malzemeleri, Tekstil
	# id = models.AutoField( primary_key = True, unique = True )
	Cinsiyet = models.ForeignKey( Cinsiyet )
	Adi = models.CharField( u'Kategori Adı', max_length = 150 )
	Logo = models.ImageField( upload_to = Logoyu_Yeniden_Isimlendir_Kategori, blank = True, null = True )
	MetaAciklama = models.CharField( u'Meta Açıklama', help_text = u'Kategori hakkında detaylı bilgi girilebilir. Max: 150 Karakter', blank = True, null = True, max_length = 150 )
	MetaEtiket = models.CharField( u'Meta Etiket', help_text = u'Yazılacak tüm kelimelerin arasına virgül ile ayırmanız gerekir. Max: 10 Kelime', blank = True, null = True, max_length = 150 )
	Slug = models.SlugField( u'Link' )



	def __unicode__( self ):
		return u"%s - %s" % (self.Cinsiyet, self.Adi)



	def related_label( self ):
		return u"%s (%s)" % (self.Adi, self.id)



	def Logoyu_Goster( self ):
		if self.Logo:
			return u'<img src="/media/%s" />' % self.Logo



	Logoyu_Goster.short_description = 'Logo'
	Logoyu_Goster.allow_tags = True



	def save( self ):

		super( Kategori, self ).save( )

		if self.Logo:

			imaj = Image.open( self.Logo )
			(Genislik, Yukseklik) = imaj.size

			MaxBoyut = 200

			if Yukseklik > Genislik:
				Oran = float( Genislik ) / float( Yukseklik )
				newGenislik = Oran * MaxBoyut
				imaj = imaj.resize( (int( floor( newGenislik ) ), MaxBoyut), Image.ANTIALIAS )

			elif Genislik > Yukseklik:
				Oran = float( Yukseklik ) / float( Genislik )
				newYukseklik = Oran * MaxBoyut
				imaj = imaj.resize( (MaxBoyut, int( floor( newYukseklik ) )), Image.ANTIALIAS )

			imaj.save( self.Logo.path )

		else:
			super( Kategori, self ).save( )


	class Meta:
		verbose_name_plural = u"2 - Kategori"
		ordering = ('Adi',)


class OrtaKategori( models.Model ):  # Anahtarlık, Bağcık, Çanta, Öorap, Kupa
	# ~ id = models.AutoField( primary_key = True, unique = True )
	UstKat = models.ForeignKey( Kategori )
	Adi = models.CharField( u'Orta Kategori Adı', max_length = 150 )
	Logo = models.ImageField( upload_to = Logoyu_Yeniden_Isimlendir_OrtaKategori, blank = True, null = True )
	MetaAciklama = models.CharField( u'Meta Açıklama', help_text = u'Kategori hakkında detaylı bilgi girilebilir. Max: 150 Karakter', blank = True, null = True, max_length = 150 )
	MetaEtiket = models.CharField( u'Meta Etiket', help_text = u'Yazılacak tüm kelimelerin arasına virgül ile ayırmanız gerekir. Max: 10 Kelime', blank = True, null = True, max_length = 150 )
	Slug = models.SlugField( u'Link' )



	def UstKategorisi( self ):
		return u'%s' % (self.UstKat)



	# ~ @staticmethod
	# ~ def autocomplete_search_fields():
	#~ return ("id__iexact", "Adi__icontains",)



	def __unicode__( self ):
		return u"%s - %s" % (self.UstKat, self.Adi)



	#~ return u"%s" %(self.Adi)


	class Meta:
		verbose_name_plural = u"3 - Orta Kategori"
		ordering = ('UstKat__Cinsiyet', 'UstKat__Adi', 'Adi' )


	def Logoyu_Goster( self ):
		if self.Logo:
			return u'<img src="/media/%s" />' % self.Logo



	Logoyu_Goster.short_description = 'Logo'
	Logoyu_Goster.allow_tags = True


class AltKategori( models.Model ):  # Deri Cüzdan, Valiz, Atkı, Boyunluk ...
	# id = models.AutoField( primary_key = True, unique=True )
	# ~ id                 =      models.AutoField(primary_key=True)
	UstKat = models.ForeignKey( Kategori )
	OrtaKat = models.ForeignKey( OrtaKategori, default = 150 )
	Adi = models.CharField( u'Kategori Adı', max_length = 150 )
	Aciklama = models.CharField( u'Kategori Açıklaması', max_length = 150, blank = True, null = True )
	Oncelik = models.IntegerField( u'Giyim Sırası', blank = True, null = True, default = 1 )
	Bolge = models.IntegerField( u'Vücut Bölgesi', blank = True, null = True, default = 1 )
	Logo = models.ImageField( upload_to = Logoyu_Yeniden_Isimlendir_AltKategori, blank = True, null = True )
	MetaAciklama = models.CharField( u'Meta Açıklama', help_text = u'Kategori hakkında detaylı bilgi girilebilir. Max: 150 Karakter', blank = True, null = True, max_length = 150 )
	MetaEtiket = models.CharField( u'Meta Etiket', help_text = u'Yazılacak tüm kelimelerin arasına virgül ile ayırmanız gerekir. Max: 10 Kelime', blank = True, null = True, max_length = 150 )
	Slug = models.SlugField( u'Link' )


	# ~ def UstKategorisi(self):
	#~ return '%s'%(self.OrtaKat)


	def __unicode__( self ):
		return u"%s %s %s %s" % (self.UstKat.Cinsiyet, self.UstKat.Adi, self.OrtaKat.Adi, self.Adi)



	#~ return u"%s" %(self.Adi)


	class Meta:
		verbose_name_plural = u"4 - Alt Kategori"
		ordering = ('OrtaKat__UstKat__Adi',)


	def OrtaKategorisi( self ):
		return re.sub( str( self.UstKat ) + ' - ', '', str( self.OrtaKat ) )



	OrtaKategorisi.allow_tags = True
	OrtaKategorisi.short_description = 'Orta Kategorisi'



	def Logoyu_Goster( self ):
		if self.Logo:
			return u'<img src="/media/%s" />' % self.Logo



	Logoyu_Goster.short_description = 'Logo'
	Logoyu_Goster.allow_tags = True


class Urun( models.Model ):  # NIKE ERKEK AYAKKABI CAPRI III LOW LEA, NIKE ERKEK AYAKKABI CAPRI III LOW LEA
	# ~ id = models.AutoField( primary_key=True, unique=True )
	UstKat = models.ForeignKey( Kategori, related_name = 'uskat+' )
	OrtaKat = ChainedForeignKey( OrtaKategori, chained_field = "UstKat", chained_model_field = "UstKat", show_all = False, auto_choose = True )
	AltKat = models.ManyToManyField( AltKategori, related_name = 'altk+' )

	Marka = models.ForeignKey( Marka, null = True )

	URL = models.CharField( u'Resim Yolu', max_length = 250, blank = True, null = True )
	URLdenYukle = models.BooleanField( default = False )

	Logo = models.ImageField( u'Ürün Fotoğrafı', upload_to = Logoyu_Yeniden_Isimlendir_Urun, blank = True, null = True )
	Logo2 = models.ImageField( u'Ürün Fotoğrafı', upload_to = Logoyu_Yeniden_Isimlendir_Urun, blank = True, null = True )
	Logo3 = models.ImageField( u'Ürün Fotoğrafı', upload_to = Logoyu_Yeniden_Isimlendir_Urun, blank = True, null = True )
	Logo4 = models.ImageField( u'Ürün Fotoğrafı', upload_to = Logoyu_Yeniden_Isimlendir_Urun, blank = True, null = True )
	Logo5 = models.ImageField( u'Ürün Fotoğrafı', upload_to = Logoyu_Yeniden_Isimlendir_Urun, blank = True, null = True )

	Adi = models.CharField( u'Stok Adı', max_length = 250 )
	StokKodu = models.CharField( u'Stok Kodu', max_length = 150 )

	KisaURL = models.CharField( u'Kısa URL', max_length = 150, null = True, blank = True )

	# ~ toplam_stok_sayisi   =         models.IntegerField(u'Toplam Stok Sayısı', default=0)

	MetaAciklama = models.CharField( u'Meta Açıklama', help_text = u'Kategori hakkında detaylı bilgi girilebilir. Max: 150 Karakter', blank = True, null = True, max_length = 150 )
	MetaEtiket = models.CharField( u'Meta Etiket', help_text = u'Yazılacak tüm kelimelerin arasını "tek boşluk" ile ayırmanız gerekir. Max: 10 Kelime', blank = True, null = True, max_length = 150 )

	Slug = models.SlugField( u'Link', max_length = 250, unique = True )
	Fiyat = models.DecimalField( u'Fiyat', max_digits = 8, decimal_places = 2, default = 0 )
	EFiyat = models.DecimalField( u'Eski Fiyatı', max_digits = 8, decimal_places = 2, default = 0 )

	KdvOrani = models.IntegerField( u'Kdv Orani', default = 0, null = True )
	Desi = models.IntegerField( u'Desi', default = 1, null = True )

	# KisaAciklama       =      HTMLField()
	KisaAciklama = models.TextField( u'Açıklama', blank = True, null = True )
	# UzunAciklama       =      models.TextField(u'Uzun Açıklama', help_text=u'Ürün hakkında detaylı bilgi', blank=True, null=True)

	# ~ Kampanya                =      models.NullBooleanField( null=True, default=0)
	Vitrin = models.NullBooleanField( u'Vitrin', help_text = u'Anasayfada gösterilmesini istiyorsanız işaretleyiniz', null = True, default = 0 )
	Yeni = models.NullBooleanField( u'Yeni', help_text = u'Yeni ürün mü?', null = True, default = 0 )
	Outlet = models.NullBooleanField( u'Outlet', help_text = u'Outlet ürün mü?', null = True, default = 0 )
	Firsat = models.NullBooleanField( u'Fırsat', help_text = u'Fırsat ürünü mü?', null = True, default = 0 )

	UcBoyutlu = models.NullBooleanField( u'3D Çekim', help_text = u'Ürünün 3D fotoğrafı mevcut mu?', null = True, default = 0 )
	HaftaninUrunu = models.NullBooleanField( u'Haftanın Ürünü', help_text = u'Haftanın Ürünü sayfasında gösterilmesini istiyorsanız işaretleyiniz', null = True, default = 0 )
	EnCokSatan = models.NullBooleanField( u'En Çok Satan Ürün', help_text = u'En Çok Satan Ürün sayfasında gösterilmesini istiyorsanız işaretleyiniz', null = True, default = 0 )
	Defolu = models.NullBooleanField( u'Defolu', help_text = u'Defolu ürün mü?', null = True, default = 0 )
	Tarih = models.DateTimeField( auto_now = True, auto_now_add = True, null = True, blank = True )



	def Logoyu_Goster( self ):
		if self.Logo:
			return u'<img src="/media/%s" width="50px"/>' % self.Logo



	Logoyu_Goster.short_description = 'Ana Resim'
	Logoyu_Goster.allow_tags = True



	def Guncelle( self ):
		return u'<a href="http://www.spormarket.com.tr/urunv3/?gun=600&model=' + self.StokKodu + u'" target="_blank">Güncelle</a>'



	Guncelle.short_description = 'Güncelle'
	Guncelle.allow_tags = True



	def AltKategorisi( self ):
		return " - ".join( [s.Adi for s in self.AltKat.all( )] )



	AltKategorisi.allow_tags = True
	AltKategorisi.admin_order_field = 'AltKat__Adi'
	AltKategorisi.short_description = 'Alt Kategorisi'



	def OrtaKategorisi( self ):

		dee = re.sub( str( self.UstKat ) + ' - ', '', str( self.OrtaKat ) )

		if dee != "None":
			return dee
		else:
			return ""



	OrtaKategorisi.allow_tags = True
	OrtaKategorisi.short_description = 'Orta Kategorisi'
	OrtaKategorisi.admin_order_field = 'OrtaKat__Adi'



	def Markasi( self ):
		return '%s' % (self.Marka)



	def __unicode__( self ):
		return u"%s %s" % (self.Adi, self.StokKodu)


	class Meta:
		verbose_name_plural = u"5 - Ürün"
		ordering = ('UstKat__Cinsiyet', 'AltKat__Adi', 'Marka')

	#
	#
	# def save(self, *args, **kwargs):
	#     if self.URLdenYukle and self.URL != '':
	#         image = ImajIndir(self.URL)
	#         try:
	#             filename = urlparse.urlparse(self.URL).path.split('/')[-1]
	#             self.Logo = filename
	#             tempfile = image
	#             tempfile_io = cStringIO.StringIO()
	#             tempfile.save(tempfile_io, format=image.format)
	#             self.Logo.save(filename, ContentFile(tempfile_io.getvalue()), save=False)
	#         except Exception, e:
	#             pass
	#
	#     super(Urun, self).save(*args, **kwargs)
	#


class MarkaAltKatAciklama( models.Model ):
	Marka = models.ForeignKey( Marka )
	AltKat = models.ManyToManyField( AltKategori )
	Aciklama = models.TextField( u'Açıklama', help_text = 'Örn: Adidas tekstil ürün kalıpları dardır. Nike ayakkabılarda bir numara büyük alınmalı.', blank = True, null = True )


	class Meta:
		verbose_name_plural = u"Marka Kategori Açıklaması"


class Varyant( models.Model ):
	# id = models.AutoField( primary_key = True, unique = True )
	Cinsiyet = models.ForeignKey( Cinsiyet, related_name = 'c+' )
	Urunu = models.ForeignKey( Urun )
	AltKat = models.ManyToManyField( AltKategori, blank = True, null = True )
	Renk = models.CharField( max_length = 100 )
	RenkKodu = models.CharField( max_length = 100 )
	Beden = models.CharField( "Beden - Numara", max_length = 100, null = True, blank = True )
	Kavala = models.CharField( max_length = 100, blank = True, null = True )
	# ~ Numara          =      models.CharField(max_length=100,  null=True)
	Barkod = models.CharField( u'Barkod', max_length = 15, unique = True )
	StokSayisi = models.IntegerField( u'Stok Sayısı', default = 0, null = True )
	EkstraFiyat = models.DecimalField( u'Ekstra Fiyat', max_digits = 8, decimal_places = 2, default = 0, null = True )
	# ~ Vitrin          =      models.NullBooleanField(u'Vitrin',  null=True, default=0)
	Defolu = models.NullBooleanField( u'Defolu Ürün', null = True, default = 0 )

	UcBoyutlu = models.NullBooleanField( u'3D Çekim', help_text = u'Varyant 3D fotoğrafı mevcut mu?', null = True, default = 0 )
	Logo1 = models.ImageField( u'Ürün Fotoğrafı', upload_to = Logoyu_Yeniden_Isimlendir_Urun_Varyant, blank = True, null = True )
	Logo2 = models.ImageField( u'Ürün Fotoğrafı', upload_to = Logoyu_Yeniden_Isimlendir_Urun_Varyant, blank = True, null = True )
	Logo3 = models.ImageField( u'Ürün Fotoğrafı', upload_to = Logoyu_Yeniden_Isimlendir_Urun_Varyant, blank = True, null = True )
	Logo4 = models.ImageField( u'Ürün Fotoğrafı', upload_to = Logoyu_Yeniden_Isimlendir_Urun_Varyant, blank = True, null = True )
	Logo5 = models.ImageField( u'Ürün Fotoğrafı', upload_to = Logoyu_Yeniden_Isimlendir_Urun_Varyant, blank = True, null = True )
	Tarih = models.DateTimeField( auto_now = True, auto_now_add = True, null = True, blank = False )



	# def save(self):
	#
	# super(Varyant, self).save()
	#
	#     Stokkodumuz = Varyant.objects.get( id = self.id ).Urunu.StokKodu
	#     Rengimiz = self.Renk
	#
	#     if self.Logo1:
	#         F_IN               =      self.Logo1
	#         FotografBoyutlandir(F_IN)
	#         Varyant.objects.filter( Renk = Rengimiz, Urunu__StokKodu = Stokkodumuz ).update(Logo1=self.Logo1)
	#
	#     if self.Logo2:
	#        F_IN = self.Logo2
	#        FotografBoyutlandir( F_IN )
	#        Varyant.objects.filter( Renk = Rengimiz, Urunu__StokKodu = Stokkodumuz ).update( Logo2 = self.Logo2 )
	#
	#     if self.Logo3:
	#        F_IN = self.Logo3
	#        FotografBoyutlandir( F_IN )
	#        Varyant.objects.filter( Renk = Rengimiz, Urunu__StokKodu = Stokkodumuz ).update( Logo3 = self.Logo3 )
	#
	#     if self.Logo4:
	#        F_IN = self.Logo4
	#        FotografBoyutlandir( F_IN )
	#        Varyant.objects.filter( Renk = Rengimiz, Urunu__StokKodu = Stokkodumuz ).update( Logo4 = self.Logo4 )
	#
	#     if self.Logo5:
	#        F_IN = self.Logo5
	#        FotografBoyutlandir( F_IN )
	#        Varyant.objects.filter( Renk = Rengimiz, Urunu__StokKodu = Stokkodumuz ).update( Logo5 = self.Logo5 )
	#
	#     else:
	#         super(Varyant, self).save()

	def __unicode__( self ):
		return u"%s %s %s" % (self.Renk, self.Beden, self.Kavala)


	class Meta:
		verbose_name_plural = u"Varyantlar"
		verbose_name = u"Varyant"


	def VaryantOlanSubeleriGosteer( self ):

		from django.db import connections




		cursor = connections["V3"].cursor( )

		VaryantBilgisi = Varyant.objects.get( id = self.id )

		strr = u"""
            SELECT
                V3_DOGUKAN.dbo.MSEnvanterDepo.M01,
                V3_DOGUKAN.dbo.MSEnvanterDepo.S01,
                V3_DOGUKAN.dbo.MSEnvanterDepo.OPT,
                V3_DOGUKAN.dbo.MSEnvanterDepo.ANADEPO,
                V3_DOGUKAN.dbo.MSEnvanterDepo.INT
             FROM V3_DOGUKAN.dbo.MSEnvanterDepo
                             WHERE (MSEnvanterDepo.ItemCode='""" + VaryantBilgisi.Urunu.StokKodu + """'
                             and MSEnvanterDepo.ColorCode='""" + VaryantBilgisi.RenkKodu.upper( ) + """'
                             and MSEnvanterDepo.ItemDim1Code='""" + VaryantBilgisi.Beden + """'
                             and MSEnvanterDepo.ItemDim2Code='""" + VaryantBilgisi.Kavala + """')  """
		cursor.execute( strr )

		for i in cursor.fetchall( ):

			Buca = "Buca:" + str( int( i[0] ) )
			Sirinyer = "Sirinyer:" + str( int( i[1] ) )
			Optimum = "Optimum:" + str( int( i[2] ) )
			AnaDepo = "AnaDepo:" + str( int( i[3] ) )
			Internet = "Internet:" + str( int( i[4] ) )

			# if str( int( row[4] ) ) != "0":Internet       =      "Internet:"     + str(int(row[4]))

			Donus = AnaDepo, Buca, Optimum, Sirinyer, Internet

			return str( Donus ).replace( '(', '' ).replace( ')', '' ).replace( "'", "" ).replace( ',', '<br />' )



	VaryantOlanSubeleriGosteer.allow_tags = True
	VaryantOlanSubeleriGosteer.short_description = 'Şubeler'


class BenzerKategoriler( models.Model ):
	# ~ id = models.AutoField( primary_key = True, unique = True )
	AltKat = models.ForeignKey( AltKategori )
	BenzerKat = models.ManyToManyField( AltKategori, related_name = 'bk+' )
	# ~ AltKat          =      ChainedForeignKey(AltKategori, chained_field="OrtaKat", chained_model_field="OrtaKat", show_all=False, auto_choose=True)

	def __unicode__( self ):
		return self.AltKat.Adi


	class Meta:
		verbose_name_plural = u"6 - Benzer Kategoriler"
		verbose_name = u"Benzer Kategori"


class BenzerUrunler( models.Model ):
	# ~ id = models.AutoField( primary_key = True, unique = True )
	# urun               =      models.ForeignKey(Urun)
	urun = models.ManyToManyField( Urun, blank = True, null = True, related_name = "benzerurunler" )
	eslesenurun = models.ManyToManyField( Urun, blank = True, null = True, related_name = "benzerurunlers" )


	class Meta:
		verbose_name_plural = u"7 - Benzer Ürünler"
		verbose_name = u"Benzer Ürün"


class ServisDurumu( models.Model ):
	Servis = models.CharField( u'Otomatik/Elle', max_length = 10, blank = False, null = False )
	Gun = models.CharField( u'Gun', max_length = 3, blank = False, null = False )
	Sorgu = models.TextField( u'Sorgu', blank = False, null = False )
	Calisiyor = models.BooleanField( u'Çalışıyor?', default = True )
	Tamamlandi = models.BooleanField( u'Tamamlandı?', default = False )
	IslemTarihi = models.DateTimeField( auto_now = True, auto_now_add = True, null = True, blank = True )
	BitisTarihi = models.DateTimeField( auto_now = True, auto_now_add = True, null = True, blank = True )
	IP = models.CharField( u'IP', max_length = 20, blank = False, null = False )



	def __unicode__( self ):
		return self.Gun


	class Meta:
		verbose_name_plural = u"Servis Durumu"


def ImajIndir( url ):
	headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0' }
	r = urllib2.Request( url, headers = headers )
	request = urllib2.urlopen( r, timeout = 10 )
	image_data = cStringIO.StringIO( request.read( ) )
	img = Image.open( image_data )
	img_copy = copy.copy( img )
	if ImajDogrula( img_copy ):
		return img
	else:
		raise Exception( u'Hatalı bir işlem yapıldı!' )


def ImajDogrula( img ):
	type = img.format
	if type in ('JPEG', 'JPG', 'PNG'):
		try:
			img.verify( )
			return True
		except:
			return False
	else:
		return False
