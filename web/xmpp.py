__author__ = 'jbn'

import logging
import sleekxmpp
from sleekxmpp.xmlstream.jid import JID
import daemon
from xml.etree import cElementTree as ET
logging.basicConfig(level=logging.ERROR, format="%(levelname)-8s %(message)s")
import sys

class FordropXmpp(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, verbose=False, priority=0):
        sleekxmpp.ClientXMPP.__init__(self, jid.full, password)
        self.jid = jid.full
        self.priority = priority
        self.verbose = verbose
        self.register_plugin('xep_0004')
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0060')
        self.add_event_handler("session_start", self.start)

    def run(self, server, threaded=False):
        self.verbose_print("==> Connecting to %s as %s.." % (server, self.jid))
        self.connect((server, 5222))
        self.process(threaded=threaded)

    def start(self, event):
        self.verbose_print("==> Connected!")
        self.verbose_print("==> Fetching roster")
        self.get_roster()
        self.send_presence(ppriority=self.priority)
        self.verbose_print("==> Send priority %i for this connection\n\n" % self.priority)

    def pubsub_event_handler(self, xml):
        for item in xml.findall('{http://jabber.org/protocol/pubsub#event}event/{http://jabber.org/protocol/pubsub#event}items/{http://jabber.org/protocol/pubsub#event}item'):
            for n in item.iter('{http://jabber.org/protocol/pubsub#event}event'):
                print "%s recieved event: %s" % (self.jid, n.text)

    def get_subscriptions(self):
        nodes_iq = self['xep_0060'].get_subscriptions('pubsub.red.local', block=True)
        for node in nodes_iq.findall('{http://jabber.org/protocol/pubsub}pubsub/{http://jabber.org/protocol/pubsub}subscriptions/{http://jabber.org/protocol/pubsub}subscription'):
            print "%s has subscribed to node %s, status is %s" % (node.get('jid'), node.get('node'), node.get('subscription'))

    def verbose_print(self, msg):
        if self.verbose:
            print msg

    def safe_disconnect(self):
        self.verbose_print("\n==> Disconnecting..")
        import threading
        self.disconnect()
        for thread in threading.enumerate():
            if thread is not threading.current_thread():
                thread.join()
        self.verbose_print("==> Disconnected!")

if __name__ == "__main__" :
    sys.exit()