# -*- coding: utf-8 -*-

from django.contrib import admin

from kampanyalar.models import YeniUyeKampanya, YeniUyeKampanyaHakEdenler, PuanKampanya, PuanKampanyaHakEdenler, FaydanilanKampanyalar, Kampanya, BirAlanaBirBedavaKampanya, TutarliGenelToplamKampanyaUcretler, TutarliGenelToplamKampanya, IkinciyeKampanya


class PuanKampanyaAdmin( admin.ModelAdmin ):
	list_display = ('Aktif', 'IndirimFiyatTuru', 'IndirimTuru', 'TutarOran', 'BaslamaZamani', 'BitirmeZamani')
	search_fields = ['Adi', ]


admin.site.register( PuanKampanya, PuanKampanyaAdmin )


class PuanKampanyaHakEdenlerAdmin( admin.ModelAdmin ):
	list_display = ('UyeID', 'Aktif', 'KazanilanPuan', 'IslemTarihi')
	search_fields = ['UyeID', ]
	ordering = ['-IslemTarihi', ]
	date_hierarchy = 'IslemTarihi'


admin.site.register( PuanKampanyaHakEdenler, PuanKampanyaHakEdenlerAdmin )


class FaydanilanKampanyalarAdmin( admin.ModelAdmin ):
	list_display = ('KampanyaAdi', 'UyeID', 'SiparisID', 'IslemTarihi')
	search_fields = ['KampanyaAdi', 'UyeID', ]
	ordering = ['-IslemTarihi', ]
	date_hierarchy = 'IslemTarihi'


admin.site.register( FaydanilanKampanyalar, FaydanilanKampanyalarAdmin )


class BirAlanaBirBedavaKampanyaAdmin( admin.ModelAdmin ):
	list_display = ('Adi', 'Aktif', 'BaslamaZamani', 'BitirmeZamani')
	search_fields = ['Adi', ]


admin.site.register( BirAlanaBirBedavaKampanya, BirAlanaBirBedavaKampanyaAdmin )


class IkinciyeKampanyaKampanyaAdmin( admin.ModelAdmin ):
	list_display = ('Adi', 'Aktif', 'BaslamaZamani', 'BitirmeZamani')
	search_fields = ['Adi', ]


admin.site.register( IkinciyeKampanya, IkinciyeKampanyaKampanyaAdmin )


class YeniUyeKampanyaAdmin( admin.ModelAdmin ):
	list_display = ('Adi', 'id', 'Aktif', 'TutarOran', 'BaslamaZamani', 'BitirmeZamani')
	search_fields = ['Adi', ]


admin.site.register( YeniUyeKampanya, YeniUyeKampanyaAdmin )


class YeniUyeKampanyaHakEdenlerAdmin( admin.ModelAdmin ):
	list_display = ('UyeID', 'Aktif', 'IslemTarihi')
	search_fields = ['UyeID', ]
	ordering = ['-IslemTarihi', ]
	date_hierarchy = 'IslemTarihi'


admin.site.register( YeniUyeKampanyaHakEdenler, YeniUyeKampanyaHakEdenlerAdmin )


class TutarliGenelToplamKampanyaUcretlerInline( admin.TabularInline ):
	model = TutarliGenelToplamKampanyaUcretler
	extra = 1


class TutarliGenelToplamKampanyaAdmin( admin.ModelAdmin ):
	list_display = ('Adi', 'Aktif', 'Marka')
	inlines = (TutarliGenelToplamKampanyaUcretlerInline,)


admin.site.register( TutarliGenelToplamKampanya, TutarliGenelToplamKampanyaAdmin )


class KampanyaAdmin( admin.ModelAdmin ):
	list_display = ('Adi', 'Aktif', 'Uyelik', 'UrunToplam', 'EnAzTutar', 'EnAzAdet', 'IndirimZamani', 'IndirimTuru', 'IndirimOrani', 'IndirimFiyatTuru', 'KampanyaKullanimSiniri', 'KalanKullanimSiniri', 'BaslamaZamani', 'BitirmeZamani')
	search_fields = ['Adi', ]


# ~ filter_horizontal = ('AltKat', 'Marka')


admin.site.register( Kampanya, KampanyaAdmin )
#
#
#
# class YonlendirmelerAdmin(admin.ModelAdmin):
# list_display                =       ('UyeID', 'YonlendirenSite')
# search_fields               =       ['YonlendirenSite', ]
#
# admin.site.register(Yonlendirmeler, YonlendirmelerAdmin)
#
#
#
# class UyeKampanyaAdmin(admin.ModelAdmin):
# list_display                =       ('UyeID', 'Adi')
#     search_fields               =       ['Adi', ]
# admin.site.register(UyeKampanya, UyeKampanyaAdmin)
