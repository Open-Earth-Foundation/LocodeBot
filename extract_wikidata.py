from SPARQLWrapper import SPARQLWrapper, JSON, CSV
from csv import DictReader, DictWriter

byregion = '''
SELECT DISTINCT ?city ?cityLabel ?location WHERE {
  hint:Query hint:optimizer "None".
  ?region wdt:P300 "%s" .
  ?city wdt:P131* ?region;
        wdt:P31/wdt:P279* wd:Q124250988;
        wdt:P625 ?location .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en,fr,es,ar,ru,zh". }
}
'''

def get_cities_in_region(code):
  sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
  sparql.setQuery(byregion % (code))
  sparql.setReturnFormat(JSON)
  try:
    results = sparql.query().convert()
  except Exception as e:
    print(e)
    results = None
  return results

def main(regions, output):
  with open(regions, 'r') as f:
    reader = DictReader(f)
    with open(output, 'w') as out:
      writer = DictWriter(out, fieldnames=['region', 'wikidata_id', 'name', 'location'])
      writer.writeheader()
      for row in reader:
        region = row['actor_id']
        results = get_cities_in_region(region)
        if results is None:
          continue
        for result in results['results']['bindings']:
          writer.writerow({
            'region': region,
            'wikidata_id': result['city']['value'].split('/')[-1],
            'name': result['cityLabel']['value'],
            'location': result['location']['value']
          })
          out.flush()

if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser(description='Get wikidata cities in a region')
  parser.add_argument('--regions', help='Regions CSV file')
  parser.add_argument('--output', help='Output CSV file')
  args = parser.parse_args()
  main(args.regions, args.output)