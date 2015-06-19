# -*- coding: utf-8 -*-

import openerp
import os
import shutil
import simplejson
import time
import base64

import openerp.addons.web.http as openerpweb
import openerp.addons.web.controllers.main as webmain

class Session1(webmain.Session):
    _cp_path = "/web/session"
    
    @openerpweb.jsonrequest
    def authenticate(self, req, db, login, password, s_code=None, base_location=None):
        if s_code and req.session._uid:
            user_code = req.session.model('res.users').read(req.session._uid, ['security_code'])
            if user_code.get('security_code') == s_code:
                return self.session_info(req)
            else:
                return {'error': True}
        else:
            self.destroy(req)
            return {'uid': False}
    
    @openerpweb.jsonrequest
    def login_check(self, req, db, login, password, base_location=None):
        wsgienv = req.httprequest.environ
        env = dict(
            base_location=base_location,
            HTTP_HOST=wsgienv['HTTP_HOST'],
            REMOTE_ADDR=wsgienv['REMOTE_ADDR'],
        )
        req.session.authenticate(db, login, password, env)
        return self.session_info(req)
    
    @openerpweb.jsonrequest
    def two_way_check(self, req):
        two_way_req = req.session.model('res.users').read(req.session._uid, ['two_way_req'])
        wsgienv = req.httprequest.environ
        whitelist_ids = req.session.model('tpt.whitelist').search([])
        whitelists = req.session.model('tpt.whitelist').read(whitelist_ids, ['name'])
        ips = [r['name'] for r in whitelists]
        print "======== check..", two_way_req
        if two_way_req.get('two_way_req') and wsgienv['REMOTE_ADDR'] not in ips:
            return {'two_way_req': True}
        else:
            return {'two_way_req': False}
