from django.shortcuts import render
from django.shortcuts import redirect
import requests
from bs4 import BeautifulSoup
from uuid import uuid4
import random

from . import metrics, pings


def index(request):
    return render(request, 'searchranking/index.html')


def exclude_sections(sections_to_exclude):
    return lambda tag: True if tag is not None and tag.strip() not in sections_to_exclude else False


class SearchResult():
    def __init__(self, title, url, short_desc):
        self.title = title.strip()
        self.url = url.strip()
        self.short_desc = short_desc.strip()


def parse_results(soup):
    heading_object = soup.find_all('h3', text=exclude_sections(
        ['People also ask', 'Images', 'Top stories', 'Videos', 'Description']))

    result = []
    for info in heading_object:
        title = info.getText()
        href = info.parent.get('href', None)
        if href is not None:
            href = href.strip('/url?q=')
            short_desc = ''
            if info.parent.parent.find_next_sibling("div"):
                divs = info.parent.parent.find_next_sibling("div").find("div")
                if divs:
                    spans = divs.find_all("span")
                    for span in spans:
                        short_desc += span.text
            result.append(SearchResult(title, href, short_desc))
    return result


def execute_query(search_text):
    headers_dict = {
        'User-Agent': 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/'}

    url = 'https://google.com/search?num=20&q=' + search_text
    request_result = requests.get(url, headers=headers_dict)
    soup = BeautifulSoup(request_result.text, "html.parser")
    return parse_results(soup)


def results(request):
    try:
        search_text = request.GET.get('search_text', None)
    except KeyError as exc:
        return render(request, "please enter search text")

    if not search_text:
        context = {"errorMsg": "Please enter search text"}
        return render(request, 'searchranking/index.html', context)

    search_results = execute_query(search_text)
    random.shuffle(search_results)
    results_context = []
    position = 0
    for search_result in search_results:
        uuid = str(uuid4().hex)
        position += 1
        session_data = build_session_data(search_result.url, "Google", search_result.title, position)
        request.session[uuid] = session_data

        result_context = {
            'url': search_result.url,
            'result_id': uuid,
            'form_name': generate_form_name(uuid),
            'title': search_result.title,
            'short_desc': search_result.short_desc
        }
        results_context.append(result_context)
    context = {"results": results_context}
    return render(request, 'searchranking/results.html', context)


def generate_form_name(uuid):
    dig = ''.join(ele for ele in uuid if ele.isdigit())
    res = ''.join(ele for ele in uuid if not ele.isdigit())
    res += dig
    return res


def build_session_data(url, engine, title, position):
    return {
        'url': url,
        'engine': engine,
        'title': title,
        'position': position
    }


def go_to_selection(request):
    result_id = request.POST.get('result_id', None)
    session_data = request.session.get(result_id)

    metrics.search.selected.set(session_data.get('position'))
    metrics.search.search_result.set(session_data.get('url'))
    pings.custom.submit()

    return redirect(session_data.get('url'))
