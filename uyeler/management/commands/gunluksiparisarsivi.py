# -*- coding: utf-8 -*-


from decimal import Decimal

from django.db.models import Sum, Avg
from django.core.management.base import BaseCommand

from uyeler.models import Siparis, GunlukSiparisArsivi, SepetUrunler


class Command( BaseCommand ):
	help = u'Günlük sipariş gelir giderlerini kaydeder'



	def handle( self, *args, **options ):

		genel_toplam = Siparis.objects.aggregate( geneltoplam_sum = Sum( 'GenelToplam' ) )
		genel_toplam_ortalama = Siparis.objects.aggregate( geneltoplam_avg = Avg( 'GenelToplam' ) )

		geneltutar_toplami = '{:0.2f}'.format( Decimal( genel_toplam['geneltoplam_sum'] ), 2 )
		geneltutar_ortalamasi = '{:0.2f}'.format( Decimal( genel_toplam_ortalama['geneltoplam_avg'] ), 2 )
		teslimedilen_toplami = '{:0.2f}'.format( Decimal( Siparis.objects.filter( Durum__id = 22 ).exclude( Durum__id = 24 ).exclude( Durum__id = 16 ).aggregate( urunlertoplamtutar_sum = Sum( 'UrunlerToplamTutar' ) ).items( )[0][1] ), 2 )
		teslimedilmeyen_toplami = '{:0.2f}'.format( Decimal( Siparis.objects.exclude( Durum__id = 22 ).exclude( Durum__id = 34 ).aggregate( urunlertoplamtutar_sum = Sum( 'UrunlerToplamTutar' ) ).items( )[0][1] ), 2 )

		try:
			yenisiparis_toplami = '{:0.2f}'.format( Decimal( Siparis.objects.filter( Durum__id = 1 ).aggregate( geneltoplam_sum = Sum( 'GenelToplam' ) ).items( )[0][1] ), 2 )
		except:
			yenisiparis_toplami = 0

		try:
			ucretiadesiistendi_toplami = '{:0.2f}'.format( Decimal( Siparis.objects.filter( Durum__id = 24 ).aggregate( geneltoplam_sum = Sum( 'GenelToplam' ) ).items( )[0][1] ), 2 )
		except:
			ucretiadesiistendi_toplami = 0

		try:
			ucretiadesiyapildi_toplami = '{:0.2f}'.format( Decimal( Siparis.objects.filter( Durum__id = 16 ).aggregate( geneltoplam_sum = Sum( 'GenelToplam' ) ).items( )[0][1] ), 2 )
		except:
			ucretiadesiyapildi_toplami = 0

		try:
			iptalodemeyapilmadi_toplami = '{:0.2f}'.format( Decimal( Siparis.objects.filter( Durum__id = 34 ).aggregate( geneltoplam_sum = Sum( 'GenelToplam' ) ).items( )[0][1] ), 2 )
		except:
			iptalodemeyapilmadi_toplami = 0

		try:
			teslimedilenindirim_toplami = '{:0.2f}'.format( Decimal( Siparis.objects.filter( Durum__id = 22 ).exclude( Durum__id = 24 ).exclude( Durum__id = 16 ).aggregate( indtoplamtutar_sum = Sum( 'IndToplamTutar' ) ).items( )[0][1] ), 2 )
		except:
			teslimedilenindirim_toplami = 0

		try:
			teslimedilmeyenindirim_toplami = '{:0.2f}'.format( Decimal( Siparis.objects.exclude( Durum__id = 22 ).exclude( Durum__id = 34 ).aggregate( indtoplamtutar_sum = Sum( 'IndToplamTutar' ) ).items( )[0][1] ), 2 )
		except:
			teslimedilmeyenindirim_toplami = 0

		urun_adeti = SepetUrunler.objects.filter( SepetID__in = Siparis.objects.values_list( 'SepetID' ) ).aggregate( adet_sum = Sum( 'Adet' ) ).items( )[0][1]
		urun_ortalama_tutar = '{:0.2f}'.format( Decimal( genel_toplam['geneltoplam_sum'] ) / SepetUrunler.objects.filter( SepetID__in = Siparis.objects.values_list( 'SepetID' ) ).aggregate( adet_sum = Sum( 'Adet' ) ).items( )[0][1], 2 )

		try:
			smsucreti_toplami = '{:0.2f}'.format( Decimal( Siparis.objects.aggregate( smsbedeli_sum = Sum( 'SMSBedeli' ) ).items( )[0][1] ), 2 )
		except:
			smsucreti_toplami = 0

		hizmetbedeli_toplami = '{:0.2f}'.format( Decimal( Siparis.objects.aggregate( hizmetbedeli_sum = Sum( 'HizmetBedeli' ) ).items( )[0][1] ), 2 )
		kargoucreti_toplami = '{:0.2f}'.format( Decimal( Siparis.objects.aggregate( kargobedeli_sum = Sum( 'KargoBedeli' ) ).items( )[0][1] ), 2 )

		kaydet = GunlukSiparisArsivi(

			geneltutar_toplami = geneltutar_toplami, geneltutar_ortalamasi = geneltutar_ortalamasi, teslimedilen_toplami = teslimedilen_toplami, teslimedilmeyen_toplami = teslimedilmeyen_toplami, yenisiparis_toplami = yenisiparis_toplami, ucretiadesiistendi_toplami = ucretiadesiistendi_toplami, ucretiadesiyapildi_toplami = ucretiadesiyapildi_toplami, iptalodemeyapilmadi_toplami = iptalodemeyapilmadi_toplami, urun_adeti = urun_adeti, urun_ortalama_tutar = urun_ortalama_tutar, smsucreti_toplami = smsucreti_toplami, hizmetbedeli_toplami = hizmetbedeli_toplami, teslimedilmeyenindirim_toplami = teslimedilmeyenindirim_toplami, teslimedilenindirim_toplami = teslimedilenindirim_toplami, kargoucreti_toplami = kargoucreti_toplami

		)

		kaydet.save( )

