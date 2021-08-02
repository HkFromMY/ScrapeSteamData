# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Compose
from w3lib.html import remove_tags
import re

def extract_percentage(string):
    # find percentage
    return re.search(r'(\d{3}|\d{2}%)', string).group()

def remove_whitespace(value):
    try:
        for i in range(len(value)):
            value[i] = value[i].strip()
        return value
    except:
        return value.strip()

def take_five(value):
    try:
        return value[:5]
    except IndexError:
        try:
            return value[:3]
        except IndexError:
            return value[0]

class SteamItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field(input_processor=MapCompose(remove_tags, remove_whitespace), output_processor=TakeFirst())
    review_summary = scrapy.Field(input_processor=MapCompose(remove_tags, remove_whitespace), output_processor=TakeFirst())
    n_reviews = scrapy.Field(output_processor=TakeFirst())
    positive_review = scrapy.Field(input_processor=MapCompose(remove_tags, remove_whitespace, extract_percentage), output_processor=TakeFirst()) # in percentage
    release_date = scrapy.Field(input_processor=MapCompose(remove_tags, remove_whitespace), output_processor=TakeFirst())
    genre = scrapy.Field(input_processor=MapCompose(remove_tags, remove_whitespace), output_processor=Compose(take_five))
    developer = scrapy.Field(input_processor=MapCompose(remove_tags, remove_whitespace), output_processor=TakeFirst())
