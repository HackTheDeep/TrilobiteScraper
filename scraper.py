import sys
import lxml.html
from lxml.cssselect import CSSSelector
import requests
from io import open as iopen
from urllib.parse import urlsplit


destinationDir = '/tmp/trilobites/'
galleryHost = 'https://www.amnh.org'

urls = [
    'https://www.amnh.org/our-research/paleontology/paleontology-faq/trilobite-website/gallery-of-trilobites/master-gallery-of-all-website-trilobites-a-c',
    'https://www.amnh.org/our-research/paleontology/paleontology-faq/trilobite-website/gallery-of-trilobites/master-gallery-of-all-website-trilobites-d-i',
    'https://www.amnh.org/our-research/paleontology/paleontology-faq/trilobite-website/gallery-of-trilobites/master-gallery-of-all-website-trilobites-j-p',
    'https://www.amnh.org/our-research/paleontology/paleontology-faq/trilobite-website/gallery-of-trilobites/master-gallery-of-all-website-trilobites-q-z'
    ]

sections = []

# Set this if you need to restart from a specific image index after a failed/aborted run
startSectionIndex = 0

# Get all image sections
for url in urls:
    response = requests.get(url)
    if response.status_code != requests.codes.ok:
        print('=====> FAILED WITH STATUS ' + str(response.status_code) + ':  ' + url)
        exit()

    dom = lxml.html.fromstring(response.text)
    # imageDownloadLinks = CSSSelector('a.fullscreen-link')(dom)
    sections = sections + CSSSelector('div.clearfix div.content')(dom)

print('FOUND ' + str(len(sections)) + ' TRILOBITES...\n\n')

# Parse each section to download image
for idx, section in enumerate(sections):
    if idx < startSectionIndex:
        continue

    # Get trilobite name from header
    trilobiteName = 'NO_NAME'
    headers = CSSSelector('h1')(section)
    if headers:
        trilobiteNameText = headers[0].text
        if trilobiteNameText:
           trilobiteName = trilobiteNameText.strip(' \r\n').replace(' ', '_')

    # Get full size image download link
    downloadRelativePath = CSSSelector('a.fullscreen-link')(section)[0].get('href')
    downloadUrl = galleryHost + downloadRelativePath

    # Get rando image ID
    pathTokens = downloadRelativePath.split('/')
    imageId = pathTokens[-2] + '_' + pathTokens[-1]

    # Download image
    fileData = requests.get(downloadUrl)

    if fileData.status_code != requests.codes.ok:
        print('=====> ' + imageId + '-' + trilobiteName + ' FAILED WITH STATUS ' + str(fileData.status_code) + ':  ' + downloadUrl + '\n')
        continue

    # Save image to disk
    destinationFilePath = destinationDir + imageId + '-' + trilobiteName + '.jpg'

    with iopen(destinationFilePath, 'wb') as file:
        file.write(fileData.content)

    print(str(idx) + ' - ' + trilobiteName + ' - ' + downloadUrl)

