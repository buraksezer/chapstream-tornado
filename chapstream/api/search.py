import json
import logging

import tornado.web

from chapstream.api.decorators import api_response
from chapstream.api import CsRequestHandler, process_response
from chapstream.backend.db.orm import chapstream_engine as engine

logger = logging.getLogger(__name__)


class PostReceivers(CsRequestHandler):
    @tornado.web.authenticated
    @api_response
    def get(self, query):
        raw_user_sql = "SELECT name, similarity(name, '"+query+"') as n_sml, " \
                       "fullname, similarity(fullname, '"+query+"') as fn_sml " \
                       "FROM users where name %% "+"'"+query+"'"+" or fullname %% "+"'"+query+"';"
        user_name_result = engine.execute(raw_user_sql).fetchall()

        raw_group_sql = "SELECT id, name, similarity(name, '"+query+"') as n_sml " \
                        "FROM groups where name %% "+"'"+query+"';"
        group_name_result = engine.execute(raw_group_sql).fetchall()

        result = {"users": [], "groups": []}
        # Create a search result for user name result
        for user_name, n_sml, user_fullname, fn_sml in user_name_result:
            if n_sml >= 0.5 or fn_sml >= 0.5:
                item = {"name": user_name, "fullname": user_fullname}
                result["users"].append(item)

        # Create a search result for group name result
        for group_id, group_name, n_sml in group_name_result:
            if n_sml > 0.2:
                item = {"name": group_name, "group_id": group_id}
                result["groups"].append(item)

        return process_response(data=result)