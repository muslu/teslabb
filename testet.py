# -*- coding: utf-8 -*-


Listem = ()

with open( "/home/muslu/arananlar.txt" ) as DosyaOku:
	Icerik = DosyaOku.read( ).split( )

	for i in Icerik:

		Listem.append( i )

