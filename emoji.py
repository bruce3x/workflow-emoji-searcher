import sys
from workflow import Workflow, web

from lxml.etree import HTML

HOST = 'https://emojipedia.org'


def extract(result, default='N/A'):
    return result[0] if result else default


def search(keyword):
    resp = web.get('{}/search/?q={}'.format(HOST, keyword))
    resp.raise_for_status()
    html = HTML(resp.text)

    results = []
    items = html.xpath('//ol[@class="search-results"]/li/h2/a')

    for item in items:
        url = item.xpath('./@href')
        emoji = item.xpath('./span/text()')
        title = item.xpath('./text()')

        results.append({
            "url": '{}{}'.format(HOST, extract(url, default="")),
            "emoji": extract(emoji),
            "title": extract(title).strip(),
        })

    return results


def main(wf):
    if wf.args:
        query = wf.args[0]
    else:
        query = None

    if query:
        results = wf.cached_data(query, lambda: search(query), max_age=5 * 60)
    else:
        results = []

    for result in results:
        wf.add_item(
            title=result['emoji'],
            subtitle=result['title'],
            icon='icon.png',
            arg=result['url'],
            valid=True,
            copytext=result['emoji'],
            quicklookurl=result['url'],
        )
    wf.send_feedback()


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))
