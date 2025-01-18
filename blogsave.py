import json
import requests
from urllib.parse import urlencode
import os
from bs4 import BeautifulSoup

def blogsave(main_folder, arti_code):
    # set the save path of member
    mb_main_folder = f"{main_folder}/{arti_code}"
    os.makedirs(mb_main_folder, exist_ok=True)

    # base blog api
    base_url = "https://www.nogizaka46.com"
    blog_api = "/s/n46/api/list/blog"
    url_params = {
        "st": 0,
        "ct": arti_code
    }
    blog_url = f"{base_url}{blog_api}?{urlencode(url_params)}"

    # initial request
    res = requests.get(blog_url)
    resContent = res.content.decode("utf-8").lstrip("\'res(").rstrip(");\'")
    blogJSON = json.loads(resContent)
    print(f"{blogJSON['count']} blogs to save...")

    # check the total blog numbers and get all blogs
    if int(blogJSON['count']) > 100:
        for i in range(100, int(blogJSON['count']), 100):
            exurl_params = {
                "st": i,
                "ct": arti_code
            }
            exblog_url = f"{base_url}{blog_api}?{urlencode(exurl_params)}"
            exres = requests.get(exblog_url)
            exresContent = exres.content.decode("utf-8").lstrip("\'res(").rstrip(");\'")
            exblogJSON = json.loads(exresContent)
            for blog in exblogJSON['data']:
                blogJSON['data'].append(blog)

    # process blog by blog
    for idx, blog in enumerate(blogJSON['data']):

        # create the folder inside the member save path
        blog_folder = f"{mb_main_folder}/{blog['code']}"
        os.makedirs(blog_folder, exist_ok=True)

        # create a json file of the blog json
        with open(f"{blog_folder}/{blog['code']}.json", "w", encoding="utf-8") as f:
            json.dump(blog, f, ensure_ascii=False, indent=4)

        # process text(html) and save the images
        soup = BeautifulSoup(blog['text'], 'html.parser')
        img_tags = soup.find_all('img')
        for img_tag in img_tags:
            if img_tag.get('src') == None:
                continue
            elif not img_tag.get('src').startswith('http'):
                img_url = f"{base_url}{img_tag.get('src')}"
            else:
                img_url = img_tag.get('src')
            file_name = img_url.split("/")[-1]
            img_response=requests.get(img_url)
            with open(f"{blog_folder}/{file_name}", 'wb') as f:
                f.write(img_response.content)
            # replacing the img src with file name only
            img_tag['src'] = file_name

        # create a html file of the blog
        with open(f"{blog_folder}/{blog['code']}.html", "w", encoding="utf-8") as f:
            f.write(str(soup))

        # Done
        print(f"Blog {idx + 1} ID: {blog['code']} saved!")

main_folder = f"{os.getenv("HOME")}/Downloads/blogsave" # replace with the path that you want to save the blog files
arti_code = 40004 # replace with the code of the member that you want to save, you may find the code inside mb.txt

blogsave(main_folder, arti_code)
