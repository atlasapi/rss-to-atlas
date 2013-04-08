#! /usr/bin/env python
import feedparser
import simplejson as json
import optparse
import urllib2
import urllib

publisher = {
    'key': 'sverigesradio.se',
    'name': 'Sveriges Radio',
    'country': 'ALL'
}

def extractBrand(feedContents, mediaType):
    brand = feedContents.feed
    content = {}
    content["title"] = brand.title
    content["description"] = brand.summary 
    content["media_type"] = mediaType
    content["image"] = brand.image.href
    content["uri"] = brand.link
    content["type"] = "brand"
    content["publisher"] = publisher
    return content

def extractEpisode(episode, brand, mediaType):
    content = {}
    content["title"] = episode.title
    content["description"] = episode.summary
    content["media_type"] = mediaType
    content["image"] = brand["image"]
    content["uri"] = episode.link
    content["type"] = "episode"
    content["publisher"] = publisher
    content["container"] = {"uri": brand["uri"]}
    locations = []
    for enclosure in episode.enclosures:
    	location = {
    	    "transport_type": "link",
    	    "uri" : enclosure.href,
    	    "available": True
        }
        locations.append(location)
    content["locations"] = locations
    return content

def postToAtlas(item, apiKey, useStage):
    headers = {'Content-Type': 'application/json'}
    subdomain = ""
    if (useStage):
	subdomain = "stage."
    atlasUrl = "http://%satlas.metabroadcast.com/3.0/content.json?apiKey=%s" % (subdomain, apiKey)
    itemJson = json.dumps(item, indent=4 * ' ')
    print atlasUrl
    print itemJson
    try:
	postReq = urllib2.Request(atlasUrl, itemJson, headers)
	postResponse = urllib2.urlopen(postReq)
	print postResponse.getcode()
	print postResponse.info()
	print postResponse.read()
    except urllib2.HTTPError as e:
	print e


def uploadFeed(feedUrl, mediaType, apiKey, useStage):
	content = feedparser.parse(feedUrl)
	brand = extractBrand(content, mediaType)
	postToAtlas(brand, apiKey, useStage)
	for entry in content.entries:
	   episode = extractEpisode(entry, brand, mediaType)
	   postToAtlas(episode, apiKey, useStage)

usage = "usage: %prog [options] feed_url"
desc="Uploads the contents of an RSS or Atom feed to Atlas."
parser = optparse.OptionParser(usage=usage, description=desc)
parser.add_option("-k", "--apiKey", help="Your Atlas API Key", dest="api_key", default="")
parser.add_option("-t", "--type", help="Media type. Should be audio or video.", dest="type", default="video")
parser.add_option("-s", "--useStage", help="If set then use stage atlas rather than production atlas", default=False, dest="useStage", action="store_true")

(opts, args) = parser.parse_args()
uploadFeed(args[0], opts.type, opts.api_key, opts.useStage)
