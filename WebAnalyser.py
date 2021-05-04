import requests
from bs4 import BeautifulSoup
import html


def soup_xpath_gen(element):
    """
    Generates an xpath string for a given BeautifulSoup element
    :param element:
    :return:
    """
    BAD_CHARS = {"\"", "'", "[", "]"}
    xpath = ""
    while element is not None and element.name != 'document':
        if element.name == 'html':
            xpath = "/html/" + xpath
            break
        else:
            items = list(element.attrs.items())
            if not items:
                el_xpath = str(element.name)
            else:
                el_xpath = str(element.name) + "["
                one = False
                for i, (k, v) in enumerate(items):
                    if not any(char in BAD_CHARS for char in v):
                        if k == "title":
                            continue
                        if one:
                            el_xpath = el_xpath + " and "
                        one = True
                        if "/" in v:
                            el_xpath += "normalize-space(@%s)" % k
                        else:
                            if isinstance(v, list):
                                v = " ".join(v)
                            el_xpath += "normalize-space(@%s)=normalize-space(\'%s\')" % (k, html.escape(v))
                el_xpath += "]"
            xpath = el_xpath + "/" + xpath
        element = element.parent
    return xpath.rstrip("/")


def get_most_common_tag(tag_list):
    return max(set(tag_list), key=tag_list.count)


class WebAnalyser:

    def __init__(self):
        self.html = None
        self.soup = None
        self.tags = []
        self.most_common_tag = None
        self.longest_paths = {}
        self.path_to_popular_tag = None

    def recursive_children(self, x, length=0, path=None, pop_count=0):
        """
        Recursively check if the current node (x) has children
        Once terminal node is selected, stop the process and create path
        Do the same process for all nodes
        :param x: html element
        :param length: length of the path to x
        :param path: path string
        :param pop_count: count of most popular tag occupancies in x
        :return:
        """

        if 'childGenerator' in dir(x):
            for child in x.childGenerator():
                name = getattr(child, 'name', None)
                if name is not None:
                    path = soup_xpath_gen(child)
                    tag_elements = child.find_all(self.most_common_tag)
                    if len(tag_elements) >= pop_count:
                        pop_count = len(tag_elements)
                        self.path_to_popular_tag = (len(tag_elements), path)
                self.recursive_children(child, length + 1, path, pop_count)
        else:
            if path is not None and not x.isspace():  # Avoid printing "\n" parsed from document
                if length in self.longest_paths:
                    self.longest_paths[length].append(path)
                else:
                    self.longest_paths[length] = [path]

    def get_html(self, url):
        while True:
            try:
                response = requests.get(url)
                self.soup = BeautifulSoup(response.text, 'html.parser')
                print("Analysing {}\n".format(url))
                break
            except Exception as e:
                print("Please check URL or try another one")
                url = input()

    def main(self):
        try:
            print("---------------------------------------------")
            print("       Welcome to Web page analyser")
            print("---------------------------------------------")

            print("\nPlease insert URL you want to analyse\n")

            url = input()  # e.g. "https://eksmaoptics.com/optical-components/"
            # scrape and parse website
            self.get_html(url)

            print("---------------------------------------------")

            # find tags
            for tag in self.soup.find_all():
                self.tags.append(tag.name)

            print("Unique tags on the website: ", set(self.tags))
            self.most_common_tag = get_most_common_tag(self.tags)
            print("Print most common tag: ", self.most_common_tag)
            print("---------------------------------------------\n")

            # find longest path
            self.recursive_children(self.soup)
            print("Longest path/paths on the website: ", self.longest_paths[max(self.longest_paths, key=int)])
            print("Path length: ", max(self.longest_paths, key=int))
            print("---------------------------------------------\n")

            # find longest path for most popular tag
            print("Longest path to the node where the most popular tag is used the most times: ", self.path_to_popular_tag[1])
            print("Tag occurrence count in the path: ", self.path_to_popular_tag[0])
            print("---------------------------------------------\n")

            print("Done")

        except Exception as e:
            print("Failed", str(e))


if __name__ == '__main__':
    analyser = WebAnalyser()
    analyser.main()
