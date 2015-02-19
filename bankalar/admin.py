# -*- coding: utf-8 -*-

from django.contrib import admin

from bankalar.models import Bankalar, Taksitler


class TaksitlerInline( admin.TabularInline ):
	model = Taksitler
	extra = 3


class BankalarAdmin( admin.ModelAdmin ):
	list_display = ('Logoyu_Goster', 'Adi', 'MusteriNumarasi')
	inlines = (TaksitlerInline,)


admin.site.register( Bankalar, BankalarAdmin )





