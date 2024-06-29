import json

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app, g
)

from yale.auth import login_required
from . import pubmed

bp = Blueprint('yale', __name__)


@bp.route('/')
def landing_page():
    return redirect(url_for('yale.search'))


def logit(msg):
    current_app.logger.info(f"[{g.user['username']}] " + msg)


@bp.route('/search', methods=('GET', 'POST'))
@login_required
def search():
    if request.method == 'POST':
        terms = request.form['terms']
        if not terms:
            flash('terms is required.')
#        logit(f'Searching for: {terms}')
        print('Calling external_search')
        search_results = pubmed.external_search(100, terms)
        print('external_search returned this string:')
        print(search_results)
        return render_template('yale/show_search_results.html',
                               terms=terms, numhits=len(search_results), search_results=search_results)

    # GET
    return render_template('yale/main.html')
