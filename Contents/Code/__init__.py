# -*- coding: utf-8 -*-
import base64, datetime, time

####################################################################################################
# Author 		: GuinuX
####################################################################################################
# Contributeur  : Macgate
####################################################################################################

PREFIX = "/video/W9Replay"
NAME   = "W9 Replay"
ART    = "art-default.jpg"
ICON   = "icon-default.png"

CATALOG_KEY = "ElFsg.Ot"
CONFIGURATION_URL = "http://www.w9replay.fr/files/w9configuration_lv3.xml?t=1"

####################################################################################################

def Start():

	Plugin.AddPrefixHandler(PREFIX, VideoMainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup("Coverflow", viewMode="Coverflow", mediaType="items")
	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")

	MediaContainer.art = R(ART)
	MediaContainer.title1 = NAME
	DirectoryItem.thumb = R(ICON)
	HTTP.CacheTime = CACHE_1HOUR
	
	Dict['CATALOG_XML'] = ''
	Dict['IMAGES_SERVER'] = ''


def VideoMainMenu():

	dir = MediaContainer(viewGroup="Coverflow")
	try:
		xml = HTTP.Request(CONFIGURATION_URL).content
	except Ex.HTTPError, e:
		Log(NAME + " Plugin : " + str(e))
		return MessageContainer(NAME, "Erreur lors de la récupération de la configuration.")
	except Exception, e :
		Log(NAME + " Plugin : " + str(e))
		return MessageContainer(NAME, "Erreur lors de la récupération de la configuration.")

	Dict['IMAGES_SERVER'] = XML.ElementFromString( xml ).xpath("/config/path/image")[0].text
	CatalogueURL = XML.ElementFromString( xml ).xpath("/config/services/service[@name='GetCatalogueService']/url")[0].text
	CatalogueURL = CatalogueURL.replace("-9.xml","-w9.xml")

	try:
		Dict['CATALOG_XML'] = HTTP.Request(CatalogueURL,cacheTime=CACHE_1HOUR).content
	except Ex.HTTPError, e:
		Log(NAME + " Plugin : " + str(e))
		return MessageContainer(NAME, "Erreur lors de la récupération du Catalogue.")
	except Exception, e :
		Log(NAME + " Plugin : " + str(e))
		return MessageContainer(NAME, "Erreur lors de la récupération du Catalogue.")


	if Dict['CATALOG_XML'].find( "<template_exchange_WEB>" ) == -1: return MessageContainer(NAME, "Flux XML non valide.")

	finXML = Dict['CATALOG_XML'].find( "</template_exchange_WEB>" ) + len( "</template_exchange_WEB>" )
	Dict['CATALOG_XML'] = Dict['CATALOG_XML'][ : finXML ]

	for category in XML.ElementFromString(Dict['CATALOG_XML']).xpath("//template_exchange_WEB/categorie"):
		nom = category.xpath("./nom")[0].text
		image = Dict['IMAGES_SERVER'] + category.get('big_img_url')
		idCategorie = category.get('id')
		dir.Append(Function(DirectoryItem(ListShows, title = nom, thumb = image), idCategorie = idCategorie, nomCategorie = nom))

	return dir


def ListShows(sender, idCategorie, nomCategorie):
	dir = MediaContainer(viewGroup="Coverflow", title1 = NAME, title2 = nomCategorie)
	search = "/template_exchange_WEB/categorie[@id='" + idCategorie + "']/categorie"

	for item in XML.ElementFromString(Dict['CATALOG_XML']).xpath(search):
		nom = item.xpath("nom")[0].text
		image = Dict['IMAGES_SERVER'] + item.get('big_img_url')
		idCategorie = item.get('id')

		dir.Append(Function(DirectoryItem(ListEpisodes, title = nom, thumb = image), idCategorie = idCategorie, nomCategorie = nom))

	return dir


def ListEpisodes(sender, idCategorie, nomCategorie):
	dir = MediaContainer(viewGroup="InfoList", title1 = NAME, title2 = nomCategorie)
	search = "//template_exchange_WEB/categorie/categorie[@id=" + idCategorie + "]/produit"

	for episode in XML.ElementFromString(Dict['CATALOG_XML']).xpath(search):
		idProduit = episode.get('id')
		nom = episode.xpath("./nom")[0].text
		description = episode.xpath("./resume")[0].text
		image = Dict['IMAGES_SERVER'] + episode.get('big_img_url')
		video = episode.xpath("./fichemedia")[0].get('video_url')[:-4]
		date_diffusion = episode.xpath("./diffusion")[0].get('date').replace(" "," à ")
		str_duree = episode.xpath("./fichemedia")[0].get('duree')
		duree = long(str_duree) / 60
		dureevideo = long(str_duree)*1000
		description = description + '\n\nDiffusé le ' + date_diffusion + '\n' + 'Durée : ' + str(duree) + ' mn'
		lienValide = "rtmp://m6dev.fcod.llnwd.net:443/a3100/d1/"
		dir.Append(RTMPVideoItem(url = lienValide, width=640, height=375, clip = video, title = nom, subtitle = nomCategorie, summary = description, duration = dureevideo , thumb = image))
	return dir
