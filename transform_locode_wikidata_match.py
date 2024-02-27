from csv import DictReader, DictWriter
from shapely.wkt import loads
from geopy.distance import geodesic

LOCODE_COLUMNS = [
    "Ch",
    "ISO 3166-1",
    "LOCODE",
    "Name",
    "NameWoDiacritics",
    "SubDiv",
    "Function",
    "Status",
    "Date",
    "IATA",
    "Coordinates",
    "Remarks"
]

# Function to parse fixed-length format
def parse_coords(fixed_str):
    lat_ddmm = fixed_str[:5]
    lon_ddmm = fixed_str[6:]

    lat_deg = int(lat_ddmm[:2])
    lat_min = int(lat_ddmm[2:4])
    lat_dir = lat_ddmm[4]

    lon_deg = int(lon_ddmm[:3])
    lon_min = int(lon_ddmm[3:5])
    lon_dir = lon_ddmm[5]

    # Convert to decimal degrees
    lat = lat_deg + lat_min / 60.0
    lon = lon_deg + lon_min / 60.0

    # Adjust for direction
    if lat_dir == 'S':
        lat = -lat
    if lon_dir == 'W':
        lon = -lon

    return lat, lon

def distance_between_points(coords, location):
  try:
    point = loads(location)
  except:
    return None
  wkt_lat, wkt_lon = point.y, point.x
  fixed_lat, fixed_lon = parse_coords(coords)
  distance = geodesic((wkt_lat, wkt_lon), (fixed_lat, fixed_lon)).kilometers
  return distance

def main(locodes, wikidata, output):

  wdcities = {}
  cc = {}

  with open(wikidata, 'r') as f:
      reader = DictReader(f)
      for row in reader:
        if wdcities.get(row['region'], None) is None:
          wdcities[row['region']] = {row['name']: row}
        else:
          wdcities[row['region']][row['name']] = row
        country_code = row['region'].split('-')[0]
        if cc.get(country_code, None) is None:
          cc[country_code] = {row['name']: [row]}
        elif cc[country_code].get(row['name'], None) is None:
          cc[country_code][row['name']] = [row]
        else:
          cc[country_code][row['name']].append(row)

  with open(locodes, 'r', encoding='iso-8859-1') as f:
    reader = DictReader(f, fieldnames=LOCODE_COLUMNS)
    with open(output, 'w') as out:
        writer = DictWriter(out, fieldnames=['LOCODE', 'wikidata_id', 'distance'])
        writer.writeheader()
        for row in reader:
            if not row['LOCODE']:
                continue
            match = None
            # Try to match by subdivision
            if row['SubDiv'] and len(row['SubDiv']) > 0:
              region_code = row['ISO 3166-1'] + '-' + row['SubDiv']
              rc = wdcities.get(region_code, None)
              if rc is None:
                continue
              match = rc.get(row['Name'], None)
              if not match:
                match = wdcities.get(row['NameWoDiacritics'], None)
            # Try to match by country
            if not match:
               country = cc.get(row['ISO 3166-1'], None)
               if country:
                  matches = country.get(row['Name'], None)
                  if matches:
                    if len(matches) == 1:
                      match = matches[0]
                    elif row['Coordinates'] and len(row['Coordinates']) > 0:
                      closest = None
                      closest_distance = None
                      for m in matches:
                        if m['location'] and len(m['location']) > 0:
                          distance = distance_between_points(row['Coordinates'], m['location'])
                          if distance is not None:
                            if closest_distance is None or distance < closest_distance:
                              closest = m
                              closest_distance = distance
                      match = closest
            if match:
              if row['Coordinates'] and len(row['Coordinates']) > 0 and match['location'] and len(match['location']) > 0:
                distance = distance_between_points(row['Coordinates'], match['location'])
              else:
                distance = None
              if distance is not None and distance > 10:
                continue
              writer.writerow({
                'LOCODE': row["ISO 3166-1"] + row['LOCODE'],
                'wikidata_id': match['wikidata_id'],
                'distance': distance
              })

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Match UN/LOCODE to Wikidata')
    parser.add_argument('--locodes', help='LOCODEs CSV file')
    parser.add_argument('--wikidata', help='Wikidata CSV file')
    parser.add_argument('--output', help='Output CSV file')
    args = parser.parse_args()
    main(args.locodes, args.wikidata, args.output)
