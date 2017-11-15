import requests
import json
from bs4 import BeautifulSoup as bs
import datetime
import urllib

url_base = "https://www.dhgate.com/wholesale/business-industrial/c011"

product_columns = ['item_code', 'product_name', 'category', 'description', 'quantity',
                    'package_size', 'gross_weight', 'image_url']
price_columns = ['quantity','price']

price_id = 1
end = False

def getImageURL(item):
    imageTag = item.select("img")

    # if imageTag is not empty
    if imageTag:
        imageTag[0] = imageTag[0]['src']
    else:
        imageTag.append(item.select(".photo")[0].find('a')['lazyload-src'])
    
    return imageTag[0]

def productInsertSQL(value_list):

    text_file.write('INSERT INTO CheapHerder_product (')
    str = ''
    for elem in product_columns:
        if str != '':
            str = str + ', ' + elem
        else:
            str = elem

    str = str + ')'
    text_file.write(str)

    text_file.write(' values (')
    for idx, val in enumerate(value_list):
        if idx != 0:
            text_file.write(', ')
        text_file.write("\'")
        text_file.write(val)
        text_file.write("\'")

    text_file.write(');')
    text_file.write('\n')


def priceInsertSQL(wprice, item_code):

    # product amount and the price
    for w in wprice:
        quantity = str(w['nums'])
        price  = w['price']
        quantity = quantity.split( )[0]
        
        global price_id

        price_insert = 'INSERT INTO CheapHerder_price ( price_id, quantity, price ) values ( ' + str(price_id) + ', ' + str(quantity) + ', ' + str(price) + ' );\n'
        product_price_insert = 'INSERT INTO CheapHerder_product_price ( item_code, price_id ) values ( ' + '\'' + str(item_code) + '\'' + ', ' + str(price_id) + ' );\n'
        price_id = price_id + 1

        text_file.write(price_insert)
        text_file.write(product_price_insert)
   


def getProductInfo(url):
    print("getting product info for url " + url)

    res = requests.get(url)

    soup = bs(res.text,"html.parser")

    value_list = []
    description_list = soup.select(".description")[0].find_all("li")
    # item_code
    item_code = (list)(description_list[1].strings)[1]
    value_list.append(item_code)
    # product_name
    value_list.append( (list)(description_list[0].strings)[1].encode("ascii", errors="ignore").decode())
    # category
    value_list.append((list)(description_list[2].strings)[1])
    # description
    value_list.append((list)(description_list[3].strings)[1].encode("ascii", errors="ignore").decode())
    # quantity
    quantity = (list)(description_list[4].strings)[1].encode("ascii", errors="ignore").decode().strip()
    value_list.append(quantity)
    # package_size
    value_list.append( (list)(description_list[5].strings)[1])
    # gross_weight
    value_list.append((list)(description_list[6].strings)[1])
    # image_url
    image_url = "http:" + soup.select(".photo-tour")[0].find('img')['src']
    value_list.append(image_url)

    productInsertSQL(value_list)

    wprice = soup.select(".wprice-line")[0].select(".js-wholesale-list")[0].find_all('li')   
    priceInsertSQL(wprice,item_code)





''' main '''

start_time  = datetime.datetime.now()
filename = 'dhgate/dhgateproducts_'+ start_time.strftime("%Y-%m-%d %H:%M") +'.txt'
text_file = open(filename, 'w')

i=0
while (end==False or i <2100 ):

    if i!=0:
        url = url_base + "-" + '{}'.format(i)
    else:
        url = url_base

    url = url + ".html"

    try:
        res = requests.get(url)

        print("retrieving products from page number: " + str(i+1))

        soup = bs(res.text,"html.parser")
        listitem = soup.find_all("div",class_="listitem")
        for idx, item in enumerate(listitem):
            
            # the rest of items are advertisements
            if idx == 24:
                break
            
            # request to product info
            productURL = "http:" + item.select(".pro-title")[0].find('a').get('href')
            getProductInfo(productURL)

        i = i+1

    except URLError as e:
	    print ('Got an error code:',e)
	    end = True

text_file.close()
end_time = datetime.datetime.now()
print('donee!!!')
print('It takes '+str(end_time-start_time))
print('finished with ' + str((i)*24) + 'products')
