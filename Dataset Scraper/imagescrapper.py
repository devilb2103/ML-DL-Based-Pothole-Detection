import base64
import os
import requests
from bs4 import BeautifulSoup
paths = ['Dataset', 'Dataset/Pothole','Dataset/Plain']

def main():
    for i in paths:
        if not os.path.exists(i):
            os.mkdir(i)
    download_images(1000)

def loadConfig():
    with open("./config.json", "r") as cfg:
        return eval(cfg.read())

def writeConfig(plain_count, pothole_count):
    data = loadConfig()
    data["plain"] = plain_count
    data["pothole"] = pothole_count
    with open("./config.json", "w+") as cfg:
        cfg.write(str(data).replace("'", '"'))


def getPageDumpData(imageType: bool) -> str:
    if(imageType):
        with open("./pothole_website_scraped.txt", "r", encoding="utf-8") as file:
            data = file.read()
            return data
    else:
        with open("./plain_road_website_scraped.txt", "r", encoding="utf-8") as file:
            data = file.read()
            return data

def download_images(num_images = 9999999):
    print('Start downloading...')

    cfg = loadConfig()
    keys = ["plain", "pothole"]
    found_image_count = [0,0]
    scraped_count = [cfg[keys[1]], cfg[keys[0]]]
    
    scrapedImages = [getPageDumpData(True), getPageDumpData(False)]
    for i in range(len(scrapedImages)):
        b_soup = BeautifulSoup(scrapedImages[i], 'html.parser')
        results = b_soup.findAll('img', {'class': 'rg_i Q4LuWd'})
        count = 0
        
        imagelinks = []
        for res in results:
            try:
                link = res['src']
                imagelinks.append(link)
                count = count + 1
                if count >= num_images:
                    break
            except KeyError:
                continue
        
        found_image_count[i] = count
        
        print(f'Found {len(imagelinks)} images')
        try:
            for imageNum, imagelink in enumerate(imagelinks):

                if(imageNum <= scraped_count[i]):
                    continue

                if("base64" not in imagelink):
                    response = requests.get(imagelink)
                    imagename = paths[i+1] + '/' + str(imageNum) + '.jpg'
                    with open(imagename, 'wb') as file:
                        file.write(response.content)
                    scraped_count[i] += 1
                else:
                    type, base64_data = imagelink.split(",")
                    image_data = base64.b64decode(base64_data)
                    imagename = paths[i+1] + '/' + str(imageNum) + '.jpg'
                    with open(imagename, 'wb') as file:
                        file.write(image_data)
                    scraped_count[i] += 1
        except Exception:
            writeConfig(scraped_count[1], scraped_count[0])
            

    print('Download Completed!')

if __name__ == '__main__':
    main()