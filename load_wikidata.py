import pywikibot
from csv import DictReader

def main(inputfile):
  # Login to Wikidata
  site = pywikibot.Site("wikidata", "wikidata")
  site.login()
  repo = site.data_repository()

  with open(inputfile, 'r') as f:
    reader = DictReader(f)
    for row in reader:
      locode = row['LOCODE']

      if locode[0:2] == 'IT':
        print(f"Skipping {locode} because Italy is complicated.")
        continue

      wikidata_id = row['wikidata_id']

      page = pywikibot.ItemPage(site, wikidata_id)

      try:
        page.get()
      except pywikibot.exceptions.IsRedirectPageError:
        print(f"Item {wikidata_id} is a redirect.")
        continue
      except Exception as e:
        print(f"Error getting item {wikidata_id}: {e}")
        continue

      # Property for UN/LOCODE
      locode_property = 'P1937'

      # Check if LOCODE already exists
      if locode_property in page.claims:
          print(f"Item {wikidata_id} already has a LOCODE value.")
          continue  # Skip to the next row in the CSV


      # Creating a new claim for LOCODE
      claim = pywikibot.Claim(site, locode_property)
      claim.setTarget(locode)
      country_code = locode[:2].lower()
      reference_url = f'https://service.unece.org/trade/locode/{country_code}.htm'
      reference = pywikibot.Claim(site, 'P854')
      reference.setTarget(reference_url)
      claim.addSources([reference])
      try:
        page.addClaim(claim, summary='Adding UN/LOCODE')
        print(f"Added UN/LOCODE {locode} to {wikidata_id}.")
      except Exception as e:
        print(f"Error adding UN/LOCODE {locode} to {wikidata_id}: {e}")
        continue

if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser(description='Add UN/LOCODE to Wikidata items')
  parser.add_argument('--inputfile', help='CSV file with LOCODEs and Wikidata IDs')
  args = parser.parse_args()
  main(args.inputfile)