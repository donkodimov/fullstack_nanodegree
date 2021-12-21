# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for


import logging
from logging import Formatter, FileHandler
from flask.json import jsonify
from flask_wtf import Form
from forms import *
from datetime import datetime
import models
from models import Venue, Show, Artist

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#
app = models.app
db = models.db

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    # date = dateutil.parser.parse(value)
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():

    areas_query = Venue.query.distinct(Venue.city, Venue.state).all()
    areas = [
        {
            "city": x.city,
            "state": x.state,
            "venues": Venue.query.filter_by(city=x.city).all(),
        }
        for x in areas_query
    ]
    return render_template("pages/venues.html", areas=areas)


@app.route("/venues/search", methods=["POST"])
def search_venues():

    search_term = request.form.get("search_term", "")
    try:
        results_query = Venue.query.filter(Venue.name.ilike("%" + search_term + "%"))
        results = {
            "count": results_query.count(),
            "data": [
                {
                    "id": x.id,
                    "name": x.name,
                    "num_upcoming_shows": Show.query.filter(
                        Show.venue_id == x.id, Show.start_time > datetime.now()
                    ).count(),
                }
                for x in results_query.all()
            ],
        }
        return render_template(
            "pages/search_venues.html",
            results=results,
            search_term=request.form.get("search_term", ""),
        )
    except:
        flash("An error occurred. Venues could not be listed.")
        return render_template("errors/500.html")


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):

    try:
        venue = Venue.query.get(venue_id)
        venue.upcoming_shows = [
            {
                "artist_id": x.artist_id,
                "artist_name": x.artist.name,
                "artist_image_link": x.artist.image_link,
                "start_time": x.start_time,
            }
            for x in venue.shows
            if x.start_time > datetime.now()
        ]

        venue.upcoming_shows_count = len(venue.upcoming_shows)
        venue.past_shows = [
            {
                "artist_id": x.artist_id,
                "artist_name": x.artist.name,
                "artist_image_link": x.artist.image_link,
                "start_time": x.start_time,
            }
            for x in venue.shows
            if x.start_time < datetime.now()
        ]
        venue.past_shows_count = len(venue.past_shows)
        return render_template("pages/show_venue.html", venue=venue)
    except:
        flash("Venues does not exist.")
        return render_template("pages/home.html")


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():

    form_input = request.form
    try:

        venue = Venue()
        form = VenueForm(request.form, obj=venue)
        form.populate_obj(venue)
        db.session.add(venue)
        db.session.commit()
        flash("Venue " + request.form["name"] + " was successfully listed!")
        return render_template("pages/home.html")
    except:
        db.session.rollback()
        flash(
            "An error occurred. Venue " + form_input["name"] + " could not be listed."
        )
        print(sys.exc_info())
        return render_template("errors/500.html")
    finally:
        db.session.close()


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    return jsonify({"success": True})


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():

    artists_query = Artist.query.all()
    artists = [{"id": x.id, "name": x.name} for x in artists_query]
    return render_template("pages/artists.html", artists=artists)


@app.route("/artists/search", methods=["POST"])
def search_artists():

    search_term = request.form.get("search_term", "")
    try:
        results_query = Artist.query.filter(Artist.name.ilike("%" + search_term + "%"))
        results = {
            "count": results_query.count(),
            "data": [
                {
                    "id": x.id,
                    "name": x.name,
                    "num_upcoming_shows": Show.query.filter(
                        Show.artist_id == x.id, Show.start_time > datetime.now()
                    ).count(),
                }
                for x in results_query.all()
            ],
        }
        return render_template(
            "pages/search_artists.html",
            results=results,
            search_term=request.form.get("search_term", ""),
        )
    except:
        flash("An error occurred. Artists could not be listed.")
        return render_template("errors/500.html")


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):

    try:
        artist = Artist.query.get(artist_id)
        artist.upcoming_shows = [
            {
                "venue_id": x.venue_id,
                "venue_name": x.venue.name,
                "venue_image_link": x.venue.image_link,
                "start_time": x.start_time,
            }
            for x in artist.shows
            if x.start_time > datetime.now()
        ]
        artist.upcoming_shows_count = len(artist.upcoming_shows)
        artist.past_shows = [
            {
                "venue_id": x.venue_id,
                "venue_name": x.venue.name,
                "venue_image_link": x.venue.image_link,
                "start_time": x.start_time,
            }
            for x in artist.shows
            if x.start_time < datetime.now()
        ]
        artist.past_shows_count = len(artist.past_shows)
        return render_template("pages/show_artist.html", artist=artist)
    except:
        flash("Artist does not exist.")
        return render_template("pages/home.html")

@app.route("/artists/<artist_id>", methods=["DELETE"])
def delete_artist(artist_id):
    try:
        Artist.query.filter_by(id=artist_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    return jsonify({"success": True})


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):

    artist = Artist.query.filter_by(id=artist_id).first_or_404()
    form = ArtistForm(obj=artist)
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    form = ArtistForm(request.form)
    print(form)
    artist = Artist.query.get(artist_id)
    try:
        artist.name = form.name.data
        artist.genres = form.genres.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.website = form.website_link.data
        artist.image_link = form.image_link.data
        artist.facebook_link = form.facebook_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data

        db.session.commit()

    except ValueError as e:
        print(e)
        flash("An error occurred. Artist " + form.name.data + " could not be updated.")
        print(sys.exc_info())
        db.session.rollback()
        return render_template("errors/500.html")
    finally:
        db.session.close()
        flash("Artist " + form.name.data + " was successfully updated!")
        return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first_or_404()
    form = VenueForm(obj=venue)

    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)
    print(form)
    venue = Venue.query.get(venue_id)
    try:
        venue.name = form.name.data
        venue.genres = form.genres.data
        venue.city = form.city.data
        venue.address = form.address.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.website_link = form.website_link.data
        venue.image_link = form.image_link.data
        venue.facebook_link = form.facebook_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data

        db.session.commit()

    except ValueError as e:
        print(e)
        flash("An error occurred. Venue " + form.name.data + " could not be updated.")
        print(sys.exc_info())
        db.session.rollback()
        return render_template("errors/500.html")
    finally:
        db.session.close()
        flash("Venue " + form.name.data + " was successfully updated!")
        return redirect(url_for("show_venue", venue_id=venue_id))
    # return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form_input = request.form
    try:
        # artist = Artist(**form_input)
        # if artist.seeking_venue:
        #     artist.seeking_venue = True
        # else:
        #     artist.seeking_venue = False
        # artist.genres = form_input.getlist("genres")
        artist = Artist()
        form = ArtistForm(request.form, obj=artist)
        form.populate_obj(artist)
        print(artist)
        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
        flash(
            "An error occurred. Artist " + form_input["name"] + " could not be listed."
        )
        print(sys.exc_info())
        return render_template("errors/500.html")
    finally:
        db.session.close()
    flash("Artist " + request.form["name"] + " was successfully listed!")
    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():

    shows_query = Show.query.all()
    shows = [
        {
            "venue_id": x.venue.id,
            "venue_name": x.venue.name,
            "artist_id": x.artist.id,
            "artist_name": x.artist.name,
            "artist_image_link": x.artist.image_link,
            "start_time": x.start_time,
        }
        for x in shows_query
    ]

    return render_template("pages/shows.html", shows=shows)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():

    form = ShowForm(request.form)
    try:
        show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            start_time=form.start_time.data,
        )
        db.session.add(show)
        db.session.commit()
    except:
        db.session.rollback()
        flash("An error occurred. Show could not be listed.")
        print(sys.exc_info())
        return render_template("errors/500.html")
    finally:
        db.session.close()
    flash("Show was successfully listed!")
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
