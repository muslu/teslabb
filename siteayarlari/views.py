# -*- coding: utf-8 -*-
import logging
import urllib
import urllib2
import json

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_protect

from siteayarlari.models import Blog, BlogKategoriler, GeriBildirimler, Sayfa2SMSArsiv, Sayfa2SMS


def Iletisim( request ):
	return render_to_response( 'iletisim.html', { }, context_instance = RequestContext( request ) )


def Hakkimizda( request ):
	return render_to_response( 'hakkimizda.html', { }, context_instance = RequestContext( request ) )


def Blogu( request ):
	kategori_listesi = BlogKategoriler.objects.order_by( '-id' )

	blog_listesi = Blog.objects.order_by( '-id' )

	etiket_listesi = Blog.objects.filter( Etiket__isnull = False ).exclude( Etiket__exact = '' )

	listem = []

	for i in etiket_listesi:

		for ii in i.Etiket.split( ', ' ):

			if not ii in listem:

				listem.append( ii )

	paginator = Paginator( blog_listesi, 5 )

	page = request.GET.get( 'sayfa' )
	try:
		bloglar = paginator.page( page )
	except PageNotAnInteger:
		bloglar = paginator.page( 1 )
	except EmptyPage:
		bloglar = paginator.page( paginator.num_pages )

	return render_to_response( 'blog_listesi.html', { 'bloglar': bloglar, 'etiketler': listem, 'kategori_listesi': kategori_listesi }, context_instance = RequestContext( request ) )


def BloguDetay( request, slug ):
	blog_detayi = Blog.objects.get( Slug = slug )

	kategori_listesi = BlogKategoriler.objects.order_by( '-id' )

	etiket_listesi = Blog.objects.filter( Etiket__isnull = False ).exclude( Etiket__exact = '' )

	listem = []

	for i in etiket_listesi:

		for ii in i.Etiket.split( ', ' ):

			if not ii in listem:

				listem.append( ii )

	return render_to_response( 'blog_detay.html', { 'blog_detayi': blog_detayi, 'etiketler': listem, 'kategori_listesi': kategori_listesi }, context_instance = RequestContext( request ) )


def BloguEtiket( request, etiket ):
	kategori_listesi = BlogKategoriler.objects.order_by( '-id' )

	blog_listesi = Blog.objects.filter( Etiket__contains = etiket )

	etiket_listesi = Blog.objects.filter( Etiket__isnull = False ).exclude( Etiket__exact = '' )

	listem = []

	for i in etiket_listesi:

		for ii in i.Etiket.split( ', ' ):

			if not ii in listem:

				listem.append( ii )

	paginator = Paginator( blog_listesi, 5 )

	page = request.GET.get( 'sayfa' )
	try:
		bloglar = paginator.page( page )
	except PageNotAnInteger:
		bloglar = paginator.page( 1 )
	except EmptyPage:
		bloglar = paginator.page( paginator.num_pages )

	return render_to_response( 'blog_listesi.html', { 'bloglar': bloglar, 'etiketler': listem, 'kategori_listesi': kategori_listesi }, context_instance = RequestContext( request ) )


def BloguKategori( request, slug ):
	kategori_listesi = BlogKategoriler.objects.order_by( '-id' )

	blog_listesi = Blog.objects.filter( Kategori__Slug = slug )

	etiket_listesi = Blog.objects.filter( Etiket__isnull = False ).exclude( Etiket__exact = '' )

	listem = []

	for i in etiket_listesi:

		for ii in i.Etiket.split( ', ' ):

			if not ii in listem:

				listem.append( ii )

	paginator = Paginator( blog_listesi, 5 )

	page = request.GET.get( 'sayfa' )
	try:
		bloglar = paginator.page( page )
	except PageNotAnInteger:
		bloglar = paginator.page( 1 )
	except EmptyPage:
		bloglar = paginator.page( paginator.num_pages )

	return render_to_response( 'blog_listesi.html', { 'bloglar': bloglar, 'etiketler': listem, 'kategori_listesi': kategori_listesi }, context_instance = RequestContext( request ) )


@csrf_protect
def Sayfa2SMSGonder( request ):
	if request.is_ajax( ):

		if request.method == 'POST':

			TelefonNo = request.POST['tel']
			url = request.POST['url']

			# url = request.build_absolute_uri( )


			x_forwarded_for = request.META.get( 'HTTP_X_FORWARDED_FOR' )
			if x_forwarded_for:
				ip = x_forwarded_for.split( ',' )[0]
			else:
				ip = request.META.get( 'REMOTE_ADDR' )

			post_url = "http://po.st/api/shorten?longUrl=https://www.sporthink.com.tr" + url + "&apiKey=1D87B898-BEA2-439E-ACBF-9199338B421C"

			postdata = { 'longUrl': url }
			headers = { 'Content-Type': 'application/json' }
			req = urllib2.Request( post_url, json.dumps( postdata ), headers )
			ret = urllib2.urlopen( req ).read( )

			kisaurl = json.loads( ret )['short_url']

			SMSMetni = Sayfa2SMS.objects.order_by( '-id' ).last( )

			Mesaj = SMSMetni.Metin + " " + str( kisaurl )

			kackere = Sayfa2SMSArsiv.objects.filter( IP = ip ).count( )

			logging.info( kackere )

			if kackere < int( SMSMetni.Limit ):

				Apimiz = "http://www.pratikbilisim.net/panel/smsgonder.php?kno=12234&kul_ad=905325614848&sifre=539425&gonderen=SPORTHINK&mesaj='" + smart_str( Mesaj ) + "'&cepteller=" + str( TelefonNo ).replace( ' ', '' )

				uo = urllib.urlopen( Apimiz )

				SMSGittiMi = uo.read( )

				if "Gonderildi" in SMSGittiMi:
					ss = Sayfa2SMSArsiv( Telefon = TelefonNo, Url = kisaurl, UUrl = url, Request = request, IP = ip, Durum = "Ok" )
					ss.save( )
					return HttpResponse( str( TelefonNo ) + " " + str( kisaurl ) + " Gönderildi" )
				else:
					ss = Sayfa2SMSArsiv( Telefon = TelefonNo, Url = kisaurl, UUrl = url, Request = request, IP = ip, Durum = "No" )
					ss.save( )
					return HttpResponse( str( TelefonNo ) + " " + str( kisaurl ) + " Gönderilemedi!" )

			else:

				return HttpResponse( "Limitiniz doldu!" )


		else:
			return HttpResponse( 'WTF!' )


@csrf_protect
def PopupMesaj( request ):
	if request.POST:

		request.encoding = 'utf-8'

		isimsoyisim = request.POST.get( 'isimsoyisim', '' )
		email = request.POST.get( 'email', '' )
		mesaj = request.POST.get( 'mesaj', '' )

		Aygit = ""
		if request.is_masaustu:
			Aygit = u"Desktop"
		if request.is_tablet:
			Aygit = u"Tablet"
		if request.is_mobile:
			Aygit = u"Telefon"

		GeriBildirimler( IsimSoyisim = isimsoyisim, Email = email, Mesaj = mesaj, Tarayici = request.META['HTTP_USER_AGENT'], Aygit = Aygit ).save( )

		return render_to_response( 'popupmesaj.html', { }, context_instance = RequestContext( request ) )





