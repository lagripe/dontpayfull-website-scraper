import requests,bs4,re,json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random as rd
'''
def getSiteMapLetterPagination(letter):
    req = requests.get('https://www.dontpayfull.com/sitemap/{}'.format(letter))
    parser = bs4.BeautifulSoup(req.content,"html.parser")
    return len(parser.find_all('ul',attrs={'class':'pagination'})[1].findChildren('a'))

def getStoresByLetter(letter):
    pageCount = getSiteMapLetterPagination(letter)
    print(pageCount)
    urlLetter = 'https://www.dontpayfull.com/sitemap/{}'.format(letter)
    for i in range(1,pageCount + 1):    
'''





# ------- Change HERE ------------
configPath = 'app-py-e36d6-firebase-adminsdk-7ik7w-49cb3022e9.json'
pushlinksPath = 'pushlinks.json'
codes_table = 'codes_collection'
deals_table = 'deals_collection'
pushlink_table = 'pushlink_collection'
minRandom = 120
maxRandom = 670
rxid = 'yacine'
store_name = 'https://www.dontpayfull.com/at/redbubble.com'
# --------------------------------

def getStoreCoupons(store_url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    req = requests.get(store_url,headers=headers)
    parser = bs4.BeautifulSoup(req.content,"html.parser")
    
    print('- - - - - - - - - Deleting old data and pushing new ones - - - - - - - - - ')
    deleteCollectionDocs(codes_table)
    deleteCollectionDocs(deals_table)
    #Upload pushlinks
    deletePushlink()
    uploadPushlinks()
    
    print('- - - - - - - - - Getting Codes - - - - - - - - - ')

    #Get Codes 
    for i,coupon in enumerate(parser.find_all('li',attrs={'class':'obox code clearfix'})):
        code,title =getCouponCode(coupon['id'])
        insertCodes(codes_table,title,code,i)
    #Get Deals 
    
    print('- - - - - - - - - Getting Deals - - - - - - - - - ')
    for i,coupon in enumerate(parser.find_all('li',attrs={'class':'obox deal clearfix'})):
        url_link,title = getCouponDeals(coupon['id'])
        insertDeals(deals_table,title,url_link,i)
    
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
def insertCodes(collection,title,code,id):
    data = {
            'rxid':rxid,
            'coupon':code,
            'title':title,
            'views':str(rd.Random().randint(minRandom,maxRandom)),
            'likes':str(rd.Random().randint(minRandom,maxRandom)),
            'shares':str(rd.Random().randint(minRandom,maxRandom))
        }
    
    doc_ref = db.collection(collection).document(str(id))
    doc_ref.set(data)
def insertDeals(collection,title,link,id):
    data = {
            'link':link,
            'title':title,
            'views':str(rd.Random().randint(minRandom,maxRandom)),
            'likes':str(rd.Random().randint(minRandom,maxRandom)),
            'shares':str(rd.Random().randint(minRandom,maxRandom))
        }
    doc_ref = db.collection(collection).document(str(id))
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

getStoreCoupons(store_name)