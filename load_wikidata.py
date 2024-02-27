import pywikibot
from csv import DictReader

def main(inputfile):
  # Login to Wikidata
  site = pywikibot.Site("wikidata", "wikidata")
  site.login()

  with open(inputfile, 'r') as f:
    reader = DictReader(f)
    for row in reader:
      locode = row['LOCODE']
      wikidata_id = row['wikidata_id']

      page = pywikibot.ItemPage(site, wikidata_id)
      page.get()

      # Property for UN/LOCODE
      locode_property = 'P1937'

      # Check if LOCODE already exists
      if locode_property in page.claims:
          print(f"Item {wikidata_id} already has a LOCODE value.")
          continue  # Skip to the next row in the CSV

      # Creating a new claim for LOCODE
      claim = pywikibot.Claim(site, locode_property)
      claim.setTarget(locode)
      page.addClaim(claim, summary='Adding UN/LOCODE')

      print(f"Added UN/LOCODE {locode} to {wikidata_id}.")

if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser(description='Add UN/LOCODE to Wikidata items')
  parser.add_argument('--inputfile', help='CSV file with LOCODEs and Wikidata IDs')
  args = parser.parse_args()
  main(args.inputfile)