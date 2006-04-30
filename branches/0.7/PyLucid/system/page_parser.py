#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Der Parser füllt eine CMS Seite mit leben ;)
Parsed die lucid-Tags/Funktionen, führt diese aus und fügt das Ergebnis in die Seite ein.
"""

__version__="0.1.4"

__history__="""
v0.1.4
    - apply_markup kommt mit markup id oder richtigen namen klar
v0.1.3
    - textile Parser erhält nun auch die PyLucid-Objekt. page_msg ist hilfreich zum debuggen des Parsers ;)
v0.1.2
    - Bug 1297263: "Can't use textile-Markup (maximum recursion limit exceeded)":
        Nun wird zuerst das Markup angewendet und dann erst die lucidTag's aufgelöst
v0.1.1
    - parser.handle_function(): toleranter wenn kein String vom Modul zurück kommt
    - Versionsnummer geändert
v0.1.0
    - Erste Version: Komplett neugeschrieben. Nachfolge vom pagerender.py
"""

__todo__ = """
in apply_markup sollte nur noch mit markup IDs erwartet werden. Solange aber die Seiten keine IDs,
sondern die richtigen Namen verwenden geht das leider noch nicht :(
"""

import sys, cgi, re, time



class render:
    """
    Parsed die Seite und wendes das Markup an.
    """
    def __init__(self, request, response):
        self.request        = request
        self.response       = response

        # shorthands
        self.page_msg       = request.page_msg
        self.db             = request.db
        self.session        = request.session
        self.preferences    = request.preferences
        self.environ        = request.environ
        self.URLs           = request.URLs
        self.tools          = request.tools

    #~ def render_page(self):
        #~ """ Baut die Seite zusammen """
        #~ template_data = self.db.side_template_by_id(self.session["page_id"])
        #~ self.response.write(template_data)
        #~ self.parser.parse(template_data, self.response)

    def render( self, side_data ):

        side_content = self.apply_markup( side_data["content"], side_data["markup"] )

        self.parser.tag_data["page_name"]           = cgi.escape( side_data["name"] )
        self.parser.tag_data["page_title"]          = cgi.escape( side_data["title"] )
        self.parser.tag_data["page_last_modified"]  = self.tools.convert_date_from_sql(
            side_data["lastupdatetime"], format = "preferences"
        )
        self.parser.tag_data["page_datetime"]       = self.tools.convert_date_from_sql(
            side_data["lastupdatetime"], format = "DCTERMS.W3CDTF"
        )
        self.parser.tag_data["page_keywords"]       = side_data["keywords"]
        self.parser.tag_data["page_description"]    = side_data["description"]

        if self.request.args.has_key("command"):
            # Ein Kommando soll ausgeführt werden -> Interne Seite
            self.parser.tag_data["robots"] = self.config.system.robots_tag["internal_pages"]
        else:
            self.parser.tag_data["robots"] = self.config.system.robots_tag["content_pages"]

        return side_content


    def apply_markup( self, content, markup ):
        """
        Wendet das Markup auf den Seiteninhalt an
        """
        # Die Markup-ID Auflösen zum richtigen Namen
        markup = self.db.get_markup_name( markup )

        if markup == "textile":
            # textile Markup anwenden
            if self.config.system.ModuleManager_error_handling == True:
                try:
                    from PyLucid_system import tinyTextile
                    out = self.tools.out_buffer()
                    tinyTextile.parser( out, self.PyLucid ).parse( content )
                    return out.get()
                except Exception, e:
                    self.page_msg( "Can't use textile-Markup (%s)" % e )
            else:
                from PyLucid_system import tinyTextile
                out = self.tools.out_buffer()
                tinyTextile.parser( out, self.PyLucid ).parse( content )
                return out.get()
        elif markup in ("none", "None", None, "string formatting"):
            return content
        else:
            self.page_msg( "Markup '%s' not supported yet :(" % markup )
            return content


    #~ def apply_template( self, side_content, template ):
        #~ """
        #~ Alle Tags im Template ausfüllen und dabei die Seite in Template einbauen
        #~ """
        #~ self.parser.tag_data["page_body"]    = side_content

        #~ side_content = self.parser.parse( template )

        #~ return side_content