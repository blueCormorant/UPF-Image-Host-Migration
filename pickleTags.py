import pickle

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
	"World Summit" : "worldsummit"
}

with open("tags.pickle", "wb") as _file:
	pickle.dump(tags, _file)

'''
with open("tags.pickle", "rb") as _file:
	print(pickle.load(_file))
'''
