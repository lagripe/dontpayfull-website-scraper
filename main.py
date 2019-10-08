import requests,bs4,re,json,fake_useragent
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random as rd


# ------- Change HERE ------------
configPath = 'app-cb48d-firebase-adminsdk-dhvhk-f28c82a462.json'
pushlinksPath = 'pushlinks.json'
collection = 'StoresCollection'
pushlink_table = 'pushlink_collection'
minRandom = 120
maxRandom = 670
headers = {'User-Agent':'Mozilla/7.0 (Windows NT 5; Win64; x32) AppleWebKit/528.36 (KHTML, like Gecko) Chrome/76.0.3865.90 Safari/544.36'}
# --------------------------------


def getSiteMapLetterPagination(letter):
    req = requests.get('https://www.dontpayfull.com/sitemap/{}'.format(letter),headers=headers)
    parser = bs4.BeautifulSoup(req.content,"html.parser")
    print(req.content)
    return len(parser.find_all('ul',attrs={'class':'pagination'})[1].findChildren('a'))

def getStoresByLetter(letter):
    pageCount = getSiteMapLetterPagination(letter)
    urlLetter = 'https://www.dontpayfull.com/sitemap/{}'.format(letter)
    stores = []
    for i in range(1,pageCount + 1):    
        req = requests.get(urlLetter+'/page/{}'.format(i),headers=headers)
        print(req.url)
        parser = bs4.BeautifulSoup(req.content,"html.parser")
        stores = stores + ['https://www.dontpayfull.com'+store.findChild('a')['href'] \
                            for store in parser.find('div',attrs={'class':'col-xs-12 sitemap page'})\
                                               .find_all('div',attrs={'class':'col-md-3 col-xs-6'})
                            ]


def getStores():
    for i in range(65,97):
        getStoresByLetter(chr(i))


getStores()


def getStoreCoupons(store_url,store_name):
    req = requests.get(store_url,headers=headers)
    parser = bs4.BeautifulSoup(req.content,"html.parser")
    
    print('- - - - - - - - - Deleting old data and pushing new ones - - - - - - - - - ')
    deleteCollectionDocs(collection)
    #Upload pushlinks
    
    print('- - - - - - - - - Getting Codes - - - - - - - - - ')

    #Get Codes 
    for i,coupon in enumerate(parser.find_all('li',attrs={'class':'obox code clearfix'})):
        code,title =getCouponCode(coupon['id'])
    #Get Deals 
    
    print('- - - - - - - - - Getting Deals - - - - - - - - - ')
    for i,coupon in enumerate(parser.find_all('li',attrs={'class':'obox deal clearfix'})):
        url_link,title = getCouponDeals(coupon['id'])
    
def getCouponCode(code):
    req = requests.get('https://www.dontpayfull.com/coupons/getcoupon/?id={}'.format(code))
    parser = bs4.BeautifulSoup(req.content,"html.parser")
    title = re.sub(r'[\n\t]+','',parser.find('h4').text)
    code = parser.find('input')['value']
    print('{} - - - > {}'.format(title,code))
    return code,title
def getCouponDeals(code):
    req = requests.get('https://www.dontpayfull.com/coupons/getcoupon/?id={}'.format(code))
    parser = bs4.BeautifulSoup(req.content,"html.parser")
    title = re.sub(r'[\n\t]+','',parser.find('h4').text)
    url_link = requests.get('https://dontpayfull.com/hop/coupon/{}?p=1&s=popup'.format(code)).url
    print('{} - - - > {}'.format(title,url_link))
    return url_link,title
def deleteCollectionDocs(collection):
    # Delete old documents
    users_ref = db.collection(collection)
    docs = users_ref.get()
    for doc in docs:
        doc.reference.delete()
def deletePushlink():
    # Delete old documents
    users_ref = db.collection(pushlink_table)
    docs = users_ref.get()
    for doc in docs:
        doc.reference.delete()
def insertCodes(collection,title,code,store_name):
    views = rd.Random().randint(minRandom,maxRandom)
    data = {
        'title':title,
        'coupon':code, 
        'store_name':store_name,
        'store_key':str(store_name[0]).upper(),
        'full_store_key':str(store_name).upper(),  
        'views':views,
        'likes':rd.Random().randint(views,maxRandom)
        }
    
    doc_ref = db.collection(collection).document()
    doc_ref.set(data)
def insertDeals(collection,title,link,store_name):
    views = rd.Random().randint(minRandom,maxRandom)
    data = {
            
        'title':title,
        'link':link,
        'store_name':store_name,
        'store_key':str(store_name[0]).upper(),  
        'full_store_key':str(store_name).upper(),  
        'views':views,
        'likes':rd.Random().randint(views,maxRandom)
        }
    doc_ref = db.collection(collection).document()
    doc_ref.set(data)
def uploadPushlinks():
    pushlinksData = []
    with open(pushlinksPath,'r') as file:
        pushlinksData = json.loads(file.read())['pushlinks']
    for id,data in enumerate(pushlinksData):
        doc_ref = db.collection(pushlink_table).document(str(id))
        doc_ref.set(data)

cred = credentials.Certificate(configPath)
firebase_admin.initialize_app(cred)
db = firestore.client()

