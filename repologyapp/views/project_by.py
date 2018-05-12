# Copyright (C) 2020 Paul Wise <pabs3@bonedaddy.net>
#
# This file is part of repology
#
# repology is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# repology is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with repology.  If not, see <http://www.gnu.org/licenses/>.

from typing import Any

import flask

from repologyapp.config import config
from repologyapp.db import get_db
from repologyapp.globals import repometadata
from repologyapp.view_registry import ViewRegistrar

@ViewRegistrar('/project-by-<field>-in/<repo>/<package>/problems')
def package_problems(field: str, repo: str, package: str) -> Any:
    autorefresh = flask.request.args.to_dict().get('autorefresh')

    if not repo or repo not in repometadata:
        flask.abort(404)

    page_size = config['PROBLEMS_PER_PAGE']
    problems = get_db().get_package_problems(field, repo, package, page_size)

    return flask.render_template(
        'repo-package-problems.html',
        repo=repo,
        package=package,
        problems=problems,
        autorefresh=autorefresh
    )


@ViewRegistrar('/project-by-<field>-in/<repo>/<package>/<page>')
def package_metapackage(field: str, repo: str, package: str, page: Optional[str] = None) -> Any:
    if not repo or repo not in repometadata or not package:
        flask.abort(404)

    metapackages = get_db().get_package_metapackage(field, repo, package)
    metapackage_count = len(metapackages)

    if metapackage_count == 0:
        flask.abort(404)
    elif metapackage_count == 1:
        page_base = 'metapackage'
        if page:
            page = '_' + page
        else:
            page = ''
        page_type = page_base + page
        metapackage = metapackages[0]
        try:
            url = flask.url_for(page_type, name=metapackage)
        except BuildError:
            flask.abort(404)
    else:
        url = flask.url_for('metapackages', repo=repo, package=package)
    return flask.redirect(url, 307)
