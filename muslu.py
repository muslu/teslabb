# -*- coding: utf-8 -*-

# ~ muslu yüksektepe
# 11.03.2014 19:09:19#      -  Muslu YÜKSEKTEPE

class app_name_degistir( str ):
	def __new__( cls, value, title ):
		instance = str.__new__( cls, value )
		instance._title = title
		return instance



	def title( self ):
		return self._title



	__copy__ = lambda self: self
	__deepcopy__ = lambda self, memodict: self


# 24.04.2014 10:12:03#      -  Muslu YÜKSEKTEPE
from django.db.models import FileField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _


class DosyaTuruKontrol( FileField ):
	"""
			2.5MB - 2621440
			5MB - 5242880
			10MB - 10485760
			20MB - 20971520
			50MB - 5242880
			100MB 104857600
			250MB - 214958080
			500MB - 429916160
	"""



	def __init__( self, *args, **kwargs ):
		self.kabuledilen_dosya_turu = kwargs.pop( "kabuledilen_dosya_turu" )
		self.en_fazla_byte = kwargs.pop( "en_fazla_byte" )

		super( DosyaTuruKontrol, self ).__init__( *args, **kwargs )



	def clean( self, *args, **kwargs ):
		data = super( DosyaTuruKontrol, self ).clean( *args, **kwargs )

		file = data.file
		try:
			content_type = file.content_type
			if content_type in self.kabuledilen_dosya_turu:
				if file._size > self.en_fazla_byte:
					raise forms.ValidationError( _( u'Kabul edilir dosya boyutu: %s, Gönderilen: %s' ) % (filesizeformat( file._size ), filesizeformat( self.en_fazla_byte )) )
			else:
				raise forms.ValidationError( _( u'Bu dosya türü kabul edilmemektedir.' ) )
		except AttributeError:
			pass

		return data
