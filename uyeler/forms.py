# -*- coding: utf-8 -*-



from django import forms

from uyeler.models import Kullanicilar


class UyeForm( forms.Form ):
	# ~ uyeid             =       forms.CharField(max_length=150,)
	uyeadi = forms.CharField( max_length = 150, )
	uyesoyadi = forms.CharField( max_length = 150, )
	uyemail = forms.EmailField( max_length = 150, )
	uyepassword = forms.CharField( max_length = 150, )
	uyepassword2 = forms.CharField( max_length = 150, )


	class Meta:
		model = Kullanicilar


	def clean_username( self ):

		username = slugify( self.cleaned_data['uyeadi'] ) + slugify( self.cleaned_data['uyesoyadi'] ) + "_" + ''.join( [random.choice( string.letters ) for i in range( 0, 5 )] )

		try:

			User.objects.get( username = username )

		except User.DoesNotExist:

			return username

		raise forms.ValidationError( "Bu kullanıcı adı daha önceden kayıt edilmiş" )



	def clean( self ):

		if self.cleaned_data['uyepassword'] != self.cleaned_data['uyepassword2']:

			raise forms.ValidationError( "Şifreler uyuşmadı" )

		return self.cleaned_data
