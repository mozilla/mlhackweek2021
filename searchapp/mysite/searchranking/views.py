from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.sessions.models import Session
import requests
from bs4 import BeautifulSoup
from uuid import uuid4
from datetime import datetime
from urllib.parse import urlparse

from . import metrics, pings, domains


def index(request):
    return render(request, 'searchranking/index.html')


def exclude_sections(sections_to_exclude):
    return lambda tag: True if tag is not None and tag.strip() not in sections_to_exclude else False


class SearchResult():
    def __init__(self, url, hostname, title, short_desc, preamble, selected, position):
        self.url = '' if url is None else url.strip()
        self.hostname = '' if url is None else hostname.strip()
        self.title = '' if title is None else title.strip()
        self.short_desc = '' if short_desc is None else short_desc.strip()
        self.preamble = '' if preamble is None else preamble.strip()
        self.selected = selected
        self.position = position


def parse_results(soup):
    heading_object = soup.find_all('h3', text=exclude_sections(
        ['People also ask', 'Images', 'Top stories', 'Videos', 'Description']))

    result = []
    for info in heading_object:
        title = info.getText()
        href = info.parent.get('href', None)
        if href is not None:
            href = href.replace('/url?q=', '')
            hostname = urlparse(href).netloc
            # only if the domain is contained in the domains list will it be included in the results.
            matched = len([s for s in domains if s in hostname]) > 0
            if matched:
                short_desc = ''
                preamble = None
                if info.parent.parent.find_next_sibling("div"):
                    divs = info.parent.parent.find_next_sibling("div").find("div")
                    if divs:
                        spans = divs.find_all("span")
                        for span in spans:
                            if preamble is None:  # preamble is the first span
                                preamble = span.text
                            short_desc += span.text
                result.append(
                    SearchResult(url=href, hostname=hostname, title=title, short_desc=short_desc, preamble=preamble,
                                 selected=True, position=len(result) + 1))
    if len(result) > 10:
        print(f"{len(result)} results found, reducing to 10.")
        result = result[:10]
    return result


def execute_query(search_text):
    headers_dict = {
        'User-Agent': 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/'}

    url = 'https://google.com/search?num=200&q=' + search_text
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
    results_context = []
    position = 0

    # clear the session of previous results.
    session_keys = list(request.session.keys())
    for key in session_keys:
        del request.session[key]

    for search_result in search_results:
        uuid = str(uuid4().hex)
        position += 1
        session_data = build_session_data(search_result, "Google", search_text)
        # add the search results to the session.
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


def build_session_data(search_result, engine, search_text):
    return {
        'search_text': search_text,
        'engine': engine,
        'url': search_result.url,
        'hostname': search_result.hostname,
        'title': search_result.title,
        'short_desc': search_result.short_desc,
        'preamble': search_result.preamble,
        'position': search_result.position
    }


def go_to_selection(request):
    result_id = request.POST.get('result_id', None)
    session_data = request.session.get(result_id)

    # 'global' values
    metrics.search.meta.search_engine.set(session_data.get('engine'))
    metrics.search.meta.search_text.set(session_data.get('search_text'))
    metrics.search.meta.session_id.set(request.session.session_key)

    # 'selected result'
    metrics.search.meta.url_select_timestamp.set(datetime.utcnow())

    # Add search results
    for key, value in request.session.items():
        pos = str(value.get('position'))
        metrics.search.meta.url['url_' + pos].set(value.get('url'))
        metrics.search.meta.hostname['hostname_' + pos].set(value.get('hostname'))
        metrics.search.meta.title['title_' + pos].set(value.get('title'))
        metrics.search.meta.short_description['short_desc_' + pos].set(value.get('short_desc'))
        metrics.search.meta.preamble['preamble_' + pos].set(value.get('preamble'))
        metrics.search.meta.position['position_' + pos].add(int(pos))

        if key == result_id:
            metrics.search.meta.selected['selected_' + pos].set(True)
        else:
            metrics.search.meta.selected['selected_' + pos].set(False)

    pings.action.submit()
    return redirect(session_data.get('url'))
