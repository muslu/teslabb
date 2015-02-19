# -*- coding: utf-8 -*-

import logging

from django.contrib import admin
from django.forms import *
from django.db import models
from django.http import HttpResponse
from django.utils.encoding import smart_unicode
from django.conf import settings
from django.contrib.admin.views.main import ChangeList
from django.db.models import Sum, Avg

from uyeler.models import FacebookProfil, Kullanicilar, SepetUrunler, Sepet, Siparis, SiparisDurumKategorileri, SiparisDurumlari, SiparisArsiv, HediyeKuponu, KKOdemeArsiv, DFOdeme, DFOdemeArsiv, SMSArsiv, GunlukSiparisArsivi
from daterange_filter.filter import DateRangeFilter


class DFOdemeArsivAdmin( admin.ModelAdmin ):
	list_display = ('Odeme', 'AdSoyad', 'SiparisNo', 'Durum', 'IP', 'Tutar', 'IslemTarihi')
	search_fields = ['AdSoyad', 'SiparisNo']


admin.site.register( DFOdemeArsiv, DFOdemeArsivAdmin )


class FacebookProfilAdmin( admin.ModelAdmin ):
	list_display = ('id', 'user', 'facebook_id')
	search_fields = ['user']


admin.site.register( FacebookProfil, FacebookProfilAdmin )


class KullanicilarAdmin( admin.ModelAdmin ):
	list_display = ('user', 'uyeadi', 'uyesoyadi', 'GezintiGecmisi', 'AramaYap', 'uyeid', 'IslemTarihi')
	search_fields = ['uyeadi', 'uyesoyadi', 'uyemail', 'uyeid']
	date_hierarchy = 'IslemTarihi'



	def queryset( self, request ):
		qs = super( KullanicilarAdmin, self ).queryset( request )
		self.request = request
		return qs



	def AramaYap( self, obj ):

		x_forwarded_for = self.request.META.get( 'HTTP_X_FORWARDED_FOR' )
		if x_forwarded_for:
			IP = x_forwarded_for.split( ',' )[0]
		else:
			IP = self.request.META.get( 'REMOTE_ADDR' )

		SANTRAL_SABIT_IP = settings.__getattr__( 'SANTRAL_SABIT_IP' )
		SANTRAL_IP = settings.__getattr__( 'SANTRAL_IP' )

		SANTRAL_DAHILI = settings.__getattr__( 'SANTRAL_DAHILI' )
		SANTRAL_PORT = settings.__getattr__( 'SANTRAL_PORT' )
		SANTRAL_CLICK2CALL = settings.__getattr__( 'SANTRAL_CLICK2CALL' )
		if str( str( self.request.user ).split( '_' )[0] ).isdigit( ):
			Dahili = str( str( self.request.user ).split( '_' )[0] )
		else:
			Dahili = SANTRAL_DAHILI

		if obj.uyetelefon and IP == SANTRAL_SABIT_IP:  # # Aynı IP kullanılıyorsa yani şirket içinde ise gibi
			return u"<a target='_blank' href='http://" + SANTRAL_IP + ":" + SANTRAL_PORT + SANTRAL_CLICK2CALL + Dahili + "&phone=" + str( obj.uyetelefon ).replace( ' ', '' ) + u"'> Ara </a>"
		else:
			return u"<a target='_blank' href='http://" + SANTRAL_SABIT_IP + ":" + SANTRAL_PORT + SANTRAL_CLICK2CALL + Dahili + "&phone=" + str( obj.uyetelefon ).replace( ' ', '' ) + u"'> Ara </a>"



	AramaYap.short_description = 'Telefon'
	AramaYap.allow_tags = True


admin.site.register( Kullanicilar, KullanicilarAdmin )


class SepetUrunlerInline( admin.TabularInline ):
	model = SepetUrunler
	formfield_overrides = { models.CharField: { 'widget': TextInput( ) }, }
	fields = ('VaryantOlanSubeleriGoster', 'VaryantResimGoster', 'VaryantBarkodGoster', 'Adet', 'VaryantID')
	extra = 0
	readonly_fields = ( 'VaryantResimGoster', 'VaryantOlanSubeleriGoster', 'VaryantBarkodGoster')


class SepetAdmin( admin.ModelAdmin ):
	list_display = ('UyeID', 'Tamamlandi', 'OzelNot', 'SiparisIDsi', 'UyeAdiGetir', 'IP', 'GezintiGecmisiIP', 'SepettekiUrunlerinToplamAdeti', 'IslemTarihi')
	search_fields = ['id', 'UyeID', 'IP', 'sepeturunler__VaryantID']
	list_per_page = 50
	inlines = (SepetUrunlerInline,)
	ordering = ['-IslemTarihi', ]
	date_hierarchy = 'IslemTarihi'
	actions_on_top = True



	def queryset( self, request ):
		qs = super( SepetAdmin, self ).queryset( request )
		self.request = request
		return qs



	def AramaYap( self, obj ):

		x_forwarded_for = self.request.META.get( 'HTTP_X_FORWARDED_FOR' )
		if x_forwarded_for:
			IP = x_forwarded_for.split( ',' )[0]
		else:
			IP = self.request.META.get( 'REMOTE_ADDR' )

		SANTRAL_SABIT_IP = settings.__getattr__( 'SANTRAL_SABIT_IP' )
		SANTRAL_IP = settings.__getattr__( 'SANTRAL_IP' )

		SANTRAL_DAHILI = settings.__getattr__( 'SANTRAL_DAHILI' )
		SANTRAL_PORT = settings.__getattr__( 'SANTRAL_PORT' )
		SANTRAL_CLICK2CALL = settings.__getattr__( 'SANTRAL_CLICK2CALL' )

		uyetelefon = Kullanicilar.objects.get( uyeid = obj.UyeID ).uyetelefon

		if str( str( self.request.user ).split( '_' )[0] ).isdigit( ):
			Dahili = str( str( self.request.user ).split( '_' )[0] )
		else:
			Dahili = SANTRAL_DAHILI

		if uyetelefon and IP == SANTRAL_SABIT_IP:  # # Aynı IP kullanılıyorsa yani şirket içinde ise gibi
			return u"<a target='_blank' href='http://" + SANTRAL_IP + ":" + SANTRAL_PORT + SANTRAL_CLICK2CALL + Dahili + "&phone=" + str( uyetelefon ).replace( ' ', '' ) + u"'> Ara </a>"
		else:
			return u"<a target='_blank' href='http://" + SANTRAL_SABIT_IP + ":" + SANTRAL_PORT + SANTRAL_CLICK2CALL + Dahili + "&phone=" + str( uyetelefon ).replace( ' ', '' ) + u"'> Ara </a>"



	AramaYap.short_description = 'Telefon'
	AramaYap.allow_tags = True



	def SiparisIDsi( self, obj ):
		siparisidne = Siparis.objects.get( SepetID = obj.id )
		return siparisidne.SiparisNo



	def UyeAdiGetir( self, obj ):
		uyeadine = Kullanicilar.objects.get( uyeid = obj.UyeID )
		return uyeadine.uyeadi + " " + uyeadine.uyesoyadi



	def UyeTelefonGetir( self, obj ):
		uyeadine = Kullanicilar.objects.get( uyeid = obj.UyeID )
		return uyeadine.uyetelefon


admin.site.register( Sepet, SepetAdmin )


def export_xls( modeladmin, request, queryset ):
	import xlwt




	response = HttpResponse( mimetype = 'application/ms-excel' )
	response['Content-Disposition'] = 'attachment; filename=Cikti.xls'
	wb = xlwt.Workbook( encoding = 'utf-8' )
	ws = wb.add_sheet( "Sayfa" )

	row_num = 0

	columns = [(u"Durum", 4000), (u"Siparis No", 3000), (u"Ad Soyad", 8000), (u"Genel Toplam", 3500), (u"Ödeme Şekli", 5000), (u"Ödeme Türü", 5000), (u"Ödeme Yapıldı Mı", 5000), (u"Sipariş Tarihi", 5000), (u"Şehir", 3500)]

	font_style = xlwt.XFStyle( )
	font_style.font.bold = True

	for col_num in xrange( len( columns ) ):
		ws.write( row_num, col_num, columns[col_num][0], font_style )
		ws.col( col_num ).width = columns[col_num][1]

	font_style = xlwt.XFStyle( )
	font_style.alignment.wrap = 1

	for obj in queryset:

		row_num += 1
		if obj.OdemeYapildi:
			OdemeYapildiMi = "Evet"
		else:
			OdemeYapildiMi = "Hayır"

		row = [smart_unicode( obj.Durum ), smart_unicode( obj.SiparisNo ), smart_unicode( obj.TAdSoyad ).title( ), smart_unicode( obj.GenelToplam ), smart_unicode( obj.OdemeTuru ), OdemeYapildiMi, smart_unicode( obj.IslemTarihi ), smart_unicode( obj.TIl ).title( ), ]
		for col_num in xrange( len( row ) ):
			ws.write( row_num, col_num, row[col_num], font_style )

	wb.save( response )
	return response


export_xls.short_description = u"Genel Rapor"


def arasexport_xls( modeladmin, request, queryset ):
	import xlwt, time




	response = HttpResponse( mimetype = 'application/ms-excel' )
	response['Content-Disposition'] = 'attachment; filename=' + time.strftime( "%d_%m_%Y" ) + '___KapidaOdemeler.xls'
	wb = xlwt.Workbook( encoding = 'utf-8' )
	ws = wb.add_sheet( "Sayfa" )

	row_num = 0

	Alanlar = "mok, ürün,   ad soyad,   adres,  ilçe,   şehir,  tel,    irsaliye no,    ilkodu, ilcekodu,   varis,  serino, desi,   tahsilat tutarı,    ödeme tipi"

	columns = [(u"mok", 1500), (u"ürün", 3000), (u"ad soyad", 8000), (u"adres", 16000), (u"ilçe", 2000), (u"şehir", 3000), (u"tel", 5000), (u"irsaliye no", 500), (u"ilkodu", 500), (u"ilcekodu", 500), (u"varis", 500), (u"serino", 500), (u"desi", 1500), (u"tahsilat tutarı", 4000), (u"ödeme tipi", 5000)]

	font_style = xlwt.XFStyle( )
	font_style.font.bold = True

	for col_num in xrange( len( columns ) ):
		ws.write( row_num, col_num, columns[col_num][0], font_style )
		ws.col( col_num ).width = columns[col_num][1]

	font_style = xlwt.XFStyle( )
	font_style.alignment.wrap = 1

	for obj in queryset:

		if (obj.OdemeTuru == "KN" or obj.OdemeTuru == "KTC") and str( obj.Durum ) == "Paketlendi":

			if obj.OdemeTuru == "KN":
				OdemeTuruNe = "Kapıda Nakit"
			if obj.OdemeTuru == "KTC":
				OdemeTuruNe = "Kapıda Tek Çekim"

			row_num += 1

			row = [row_num, "Ayakkabı", smart_unicode( obj.TAdSoyad ).title( ), smart_unicode( obj.TAdres ).title( ), "", smart_unicode( obj.TIl ).title( ), smart_unicode( obj.Telefon ), "", "", "", "", "", "2", smart_unicode( obj.GenelToplam ), smart_unicode( OdemeTuruNe ),

			]
			for col_num in xrange( len( row ) ):
				ws.write( row_num, col_num, row[col_num], font_style )

	wb.save( response )
	return response


arasexport_xls.short_description = u"Günlük Kapıda Ödemeler - Excel"


def gelenlerexport_xls( modeladmin, request, queryset ):
	import xlwt, time




	response = HttpResponse( mimetype = 'application/ms-excel' )
	response['Content-Disposition'] = 'attachment; filename=' + time.strftime( "%d_%m_%Y" ) + '___GelenKargolar.xls'
	wb = xlwt.Workbook( encoding = 'utf-8' )
	ws = wb.add_sheet( "Sayfa" )

	row_num = 0

	columns = [(u"Sira", 1500), (u"Sipariş No", 5000), (u"Ad Soyad", 7000), (u"Adres", 13000), (u"Genel Toplam", 4000), (u"Ürün Toplam", 4000), (u"Ödeme", 6000), (u"Degisim Iade", 8000), ]

	font_style = xlwt.XFStyle( )
	font_style.font.bold = True

	for col_num in xrange( len( columns ) ):
		ws.write( row_num, col_num, columns[col_num][0], font_style )
		ws.col( col_num ).width = columns[col_num][1]

	font_style = xlwt.XFStyle( )
	font_style.alignment.wrap = 1

	for obj in queryset:

		if str( obj.Durum ) == "Ücret İadesi İstendi" or str( obj.Durum ) == "Ürün Değişimi İstendi":

			if str( obj.Durum ) == "Ücret İadesi İstendi":
				DegisimIade = "Ücret İadesi"
			else:
				DegisimIade = "Ürün Değişimi"

			if obj.UrunlerToplamTutar >= 100:
				OdemeNasil = "Ücret Alıcı"
			else:
				OdemeNasil = "Gönderici Ödemeli"

				pattern = xlwt.Pattern( )
				pattern.pattern = xlwt.Pattern.SOLID_PATTERN
				pattern.pattern_fore_colour = xlwt.Style.colour_map['red']
				font_style.pattern = pattern

			row_num += 1

			row = [row_num, smart_unicode( obj.SiparisNo ), smart_unicode( obj.TAdSoyad ).title( ), smart_unicode( obj.TAdres ).title( ), smart_unicode( obj.GenelToplam ), smart_unicode( obj.UrunlerToplamTutar ), smart_unicode( OdemeNasil ), smart_unicode( DegisimIade ),

			]

			for col_num in xrange( len( row ) ):
				ws.write( row_num, col_num, row[col_num], font_style )

	wb.save( response )
	return response


gelenlerexport_xls.short_description = u"Günlük Gelen Kargolar - Excel"


def gecikenlere_sms( modeladmin, request, queryset ):
	now = datetime.now( )

	Uyeler = []

	for oo in queryset:

		if (oo.Durum.Durum == u"Sipariş Oluşturuldu" or oo.Durum.Durum == u"Ürünler Bulunuyor" or oo.Durum.Durum == u"Ürün(ler) Bulundu" or oo.Durum.Durum == u"Hazırlanıyor" or oo.Durum.Durum == u"Paketlendi" ) and now.hour > 14:

			if not oo.UyeID in Uyeler:

				Uyeler.append( oo.UyeID )

				Mesaj = "Merhaba " + oo.TAdSoyad.split( ' ' )[0].title( ) + ", " + oo.SiparisNo + u" nolu siparisin yarin Aras kargo firmasina teslim edilecek. Gecikme icin ozur dileriz. 02323200333"

				logging.info( Mesaj )

			# ~ Apimiz = u"http://www.pratikbilisim.net/panel/smsgonder.php?kno=12234&kul_ad=905325614848&sifre=539425&gonderen=SPORMARKET&mesaj='" + Mesaj + "'&cepteller=" + oo.Telefon.replace( ' ', '' )
			# ~ uo = urllib.urlopen( Apimiz )
			# ~
			#~ SMSGittiMi = uo.read( )
			#~ if "Gonderildi" in SMSGittiMi:
			#~ smsekle = SMSArsiv( UyeID = oo.UyeID, Telefon = oo.Telefon.replace( ' ', '' ), Mesaj = Mesaj, Durum = True )
			#~ smsekle.save( )
			#~ else:
			#~ smsekle = SMSArsiv( UyeID = oo.UyeID, Telefon = oo.Telefon.replace( ' ', '' ), Mesaj = Mesaj, Durum = False )
			#~ smsekle.save( )


gecikenlere_sms.short_description = u"Devire Kalanlar - SMS"


class ToplamveOrtalamaSiparisTutarlari( ChangeList ):
	def get_results( self, *args, **kwargs ):
		super( ToplamveOrtalamaSiparisTutarlari, self ).get_results( *args, **kwargs )

		q = self.result_list.aggregate( geneltoplam_sum = Sum( 'GenelToplam' ) )
		qq = self.result_list.aggregate( geneltoplam_avg = Avg( 'GenelToplam' ) )

		try:
			self.geneltutar_toplami = '{:0.2f}'.format( Decimal( q['geneltoplam_sum'] ), 2 )
		except:
			self.geneltutar_toplami = 0

		try:
			self.geneltutar_ortalamasi = '{:0.2f}'.format( Decimal( qq['geneltoplam_avg'] ), 2 )
		except:
			self.geneltutar_ortalamasi = 0

		try:
			self.urun_adeti = SepetUrunler.objects.filter( SepetID__in = self.queryset.values_list( 'SepetID' ) ).aggregate( adet_sum = Sum( 'Adet' ) ).items( )[0][1]
		except:
			self.urun_adeti = 0

		try:
			self.urun_ortalama_tutar = '{:0.2f}'.format( Decimal( q['geneltoplam_sum'] ) / SepetUrunler.objects.filter( SepetID__in = self.queryset.values_list( 'SepetID' ) ).aggregate( adet_sum = Sum( 'Adet' ) ).items( )[0][1], 2 )
		except:
			self.urun_ortalama_tutar = 0

		try:
			self.teslimedilen_toplami = '{:0.2f}'.format( Decimal( self.queryset.filter( Durum__id = 22 ).exclude( Durum__id = 24 ).exclude( Durum__id = 16 ).aggregate( urunlertoplamtutar_sum = Sum( 'UrunlerToplamTutar' ) ).items( )[0][1] ), 2 )
		except:
			self.teslimedilen_toplami = 0

		try:
			self.smsucreti_toplami = '{:0.2f}'.format( Decimal( self.queryset.aggregate( smsbedeli_sum = Sum( 'SMSBedeli' ) ).items( )[0][1] ), 2 )
		except:
			self.smsucreti_toplami = 0

		try:
			self.hizmetbedeli_toplami = '{:0.2f}'.format( Decimal( self.queryset.aggregate( hizmetbedeli_sum = Sum( 'HizmetBedeli' ) ).items( )[0][1] ), 2 )
		except:
			self.hizmetbedeli_toplami = 0

		try:
			self.kargoucreti_toplami = '{:0.2f}'.format( Decimal( self.queryset.aggregate( kargobedeli_sum = Sum( 'KargoBedeli' ) ).items( )[0][1] ), 2 )
		except:
			self.kargoucreti_toplami = 0

		try:
			self.vadefarki_toplami = '{:0.2f}'.format( Decimal( self.queryset.aggregate( vadefarki_sum = Sum( 'VadeFarki' ) ).items( )[0][1] ), 2 )
		except:
			self.vadefarki_toplami = 0

		try:
			self.teslimedilenindirim_toplami = '{:0.2f}'.format( Decimal( self.queryset.filter( Durum__id = 22 ).exclude( Durum__id = 24 ).exclude( Durum__id = 16 ).aggregate( indtoplamtutar_sum = Sum( 'IndToplamTutar' ) ).items( )[0][1] ), 2 )
		except:
			self.teslimedilenindirim_toplami = 0

		try:
			self.ucretiadesiistendi_toplami = '{:0.2f}'.format( Decimal( self.queryset.filter( Durum__id = 24 ).aggregate( geneltoplam_sum = Sum( 'GenelToplam' ) ).items( )[0][1] ), 2 )
		except:
			self.ucretiadesiistendi_toplami = 0

		try:
			self.ucretiadesiyapildi_toplami = '{:0.2f}'.format( Decimal( self.queryset.filter( Durum__id = 16 ).aggregate( geneltoplam_sum = Sum( 'GenelToplam' ) ).items( )[0][1] ), 2 )
		except:
			self.ucretiadesiyapildi_toplami = 0

		try:
			self.teslimedilmeyen_toplami = '{:0.2f}'.format( Decimal( self.queryset.exclude( Durum__id = 22 ).exclude( Durum__id = 34 ).aggregate( urunlertoplamtutar_sum = Sum( 'UrunlerToplamTutar' ) ).items( )[0][1] ), 2 )
		except:
			self.teslimedilmeyen_toplami = 0

		try:
			self.teslimedilmeyenindirim_toplami = '{:0.2f}'.format( Decimal( self.queryset.exclude( Durum__id = 22 ).exclude( Durum__id = 34 ).aggregate( indtoplamtutar_sum = Sum( 'IndToplamTutar' ) ).items( )[0][1] ), 2 )
		except:
			self.teslimedilmeyenindirim_toplami = 0

		try:
			self.yenisiparis_toplami = '{:0.2f}'.format( Decimal( self.queryset.filter( Durum__id = 1 ).aggregate( geneltoplam_sum = Sum( 'GenelToplam' ) ).items( )[0][1] ), 2 )
		except:
			self.yenisiparis_toplami = 0

		try:
			self.iptalodemeyapilmadi_toplami = '{:0.2f}'.format( Decimal( self.queryset.filter( Durum__id = 34 ).aggregate( geneltoplam_sum = Sum( 'GenelToplam' ) ).items( )[0][1] ), 2 )
		except:
			self.iptalodemeyapilmadi_toplami = 0

		try:
			self.test_toplami = '{:0.2f}'.format( Decimal( self.queryset.filter( Durum__id = 47 ).aggregate( geneltoplam_sum = Sum( 'GenelToplam' ) ).items( )[0][1] ), 2 )
		except:
			self.test_toplami = 0


class SiparisAdmin( admin.ModelAdmin ):
	list_display = ( 'Durum', 'Yazdir', 'KargoyuGoster', 'OzelNot', 'OzelNotMusteri', 'OdemeYapildi', 'OdemeTuruAciklama', 'Banka', 'SiparisNo', 'TAdSoyad', 'GenelToplam', 'IslemTarihi', 'AramaYap')
	# 'SepetiGoster',
	search_fields = ['SiparisNo', 'OdemeTuru', 'TAdSoyad', 'TIl', 'Telefon', 'Mail', 'FTC_VergiNo']
	ordering = ['-IslemTarihi', ]
	date_hierarchy = 'IslemTarihi'
	actions = [export_xls, arasexport_xls, gelenlerexport_xls, gecikenlere_sms]
	list_per_page = 40
	actions_on_top = True
	list_filter = (('IslemTarihi', DateRangeFilter), 'Durum', 'OdemeYapildi', 'OdemeTuru', 'TIl')



	def queryset( self, request ):
		qs = super( SiparisAdmin, self ).queryset( request )
		self.request = request
		return qs



	def AramaYap( self, obj ):

		x_forwarded_for = self.request.META.get( 'HTTP_X_FORWARDED_FOR' )
		if x_forwarded_for:
			IP = x_forwarded_for.split( ',' )[0]
		else:
			IP = self.request.META.get( 'REMOTE_ADDR' )

		SANTRAL_SABIT_IP = settings.__getattr__( 'SANTRAL_SABIT_IP' )
		SANTRAL_IP = settings.__getattr__( 'SANTRAL_IP' )

		SANTRAL_DAHILI = settings.__getattr__( 'SANTRAL_DAHILI' )
		SANTRAL_PORT = settings.__getattr__( 'SANTRAL_PORT' )
		SANTRAL_CLICK2CALL = settings.__getattr__( 'SANTRAL_CLICK2CALL' )

		# "/Services/callservice.aspx?username=click2call&password=cl12sprtf&exten=&phone="


		if str( str( self.request.user ).split( '_' )[0] ).isdigit( ):
			Dahili = str( str( self.request.user ).split( '_' )[0] )
		else:
			Dahili = SANTRAL_DAHILI

		if obj.Telefon and IP == SANTRAL_SABIT_IP:  # # Aynı IP kullanılıyorsa yani şirket içinde ise gibi
			return u"<a target='_blank' href='http://" + SANTRAL_IP + ":" + SANTRAL_PORT + SANTRAL_CLICK2CALL + Dahili + "&phone=" + str( obj.Telefon ).replace( ' ', '' ) + u"'> Ara </a>"
		else:
			return u"<a target='_blank' href='http://" + SANTRAL_SABIT_IP + ":" + SANTRAL_PORT + SANTRAL_CLICK2CALL + Dahili + "&phone=" + str( obj.Telefon ).replace( ' ', '' ) + u"'> Ara </a>"



	AramaYap.short_description = 'Telefon'
	AramaYap.allow_tags = True



	def get_changelist( self, request, **kwargs ):
		return ToplamveOrtalamaSiparisTutarlari



	def KargoyuGoster( self, obj ):
		if obj.TakipNo:
			if obj.Durum.Durum != "Teslim Edildi":
				return u"<a target='_blank' href='http://kargotakip.araskargo.com.tr/mainpage.aspx?code=" + obj.TakipNo + u"'> Göster </a>"
			# return u"<a target='_blank' href='http://www.araskargo.com.tr/web_18712_1/cargo_tracking_detail.aspx?query=sporthink.com.tr&kargo_takip_no=" + obj.TakipNo + u"'> Göster </a>"
		if obj.Durum.Durum == "Paketlendi" or obj.Durum.Durum == u"Değişim Paketlendi":
			return u"<a target='_blank' href='/admin/uyeler/siparis/" + str( obj.id ) + u"/'> Takip No Gir </a>"
		else:
			return ""



	KargoyuGoster.short_description = 'Kargo'
	KargoyuGoster.allow_tags = True



	def OdemeTuruAciklama( self, obj ):
		if obj.OdemeTuru == "KN":
			return "Kapıda Nakit"
		if obj.OdemeTuru == "KTC":
			return "Kapıda Tek Çekim"
		if obj.OdemeTuru == "HA":
			return "Havale"
		if obj.OdemeTuru == "KKTC":
			return "Kredi Kartı Tek Çekim"
		if obj.OdemeTuru == "KKT":
			return "Kredi Kartı Taksitli"
		if obj.OdemeTuru == "MA":
			return "Mağazadan Ödeme"
		if obj.OdemeTuru == "OP":
			return "Ödemeyi Paylaş"



	OdemeTuruAciklama.short_description = 'Ödeme Türü'


admin.site.register( Siparis, SiparisAdmin )


class GunlukSiparisArsiviAdmin( admin.ModelAdmin ):
	list_display = ( 'IslemTarihi', 'geneltutar_toplami', 'teslimedilen_toplami', 'teslimedilenindirim_toplami', 'teslimedilmeyen_toplami', 'teslimedilmeyenindirim_toplami', 'ucretiadesiistendi_toplami', 'ucretiadesiyapildi_toplami', 'iptalodemeyapilmadi_toplami', 'smsucreti_toplami', 'hizmetbedeli_toplami', 'kargoucreti_toplami', 'geneltutar_ortalamasi', 'urun_ortalama_tutar', 'urun_adeti'  )
	ordering = ['id', '-IslemTarihi', ]


admin.site.register( GunlukSiparisArsivi, GunlukSiparisArsiviAdmin )


class SiparisDurumKategorileriAdmin( admin.ModelAdmin ):
	list_display = ('Adi',)
	ordering = ['Adi', ]


admin.site.register( SiparisDurumKategorileri, SiparisDurumKategorileriAdmin )


class SiparisDurumlariAdmin( admin.ModelAdmin ):
	list_display = ('Durum',)
	ordering = ['Durum', ]


admin.site.register( SiparisDurumlari, SiparisDurumlariAdmin )


class SiparisArsivAdmin( admin.ModelAdmin ):
	list_display = ('IslemTarihi', 'SiparisTarihi', 'SiparisNo', 'Durum', 'OzelNot', 'TAdSoyad', 'Telefon', 'Mail', 'IslemYapan')
	search_fields = ['SiparisNo', 'Durum', 'IslemYapan']
	ordering = ['-IslemTarihi', 'Durum']
	date_hierarchy = 'IslemTarihi'


admin.site.register( SiparisArsiv, SiparisArsivAdmin )


class HediyeKuponuAdmin( admin.ModelAdmin ):
	list_display = ('IslemTarihi', 'Kod', 'IndirimTuru', 'TutarOran', 'Kullanildi', 'Kullanan', 'UyelikZorunlu')
	list_filter = ('IslemTarihi', 'Kullanildi')
	search_fields = ['Kullanildi', 'IslemYapan', 'Kod']
	ordering = ['-IslemTarihi', 'Kullanildi']
	date_hierarchy = 'IslemTarihi'
	filter_horizontal = ('Urun', )


admin.site.register( HediyeKuponu, HediyeKuponuAdmin )


class DFOdemeAdmin( admin.ModelAdmin ):
	list_display = ('IslemTarihi', 'Tutar')
	date_hierarchy = 'IslemTarihi'


admin.site.register( DFOdeme, DFOdemeAdmin )


class KKOdemeArsivAdmin( admin.ModelAdmin ):
	list_display = ( 'SiparisNo', 'Hata', 'ip', 'FormatliGenelToplam', 'Taksit', 'BankaAdi', 'IslemTarihi')
	search_fields = ['SiparisNo', 'UyeID', ]
	ordering = ['-IslemTarihi', ]
	date_hierarchy = 'IslemTarihi'

	list_filter = ('IslemTarihi', 'BankaAdi', 'UyeID')


admin.site.register( KKOdemeArsiv, KKOdemeArsivAdmin )


class SMSArsivAdmin( admin.ModelAdmin ):
	list_display = ( 'UyeID', 'Durum', 'GonderenTelefon', 'Telefon', 'Mesaj', 'IslemTarihi')
	search_fields = ['UyeID', 'Mesaj', ]
	ordering = ['-IslemTarihi', ]
	date_hierarchy = 'IslemTarihi'

	list_filter = ('UyeID', 'Durum', 'Mesaj')


admin.site.register( SMSArsiv, SMSArsivAdmin )




