import scrapy
from scrapy.selector import Selector
from scrapy.loader import ItemLoader
from steam.items import SteamItem
from scrapy import FormRequest
import json

class SteamSpider(scrapy.Spider):
    name = "steam"
    start_urls = ["https://store.steampowered.com/contenthub/querypaginated/freetoplay/TopSellers/render/?query=&start=0&count=15&cc=MY&l=english&v=4&tag="]
    start_page = 0
    
    def parse(self, response):
        # steam uses AJAX to fetch data so it's dynamic sites
        # we send GET request to the link which fetch data first
        # then extract the html string out from the link after that perform normal scraping using css selector
        info = json.loads(response.body)['results_html']
        parsed_html = Selector(text=info)  # convert the html string into selector object 
        target_links = parsed_html.css("a.tab_item") # get the link of every game

        for link in target_links:
            # where the link located
            targeted_link = link.css("a.tab_item::attr(href)").get()
            # for each link obtained, we send a GET request and call parse_product function to parse the information we want
            yield scrapy.Request(
                url=targeted_link,
                callback=self.parse_product,
                meta={'targeted_link': targeted_link},  # this data can be used as arguments to be passed into parse_product
                dont_filter=True  # this is because we will request again so disabling duplicate 
            )

        # next page 
        self.start_page += 15  # after analyzing every transition of the page the count + 15 and max count is 632 which totals 42 pages
        next_page = "https://store.steampowered.com/contenthub/querypaginated/freetoplay/TopSellers/render/?query=&start=%d&count=15&cc=MY&l=english&v=4&tag=" % self.start_page
        # max page count 632
        while self.start_page < 632:
            yield scrapy.Request(url=next_page, callback=self.parse)

    
    # function used to parse product's (game) information
    def parse_product(self, response):
        # bypass the steam agecheck by passing in custom values
        if '/agecheck/app' in response.url:
            # send GET request to the link again by passing cookies
            yield scrapy.Request(
                url=response.meta.get('targeted_link'),  # extract arguments from meta property
                callback=self.parse_product,
                cookies= {
                    # this can be obtained from Inspect >> Application >> Storage >> Cookies
                    "lastagecheckage": "1-0-1985",
                    "birthtime": "-65865599"
                },
                dont_filter=True
            )
        # if the agecheck is bypassed
        else:
            # load the item into field defined in items.py
            target = response.css("div.glance_ctn")
            l = ItemLoader(item=SteamItem(), selector=target)
            # load the data in
            # first arguments is the field name while second arguments is where the information located
            l.add_css('name', 'div.apphub_AppName')
            l.add_css('review_summary', 'span.game_review_summary')
            l.add_css('n_reviews', 'div.summary.column meta::attr(content)')
            l.add_css('positive_review', 'span.nonresponsive_hidden.responsive_reviewdesc')
            l.add_css('release_date', 'div.release_date div.date')
            l.add_css('genre', 'div.glance_tags.popular_tags a')  # automatically uses getall()
            l.add_css('developer', 'div.summary.column#developers_list  a')

            # load the item then yield them (output them to csv or json file)
            yield l.load_item()
