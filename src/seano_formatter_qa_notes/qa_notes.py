"""
support/seano/views/qa_notes.py

Infrastructure to convert a seano query output file into what is known as the QA Notes page (single-file HTML+CSS+JS)

The public entry point here is the function named ``compile_qa_notes()``.
"""
import argparse
import datetime
import sys
from .shared.components import *
from .shared.hlist import seano_read_hlist, SeanoUnlocalizedHListNode
from .shared.html_buf import SeanoHtmlBuffer, html_escape as escape
from .shared.markup import SeanoMarkdown, SeanoReStructuredText
from .shared.metacache import SeanoMetaCache
from .shared.schema_plumbing import seano_minimum_descendant_list


class QANotesRenderInfrastructure(object):
    '''
    The render infrastructure has stack-local state.  That means the storage of such state cannot be global, or
    else this infrastructure becomes non-thread-safe (and resetting state between runs becomes more complicated).
    The two other options are to use function-local storage, and class-local storage.  Between those two, class-
    local storage is easier to unit test.  (Not that we have unit tests, but I can dream, right?)
    '''
    def __init__(self):
        self._next_elem_uid = 0

    def compile_ticket_url(self, url):  #pylint: disable=R0201
        if url is None:
            # Visually matches font size of tickets in support/seano/views/shared/components.py, despite
            # this font size being...  larger?  It's probably an illusion caused by use of italics.
            return '<span style="font-size:90%"><em>No ticket associated</em></span>'
        return seano_render_html_ticket(url)

    def _get_elem_uid(self):
        self._next_elem_uid = self._next_elem_uid + 1
        return self._next_elem_uid

    def run(self, srcdata):
        self._next_elem_uid = 0
        cmc = SeanoMetaCache(srcdata)
        with SeanoHtmlBuffer() as f:
            f.write_head('''<title>QA Notes for ''')
            f.write_head(escape(cmc.everything['project_name']['en-US']))
            f.write_head(''' v''')
            f.write_head(escape(cmc.releases[0]['name']))
            f.write_head('''</title>''')
            f.write_css(SeanoReStructuredText('sample text').toHtmlBlock().css) # Write out Pygments' CSS sheet
            f.write_css('''
body {
    font-family: sans-serif;
    -webkit-text-size-adjust: 100%;
}
a {
    color: #0175bb; /* Bahama */
}
a:visited {
    color: #1997EB; /* Denim */
}
blockquote {
    border-left: 0.2em solid #8DD2FC; /* Cornflower */
}
pre, pre.code, code, tt.literal {
    background-color: #F4FAFB; /* Lily White */
    border: 0.05em solid #BDE6FE; /* French Pass */
    border-radius: 0.2em;
}
pre {
    font-size: 110%;
    overflow: scroll;
    padding: 0.6em;
    margin-left: 1.5em;
}
code, tt.literal {
    display: inline-block;
    font-family: Courier, monospace;
    padding: 0 0.1em 0 0.2em;
}
pre > code {
    padding: 0;
    border: none;
}
.unimportant-long-sha1 {
    word-break: break-all;
}

.build-uniq-div {
    background: #D3ECD6; /* Pistachio */
    padding: 0.5em;
    margin-bottom: 1em;
}
.build-uniq-div > .head {
    display: block;
    margin: 0 0 0.5em 0;
}
.build-uniq-div > .build-uniq-data {
    background: white;
}
.build-uniq-div > .build-uniq-data > .data {
    display: inline-block;
    margin: 0.5em 1em 0.5em 1em;
}

.release-head {
    background: #8DD2FC; /* Cornflower */
    padding: 0.5em;
    margin-bottom: 0.2em;
}
.release-head > .release-name {
    display: inline-block;
    font-size: 110%;
    font-weight: bold;
}
.release-head > .release-since {
    display: inline-block;
    margin-left: 1em;
}
.release-head > .show-release, .release-head > .hide-release {
    float: right;
}
.release-head > .show-release > a, .release-head > .hide-release > a {
    color: black;
}

.note-head {
    display: inline-block;
    margin: 0 0 1em 0;
}
.note-head > .internal-short {
    font-weight: bold;
}
.note-head > .ticket {
    display: inline-block;
    margin-left: 1em;
    font-size: 90%;
}
.release-subhead > .show-release-notes, .release-subhead > .show-qa-notes {
    display: inline-block;
    margin-left: 1em;
    margin-bottom: 0.1em;
    padding: 0.2em 0.7em 0.2em 0.7em;
}
.release-subhead > .hide-release-notes, .release-subhead > .hide-qa-notes {
    display: inline-block;
    margin-left: 1em;
    margin-bottom: 0.1em;
    padding: 0.2em 0.7em 0.2em 0.7em;
    background: #BDE6FE; /* French Pass */
}
.note-head > .show-technical, .note-head > .hide-technical {
    font-size: 75%; /* Matches font size of tickets in support/seano/views/shared/components.py */
}
.release-notes-body {
    margin: 1em;
    padding: 1em;
    background: rgb(236,236,236); /* Off-white of background of System Preferences in light mode */
}
.rnhover {
    background: #BDE6FE; /* French Pass */
}
.public-release-notes, .internal-release-notes, .testing, .technical {
    margin-left: 1em;
}
.custsrv-release-notes {
    margin-left: 2em;
}
.custsrv-release-notes > :first-child {
    margin-left: -1em;
}
p {
    margin-top: 0;
}
ol, ul {
    margin-bottom: 1em;
}
.clarification {
    font-weight: normal;
    font-size: 80%;
    font-style: italic;
    color: grey;
}
@media (prefers-color-scheme: dark) {
    body {
        background-color: #292A2F; /* Xcode's off-black background color */
        color: white;
    }
    a {
        color: #8DD2FC; /* Cornflower */
    }
    a:visited {
        color: #E5F5FE; /* Aqua Spring */
    }
    blockquote {
        border-left: 0.2em solid #0175bb; /* Bahama */
    }
    pre, pre.code, code, tt.literal {
        background-color: #454545; /* Custom dark gray */
        border: 0.1em solid #07466D; /* Regal Blue */
        border-radius: 0.3em;
    }
    pre > code {
        border: none;
    }
    .build-uniq-div, .build-uniq-div > .head {
        background: #38823E; /* Goblin */
    }
    .build-uniq-div > .build-uniq-data {
        background: black;
    }
    .release-head,
    .release-head > .release-name,
    .release-head > .release-since,
    .release-head > .show-release > a,
    .release-head > .hide-release > a {
        background-color: #0175bb; /* Bahama */
    }
    .release-head > .show-release > a, .release-head > .hide-release > a {
        color: white;
    }
    .release-subhead > .hide-release-notes, .release-subhead > .hide-qa-notes {
        background: #8DD2FC; /* Cornflower */
    }
    .release-subhead > .hide-release-notes > a, .release-subhead > .hide-qa-notes > a {
        color: black;
        background: #8DD2FC; /* Cornflower */
    }
    .release-notes-body {
        background-color: rgb(63,65,68); /* Cocoa window title bar color in dark mode */
    }
    .rnhover {
        background: #0175bb; /* Bahama */
    }
}''')
            f.write_js('''function showRelease(id) {
    document.getElementById('show-release-' + id).style.display = 'none';
    document.getElementById('hide-release-' + id).style.display = 'inline-block';
    document.getElementById('release-body-' + id).style.display = 'block';
}
function hideRelease(id) {
    document.getElementById('show-release-' + id).style.display = 'inline-block';
    document.getElementById('hide-release-' + id).style.display = 'none';
    document.getElementById('release-body-' + id).style.display = 'none';
}
function showReleaseNotes(id) {
    document.getElementById('show-release-notes-' + id).style.display = 'none';
    document.getElementById('hide-release-notes-' + id).style.display = 'inline-block';
    document.getElementById('release-notes-' + id).style.display = 'block';
}
function hideReleaseNotes(id) {
    document.getElementById('show-release-notes-' + id).style.display = 'inline-block';
    document.getElementById('hide-release-notes-' + id).style.display = 'none';
    document.getElementById('release-notes-' + id).style.display = 'none';
}
function showQaNotes(id) {
    document.getElementById('show-qa-notes-' + id).style.display = 'none';
    document.getElementById('hide-qa-notes-' + id).style.display = 'inline-block';
    document.getElementById('qa-notes-' + id).style.display = 'block';
}
function hideQaNotes(id) {
    document.getElementById('show-qa-notes-' + id).style.display = 'inline-block';
    document.getElementById('hide-qa-notes-' + id).style.display = 'none';
    document.getElementById('qa-notes-' + id).style.display = 'none';
}
function showTechnical(id) {
    document.getElementById('show-technical-' + id).style.display = 'none';
    document.getElementById('hide-technical-' + id).style.display = 'inline-block';
    document.getElementById('technical-' + id).style.display = 'block';
}
function hideTechnical(id) {
    document.getElementById('show-technical-' + id).style.display = 'inline-block';
    document.getElementById('hide-technical-' + id).style.display = 'none';
    document.getElementById('technical-' + id).style.display = 'none';
}''')
            f.write_body('''<h2>QA Notes for ''')
            f.write_body(escape(cmc.everything['project_name']['en-US']))
            f.write_body(' v')
            f.write_body(escape(cmc.releases[0]['name']))
            f.write_body('</h2><p>Commit <code class="unimportant-long-sha1">')
            # IMPROVE: ABK: This lies when the working directory is dirty.  How best to fix?
            f.write_body(escape(cmc.releases[0].get('commit', None)                         # Normal committed work
                                or (len(cmc.releases) > 1 and cmc.releases[1].get('commit', None)) # Dirty checkout
                                or '???'))                                                       # Unexpected error
            f.write_body('</code>, built on ')
            # IMPROVE: ABK: This line makes the output non-deterministic.  Is that bad?
            # IMPROVE: ABK: Yes, that is bad.  The date should be present in the query output.
            f.write_body(datetime.datetime.today().strftime('%m/%d/%Y at %I:%M %p %Z'))
            f.write_body('</p>')
            bu = seano_read_hlist([cmc.everything], ['build-uniqueness-list-md', 'build-uniqueness-list-rst'], ['en-US'])
            if bu:
                f.write_body('<div class="build-uniq-div"><span class="head">Build Uniqueness</span>')
                f.write_body('<div class="build-uniq-data">')
                for data in sorted([x.element.toHtmlLine().html for x in bu], key=lambda s: s.lower()):
                    f.write_body('<span class="data">')
                    f.write_body(data)
                    f.write_body('</span>')
                f.write_body('</div></div>')
            release_count = 0
            for release in cmc.releases:
                release_count = release_count + 1
                if release_count > 5:
                    break
                self.write_release(f, release, cmc, release_count <= 1)

            return f.all_data()

    def write_release(self, f, release, cmc, is_first_release):
        release_div_id = self.write_release_head(f, release, cmc, is_first_release)
        self.write_release_body(f, release, is_first_release, release_div_id)

    def write_release_head(self, f, release, cmc, is_first_release):
        release_div_id = self._get_elem_uid()
        f.write_body('<div class="release-head"><span class="release-name">Changes in ')
        f.write_body(escape(release['name']))
        f.write_body('</span><span class="release-since">(since ')
        bag = [x['name'] for x in release['after']]
        bag = seano_minimum_descendant_list(bag, cmc)
        f.write_body(escape(' and '.join(bag) or 'the dawn of time'))
        f.write_body(')</span>')
        f.write_body('<span class="show-release" id="show-release-%d" style="display:%s">' \
                     '''<a href="javascript:showRelease('%d')">Show</a></span>''' % (
                         release_div_id, 'inline-block' if not is_first_release else 'none', release_div_id))
        f.write_body('<span class="hide-release" id="hide-release-%d" style="display:%s">' \
                     '''<a href="javascript:hideRelease('%d')">Hide</a></span>''' % (
                         release_div_id, 'none' if not is_first_release else 'inline-block', release_div_id))
        f.write_body('</div>') # end of "release-head" div
        return release_div_id

    def write_release_body(self, f, release, is_first_release, release_body_div_id):
        f.write_body('<div id="release-body-%d" class="release-body" style="display:%s">' % (
                         release_body_div_id, 'none' if not is_first_release else 'block'))
        release_notes_id, qa_notes_id = self.write_release_section_toggles(f)
        self.write_release_notes(f, release, release_notes_id)
        self.write_qa_notes(f, release, qa_notes_id)
        f.write_body('</div>')

    def write_release_section_toggles(self, f):
        release_notes_id = self._get_elem_uid()
        qa_notes_id = self._get_elem_uid()
        f.write_body('<div class="release-subhead">')
        f.write_body('<span class="show-release-notes" id="show-release-notes-%d" style="display:inline-block">' \
                     '''<a href="javascript:showReleaseNotes('%d')">Release Notes</a></span>''' % (
                         release_notes_id, release_notes_id))
        f.write_body('<span class="hide-release-notes" id="hide-release-notes-%d" style="display:none">' \
                     '''<a href="javascript:hideReleaseNotes('%d')">Release Notes</a></span>''' % (
                         release_notes_id, release_notes_id))
        f.write_body('<span class="show-qa-notes" id="show-qa-notes-%d" style="display:none">' \
                     '''<a href="javascript:showQaNotes('%d')">QA Notes</a></span>''' % (
                         qa_notes_id, qa_notes_id))
        f.write_body('<span class="hide-qa-notes" id="hide-qa-notes-%d" style="display:inline-block">' \
                     '''<a href="javascript:hideQaNotes('%d')">QA Notes</a></span>''' % (
                         qa_notes_id, qa_notes_id))
        f.write_body('</div>') # end of "release-subhead" div
        return release_notes_id, qa_notes_id

    def write_release_notes(self, f, release, release_notes_id): #pylint: disable=R0201
        def render_mouse_hover_toggle_logic(identifiers):
            # Here, we expect that we are within the attribute list of the start of an HTML element of some kind.
            # Here, we add the class, onmouseover, and onmouseleave elements.
            # The caller is expected to close this element (i.e., write the '>')
            return ''.join([
                ' class="',
                ' '.join(identifiers),
                '" onmouseover="',
                ';'.join(['''Array.prototype.forEach.call(document.getElementsByClassName('%s'), function(e){e.classList.toggle('rnhover', true)})''' % (s,) for s in identifiers]), #pylint: disable=C0301
                '" onmouseleave="',
                ';'.join(['''Array.prototype.forEach.call(document.getElementsByClassName('%s'), function(e){e.classList.toggle('rnhover', false)})''' % (s,) for s in identifiers]), #pylint: disable=C0301
                '"',
            ])

        def write_hlist(hlist, default, is_blob_field=False, include_tickets=False):
            if not hlist:
                f.write_body(default)
                return
            def block_formatter(node):
                base_func = seano_html_hlist_blob_formatter_simple
                result = base_func(node=node)
                styles = ['r%dp%s' % (release_notes_id, id) for id in node.note_ids]
                return '<div' + render_mouse_hover_toggle_logic(styles) + '>' + result + '</div>'
            def line_formatter(node):
                base_func = seano_html_hlist_line_formatter_text_with_tickets(notes=release.get('notes') or []) if include_tickets \
                    else seano_html_hlist_line_formatter_simple
                result = base_func(node=node)
                styles = ['r%dp%s' % (release_notes_id, id) for id in node.element.tags]
                return '<span' + render_mouse_hover_toggle_logic(styles) + '>' + result + '</span>'
            f.write_body(seano_render_html_hlist(hlist, is_blob_field=is_blob_field, block_formatter=block_formatter, line_formatter=line_formatter))
        f.write_body('<div id="release-notes-%d" class="release-notes-body" style="display:none">' %(release_notes_id,))
        f.write_body('<div class="public-release-notes">')
        backstory_clarification = ''
        if any([x.get('is-copied-from-backstory') for x in release.get('notes') or []]):
            backstory_clarification = ' <span class="clarification">(includes backstories)</span>'
        f.write_body('<h4>Public Release Notes' + backstory_clarification + '</h4>')
        write_hlist(hlist=seano_read_hlist(notes=release.get('notes') or [],
                                          keys=['customer-short-loc-hlist-md', 'customer-short-loc-hlist-rst'],
                                          localizations=['en-US']),
                    default='<p><em>No public release notes</em></p>')
        f.write_body('</div>')
        f.write_body('<div class="internal-release-notes">')
        f.write_body('<h4>Internal Release Notes</h4>')
        write_hlist(hlist=seano_read_hlist(notes=[x for x in release.get('notes') or [] if not x.get('is-copied-from-backstory')],
                                          keys=['employee-short-loc-hlist-md', 'employee-short-loc-hlist-rst'],
                                          localizations=['en-US']),
                    default='<p><em>No internal release notes</em></p>',
                    include_tickets=True)
        f.write_body('</div>')
        f.write_body('<div class="custsrv-release-notes">')
        f.write_body('<h4>Member Care Notes</h4>')
        write_hlist(hlist=seano_read_hlist(notes=[x for x in release.get('notes') or [] if not x.get('is-copied-from-backstory')],
                                          keys=['mc-technical-loc-md', 'mc-technical-loc-rst'],
                                          localizations=['en-US']),
                    is_blob_field=True,
                    default='<p><em>No Member Care notes</em></p>')
        f.write_body('</div>')
        f.write_body('</div>')

    def write_qa_notes(self, f, release, qa_notes_id):
        f.write_body('<div id="qa-notes-%d">' % (qa_notes_id,))
        notes_new_in_this_release = [x for x in release['notes'] if not x.get('is-copied-from-backstory')]
        if not release['notes']:
            f.write_body('<p class="testing"><em>No changes</em></p>')
        elif not notes_new_in_this_release:
            f.write_body('<p class="testing"><em>No changes, however some release notes were repeated '
                         'from earlier work</em></p>')
        else:
            f.write_body('<ul>')
            for note in notes_new_in_this_release:
                f.write_body('<li><span class="note-head"><span class="internal-short">')
                head = seano_read_hlist([note], ['employee-short-loc-hlist-md', 'employee-short-loc-hlist-rst'], ['en-US']).first()
                f.write_body(head.toHtmlLine().html or 'Internal release note missing')
                f.write_body('</span>') # employee-short-loc-hlist-*
                for t in note.get('tickets', None) or [None]: # None is used to indicate secret work
                    f.write_body('<span class="ticket">')
                    f.write_body(self.compile_ticket_url(t))
                    f.write_body('</span>')
                technical = seano_read_hlist([note], ['employee-technical-loc-md', 'employee-technical-loc-rst'], ['en-US'])
                if technical:
                    tech_id = self._get_elem_uid()
                    f.write_body('<span class="ticket show-technical" id="show-technical-%d">' \
                                 '''<a href="javascript:showTechnical('%d')">More details</a></span>''' % (
                                     tech_id, tech_id))
                    f.write_body('<span class="ticket hide-technical" id="hide-technical-%d" style="display:none">' \
                                 '''<a href="javascript:hideTechnical('%d')">Fewer details</a></span>''' % (
                                     tech_id, tech_id))
                f.write_body('</span>') # note-head
                if technical:
                    f.write_body('<div class="technical" id="technical-%d" style="display:none">' % (tech_id,))
                    f.write_body(seano_render_html_hlist(technical, is_blob_field=True))
                    f.write_body('</div>')
                f.write_body('<div class="testing">')
                f.write_body(seano_render_html_hlist(seano_read_hlist([note], ['qa-technical-loc-md', 'qa-technical-loc-rst'], ['en-US']), is_blob_field=True)
                             or SeanoMarkdown('*QA Notes missing*').toHtmlBlock().html)
                f.write_body('</div></li>')
            f.write_body('</ul>')
        f.write_body('</div>')


def format_qa_notes(*args):
    '''
    Given a Json blob (in serialized form), return the contents of the corresponding QA Notes page.

    The QA Notes page is implemented using HTML+CSS+JS; as such, if you are going to save it to a file, you probably
    want to use a ``.html`` extension.
    '''
    parser = argparse.ArgumentParser()
    parser.prog = ' '.join([parser.prog, 'format', 'qa_notes'])
    parser.add_argument('--src', action='store', default='-', help='Input file; use a single hyphen for stdin; default is to use stdin')
    parser.add_argument('--out', action='store', default='-', help='Output file; use a single hyphen for stdout; default is to use stdout')

    ns = parser.parse_args(args)

    if ns.src in ['-']:
        data = sys.stdin.read()
    else:
        with open(ns.src, 'r') as f:
            data = f.read()

    result = QANotesRenderInfrastructure().run(data)

    if ns.out in ['-']:
        sys.stdout.write(result)
    else:
        with open(ns.out, 'w') as f:
            f.write(result)
