import json
import logging

import tornado.web
from sqlalchemy import func

from chapstream.api.decorators import api_response
from chapstream.api import CsRequestHandler, process_response
from chapstream.backend.db.orm import chapstream_engine as engine
from chapstream.backend.db.models.group import Group


logger = logging.getLogger(__name__)


class PostReceivers(CsRequestHandler):
    @tornado.web.authenticated
    @api_response
    def get(self, query):
        # TODO: Use sqlalchemy for doing that
        # TODO: Check relationship status
        raw_user_sql = "SELECT name, similarity(name, '"+query+"') as n_sml, " \
                       "fullname, similarity(fullname, '"+query+"') as fn_sml " \
                       "FROM users where name %% "+"'"+query+"'"+" or fullname %% "+"'"+query+"';"
        user_name_result = engine.execute(raw_user_sql).fetchall()

        groups = self.session.query(Group).filter(Group.name_tsv.op('@@')
                                                  (func.plainto_tsquery(query)))

        result = {"users": [], "groups": []}
        # Create a search result for user name result
        logger.info(user_name_result)
        for user_name, n_sml, user_fullname, fn_sml in user_name_result:
            if n_sml >= 0.2 or fn_sml >= 0.2:
                item = {"name": user_name, "fullname": user_fullname}
                result["users"].append(item)

        # Create a search result for group name result
        for group in groups:
            # TODO: Check subscription for the current user
            item = {"name": group.name, "group_id": group.id}
            result["groups"].append(item)

        return process_response(data=result)