#!/usr/bin/env python3

import argparse
import requests
from bs4 import BeautifulSoup
from launchpadlib.launchpad import Launchpad

class Repo:
    def __init__(self, user, name, url):
        self.user = user
        self.name = name
        self.url = url

    def search(self, lp, codename, cpu_arch, noexact, search):
        owner = lp.people[self.user]
        archive = owner.getPPAByName(distribution=lp.distributions["ubuntu"], name=self.name)
        binaries = archive.getPublishedBinaries(status='Published', binary_name=search, exact_match=not noexact)

        packages = []
        if len(binaries) > 0:
            for binary in binaries:
                distro_arch_series = binary.distro_arch_series_link
                binary_codename = distro_arch_series.split('/')[-2]
                binary_arch = distro_arch_series.split('/')[-1]
                if (codename is None or codename.lower() == binary_codename) and (cpu_arch is None or cpu_arch == binary_arch):
                    packages.append(Package(self.user, self.name, binary.binary_package_name, binary.binary_package_version, binary_codename, binary_arch))
        return packages


class Package:
    def __init__(self, user, repo, name, version, series, arch):
        self.user = user
        self.repo = repo
        self.name = name
        self.version = version
        self.series = series
        self.arch = arch


def search_ppa(search):
    resp = requests.get(f"https://launchpad.net/ubuntu/+ppas?name_filter={search}&batch=300")
    soup = BeautifulSoup(resp.text, "html.parser")
    results = soup.select('tr.ppa_batch_row > td > a:not([href=""])')
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
    parser.add_argument("-a", "--arch", type=str, help="CPU architecture, one of amd64, i386, armhf, arm64, etc.")
    parser.add_argument("--noexact", action="store_true", help="also search for not exact match")
    parser.add_argument("package", type=str, help="exact name of the package you want to search")
    args = parser.parse_args()

    lp = Launchpad.login_anonymously("ppa-search", "edge", "~/.launchpadlib/cache/", version="devel")

    repos = search_ppa(args.package)
    for i in range(len(repos)):
        print(f"\rSearching {i + 1}/{len(repos)}", end='')
        packages = repos[i].search(lp, args.codename, args.arch, args.noexact, args.package)
        for package in packages:
            print(f"\r{package.name} {package.version} ppa:{package.user}/{package.repo} {package.series.capitalize()} ({package.arch})")

    print("\rSearch is finished.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
