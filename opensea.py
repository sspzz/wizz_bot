import requests
import json
from dateutil.parser import parse

contract_wizards = "0x521f9c7505005cfa19a8e5786a9c3c9c9f5e6f42"
contract_flames = "0x31158181b4b91a423bfdc758fc3bf8735711f9c5"

class Listing(object):
	def __init__(self, wiz_id, name, image_url, price, currency, date, permalink):
		self.wiz_id = wiz_id
		self.name = name
		self.image_url = image_url
		self.price = price
		self.currency = currency
		self.date = date
		self.permalink = permalink

	@property
	def date_str(self):
		return self.date.strftime('%d/%m/%Y %H:%M')

	@staticmethod
	def from_json(json):
		wiz_id = json.get("asset").get("token_id")
		name = json.get("asset").get("name")
		image_url = json.get("asset").get("image_url")
		price_str = json.get("total_price")
		if price_str is None:
			price_str = json.get("starting_price")
		price = "N/A" if price_str is None else float(price_str) / 1000000000000000000.0
		currency = json.get("payment_token").get("symbol")
		date = parse(json.get("created_date"))
		link = json.get("asset").get("permalink")
		return Listing(wiz_id, name, image_url, price, currency, date, link)

	def __repr__(self):
		return "{}, #{} - {}, {} {}".format(self.date_str, self.wiz_id, self.name, self.price, self.currency)


def get_listings(contract_address, num):
	parameters = { 
		"only_opensea": False, 
		"offset": 0, 
		"limit": num, 
		"asset_contract_address": contract_address, 
		"event_type": "created" 
	}
	headers = {"Accept": "application/json"}
	url = "https://api.opensea.io/api/v1/events"
	response = requests.request("GET", url, headers=headers, params=parameters)
	listings = response.json().get("asset_events")
	return list(map(lambda w: Listing.from_json(w), listings))

def get_latest_listing(contract_address):
	return get_listings(contract_address, 1)[0]

def get_sales(contract_address, num):
	parameters = { 
		"only_opensea": False, 
		"offset": 0, 
		"limit": num, 
		"asset_contract_address": contract_address, 
		"event_type": "successful" 
	}
	headers = {"Accept": "application/json"}
	url = "https://api.opensea.io/api/v1/events"
	response = requests.request("GET", url, headers=headers, params=parameters)
	listings = response.json().get("asset_events")
	return list(map(lambda w: Listing.from_json(w), listings))

def get_latest_sale(contract_address):
	return get_sales(contract_address, 1)[0]


if __name__ == "__main__":
	print("Leatest 10 sales:")
	for l in get_sales(contract_wizards, 10):
		print("   - {}".format(l))

	print("Latest 10 listings:")
	for l in get_listings(contract_wizards, 10):
		print("   - {}".format(l))

	print("Latest flame sale:")
	print("   - {}".format(get_latest_sale(contract_flames)))
