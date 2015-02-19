# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.utils.functional import curry
from django.views.defaults import *
from django.views.generic import TemplateView

from kategoriler.views import *
from uyeler.views import *




admin.autodiscover( )

urlpatterns = patterns( '',


                        url( r'^$', AnaSayfa, name = "AnaSayfa" ),

                        url( r'^online-([\w\-]+)--([\w\-]+)-satis-modelleri/([\w\-]+)/$', UrunListesi, name = 'UrunListesiAltKat' ), url( r'^([\w\-]+)--([\w\-]+)-urunleri/([\w\-]+)/$', UrunListesi, name = 'UrunListesiOrtaKat' ),

                        url( r'^([\w\-]+)([\w\-]+)-online-satis/([\w\-]+)/$', UrunListesi, name = 'UrunListesiMarka' ),

                        url( r'^yeni-([\w\-]+)-([\w\-]+)-([\w\-]+)-urunleri/$', UrunListesi, name = 'UrunListesiYeniCinsiyet' ), url( r'^yeni-([\w\-]+)-([\w\-]+)-([\w\-]+)/$', UrunListesi, name = 'UrunListesiYeni' ), url( r'^firsat-([\w\-]+)-([\w\-]+)-([\w\-]+)-urunleri/$', UrunListesi, name = 'UrunListesiFirsatCinsiyet' ), url( r'^firsat-([\w\-]+)-([\w\-]+)-([\w\-]+)/$', UrunListesi, name = 'UrunListesiFirsat' ),

                        url( r'^outlet-([\w\-]+)-([\w\-]+)-([\w\-]+)/$', UrunListesi, name = 'UrunListesiOutlet' ), url( r'^haftanin-([\w\-]+)-([\w\-]+)-([\w\-]+)/$', UrunListesi, name = 'UrunListesiHaftaninUrunu' ),


                        url( r'^bul/$', Bul ), url( r'^oto\.xml$', UrunAraXML, name = "UrunAraXML" ), url( r'^gm\.xml$', GoogleMerchantXML, name = "GoogleMerchantXML" ), url( r'^gxml/$', GenelXML ), url( r'^sitemap\.xml$', GoogleSitemapXML, name = "GoogleSitemapXML" ),


                        url( r'^([\w\-]+)/([\w\-]+)-satin-al/([\w\-]+)/$', UrunDetayii, name = 'UrunDetayii' ), url( r'^vd/([\w\-]+)/$', VarID, name = 'VarID' ),

                        url( r'^ud/([\w\-]+)/$', UrunVaryantSecimi, name = 'UrunVaryantSecimi' ), url( r'^urunsil/([\w\-]+)/$', SepettenUrunSil, name = 'SepettenUrunSil' ),


                        url( r'^sepeteekle/$', SepeteUrunEkle, name = 'SepeteUrunEkle' ), url( r'^sepetim/$', Sepetim, name = 'Sepetim' ),


                        url( r'^ssdegistir/([\w\-]+)/([\w\-]+)/$', SSDegistir ),


                        url( r'^odemeyap/([\w\-]+)/$', OdemeYaptir ), url( r'^op/([\w\-]+)/$', OP ), url( r'^sps/([\w\-]+)/$', SiparisSesliCevap ),

                        url( r'^odemeyiyap/$', TemplateView.as_view( template_name = "odemeyiyap.html" ) ),


                        url( r'^urunv3K/$', urunv3KategoriEkle ), url( r'^urunv3/$', urunv3 ),


                        url( r'^bilgi/$', bilgi ), url( r'^iletisimform/$', iletisimform ),


                        url( r'^siparistamamla/$', SiparisTamamla ), url( r'^siparistamamlandi/$', SiparisTamamlandi ), url( r'^bankaya/([\w\-]+)/$', Bankaya ), url( r'^odemetamamlanamadi/$', OdemeTamamlanamadi ), url( r'^odemetamamlandi/$', OdemeTamamlandi ),


                        url( r'^sipdetay/$', SiparisDetayGoster ),

                        url( r'^dftamamlanamadi/$', DFOdemeYapilamadi ), url( r'^dftamamlandi/$', DFOdemeYapildi ),


                        url( r'^df/$', DFOdemeYap, name = 'DFOdemeYap' ),


                        url( r'^yazdir/([\w\-]+)/$', Yazdir ),

                        url( r'^sk/([\w\-]+)/$', SiparisKontrol ), url( r'^sk2/([\w\-]+)/$', SiparisKontrol2 ), url( r'^sksporla/([\w\-]+)/$', SiparisKontrolSporLA ),


                        url( r'^uyecikisyap/$', UyeCikisYap ), url( r'^uyekayitekle/$', UyeKayitEkle ),

                        url( r'^giris/$', TemplateView.as_view( template_name = "login.html" ) ), url( r'^kayit/$', TemplateView.as_view( template_name = "login.html" ) ),

                        url( r'^uyegirisyap/$', UyeGirisYap ),


                        url( r'^umk/$', UyeKayitliMi_Mail ), url( r'^hesabim/$', Hesabim ),


                        url( r'^kuol/$', KullaniciOlustur ),

                        url( r'^admin/', include( admin.site.urls ) ),


                        url( r'^tuketici-haklari/$', TemplateView.as_view( template_name = "tuketicihaklari.html" ) ), url( r'^tuketici-haklari-iframe/$', TemplateView.as_view( template_name = "tuketici_haklari_iframe.html" ) ), url( r'^odeme-teslimat-sartlari/$', TemplateView.as_view( template_name = "odemeveteslimatsartlari.html" ) ), url( r'^gizlilik-guvenlik/$', TemplateView.as_view( template_name = "gizlilikveguvenlik.html" ) ), url( r'^iade-sartlari/$', TemplateView.as_view( template_name = "degisimiadesartlari.html" ) ), url( r'^garanti-sartlari/$', TemplateView.as_view( template_name = "garantisartlari.html" ) ), url( r'^hakkimizda/$', TemplateView.as_view( template_name = "hakkimizda.html" ) ), url( r'^iletisim/$', TemplateView.as_view( template_name = "iletisim.html" ) ), url( r'^magazalarimiz/$', TemplateView.as_view( template_name = "magazalarimiz.html" ) ), url( r'^sss/$', TemplateView.as_view( template_name = "sss.html" ) ),  # url( r'^sitemap.xml$', TemplateView.as_view( template_name = "sitemap.xml", content_type='text/xml') ),




                        url( r'^robots.txt$', TemplateView.as_view( template_name = "robots.txt", content_type = 'text/plain' ) ),


                        url( r'^tinymce/', include( 'tinymce.urls' ) ), url( r'^chaining/', include( 'smart_selects.urls' ) ),

                        url( r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT, } ),


)

handler500 = curry( server_error, template_name = '500.html' )


