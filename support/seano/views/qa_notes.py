"""
support/seano/views/qa_notes.py

Infrastructure to convert a seano query output file into what is known as the QA Notes page (single-file HTML+CSS+JS)

The public entry point here is the function named ``compile_qa_notes()``.
"""
import datetime
import json
from .shared.hlist import seano_cascade_hlist
from .shared.html_buf import SeanoHtmlBuffer, html_escape as escape
from .shared.links import get_ticket_display_name
from .shared.markup import rst_to_html, rst_line_to_html


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
            return '<span style="color: red">BAD DEVELOPER NO SECRET WORK</span>'
        return '<a href="' + url + '" target="_blank">' + get_ticket_display_name(url) + '</a>'

    def _get_elem_uid(self):
        self._next_elem_uid = self._next_elem_uid + 1
        return self._next_elem_uid

    def run(self, srcdata):
        self._next_elem_uid = 0
        srcjson = json.loads(srcdata)
        releases = srcjson['releases']
        with SeanoHtmlBuffer() as f:
            f.write_head('''<title>QA Notes for ''')
            f.write_head(escape(srcjson['project_name']['en-US']))
            f.write_head(''' v''')
            f.write_head(escape(releases[0]['name']))
            f.write_head('''</title>''')
            f.write_css(rst_to_html('sample text').css) # Write out Pygments' CSS sheet
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
pre, pre.code, code {
    background-color: #F4FAFB; /* Lily White */
    border: 0.05em solid #BDE6FE; /* French Pass */
    border-radius: 0.2em;
}
pre {
    overflow: scroll;
    padding: 0.6em;
    margin-left: 1.5em;
}
code {
    display: inline-block;
    font-family: Courier, monospace;
    padding: 0.1em 0.2em 0.1em 0.2em;
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
    pre, pre.code, code {
        background-color: #101030; /* Custom dark blue */
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
            f.write_body(escape(srcjson['project_name']['en-US']))
            f.write_body(' v')
            f.write_body(escape(releases[0]['name']))
            f.write_body('</h2><p>Commit <code class="unimportant-long-sha1">')
            # IMPROVE: ABK: This lies when the working directory is dirty.  How best to fix?
            f.write_body(escape(releases[0].get('commit', None)                              # Normal committed work
                                or (len(releases) > 1 and releases[1].get('commit', None))   # Dirty working directory
                                or '???'))                                                   # Unexpected error
            f.write_body('</code>, built on ')
            # IMPROVE: ABK: This line makes the output non-deterministic.  Is that bad?
            f.write_body(datetime.datetime.today().strftime('%m/%d/%Y at %I:%M %p %Z'))
            f.write_body('</p>')
            if srcjson.get('build-uniqueness-list-rst'):
                f.write_body('<div class="build-uniq-div"><span class="head">Build Uniqueness</span>')
                f.write_body('<div class="build-uniq-data">')
                for data in sorted(srcjson['build-uniqueness-list-rst'], key=lambda s: s.lower()):
                    f.write_body('<span class="data">')
                    f.write_body(rst_line_to_html(data).html)
                    f.write_body('</span>')
                f.write_body('</div></div>')
            release_count = 0
            for release in releases:
                release_count = release_count + 1
                if release_count > 5:
                    break
                self.write_release(f, release, release_count <= 1)

            return f.all_data()

    def write_release(self, f, release, is_first_release):
        release_div_id = self.write_release_head(f, release, is_first_release)
        self.write_release_body(f, release, is_first_release, release_div_id)

    def write_release_head(self, f, release, is_first_release):
        release_div_id = self._get_elem_uid()
        f.write_body('<div class="release-head"><span class="release-name">Changes in ')
        f.write_body(escape(release['name']))
        f.write_body('</span><span class="release-since">(since ')
        f.write_body(escape(' and '.join(release['after']) or 'the dawn of time'))
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
        def write_mouse_hover_toggle_logic(identifiers):
            # Here, we expect that we are within the attribute list of the start of an HTML element of some kind.
            # Add class, onmouseover, and onmouseleave:
            f.write_body(' class="')
            f.write_body(' '.join(identifiers))
            f.write_body('" onmouseover="')
            f.write_body(';'.join(['''Array.prototype.forEach.call(document.getElementsByClassName('%s'), function(e){e.classList.toggle('rnhover', true)})''' % (s,) for s in identifiers])) #pylint: disable=C0301
            f.write_body('" onmouseleave="')
            f.write_body(';'.join(['''Array.prototype.forEach.call(document.getElementsByClassName('%s'), function(e){e.classList.toggle('rnhover', false)})''' % (s,) for s in identifiers])) #pylint: disable=C0301
            f.write_body('"')
            # Here, we have finished writing all of our attributes.
            # The caller is expected to close this element (i.e., write the '>')
        def write_hlist(key, default):
            def write_lst(lst, default=None):
                if not lst:
                    if default:
                        f.write_body(default)
                    return
                f.write_body('<ul>')
                for n in lst:
                    styles = ['r%dp%d' % (release_notes_id, t) for t in n['tags']]
                    f.write_body('<li><span')
                    write_mouse_hover_toggle_logic(styles)
                    f.write_body('>')
                    f.write_body(rst_line_to_html(n['head']).html)
                    f.write_body('</span>')
                    write_lst(n['children'])
                    f.write_body('</li>')
                f.write_body('</ul>')
            write_lst(seano_cascade_hlist(release.get('notes', None) or [], key=key), default)
        def write_plist(keys, default):
            did_write_notes = False
            # ABK: The tag here is mirroring the behavior of seano_cascade_hlist()
            tag = -1
            for n in release.get('notes', None) or []:
                tag = tag + 1 # Assume notes are traversed in the same order as in seano_cascade_hlist() (they are)
                style = 'r%dp%d' % (release_notes_id, tag)
                for k in keys:
                    # ABK: By deliberately checking for this key first, we allow it to exist but be empty,
                    #      enabling the writer of the documentation to effectively remove all mention of
                    #      this note from this documentation view.
                    if k in n:
                        txt = (n[k] or {}).get('en-US', None) or ''
                        if txt:
                            f.write_body('<div')
                            write_mouse_hover_toggle_logic([style])
                            f.write_body('>')
                            if isinstance(txt, list):
                                def write_lst(lst):
                                    f.write_body('<ul>')
                                    for node in lst:
                                        f.write_body('<li>')
                                        f.write_body(rst_line_to_html(node['head']).html)
                                        c = node['children']
                                        if c:
                                            write_lst(c)
                                        f.write_body('</li>')
                                    f.write_body('</ul>')
                                for node in seano_cascade_hlist([n], k):
                                    f.write_body('<p>')
                                    f.write_body(rst_line_to_html(node['head']).html)
                                    c = node['children']
                                    if c:
                                        write_lst(c)
                                    f.write_body('</p>\n')
                            else: # Assume string
                                f.write_body(rst_to_html(txt).html)
                            f.write_body('</div>')
                            did_write_notes = True
                        break
            if not did_write_notes:
                f.write_body(default)
        f.write_body('<div id="release-notes-%d" class="release-notes-body" style="display:none">' %(release_notes_id,))
        f.write_body('<div class="public-release-notes">')
        f.write_body('<h4>Public Release Notes</h4>')
        write_hlist(key='customer-short-loc-hlist-rst', default='<p><em>No public release notes</em></p>')
        f.write_body('</div>')
        f.write_body('<div class="internal-release-notes">')
        f.write_body('<h4>Internal Release Notes</h4>')
        write_hlist(key='employee-short-loc-hlist-rst', default='<p><em>No internal release notes</em></p>')
        f.write_body('</div>')
        f.write_body('<div class="custsrv-release-notes">')
        f.write_body('<h4>Customer Service Notes</h4>')
        write_plist(keys=['cs-technical-loc-rst', 'employee-short-loc-hlist-rst'],
                    default='<p><em>No Customer Service notes</em></p>')
        f.write_body('</div>')
        f.write_body('</div>')

    def write_qa_notes(self, f, release, qa_notes_id):
        f.write_body('<div id="qa-notes-%d">' % (qa_notes_id,))
        if not release['notes']:
            f.write_body('<p class="testing"><em>No changes</em></p>')
        else:
            f.write_body('<ul>')
            for note in release['notes']:
                f.write_body('<li><span class="note-head"><span class="internal-short">')
                head = note.get('employee-short-loc-hlist-rst', {}).get('en-US', [None])[0]
                if head and isinstance(head, dict):
                    head = list(head.keys())[0]
                f.write_body(rst_line_to_html(head or 'Internal release note missing').html)
                f.write_body('</span>') # employee-short-loc-hlist-rst
                for t in note.get('tickets', None) or [None]: # None is used to indicate secret work
                    f.write_body('<span class="ticket">')
                    f.write_body(self.compile_ticket_url(t))
                    f.write_body('</span>')
                technical = note.get('employee-technical-loc-rst', {}).get('en-US', '')
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
                    f.write_body(rst_to_html(technical).html)
                    f.write_body('</div>')
                f.write_body('<div class="testing">')
                f.write_body(rst_to_html(note.get('employee-testing-loc-rst', {}).get('en-US', '')
                                         or '`QA Notes missing`').html)
                f.write_body('</div></li>')
            f.write_body('</ul>')
        f.write_body('</div>')


def compile_qa_notes(srcdata):
    '''
    Given a Json blob (in serialized form), return the contents of the corresponding QA Notes page.

    The QA Notes page is implemented using HTML+CSS+JS; as such, if you are going to save it to a file, you probably
    want to use a ``.html`` extension.
    '''
    return QANotesRenderInfrastructure().run(srcdata)
