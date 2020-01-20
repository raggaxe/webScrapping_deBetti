from bs4 import BeautifulSoup
import requests
import datetime
import csv


def list_content(url, paginas):
    data = []
    pages = []
    filename = "./uploads/debetti " + datetime.datetime.now().strftime("%d-%m-%Y-%H-%M") + ".csv"
    with open(filename, "w+") as f:
        writer = csv.writer(f)
        writer.writerow(["ITEM", "FOTO","TIPO PRECO", "PRECO", "DATA"])

    paginas = paginas + 1
    for i in range(1, paginas):
        urlpass = url + '?page='+ str(i)
        pages.append(urlpass)


    for page in pages:
        source = requests.get(page).text
        page_soup = BeautifulSoup(source, features="lxml")
        containers = page_soup.find_all("div", {"class": "grid grid--no-gutters grid--uniform"})
        # containers = page_soup.find_all("div", {"class": "page-width"})
        print(page)
        for container in containers:
            try:
                card = container.find_all("a", {"class": "product-card"})
                for produtos in card:
                    picture = produtos.find("img").get('src')
                    name = produtos.find("div", {"class": "product-card__name"}).text
                    print(name)
                    if produtos.find("span", {"class": "visually-hidden"}) in card:
                        type = produtos.find("span", {"class": "visually-hidden"})
                    else:
                        type = 'Preço normal'
                    print(type)
                    preco = container.find("div", {"class": "product-card__price"}).text.replace(type,'').strip()
                    print(preco)
                    foto = str('https:'+picture)
                    scrapping = ({
                        "nome" : name,
                        "foto" : foto,
                        "tipo": type,
                         "preco": preco,
                        'data': datetime.datetime.now().strftime("%d-%m-%Y às %H:%M")
                    })
                    data.append(scrapping)

                    with open(filename, "a") as f:
                        writer = csv.writer(f)
                        writer.writerow([name, foto, type,preco, datetime.datetime.now().strftime("%d-%m-%Y às %H:%M")])
                return data , filename
            except AttributeError or IndexError:
                print("Não Funcionou")
















