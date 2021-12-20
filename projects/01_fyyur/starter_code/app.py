#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

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

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = models.app
db = models.db

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  #date = dateutil.parser.parse(value)
  if isinstance(value, str):    
    date = dateutil.parser.parse(value)  
  else:    
    date = value 
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  
  areas_query = Venue.query.distinct(Venue.city, Venue.state).all()
  areas = [{'city': x.city, 'state': x.state, 'venues': Venue.query.filter_by(city = x.city).all()} for x in areas_query]
  return render_template('pages/venues.html', areas=areas);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  search_term = request.form.get('search_term', '')
  try:
      results_query = Venue.query.filter(Venue.name.ilike('%'+search_term+'%'))
      results = {'count': results_query.count(),
                  'data': [{
                    'id': x.id,
                    'name': x.name,
                    'num_upcoming_shows': Show.query.filter(Show.venue_id==x.id,
                                          Show.start_time > datetime.now()).count()} for x in results_query.all()]}
      return render_template('pages/search_venues.html', results=results, search_term=request.form.get('search_term', ''))
  except:
      flash('An error occurred. Venues could not be listed.')
      return render_template('errors/500.html')
  
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  try:
      venue = Venue.query.get(venue_id)
      venue.upcoming_shows = [{'artist_id': x.artist_id, 
                              'artist_name': x.artist.name,
                              'artist_image_link': x.artist.image_link,
                              'start_time': x.start_time} for x in venue.shows if x.start_time > datetime.now()]
      
      venue.upcoming_shows_count = len(venue.upcoming_shows)
      venue.past_shows = [{'artist_id': x.artist_id, 
                          'artist_name': x.artist.name,
                          'artist_image_link': x.artist.image_link,
                          'start_time': x.start_time} for x in venue.shows if x.start_time < datetime.now()]
      venue.past_shows_count = len(venue.past_shows)
      return render_template('pages/show_venue.html', venue=venue)
  except:
      flash('Venues does not exist.')
      return render_template('pages/home.html')


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  form_input = request.form
  try:
      venue = Venue(**form_input)
      if venue.seeking_talent:
          venue.seeking_talent = True
      else:
          venue.seeking_talent = False
      venue.genres = form_input.getlist('genres')
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
  except:
      db.session.rollback()
      flash('An error occurred. Venue ' + form_input['name'] + ' could not be listed.')
      print(sys.exc_info())
      return render_template('errors/500.html')
  finally:
      db.session.close()

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  try:
      Venue.query.filter_by(id=venue_id).delete() 
      db.session.commit()
  except:
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  return jsonify({'success': True})


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  artists_query = Artist.query.all()
  artists = [{'id': x.id, 'name': x.name} for x in artists_query]
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
 
  search_term = request.form.get('search_term', '')
  try:
      results_query = Artist.query.filter(Artist.name.ilike('%'+search_term+'%'))
      results = {'count': results_query.count(),
                  'data': [{
                    'id': x.id,
                    'name': x.name,
                    'num_upcoming_shows': Show.query.filter(Show.artist_id==x.id,
                                          Show.start_time > datetime.now()).count()} for x in results_query.all()]}
      return render_template('pages/search_artists.html', results=results, search_term=request.form.get('search_term', ''))
  except:
      flash('An error occurred. Artists could not be listed.')
      return render_template('errors/500.html')


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  try:
      artist = Artist.query.get(artist_id)
      artist.upcoming_shows = [{'venue_id': x.venue_id, 
                              'venue_name': x.venue.name,
                              'venue_image_link': x.venue.image_link,
                              'start_time': x.start_time} for x in artist.shows if x.start_time > datetime.now()]
      artist.upcoming_shows_count = len(artist.upcoming_shows)
      artist.past_shows = [{'venue_id': x.venue_id, 
                          'venue_name': x.venue.name,
                          'venue_image_link': x.venue.image_link,
                          'start_time': x.start_time} for x in artist.shows if x.start_time < datetime.now()]
      artist.past_shows_count = len(artist.past_shows)
      return render_template('pages/show_artist.html', artist=artist)
  except:
      return render_template('errors/500.html')

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form_input = request.form
  try:
      artist = Artist(**form_input)
      if artist.seeking_venue:
          artist.seeking_venue = True
      else:
          artist.seeking_venue = False
      artist.genres = form_input.getlist('genres') 
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
  except:
      db.session.rollback()
      flash('An error occurred. Artist ' + form_input['name'] + ' could not be listed.')
      print(sys.exc_info())
      return render_template('errors/500.html')
  finally:
      db.session.close()

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  shows_query = Show.query.all()
  shows = [{'venue_id': x.venue.id,
            'venue_name': x.venue.name,
            'artist_id': x.artist.id, 
            'artist_name': x.artist.name, 
            'artist_image_link': x.artist.image_link, 
            'start_time': x.start_time} for x in shows_query]

  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form_input = request.form
  print(form_input) 
  try:
      show = Show(**form_input)
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
      return render_template('pages/home.html')
  except:
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
      print(sys.exc_info())
      return render_template('errors/500.html')
  finally:
      db.session.close()
  
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
