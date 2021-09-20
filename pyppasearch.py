#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import argparse


class Repo:
    def __init__(self, user, name, url):
        self.user = user
        self.name = name
        self.url = url

    def search(self, search):
        resp = requests.get(self.url)
        soup = BeautifulSoup(resp.text, "html.parser")
        thead = soup.select("thead > tr > th")
        series_index = 3
        # Sometimes there is "Uploader" in table, so position of index will change
        for j in range(len(thead)):
            if thead[j].text == "Series":
                series_index = j
                break
        results = soup.select("tbody > tr.archive_package_row")
        packages = []
        for result in results:
            source = result.select_one("a.sprite").text
            name = source.split()[0]
            version = source.split()[2]
            series = result.select_one(f"td:nth-of-type({series_index + 2})").text
            if name == search:
                packages.append(Package(self.user, self.name, name, version, series))
        return packages


class Package:
    def __init__(self, user, repo, name, version, series):
        self.user = user
        self.repo = repo
        self.name = name
        self.version = version
        self.series = series


def search_ppa(search):
    resp = requests.get(f"https://launchpad.net/ubuntu/+ppas?name_filter={search}&batch=300")
    soup = BeautifulSoup(resp.text, "html.parser")
    results = soup.select("tr.ppa_batch_row > td > a")
    repos = []
    for result in results:
        url = "https://launchpad.net" + result['href'] + "/+packages?batch=300"
        name = str(result['href']).split('/')[-1]
        user = str(result['href'])[2:].split('/')[0]
        repos.append(Repo(user, name, url))
    return repos


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--codename", type=str, help="First word of Ubuntu code name, e.g. Focal")
    parser.add_argument("package", type=str, help="exact name of the package you want to search")
    args = parser.parse_args()

    repos = search_ppa(args.package)
    for i in range(len(repos)):
        print(f"\rSearching {i + 1}/{len(repos)}", end='')

        packages = repos[i].search(args.package)
        for package in packages:
            if args.codename is None or package.series == args.codename:
                print(f"\r{package.name} {package.version} {package.user}/{package.repo} {package.series}")

    print("\rSearch is finished.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
