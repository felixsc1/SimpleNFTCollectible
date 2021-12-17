from brownie import AdvancedCollectible, network
from scripts.helpful_scripts import get_breed
from metadata.sample_metadata import metadata_template
from pathlib import Path
import requests


def main():
    advanced_collectible = AdvancedCollectible[-1]
    number_of_advanced_collectibles = advanced_collectible.tokenCounter()
    print(f"you have created {number_of_advanced_collectibles} collectibles!")
    # Now loop through each collectible and create its metadata json
    # which looks like this: https://ipfs.io/ipfs/Qmd9MCGtdVz2miNumBHDbvj8bigSgTwnr4SbyH6DNnpWdt?filename=0-PUG.json
    for token_id in range(number_of_advanced_collectibles):
        breed = get_breed(advanced_collectible.tokenIdToBreed(token_id))
        metadata_file_name = f"./metadata/{network.show_active()}/{token_id}-{breed}.json"
        collectible_metadata = metadata_template
        if Path(metadata_file_name).exists():
            print(f"{metadata_file_name} already exists! Delete it to overwrite")
        else:
            print(f"creating Metadata file: {metadata_file_name}")
            # the way the template was specified, can now fill in the data as with any python dict
            collectible_metadata["name"] = breed
            collectible_metadata["description"] = f"An adorable {breed} pup!"
            # To assign the image, it must be already uploaded to IPFS, separate function below
            # make breed name match our png filenames
            image_path = "./img/" + breed.lower().replace("_", "-") + ".png"
            image_uri = upload_to_ipfs(image_path)
            collectible_metadata["image"]
            print(collectible_metadata)


def upload_to_ipfs(filepath):
    # context manager. "rb" means open read-only as binary(needed for images)
    with Path(filepath).open("rb") as fp:
        image_binary = fp.read()  # now whole image is stored as binary
        # upload stuff...
        ipfs_url = "http://127.0.0.1:5001"
        endpoint = "/api/v0/add"
        response = requests.post(
            ipfs_url + endpoint, files={"file": image_binary})
        print(response.json())
        ipfs_hash = response.json()["Hash"]
        # "./img/0-PUG.png" --> "0-PUG.png"
        # split("/") will split it up by dashes into an array, then we grab the last element.
        filename = filepath.split("/")[-1:][0]
        image_uri = f"https://ipfs.io/ipfs/{ipfs_hash}?filename={filename}"
        # should then look like "https://ipfs.io/ipfs/Qmd9MCGtdVz2miNumBHDbvj8bigSgTwnr4SbyH6DNnpWdt?filename=0-PUG.json"
        # first part is the hash of the image (calculated by ipfs) followed by filename.
        # If image were manipulated, hash would no longer match.
        print(image_uri)
        return image_uri