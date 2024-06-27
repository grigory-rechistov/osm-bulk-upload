import sys
import xml.etree.cElementTree as ElementTree
from oauthcli import OpenStreetMapAuth


class HTTPError(Exception):
    pass


class OSM_API(object):
    client_id = 'w2dn9_-3kWlROhfmsY8giTIC1XiewJCijZskbF8lltk'
    client_secret = 'q2DThNZJcFBA12STvmvXOz9zMBdr0zvkCgiLkX31tp0'

    def __init__(self):
        self.auth = OpenStreetMapAuth(
            self.client_id, self.client_secret, ['read_prefs', 'write_api'])
        self.auth.auth_server(token_test=lambda r: r.get('user/details'))
        self.changeset = None
        self.progress_msg = None

    def __del__(self):
        if False and self.changeset is not None:
            self.close_changeset()

    def msg(self, mesg):
        sys.stderr.write("\r%s…                        " % (self.progress_msg))
        sys.stderr.write("\r%s… %s" % (self.progress_msg, mesg))
        sys.stderr.flush()

    def _run_request(self, method, url, body=None, progress=0,
                     content_type="text/xml"):
        headers = {}
        if body:
            headers["Content-Type"] = content_type

        response = self.auth.request(method, url, data=body, headers=headers)
        if response.status_code != 200:
            err = response.text
            raise HTTPError(response.status_code, "{} ({})".format(
                response.status_code, response.url), err)
        return response.text

    def create_changeset(self, created_by, comment, source=None, url=None):
        if self.changeset is not None:
            raise RuntimeError("Changeset already opened")
        self.progress_msg = "I'm creating the changeset"
        self.msg("")
        root = ElementTree.Element("osm")
        element = ElementTree.SubElement(root, "changeset")
        if url:
            ElementTree.SubElement(element, "tag", {"k": "url", "v": url})
        ElementTree.SubElement(element, "tag", {"k": "import", "v": "yes"})
        ElementTree.SubElement(element, "tag", {"k": "created_by", "v": created_by})
        ElementTree.SubElement(element, "tag", {"k": "comment", "v": comment})
        if source:
            ElementTree.SubElement(element, "tag", {"k": "source", "v": source})
        body = ElementTree.tostring(root, "utf-8")
        reply = self._run_request("PUT", "changeset/create", body)
        changeset = int(reply.strip())
        self.msg("done.\nChangeset ID: %i" % (changeset))
        sys.stderr.write("\n")
        self.changeset = changeset

    def upload(self, change):
        if self.changeset is None:
            raise RuntimeError("Changeset not opened")
        self.progress_msg = "Now I'm sending changes"
        self.msg("")
        for operation in change:
            if operation.tag not in ("create", "modify", "delete"):
                continue
            for element in operation:
                element.attrib["changeset"] = str(self.changeset)
        body = ElementTree.tostring(change, "utf-8")
        reply = self._run_request(
            "POST", "changeset/{}/upload".format(self.changeset), body, 1)
        self.msg("done.")
        sys.stderr.write("\n")
        return reply

    def close_changeset(self):
        if self.changeset is None:
            raise RuntimeError("Changeset not opened")
        self.progress_msg = "Closing"
        self.msg("")
        self._run_request("PUT", "changeset/{}/close".format(self.changeset))
        self.changeset = None
        self.msg("done, too.")
        sys.stderr.write("\n")

    def get_changeset_tags(self):
        if self.changeset is None:
            raise RuntimeError("Changeset not opened")
        self.progress_msg = u"Getting changeset tags"
        self.msg(u"")
        reply = self._run_request(
            "GET", "changeset/{}".format(self.changeset), None)
        root = ElementTree.XML(reply)
        if root.tag != "osm" or root[0].tag != "changeset":
            sys.stderr.write("API returned unexpected XML!\n")
            sys.exit(1)

        for element in root[0]:
            if element.tag == "tag" and "k" in element.attrib and \
                    "v" in element.attrib:
                self.tags[element.attrib["k"]] = element.attrib["v"]

        self.msg(u"done.")
        sys.stderr.write('\n')

    def set_changeset_tags(self):
        self.progress_msg = u"Setting new changeset tags"
        self.msg(u"")

        root = ElementTree.Element("osm")
        element = ElementTree.SubElement(root, "changeset")
        for key in self.tags:
            ElementTree.SubElement(
                element, "tag", {"k": key, "v": self.tags[key]})

        self._run_request(
            "PUT", "changeset/{}".format(self.changeset),
            ElementTree.tostring(root, "utf-8"))

        self.msg(u"done, too.")
        sys.stderr.write('\n')
