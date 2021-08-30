from django.shortcuts import render
from django.shortcuts import redirect
import requests
from bs4 import BeautifulSoup
from uuid import uuid4
from datetime import datetime
from urllib.parse import urlparse

from . import metrics, pings


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
    # TODO GLE is shuffle needed.  If shuffled will need to reset position field
    # random.shuffle(search_results)
    results_context = []
    position = 0
    for search_result in search_results:
        uuid = str(uuid4().hex)
        position += 1
        session_data = build_session_data(search_result, "Google", search_text)
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
    metrics.search.search_engine.set(session_data.get('engine'))
    metrics.search.search_text.set(session_data.get('search_text'))
    metrics.search.session_id.set(request.session.session_key)

    # 'selected result'
    metrics.search.url_select_timestamp.set(datetime.utcnow())

    metrics.search.selection.record(metrics.search.SelectionExtra(url=session_data.get('url')))
    metrics.search.selection.record(metrics.search.SelectionExtra(hostname=session_data.get('hostname')))
    metrics.search.selection.record(metrics.search.SelectionExtra(title=session_data.get('title')))
    metrics.search.selection.record(metrics.search.SelectionExtra(short_description=session_data.get('short_desc')))
    metrics.search.selection.record(metrics.search.SelectionExtra(preamble=session_data.get('preamble', '')))
    metrics.search.selection.record(metrics.search.SelectionExtra(position=session_data.get('position')))
    metrics.search.selection.record(metrics.search.SelectionExtra(selected=True))

    position = str(session_data.get('position'))
    # for i in range(2):
    #     unselected_pos = str(i)
    #     metrics.search.unselected_url['unselected_' + unselected_pos].set("dummy_url" + unselected_pos)
    #     metrics.search.unselected_hostname['unselected_' + unselected_pos].set("dummy_hostname" + unselected_pos)
    #     metrics.search.unselected_title['unselected_' + unselected_pos].set("dummy_title" + unselected_pos)
    #     metrics.search.unselected_short_description['unselected_' + unselected_pos].set("dummy_descr" + unselected_pos)
    #     metrics.search.unselected_preamble['unselected_' + unselected_pos].set("dummy_pre" + unselected_pos)
    #     metrics.search.unselected_position['unselected_' + unselected_pos].set(unselected_pos)

    pings.action.submit()
    return redirect(session_data.get('url'))
