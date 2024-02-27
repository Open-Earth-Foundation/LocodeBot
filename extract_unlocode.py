import urllib.request
import tempfile
import zipfile
import os

def main(url, output_dir):
  # Ensure the output directory exists
  if not os.path.exists(output_dir):
      os.makedirs(output_dir)

  # Create a temporary file
  with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
      # Download the ZIP file and save it to the temporary file
      urllib.request.urlretrieve(url, tmp_file.name)

      # Open the ZIP file
      with zipfile.ZipFile(tmp_file.name, 'r') as zip_ref:
          # Extract its contents to the specified output directory
          zip_ref.extractall(output_dir)

  # Delete the temporary ZIP file
  os.remove(tmp_file.name)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Download and extract UN/LOCODE ZIP file')
    parser.add_argument(
        '--url',
        default='https://service.unece.org/trade/locode/loc232csv.zip', help='URL of the ZIP file to download'
    )
    parser.add_argument(
        '--output_dir',
        default='data', help='Directory where the contents of the ZIP file will be extracted'
    )
    args = parser.parse_args()
    main(args.url, args.output_dir)