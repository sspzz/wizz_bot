from flask import Flask
from flask import request
from flask import send_from_directory, send_file, render_template, redirect, url_for
from wizz import WizardFactory
import random
import os

app = Flask(__name__)

def _send(file):
	np = os.path.normpath(file)
	return send_from_directory(os.path.join(app.root_path, os.path.dirname(np)), os.path.basename(np))


#
# Root
#
@app.route('/', methods=['POST', 'GET'])
def root():
	if request.form:
		token_id = request.form['token_id']
		token_type = request.form['token_type']
		return redirect(url_for("{}_root".format(token_type), token_id=token_id))
	else:
		return render_template('root.html')


#
# Wizards
#
@app.route('/wizards/<token_id>')
def wizard_root(token_id):
	return render_template('wiz.html', name="Wizard #{}".format(token_id))

@app.route('/wizards/<token_id>/gm')
def wizard_gm(token_id):
	wiz = WizardFactory.get_wizard(token_id)
	return _send(wiz.gm)

@app.route('/wizards/<token_id>/poster')
def wizard_poster(token_id):
	return send_file(WizardFactory.anatomy(token_id)[1], mimetype='image/png')

@app.route('/wizards/<token_id>/walkcycle')
def wizard_walkcycle(token_id):
	wiz = WizardFactory.get_wizard(token_id)
	return _send(wiz.walkcycle_large)

@app.route('/wizards/<token_id>/walkfam')
def wizard_walkcycle_with_familiar(token_id):
	wiz = WizardFactory.get_wizard(token_id)
	return _send(wiz.walkcycle_with_familiar)

@app.route('/wizards/<token_id>/walkfamr')
def wizard_walkcycle_with_familiar_reverse(token_id):
	wiz = WizardFactory.get_wizard(token_id)
	return _send(wiz.walkcycle_with_familiar_reversed)

@app.route('/wizards/<token_id>/familiar')
def wizard_familiar_walkcycle(token_id):
	wiz = WizardFactory.get_wizard(token_id)
	return _send(wiz.walkcycle_familiar_large)

@app.route('/wizards/<token_id>/mugshot')
def wizard_mugshot(token_id):
	wiz = WizardFactory.get_wizard(token_id)
	return _send(wiz.mugshot)

@app.route('/wizards/<token_id>/rip')
def wizard_rip(token_id):
	wiz = WizardFactory.get_wizard(token_id)
	return _send(wiz.rip)

#
# Souls
#
@app.route('/souls/<token_id>')
def soul_root(token_id):
	return render_template('soul.html', name="Soul #{}".format(token_id))

@app.route('/souls/<token_id>/poster')
def soul_poster(token_id):
	return send_file(WizardFactory.anatomy(token_id, is_soul=True)[1], mimetype='image/png')

@app.route('/souls/<token_id>/mugshot')
def soul_mugshot(token_id):
	soul = WizardFactory.get_wizard(token_id, is_soul=True)
	return _send(soul.mugshot)
#
# Warriors
#
@app.route('/warriors/<token_id>')
def warrior_root(token_id):
	return render_template('war.html', name="Warrior #{}".format(token_id))

@app.route('/warriors/<token_id>/poster')
def warrior_poster(token_id):
	return send_file(WizardFactory.anatomy(token_id, is_warrior=True)[1], mimetype='image/png')
