from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/api', methods=['POST'])
def scrape():
    page_num = request.form.get('page_num')

    base_url = "https://nl.trustpilot.com"
    url = f"https://nl.trustpilot.com/categories/beauty_wellbeing?page={page_num}&sort=reviews_count&fbclid=IwAR2g_Ot3W0jlCMNijbTklfO68M8tHnDdvK6G4BWUco4W2l9jbQmQc7c1134"

    data = []
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract specific elements from the HTML
        # Find all <a> tags with name attribute set to 'business-unit-card'
        links = soup.find_all("a", attrs={"name": "business-unit-card"})
        count = 1
        for link in links:
            link_url = link.get("href")
            # Send a GET request to the extracted link
            link_response = requests.get(base_url + link_url)

            
            if link_response.status_code == 200:
                print(count)
                # Parse the HTML content of the link
                link_soup = BeautifulSoup(link_response.content, "html.parser")

                company_name = link_soup.find("span", class_="typography_display-s__qOjh6 typography_appearance-default__AAY17 title_displayName__TtDDM")
                website = link_soup.find("a", class_="link_internal__7XN06 link_wrapper__5ZJEx")
                # telephone = link_soup.find("a", class_="link_internal__7XN06 typography_body-m__xgxZ_ typography_appearance-action__9NNRY link_link__IZzHN link_underlined__OXYVM")
                number_of_reviews = link_soup.find("p", class_="typography_body-l__KUYFJ typography_appearance-default__AAY17")
                # address = link_soup.find("ul", class_="typography_body-m__xgxZ_ typography_appearance-default__AAY17 styles_contactInfoAddressList__RxiJI").find_all("li")
                # email = link_soup.find("a", class_="link_internal__7XN06 typography_body-m__xgxZ_ typography_appearance-action__9NNRY link_link__IZzHN link_underlined__OXYVM")
                card_sections = link_soup.find_all('div', class_='card_cardContent__sFUOe')
                contact_section = None

                for card_section in card_sections:
                    has_contacts_heading = card_section.find('h4', string='Contact')

                    if has_contacts_heading:
                        contact_section = card_section
                        break

                if contact_section:
                    telephone = contact_section.find('a', href=lambda href: href and href.startswith('tel:'))
                    address = contact_section.find('ul', class_="styles_contactInfoAddressList__RxiJI").find_all('li')
                    email = contact_section.find('a', href=lambda href: href and href.startswith('mailto:'))
                else:
                    telephone = None
                    address = None
                    email = None

                company = {
                    'company_name': '',
                    'website': '',
                    'telephone': '',
                    'number_of_reviews': '',
                    'address': '',
                    'email': ''
                }

                if company_name:
                    company['company_name'] = company_name.text.strip()
                
                if website:
                    website_dom = urlparse(website.get("href"))
                    website_dom = website_dom.netloc.replace("www.", "")
                    company['website'] = website_dom

                if telephone:
                    telephone = telephone.text.replace("+", "").strip()
                    company["telephone"] = telephone

                if number_of_reviews:
                    number_of_reviews = number_of_reviews.text.split()[0]
                    company['number_of_reviews'] = number_of_reviews

                if address:
                    combined_line = ' '.join([li.get_text(strip=True) for li in address])
                    company['address'] = combined_line          

                if email:
                    company['email'] = email.text.strip()

                data.append(company)
                count+=1

    return jsonify(data)
                

if __name__ == '__main__':
    app.run(debug=True)