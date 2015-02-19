# -*- coding: utf-8 -*-

import os

from django.db import models
from django.template.defaultfilters import slugify


def Logoyu_Yeniden_Isimlendir_Banka( instance, filename ):
	f, ext = os.path.splitext( filename )
	return '%s%s%s' % ('banka_logolar/', slugify( instance.Adi ), ext)


class Bankalar( models.Model ):
	Aktif = models.BooleanField( u'Aktif', default = 1 )

	Adi = models.CharField( u'Banka Adı', max_length = 150, unique = True )
	DigerBankalar = models.CharField( u'Diğer Bankalar', max_length = 250, blank = True, null = True )

	MusteriNumarasi = models.CharField( u'Müşteri Numarası', max_length = 150 )

	APIKullaniciAdi = models.CharField( u'API Kullanıcı Adı', help_text = "API kullanıcısı için tanımlanan isim", max_length = 150, blank = True, null = True )
	APIKullaniciParolasi = models.CharField( u'API Kullanıcı Parolası', help_text = "API kullanıcısı için tanımlanan parola", max_length = 150, blank = True, null = True )
	HostAdresi = models.CharField( u'Host Adresi', max_length = 150, blank = True, null = True )
	TerminalID = models.CharField( u'Terminal ID', max_length = 150, blank = True, null = True )

	D3URL = models.CharField( u'3D URL', max_length = 150, blank = True, null = True )
	MagazaAdi = models.CharField( u'Mağaza Adı', help_text = "Kendiniz belirleyebilirsiniz. Türkçe karakter kullanmayınız.", max_length = 150, blank = True, null = True )
	GuvenlikAnahtari = models.CharField( u'3D Güvenlik Anahtarı', help_text = "Sanal POS yönetim panelinden sürekli değiştirmeniz önerilir.", max_length = 150, blank = True, null = True )

	Logo = models.ImageField( upload_to = Logoyu_Yeniden_Isimlendir_Banka, blank = True, null = True )



	def Logoyu_Goster( self ):
		if self.Logo:
			return u'<img src="/media/%s" />' % self.Logo



	Logoyu_Goster.short_description = 'Logo'
	Logoyu_Goster.allow_tags = True



	def __unicode__( self ):
		return u"%s" % (self.Adi)


	class Meta:
		verbose_name_plural = u"Banka Bilgileri"
		verbose_name = u"Banka"
		ordering = ('Adi',)


class Taksitler( models.Model ):
	Banka = models.ForeignKey( Bankalar )
	Taksit = models.IntegerField( max_length = 2, blank = True, null = True )
	EkTaksit = models.IntegerField( u"Ek Taksit", max_length = 2, blank = True, null = True, default = 0 )
	FaizOrani = models.IntegerField( u"Faiz Oranı", max_length = 2, blank = True, null = True, default = 0 )


	class Meta:
		verbose_name_plural = u"Banka Taksitleri"
		verbose_name = u"Taksit"
		ordering = ['EkTaksit', 'FaizOrani', 'Taksit', ]