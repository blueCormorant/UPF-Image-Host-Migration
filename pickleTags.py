import pickle
import pycountry

tags = {
	"Africa Day" : "africaday",
	"Ambassador for Peace" : "afp",
	"Ambassadors for Peace" : "afp",
	"American Clergy Leadership Conference" : "aclc",
	"American Leadership Conference" : "alc",
	"Balkans" : "balkans",
	"Global Day of Parents" : "gdp",
	"International Association of Parlimentarians for Peace" : "iapp",
	"International Day of Families" : "idp",
	"International Day of Peace" : "idp",
	"International Leadership Conference" : "ilc",
	"International Women's Day" : "iwd",
	"International Womens Day" : "iwd",
	"International Women Day" : "iwd",
	"International Women Day" : "iwd",
	"International Year of the Family" : "internationalyearofthefamily",
	"Interreligious Association for Peace and Development" : "iapd",
	"Intereligious Association for Peace and Development" : "iapd",
	"Interreligious Leadership Conference" : "irlc",
	"Intereligious Leadership Conference" : "irlc",
	"Peace Road" : "peaceroad",
	"Religious Youth Service" : "rys",
	"Sunhak" : "sunhakpeaceprize",
	"Sustainable Development" : "sdg",
	"Washington Times" : "washingtontimes",
	"Women's Federation for World Peace" : "wfwp",
	"Womens Federation for World Peace" : "wfwp",
	"Women Federation for World Peace" : "wfwp",
	"World Summit" : "worldsummit",
	"Ivory Coast" : "IvoryCoast",
	"IvoryCoast" : "IvoryCoast",
	"ivorycoast" : "IvoryCoast",
	"ivory coast" : "IvoryCoast",
}

replacements = {
	"Russian Federation" : "Russia",
	"Lao People's Democratic Republic" : "Laos",
	"Palestine, State of" : "Palestine",
	"Syrian Arab Republic" : "Syria"
}


for country in pycountry.countries:

	shortestName = country.name

	names = []

	try:
		names.append(country.official_name)
		shortestName = country.official_name
	except AttributeError:
		pass

	try:
		names.append(country.common_name)
		if len(country.common_name) < len(shortestName):
			shortestName = country.common_name
	except AttributeError:
		pass

	try:
		names.append(country.name)
		if len(country.name) < len(shortestName):
			shortestName = country.name
	except AttributeError:
		pass

	for key in replacements:
		if shortestName == key:
			shortestName = replacements[key]

	for name in names:
		tags[name] = shortestName



'''
with open("tags.pickle", "wb") as _file:
	pickle.dump(tags, _file)


'''
with open("tags.pickle", "rb") as _file:
	tags = pickle.load(_file)
	for key in tags:
		print(key, " : ", tags[key])

