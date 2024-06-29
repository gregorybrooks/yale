import json
import time
from collections import OrderedDict
from datetime import datetime

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app, g
)

from yale.auth import login_required
from . import pubmed

bp = Blueprint('yale', __name__)


@bp.route('/')
def landing_page():
    return redirect(url_for('yale.websearch'))


def logit(msg):
    current_app.logger.info(f"[{g.user['username']}] " + msg)


@bp.route('/websearch', methods=('GET', 'POST'))
@login_required
def websearch():
    if request.method == 'POST':
        terms = request.form['terms']
        if not terms:
            flash('terms is required.')
        search_results = pubmed.external_search(100, terms)
        return render_template('yale/show_search_results.html',
                               terms=terms, numhits=len(search_results), search_results=search_results)

    # GET
    return render_template('yale/main.html')

@bp.route('/search/<terms>', methods=('GET', 'POST'))
@login_required
def api_search(terms):
    start = time.time()
    startstring = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    reply = OrderedDict()
    reply['created_time'] = startstring
    reply["run_seconds"] = f"{time.time() - start}"
    reply["query"] = terms
    reply["status"] = 'completed'
    reply["result"] = pubmed.external_search(100, terms)
    return reply
