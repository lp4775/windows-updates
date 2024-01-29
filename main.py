import gzip
import shutil
import requests
import json
import os

WINBINDEX_URL = "https://winbindex.m417z.com/data/by_filename_compressed/{}.json.gz"

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File '{file_path}' has been deleted.")
    else:
        print(f"The file '{file_path}' does not exist.")

def download_file(url, filename):
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"File downloaded: {filename}")
    else:
        print(f"Failed to download file: status code {response.status_code}")

version_dict = {}

file_names = [
    "ntoskrnl.exe", 
    "ntdll.dll", 
    "ci.dll", 
    "kernel32.dll", 
    "kernelbase.dll"
]

for file_name in file_names:
    compressed_file = f"{file_name}.gz"
    json_file = f"{file_name}.json"

    download_file(WINBINDEX_URL.format(file_name), compressed_file)

    with gzip.open(compressed_file, 'rb') as f_in:
        with open(json_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    with open(json_file, 'r') as file_handle:
        dictionary = json.load(file_handle)
        for key in dictionary:
            for windows_version in dictionary[key]["windowsVersions"]:
                if windows_version not in version_dict:
                    version_dict[windows_version] = []
                
                updates = dictionary[key]["windowsVersions"][windows_version]
                for update in updates:
                    if "windowsVersionInfo" in dictionary[key]["windowsVersions"][windows_version][update].keys():
                        release_date = dictionary[key]["windowsVersions"][windows_version][update]['windowsVersionInfo']['releaseDate']
                    else:
                        release_date = dictionary[key]["windowsVersions"][windows_version][update]['updateInfo']['releaseDate']
                    
                    update_tuple = (update, release_date)
                    if update_tuple not in version_dict[windows_version]:
                        version_dict[windows_version].append(update_tuple)

    delete_file(compressed_file)
    delete_file(json_file)

for version in version_dict:
    # Sorting by update name
    version_dict[version] = sorted(version_dict[version], key=lambda x: x[0])

with open('version_dict.json', 'w') as file_handle:
    json.dump(version_dict, file_handle, indent=4)