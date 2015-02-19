# -*- coding: utf-8 -*-


import logging
import re
import string
import random
import gc

from django.utils.html import strip_spaces_between_tags
from django.shortcuts import render_to_response
from django.template import RequestContext

from kategoriler import gelismisaygitraporlama
from siteayarlari.models import CeM
from teslabb import settings


class IPOgrenMiddleware( object ):
	def process_request( self, request ):

		#
		# for k, v in request.COOKIES.iteritems( ):
		# logging.info(k)
		# logging.info(v)


		# try:
		# UyeID           = Kullanicilar.objects.get( user = request.user ).uyeid
		# except:
		#     UyeID = request.COOKIES.get( 'UyeID' )
		#     if not UyeID:
		#         UyeID = ''.join( [random.choice( string.digits ) for i in range( 0, 8 )] )
		#
		# request.uyeid = UyeID




		reg_b = re.compile( r"android|avantgo|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|symbian|treo|up\\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino", re.I | re.M )
		reg_v = re.compile( r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|e\\-|e\\/|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\\-|2|g)|yas\\-|your|zeto|zte\\-", re.I | re.M )

		request.mobile = False
		user_agent = ""
		if request.META.has_key( 'HTTP_USER_AGENT' ):
			user_agent = request.META['HTTP_USER_AGENT']
			b = reg_b.search( user_agent )
			v = reg_v.search( user_agent[0:4] )
			if b or v:
				request.mobile = True

		if "ipad" in user_agent.lower( ):
			request.mobile = True

		x_forwarded_for = request.META.get( 'HTTP_X_FORWARDED_FOR' )
		if x_forwarded_for:
			request.ipadres = x_forwarded_for.split( ',' )[0]
		else:
			request.ipadres = request.META.get( 'REMOTE_ADDR' )


class MobileDetectionMiddleware( object ):
	def process_request( self, request ):
		is_mobile = False;

		if request.META.has_key( 'HTTP_USER_AGENT' ):
			user_agent = request.META['HTTP_USER_AGENT']

			pattern = "(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|windows ce|pda|mobile|mini|palm|netfront)"
			prog = re.compile( pattern, re.IGNORECASE )
			match = prog.search( user_agent )

			if match:
				is_mobile = True;
			else:
				# Nokia wap için
				# http://www.developershome.com/wap/xhtmlmp/xhtml_mp_tutorial.asp?page=mimeTypesFileExtension

				if request.META.has_key( 'HTTP_ACCEPT' ):
					http_accept = request.META['HTTP_ACCEPT']

					pattern = "application/vnd\.wap\.xhtml\+xml"
					prog = re.compile( pattern, re.IGNORECASE )

					match = prog.search( http_accept )

					if match:
						is_mobile = True

			if not is_mobile:

				user_agents_test = ("w3c ", "acs-", "alav", "alca", "amoi", "audi", "avan", "benq", "bird", "blac", "blaz", "brew", "cell", "cldc", "cmd-", "dang", "doco", "eric", "hipt", "inno", "java", "jigs", "kddi", "keji", "leno", "lg-c", "lg-d", "lg-g", "lge-", "maui", "maxo", "midp", "mits", "mmef", "mobi", "mot-", "moto", "mwbp", "nec-", "newt", "noki", "xda", "palm", "pana", "pant", "phil", "play", "port", "prox", "qwap", "sage", "sams", "sany", "sch-", "sec-", "send", "seri", "sgh-", "shar", "sie-", "siem", "smal", "smar", "sony", "sph-", "symb", "t-mo", "teli", "tim-", "tosh", "tsm-", "upg1", "upsi", "vk-v", "voda", "wap-", "wapa", "wapi", "wapp", "wapr", "webc", "winw", "winw", "xda-",)

				test = user_agent[0:4].lower( )
				if test in user_agents_test:
					is_mobile = True


			# logging.info("------------->" + str(user_agent))


			if "ipad" in user_agent.lower( ):
				is_mobile = True

		request.is_mobile = is_mobile


class MobileDetectMiddleware( object ):
	def process_request( self, request ):
		import re




		reg_b = re.compile( r"android|avantgo|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|symbian|treo|up\\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino", re.I | re.M )
		reg_v = re.compile( r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|e\\-|e\\/|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\\-|2|g)|yas\\-|your|zeto|zte\\-", re.I | re.M )

		request.mobile = False
		if request.META.has_key( 'HTTP_USER_AGENT' ):
			user_agent = request.META['HTTP_USER_AGENT']
			b = reg_b.search( user_agent )
			v = reg_v.search( user_agent[0:4] )
			if b or v:
				request.mobile = True


class SayfaTazeleMiddleware( object ):
	def process_response( self, request, response ):

		# try:

		for i in settings.YONLENDIRME:

			if i.split( ':' )[0] in request.build_absolute_uri( ):
				response.content = response.content + '<meta http-equiv="refresh" content="' + i.split( ':' )[1] + '">'
				return response

		return response



	# except:
	# response.content = response.content + '<meta http-equiv="refresh" content="6">'
	# return response


class GelismisAygitRaporlamaMiddleware( object ):
	def process_request( self, request ):

		is_mobile = False;
		is_tablet = False;
		is_phone = False;
		is_masaustu = False;
		is_bot = False;
		bot = False

		user_agent = request.META.get( "HTTP_USER_AGENT" )
		http_accept = request.META.get( "HTTP_ACCEPT" )

		if user_agent and http_accept:
			agent = gelismisaygitraporlama.UAgentInfo( userAgent = user_agent, httpAccept = http_accept )
			is_tablet = agent.detectTierTablet( )
			is_phone = agent.detectTierIphone( )
			is_mobile = is_tablet or is_phone or agent.detectMobileQuick( )
			is_masaustu = not is_mobile

			if "Googlebot" in user_agent or "YandexBot" in user_agent or "YandexMetrika" or "AhrefsBot" in user_agent or "bingbot" in user_agent:
				bot = True

		request.is_mobile = is_mobile
		request.is_tablet = is_tablet
		request.is_phone = is_phone
		request.is_masaustu = is_masaustu
		request.is_bot = bot


def queryset_iterator( queryset, chunksize = 1000 ):
	pk = 0
	last_pk = queryset.order_by( '-pk' )[0].pk
	queryset = queryset.order_by( 'pk' )
	while pk < last_pk:
		for row in queryset.filter( pk__gt = pk )[:chunksize]:
			pk = row.pk
			yield row
		gc.collect( )


class CeMiddleware( object ):
	def process_response( self, request, response ):


		x_forwarded_for = request.META.get( 'HTTP_X_FORWARDED_FOR' )
		if x_forwarded_for:
			ip = x_forwarded_for.split( ',' )[0]
		else:
			ip = request.META.get( 'REMOTE_ADDR' )

		AcilanSayfa = request.build_absolute_uri( )

		# logging.info("\n\n")
		# logging.info(ip == "88.250.159.71")
		# logging.info("online-satin-al" in AcilanSayfa)
		# logging.info(not request.user.is_authenticated( ))

		if "yeni-urunler" in AcilanSayfa and not request.user.is_authenticated( ) and ip == "88.250.159.71":

			try:

				obj = CeM.objects.get( url = AcilanSayfa ).htmldosyasi

				logging.info( AcilanSayfa + " zaten vardı" )

				# cont = strip_spaces_between_tags( obj.icerik )
				# icerik = re.sub( r'^\s+<', '<', cont )

				return render_to_response( 'cachem/' + obj + '.html', context_instance = RequestContext( request ) )

			# return HttpResponse( icerik )


			except CeM.DoesNotExist:

				htmldosya = str( ''.join( random.choice( string.ascii_lowercase ) for i in range( 12 ) ) )

				obj = CeM( url = AcilanSayfa, icerik = response.content, htmldosyasi = htmldosya )
				obj.save( )
				logging.info( AcilanSayfa + " yeni kayıt açıldı" )

				cont = strip_spaces_between_tags( response.content )
				response.content = re.sub( r'^\s+<', '<', cont )

				file = open( '/home/muslu/django/teslabb/templates/cachem/' + htmldosya + '.html', 'w+' )  # fiziksel yolu sonra değiştirmek lazım gibi
				file.write( response.content )
				file.close( )

				return response

		return response

