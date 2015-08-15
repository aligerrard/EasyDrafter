from flask import Flask, request, jsonify, render_template, redirect, flash, session
import os
# from flask_debugtoolbar import DebugToolbarExtension
import jinja2

import model

from model import User, Size_Chart, Measurement_Chart, connect_to_db, db


app = Flask(__name__)

app.secret_key = os.environ['SECRET_KEY'] 
#much source secrets.sh each time you enter virtual env, will go away after each session

app.jinja_env.undefined = jinja2.StrictUndefined

@app.route('/')
def home_page():
	return render_template('/splash-page.html')


@app.route('/start')
def measure_page():
    """Allow input of measurements to find side template pattern"""

    return render_template("basic-measure-page.html")


@app.route('/front-draft')
def front_draft_page():
    """Use template measurements to draft a front block that closest fit them and allow users to change block to fit them using inputs """
    
    # session['measurements'] = {}

    bust_input = request.args.get("bust")
    waist_input = request.args.get("waist")


    if float(bust_input) / float(waist_input) > 1.40: # the largest ratio of waist to bust in my standard sizes
        size_chart = Size_Chart.query.filter(Size_Chart.bust >= float(bust_input), Size_Chart.bust > float(bust_input) -1 ).first()
        # print size_chart
        size_chart_dictionary = size_chart.__dict__
        # print size_chart_dictionary
        del size_chart_dictionary['_sa_instance_state']
        session['measurements'] = size_chart_dictionary
       

    else:
        size_chart = Size_Chart.query.filter(Size_Chart.waist >= float(waist_input), Size_Chart.waist > float(waist_input) -1 ).first()
        # print size_chart
        size_chart_dictionary = size_chart.__dict__
        # print size_chart_dictionary
        del size_chart_dictionary['_sa_instance_state']
        session['measurements'] = size_chart_dictionary
 


    session['measurements']['nickname'] = request.args.get("nickname")
    print session['measurements']['nickname']
    print session['measurements']
    session['measurements']['bust'] = bust_input
    session['measurements']['waist'] = waist_input


    return render_template("front-draft.html", size_chart=session['measurements'])


@app.route('/back-draft')
def back_draft_page():
    """Take Front Draft measurements, save them to session, and draft a Back Draft."""

    session['measurements']['full_length'] = request.args.get('full-length')
    session['measurements']['center_front'] = request.args.get('center-front')
    session['measurements']['front_shoulder_slope'] = request.args.get('front-shoulder-slope')
    session['measurements']['strap'] = request.args.get('strap')
    session['measurements']['front_across_shoulder'] = request.args.get('front-across-shoulder')
    session['measurements']['across_chest'] = request.args.get('across-chest')
    session['measurements']['bust_depth'] = request.args.get('bust-depth')
    session['measurements']['shoulder_length'] = request.args.get('shoulder-length')
    session['measurements']['bust_arc'] = request.args.get('bust-arc')
    session['measurements']['bust_span'] = request.args.get('bust-span')
    session['measurements']['waist_arc'] = request.args.get('waist-arc')
    session['measurements']['dart_placement'] = request.args.get('dart-placement')
    session['measurements']['side_length'] = request.args.get('side-length')


    return render_template("back-draft.html", size_chart=session['measurements'])


@app.route('/pattern')
def pattern_page():
    """Send Back Draft measurements to session and save measurement chart to db"""

    session['measurements']['full_length_back'] = request.args.get("full-length-back")
    session['measurements']['center_back'] = request.args.get("center-back")
    session['measurements']['back_shoulder_slope'] = request.args.get("back-shoulder-slope")
    session['measurements']['across_back'] = request.args.get("across-back")
    session['measurements']['back_arc'] = request.args.get("back-arc")
    session['measurements']['waist_arc_back'] = request.args.get("waist-arc-back")
    session['measurements']['back_neck'] = request.args.get("back-neck")
    session['measurements']['back_across_shoulder'] = request.args.get("back-across-shoulder")
    session['measurements']['back_dart_intake'] = request.args.get("back-dart-intake")

    return render_template("canvas.html", size_chart=session['measurements'])
                            

@app.route('/save')
def save_pattern():
    """Redirect after Save Block measurements"""
    measurements_to_add = Measurement_Chart(
        nickname=session['measurements']['nickname'],
        user_id=session['current_user_id'],
        bust=session['measurements']['bust'],   
        waist=session['measurements']['waist'],

        full_length=session['measurements']['full_length'],
        center_front=session['measurements']['center_front'],
        front_shoulder_slope=session['measurements']['front_shoulder_slope'],
        strap=session['measurements']['strap'],
        front_across_shoulder=session['measurements']['front_across_shoulder'],
        across_chest=session['measurements']['across_chest'],
        bust_depth=session['measurements']['bust_depth'],
        shoulder_length=session['measurements']['shoulder_length'],
        bust_arc=session['measurements']['bust_arc'],
        bust_span=session['measurements']['bust_span'],
        waist_arc=session['measurements']['waist_arc'],
        dart_placement=session['measurements']['dart_placement'],
        side_length=session['measurements']['side_length'],

        full_length_back=session['measurements']['full_length_back'],
        center_back=session['measurements']['center_back'],
        back_shoulder_slope=session['measurements']['back_shoulder_slope'],
        across_back=session['measurements']['across_back'],
        back_arc=session['measurements']['back_arc'],
        waist_arc_back=session['measurements']['waist_arc_back'],
        back_neck=session['measurements']['back_neck'],
        back_across_shoulder=session['measurements']['back_across_shoulder'],
        back_dart_intake=session['measurements']['back_dart_intake'])
 
    # print measurements_to_add
     
    db.session.add(measurements_to_add)
    db.session.commit() 

  
    flash("Save Successful!!")
    return redirect("/profile")


@app.route('/print/<int:chart_id_selected>')
def print_page(chart_id_selected):
    """Checks chart_id of selected measurement chart and allows you to print"""

    current_chart = Measurement_Chart.query.filter(Measurement_Chart.chart_id==chart_id_selected).first()

    current_chart_dict = current_chart.__dict__

    if current_chart_dict['_sa_instance_state']:
        del current_chart_dict['_sa_instance_state']
    
    session['measurements'] = current_chart_dict

    return render_template("canvas.html", size_chart=session['measurements'])


@app.route("/login", methods=["GET"])
def show_login():
    """Show login form."""

    return render_template("login.html")


@app.route("/login", methods=["POST"])
def process_login():
    """Log user into site.
    Find the user's login credentials look up the user, and store them in the session.
    """

    email_input = request.form.get("email")
    pword_input = request.form.get("password")


    session['logged_in_customer_email'] = email_input


    user = User.query.filter(User.email == email_input).one()

    if user:
        if pword_input != user.password:
            flash("Incorrect password")
            return redirect("/login")
        else:
            flash("Login successful!!")
            current_user = User.query.filter_by(email=email_input).first()
            current_user_dict = current_user.__dict__
            session['current_user_id'] = current_user_dict['user_id']
            print session['current_user_id']
            session['logged_in_customer_email'] = email_input
            return redirect("/profile")
        
    else:
        flash("No such email")
        return redirect("/login")


@app.route('/profile')
def user_profile_page():
    """Display user information and saved blocks"""

    user_email = session['logged_in_customer_email']

    user = User.query.filter(User.email==user_email).one()
    print type(user)

    saved_blocks = Measurement_Chart.query.filter(Measurement_Chart.user_id==1).all()

    return render_template("profile.html", user=user, session=session, savedblocks=saved_blocks)


@app.route("/logout")
def process_logout():
    """Log out user and send them to the splash page"""
    del session['logged_in_customer_email']
    del session['current_user_id']
    del session['measurements']
    flash("You have been logged out")
    return redirect("/")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    connect_to_db(app)
    app.run(debug=True, port=port)
