from typing import List
import re
import os
import glob
import urllib.request
from urllib.parse import urlparse
import hashlib
from collections import defaultdict

# To debug, insert the line below where you want to
# start pdb
# import pdb; pdb.set_trace()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except:
        return False


def parse_param(string: str, key: str) -> List[str]:
    # First try array match
    match = re.search(r'^' + key + r'=\((.*?)\)', string, re.DOTALL | re.MULTILINE)
    # Match single quota string
    if not match:
        match = re.search(r'^' + key + r'=\'(.*?)\'', string, re.DOTALL | re.MULTILINE)
    # Match double quota string
    if not match:
        match = re.search(r'^' + key + r'=\"(.*?)\"', string, re.DOTALL | re.MULTILINE)

    if match:
        values = [v.strip('\'"') for v in " ".join(match.group(1).replace('\n', '').split()).split(' ')]
    else:
        values = []

    return values

def parse_dependencies(file_path) -> List[str]:
    with open(file_path, 'r') as file:
        content = file.read()
    return parse_param(content, "DEPENDENCY_MODULE_LIST")

def create_all_build_list(files):
    graph = defaultdict(list)
    package_to_file_dict = defaultdict(list)
    for file in files:
        _, package_name, build_script = file.split(os.sep)[-3:]
        version = build_script.replace('.sh', '')
        dependencies = parse_dependencies(file)
        graph[(package_name, version)].extend(dependencies)
        package_to_file_dict[(package_name, version)] = file
    return [graph, package_to_file_dict]

def topological_sort(graph):
    in_degree = {node: 0 for node in graph}
    for node in graph:
        for _ in graph[node]:
            in_degree[node] += 1

    queue = []
    sorted_order = []
    for node in in_degree:
        if in_degree[node] == 0:
            sorted_order.append(node)
        else:
            queue.append(node)

    while queue:
        n = len(sorted_order)
        for parent in queue:
            for child in graph[parent]:
                if child in sorted_order:
                    in_degree[parent] -= 1
                if in_degree[parent] == 0:
                    sorted_order.append(parent)
                    queue.remove(parent)
                    break
        if len(sorted_order) == n:
            raise RuntimeError(f"Missing dependency detected for one of the following packages: {queue}")

    # Check if we have a cycle
    if len(sorted_order) == len(in_degree):
        return sorted_order
    else:
        # In case there is a cycle, which is a dependency that doesn't resolve
        raise Exception(f'There is a cycle in the dependency graph or an unresolved dependency: {[node for node in in_degree if in_degree[node] > 0]}')

def get_all_deps(graph, parent):
    visited = set()
    ordered_dependencies = []

    def dfs(node):
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor)
        if node not in visited:
            visited.add(node)
            ordered_dependencies.append(node)
    dfs(parent)
    return ordered_dependencies

def get_sub_graph(start, graph):
    visited = set()
    def dfs(node):
        if node not in visited:
            visited.add(node)
            for neighbor in graph.get(node, []):
                dfs(neighbor)
    dfs(start)
    visited = visited.append(start)
    sub_graph = {k: graph[k] for k in list(visited) if k in graph}
    return sub_graph

def read_module_help(script_content):
    pkg_help_pattern = re.compile(r'''MODULEFILE_HELP\s*=\s*(?P<quote>["'])(.*?)(?P=quote)''', re.DOTALL)
    match = pkg_help_pattern.search(script_content)
    if match:
        return match.group(2)
    else:
        return "\n"

def download_and_verify(url, pkg_download_dir, md5sum, archive_name: str = None):
    if uri_validator(url):
        parsed_url = urlparse(url)
        if archive_name is None:
            file_name = os.path.basename(parsed_url.path)
        else:
            file_name = archive_name
    else:
        if archive_name is None:
            file_name = url.split(os.sep)[-1]
        else:
            file_name = archive_name
        url = os.path.expandvars(url)

    downloaded_file_path = os.path.join(pkg_download_dir, file_name)

    if os.path.isfile(downloaded_file_path):
        existing_file_md5 = hashlib.md5(open(downloaded_file_path, 'rb').read(), usedforsecurity=False).hexdigest()
        if existing_file_md5 != md5sum:
            os.remove(downloaded_file_path)
        else:
            print(f"{bcolors.OKGREEN}Found existing valid file: {downloaded_file_path}{bcolors.ENDC}")
            return [downloaded_file_path, True]

    try:
        print(f"{bcolors.OKCYAN}Downloading file: {file_name} from {url}{bcolors.ENDC}")
        urllib.request.urlretrieve(url, downloaded_file_path)
    except:
        print(f"{bcolors.WARNING}Encountered an error while downloading file: {file_name} from {url}{bcolors.ENDC}")
        return [url, False]

    # Verify the MD5
    file_md5 = hashlib.md5(open(downloaded_file_path, 'rb').read(), usedforsecurity=False).hexdigest()
    if file_md5 != md5sum:
        os.remove(downloaded_file_path)
        print(f"{bcolors.WARNING}MD5 checksum failed for {downloaded_file_path}{bcolors.ENDC}")
        return [url, False]

    print(f"{bcolors.OKGREEN}Verified: {downloaded_file_path}{bcolors.ENDC}")
    return [downloaded_file_path, True]

def archive_from_url(url: str) -> str:
    """
    Obtains the archive name from a provided url
    """

    # Strip an url parameters
    url = url.split("?")[0]
    # Remove trailing '/'
    if '/' == url[-1]:
        url = url[0:-1]

    return os.path.basename(url)


def process_and_download_build_file(file_path, transferred_file, download_dir, transfer_file) -> str:

    return_msg = ""

    package_name, build_script = file_path.split(os.sep)[-2:]
    version = build_script.replace('.sh', '')
    package_version = os.path.join(package_name, version)
    pkg_download_dir = os.path.join(download_dir, package_version)

    # Read the script file and find DOWNLOAD_URL and PKG_MD5SUM
    with open(file_path, 'r') as script_file:
        script_content = script_file.read()

    download_urls = parse_param(script_content, "DOWNLOAD_URL")
    archive_md5s = parse_param(script_content, "ARCHIVE_MD5")
    archive_names = parse_param(script_content, "ARCHIVE_NAME")

    if len(archive_names) < len(download_urls):
        for i in range(len(download_urls)):
            archive_names.append('')

    if len(download_urls) != len(archive_md5s):
        raise ValueError("Mismatch in number of download URLs and archive MD5 sums")

    if len(download_urls) != len(archive_names):
        raise ValueError("Invalid archive name provided")

    for download_url, pkg_md5sum, archive_name in list(zip(download_urls, archive_md5s, archive_names)):

        if 0 == len(download_url):
            # We assume any empty DOWNLOAD_URL is a local module
            return_msg += f"Skipping {package_version} since DOWNLOAD_URL is not set\n"
            continue;

        if 0 == len(archive_name):
            archive_name = archive_from_url(download_url)

        pkg_help = read_module_help(script_content)

        # Check if package info exists in the flat file
        if os.path.isfile(transferred_file):
            with open(transferred_file, 'r') as f:
                existing_packages = f.read()

            if package_version in existing_packages and download_url in existing_packages and pkg_md5sum in existing_packages:
                continue  # Package already listed, nothing to do

        # Download and verify the package
        try:
            if not os.path.exists(pkg_download_dir):
                os.makedirs(pkg_download_dir)

            [out_file, success] = download_and_verify(download_url, pkg_download_dir, pkg_md5sum, archive_name=archive_name)
            if not success:
                return_msg += f"Failed to download or use file from: {out_file}\n"
                continue;

            # Update the flat file with the new package information
            with open(transferred_file, 'a') as f:
                f.write(f"{package_version},{download_url},{pkg_md5sum
