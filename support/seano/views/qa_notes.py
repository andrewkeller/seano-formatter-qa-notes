from waflib import Task
import datetime
try:
    from html import escape  # python 3.x
except ImportError:
    from cgi import escape  # python 2.x
import json
import re
import subprocess

jira_url_regex = re.compile(r'^https?://[^/]*jira[^/]*/browse/([A-Z]+\-[0-9]+)$')
redmine_url_regex = re.compile(r'^https?://[^/]*redmine[^/]*/issues/([0-9]+)$')
def compile_ticket_url(url):
    if url is None:
        return '<span style="color: red">BAD DEVELOPER NO SECRET WORK</span>'
    m = jira_url_regex.match(url)
    if m:
        return '<a href="' + url + '" target="_blank">' + m.group(1) + '</a>'
    m = redmine_url_regex.match(url)
    if m:
        return '<a href="' + url + '" target="_blank">' + m.group(1) + '</a>'
    bld.fatal("Don't know how to display URL in QA Notes: %s" % (url,))

def get_host_os_version():
    info = subprocess.check_output(['system_profiler', 'SPSoftwareDataType']).splitlines()
    info = [x.strip() for x in info]
    info = [x.partition(':') for x in info]
    info = {x[0].strip() : x[2].strip() for x in info}
    return info['System Version']

def get_host_xcode_version():
    lines = subprocess.check_output(['xcodebuild', '-version']).splitlines()
    return lines[0] + ' (' + lines[1].rpartition('Build version ')[2] + ')'

def get_source_tree_version():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD^{tree}']).strip()

class qa_notes_render_task(Task.Task):
    vars = ['CURRENT_SOURCE_VERSION']

    def keyword(self):
        return 'Rendering QA Notes'

    def __str__(self):
        return ', '.join([node.path_from(node.ctx.launch_node()) for node in self.outputs])

    def _get_elem_uid(self):
        self._next_elem_uid = self._next_elem_uid + 1
        return self._next_elem_uid

    def run(self):
        self._next_elem_uid = 0
        releases = json.loads(self.inputs[0].read())['releases']
        with open(self.outputs[0].abspath(), 'w') as f:
            f.write('''<html><head>''')
            f.write('''<meta charset="utf-8">''')
            f.write('''<meta name="viewport" content="width=device-width, initial-scale=1.0">''')
            f.write('''<title>QA Notes for CE Mac Client v''')
            f.write(escape(releases[0]['name']))
            f.write('''</title><style type="text/css">
* {
    font-family: sans-serif;
    -webkit-text-size-adjust: 100%;
}
a {
    color: #0175bb; /* Bahama */
}
a:visited {
    color: #1997EB; /* Denim */
}
pre {
    overflow: scroll;
    padding: 0.6em;
    margin-left: 1.5em;
    background-color: #F4FAFB; /* Lily White */
    border: 0.05em solid #BDE6FE; /* French Pass */
    border-radius: 0.2em;
}
code {
    display: inline-block;
    font-family: Courier, monospace;
    padding: 0.1em 0.2em 0.1em 0.2em;
    background-color: #F4FAFB; /* Lily White */
    border: 0.05em solid #BDE6FE; /* French Pass */
    border-radius: 0.2em;
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
.rnhover {
    background: #BDE6FE; /* French Pass */
}
.public-release-notes, .internal-release-notes, .testing, .technical {
    margin-left: 1em;
}
p {
    margin-top: 0;
}
ol, ul {
    margin-bottom: 1em;
}
@media (prefers-color-scheme: dark) {
    * {
        background-color: black;
        color: white;
    }
    a {
        color: #8DD2FC; /* Cornflower */
    }
    a:visited {
        color: #E5F5FE; /* Aqua Spring */
    }
    pre {
        background-color: #101030; /* Custom dark blue */
        border: 0.1em solid #07466D; /* Regal Blue */
        border-radius: 0.3em;
    }
    code {
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
    .rnhover {
        background: #0175bb; /* Bahama */
    }
}
</style><script>
function showRelease(id) {
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
}
</script></head><body><h2>QA Notes for CE Mac Client v''')
            f.write(escape(releases[0]['name']))
            f.write('</h2><p>Commit <code class="unimportant-long-sha1">')
            f.write(self.bld.env.CURRENT_SOURCE_VERSION)
            f.write('</code>, built on ')
            f.write(datetime.datetime.today().strftime('%m/%d/%Y at %I:%M %p %Z'))
            f.write('</p><div class="build-uniq-div"><span class="head">Build Uniqueness</span>')
            f.write('<div class="build-uniq-data"><span class="data">Tree <code class="unimportant-long-sha1">')
            f.write(get_source_tree_version())
            f.write('</code></span><span class="data">')
            f.write(get_host_os_version())
            f.write('</span><span class="data">')
            f.write(get_host_xcode_version())
            f.write('</span></div></div>')
            release_count = 0
            for release in releases:
                release_count = release_count + 1
                if release_count > 5:
                    break
                self.write_release(f, release, release_count <= 1)
            f.write('''</body></html>''')
        return 0

    def write_release(self, f, release, is_first_release):
        release_div_id = self.write_release_head(f, release, is_first_release)
        self.write_release_body(f, release, is_first_release, release_div_id)

    def write_release_head(self, f, release, is_first_release):
        release_div_id = self._get_elem_uid()
        f.write('<div class="release-head"><span class="release-name">Changes in ')
        f.write(escape(release['name']))
        f.write('</span><span class="release-since">(since ')
        f.write(escape(' and '.join(release['after'])))
        f.write(')</span>')
        f.write('<span class="show-release" id="show-release-%d" style="display:%s">' \
                '''<a href="javascript:showRelease('%d')">Show</a></span>''' % (
                    release_div_id, 'inline-block' if not is_first_release else 'none', release_div_id))
        f.write('<span class="hide-release" id="hide-release-%d" style="display:%s">' \
                '''<a href="javascript:hideRelease('%d')">Hide</a></span>''' % (
                    release_div_id, 'none' if not is_first_release else 'inline-block', release_div_id))
        f.write('</div>') # end of "release-head" div
        return release_div_id

    def write_release_body(self, f, release, is_first_release, release_body_div_id):
        f.write('<div id="release-body-%d" class="release-body" style="display:%s">' % (
                release_body_div_id, 'none' if not is_first_release else 'block'))
        release_notes_id, qa_notes_id = self.write_release_section_toggles(f)
        self.write_release_notes(f, release, release_notes_id)
        self.write_qa_notes(f, release, qa_notes_id)
        f.write('</div>')

    def write_release_section_toggles(self, f):
        release_notes_id = self._get_elem_uid()
        qa_notes_id = self._get_elem_uid()
        f.write('<div class="release-subhead">')
        f.write('<span class="show-release-notes" id="show-release-notes-%d" style="display:inline-block">' \
                '''<a href="javascript:showReleaseNotes('%d')">Release Notes</a></span>''' % (
                    release_notes_id, release_notes_id))
        f.write('<span class="hide-release-notes" id="hide-release-notes-%d" style="display:none">' \
                '''<a href="javascript:hideReleaseNotes('%d')">Release Notes</a></span>''' % (
                    release_notes_id, release_notes_id))
        f.write('<span class="show-qa-notes" id="show-qa-notes-%d" style="display:none">' \
                '''<a href="javascript:showQaNotes('%d')">QA Notes</a></span>''' % (
                    qa_notes_id, qa_notes_id))
        f.write('<span class="hide-qa-notes" id="hide-qa-notes-%d" style="display:inline-block">' \
                '''<a href="javascript:hideQaNotes('%d')">QA Notes</a></span>''' % (
                    qa_notes_id, qa_notes_id))
        f.write('</div>') # end of "release-subhead" div
        return release_notes_id, qa_notes_id

    def write_release_notes(self, f, release, release_notes_id):
        def write_notes(key, default):
            def write_lst(lst, default=None):
                if not lst:
                    if default:
                        f.write(default)
                    return
                f.write('<ul>')
                for n in lst:
                    styles = ['r%dp%d' % (release_notes_id, t) for t in n['tags']]
                    f.write('<li><span class="')
                    f.write(' '.join(styles))
                    f.write('" onmouseover="')
                    f.write(';'.join(['''Array.prototype.forEach.call(document.getElementsByClassName('%s'), function(e){e.classList.toggle('rnhover', true)})''' % (s,) for s in styles]))
                    f.write('" onmouseleave="')
                    f.write(';'.join(['''Array.prototype.forEach.call(document.getElementsByClassName('%s'), function(e){e.classList.toggle('rnhover', false)})''' % (s,) for s in styles]))
                    f.write('">')
                    f.write(self.bld.seano_markup_line_to_html(n['head']))
                    f.write('</span>')
                    write_lst(n['children'])
                    f.write('</li>')
                f.write('</ul>')
            write_lst(bld.seano_cascade_release_note_trees(release.get('notes', None) or [], key), default)
        f.write('<div id="release-notes-%d" style="display:none">' % (release_notes_id,))
        f.write('<div class="public-release-notes">')
        f.write('<h4>Public Release Notes</h4>')
        write_notes('public-short', '<p><em>No public release notes</em></p>')
        f.write('</div>')
        f.write('<div class="internal-release-notes">')
        f.write('<h4>Internal Release Notes</h4>')
        write_notes('internal-short', '<p><em>No internal release notes</em></p>')
        f.write('</div>')
        f.write('</div>')

    def write_qa_notes(self, f, release, qa_notes_id):
        f.write('<div id="qa-notes-%d">' % (qa_notes_id,))
        if not release['notes']:
            f.write('<p class="testing"><em>No changes</em></p>')
        else:
            f.write('<ul>')
            for note in release['notes']:
                f.write('<li><span class="note-head"><span class="internal-short">')
                head = note.get('internal-short', {}).get('en-US', [None])[0]
                if head and type(head) == dict:
                    head = head.keys()[0]
                f.write(self.bld.seano_markup_line_to_html(head or 'Internal release note missing'))
                f.write('</span>') # internal-short
                for t in note.get('tickets', None) or [None]: # None is used to indicate secret work
                    f.write('<span class="ticket">')
                    f.write(compile_ticket_url(t))
                    f.write('</span>')
                technical = note.get('technical', {}).get('en-US', '')
                if technical:
                    tech_id = self._get_elem_uid()
                    f.write('<span class="ticket show-technical" id="show-technical-%d">' \
                            '''<a href="javascript:showTechnical('%d')">More details</a></span>''' % (
                                tech_id, tech_id))
                    f.write('<span class="ticket hide-technical" id="hide-technical-%d" style="display:none">' \
                            '''<a href="javascript:hideTechnical('%d')">Fewer details</a></span>''' % (
                                tech_id, tech_id))
                f.write('</span>') # note-head
                if technical:
                    f.write('<div class="technical" id="technical-%d" style="display:none">' % (tech_id,))
                    f.write(self.bld.seano_markup_to_html(technical))
                    f.write('</div>')
                f.write('<div class="testing">')
                f.write(self.bld.seano_markup_to_html(note.get('testing', {}).get('en-US', '')
                        or '_QA Notes missing_'))
                f.write('</div></li>')
            f.write('</ul>')
        f.write('</div>')


t = qa_notes_render_task(env=bld.env)
t.set_inputs(bld.get_compiled_seano_db_node())
t.set_outputs(bld.path.find_or_declare('qa-notes.html'))
bld.add_to_group(t)
