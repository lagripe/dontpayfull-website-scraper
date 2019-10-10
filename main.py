import requests,bs4,re,json,fake_useragent,time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random as rd


# ------- Change HERE ------------
configPath = 'app-cb48d-firebase-adminsdk-dhvhk-f28c82a462.json'
pushlinksPath = 'pushlinks.json'
collection = 'Stores'
pushlink_table = 'pushlink_collection'
minRandom = 120
maxRandom = 670
headers = {
    'Upgrade-Insecure-Requests':'1',
    'Sec-Fetch-Mode':'navigate',
    'Sec-Fetch-User':'?1',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'User-Agent':'Mozilla/6.0 (Windows NT 5; Win64; x32) AppleWebKit/528.36 (KHTML, like Gecko) Chrome/76.5.3865.90 Safari/544.36'}
# --------------------------------


def getSiteMapLetterPagination(letter):
    req = requests.get('https://www.dontpayfull.com/sitemap/{}'.format(letter),headers=headers)
    parser = bs4.BeautifulSoup(req.content,"html.parser")
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
    getCouponsByLetter(stores)
    time.sleep(secs=30)
def getStores():
    print('- - - - - - - - - Deleting old data and pushing new ones - - - - - - - - - ')
    deleteCollectionDocs(collection)
    for i in range(65,97):
        getStoresByLetter(chr(i))

def getCouponsByLetter(stores):
    for store_url in stores:
        getStoreCoupons(store_url)

def getStoreCoupons(store_url):
    req = requests.get(store_url,headers=headers)
    parser = bs4.BeautifulSoup(req.content,"html.parser")
    store_name = parser.find('div',attrs={'class':'store-title clearfix'}).findChild('h1').findChild('strong').text
    image_url = store_url.split('/')[-1]
    print('Store name ---> {}'.format(store_name))
    #Upload pushlinks
    
    print('- - - - - - - - - Getting Codes - - - - - - - - - ')
    #Get Codes 
    for coupon in parser.find_all('li',attrs={'class':'obox code clearfix'}):
        code,title =getCouponCode(coupon['id'])
        insertCodes(collection,title,code,store_name,image_url)
    
    #Get Deals 
    print('- - - - - - - - - Getting Deals - - - - - - - - - ')
    for coupon in parser.find_all('li',attrs={'class':'obox deal clearfix'}):
        url_link,title = getCouponDeals(coupon['id'])
        insertDeals(collection,title,url_link,store_name,image_url)
    
def getCouponCode(code):
    req = requests.get('https://www.dontpayfull.com/coupons/getcoupon/?id={}'.format(code))
    parser = bs4.BeautifulSoup(req.content,"html.parser")
    title = re.sub(r'[\n\tÂ]+','',parser.find('h4').text)
    code = parser.find('input')['value']
    print('{} - - - > {}'.format(title,code))
    return code,title
def getCouponDeals(code):
    req = requests.get('https://www.dontpayfull.com/coupons/getcoupon/?id={}'.format(code))
    parser = bs4.BeautifulSoup(req.content,"html.parser")
    title = re.sub(r'[\n\tÂ]+','',parser.find('h4').text)
    url_link = requests.get('https://dontpayfull.com/hop/coupon/{}?p=1&s=popup'.format(code),headers=headers).url
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
def insertCodes(collection,title,code,store_name,image_url):
    views = rd.Random().randint(minRandom,maxRandom)
    dataStore={
        'image':image_url,
        'store_name':store_name,
        'store_key':str(store_name[0]).upper(),
        'full_store_key':str(store_name).upper()
    }
    data = {
        'title':title,
        'coupon':code, 
        'views':views,
        'likes':rd.Random().randint(minRandom,views)
        }
    store_ref  = db.collection(collection).document(store_name)
    store_ref.set(dataStore)
    doc_ref = store_ref.collection('codes').document()
    doc_ref.set(data)
def insertDeals(collection,title,link,store_name,image_url):
    views = rd.Random().randint(minRandom,maxRandom)
    dataStore={
        'image':image_url,
        'store_name':store_name,
        'store_key':str(store_name[0]).upper(),
        'full_store_key':str(store_name).upper()
    }
    data = {
            
        'title':title,
        'link':link,
        'views':views,
        'likes':rd.Random().randint(minRandom,views)
        }
    store_ref  = db.collection(collection).document(store_name)
    store_ref.set(dataStore)
    doc_ref = store_ref.collection('deals').document()
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

getStores()
