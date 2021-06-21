#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import os
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func 
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: DONE: connect to a local postgresql database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQL_URI")
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: DONE: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    past_shows_count = db.Column(db.Integer)
    upcoming_shows_count = db.Column(db.Integer)
    # 'PastShow': name of the child class 
    # 'venue': custom property name of a single parent object assigned to any child object 
    past_shows = db.relationship('PastShow', backref='venue', lazy=True)
    upcoming_shows = db.relationship('UpcomingShow', backref='venue', lazy=True)

    def __repr__(self):
        return f'Venue: id({self.id}), name({self.name})'

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: DONE: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    past_shows_count = db.Column(db.Integer)
    upcoming_shows_count = db.Column(db.Integer)
    past_shows = db.relationship('PastShow', backref='artist', lazy=True)
    upcoming_shows = db.relationship('UpcomingShow', backref='artist', lazy=True)

    def __repr__(self):
        return f'Artist: id({self.id}), name({self.name})'

# TODO: DONE: Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class PastShow(db.Model):
    __tablename__ = 'past_shows'
    
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String)
    # Set up foreign key constraint, 'name_of_parent_table.id'
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)

    def __repr__(self):
        return f'PastShow: id({self.id}), name({self.start_time})'
    
class UpcomingShow(db.Model):
    __tablename__ = 'upcoming_shows'
    
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)

    def __repr__(self):
       return f'UpcomingShow: id({self.id}), name({self.start_time})'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
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
  # TODO: DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()
  return render_template('pages/venues.html', areas=venues);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')
  venues_found = db.session.query(Venue).filter(Venue.name.contains(search_term)).all()
  venues_displayed = []
  for venue in venues_found:
    venue_displayed = {
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": venue.upcoming_shows_count
    }
    venues_displayed.append(venue_displayed)
  response = {
    "count": len(venues_displayed),
    "data": venues_displayed
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: DONE: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: DONE: insert form data as a new Venue record in the db, instead
  error = False
  try:
    form = request.form
    name = form['name']
    city = form['city']
    state = form['state']
    address = form['address']
    phone = form['phone']
    genres = form['genres']
    facebook_link = form['facebook_link']
    image_link = form['image_link']
    website_link = form['website_link']
    seeking_talent = hasattr(form, 'seeking_talent')
    seeking_description = form['seeking_description']
    past_shows_count = 0
    upcoming_shows_count = 0
    # TODO: DONE: modify data to be the data object returned from db insertion
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, facebook_link=facebook_link,
    genres=genres, website=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()

  except():
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # TODO: DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.') 
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # Fix genres 

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  form = request.form
  error = False
  try:
    venue = Venue.query.get(venue_id)
    for past_show in venue.past_shows:
      db.session.delete(past_show)
    for upcoming_show in venue.upcoming_shows:
      db.session.delete(upcoming_show)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + form['name'] + ' could not be deleted.') 
  else:
    flash('Venue ' + form['name'] + ' was successfully deleted!')
  return render_template('pages/home.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: DONE: replace with real data returned from querying the database
  artists = Artist.query.all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  artists_found = db.session.query(Artist).filter(Artist.name.contains(search_term)).all()
  artists_displayed = []
  for artist in artists_found:
    artist_displayed = {
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": artist.upcoming_shows_count
    }
    artists_displayed.append(artist_displayed)
  response = {
    "count": len(artists_displayed),
    "data": artists_displayed
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: DONE: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  return render_template('pages/show_artist.html', artist=artist)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: DONE: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.website_link.data = artist.website_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = request.form
  error = False 
  try:
    artist = Artist.query.get(artist_id)
    artist.name = form['name']
    artist.city = form['city']
    artist.state = form['state']
    artist.phone = form['phone']
    artist.genres = form['genres']
    artist.facebook_link = form['facebook_link']
    artist.image_link = form['image_link']
    artist.website_link = form['website_link']
    artist.seeking_venue = hasattr(form, 'seeking_venue')
    artist.seeking_description = form['seeking_description']
    db.session.commit()

  except():
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + form['name'] + ' could not be edited.') 
  else:
    flash('Artist ' + form['name'] + ' was successfully edited')
 
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  #form.website_link.data = venue.website_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  # TODO: DONE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = request.form
  error = False 
  try:
    venue = Venue.query.get(venue_id)
    venue.name = form['name']
    venue.city = form['city']
    venue.state = form['state']
    venue.phone = form['phone']
    venue.genres = form['genres']
    venue.facebook_link = form['facebook_link']
    venue.image_link = form['image_link']
    venue.website_link = form['website_link']
    venue.seeking_talent = hasattr(form, 'seeking_talent')
    venue.seeking_description = form['seeking_description']
    db.session.commit()

  except():
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + form['name'] + ' could not be edited.') 
  else:
    flash('Venue ' + form['name'] + ' was successfully edited')
    
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
  # TODO: DONE: insert form data as a new Venue record in the db, instead
  # TODO: DONE: modify data to be the data object returned from db insertion
  error = False
  try:
    form = request.form
    name = form['name']
    city = form['city']
    state = form['state']
    phone = form['phone']
    genres = form['genres']
    facebook_link = form['facebook_link']
    image_link = form['image_link']
    website_link = form['website_link']
    seeking_venue = hasattr(form, 'seeking_venue')
    seeking_description = form['seeking_description']
    past_shows_count = 0
    upcoming_shows_count = 0
    
    artist = Artist(name=name, city=city, state=state, phone=phone, image_link=image_link, facebook_link=facebook_link,
    genres=genres, website_link=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()

  except():
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # TODO: DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue ' + artist.name + ' could not be listed.') 
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = UpcomingShow.query.all()
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: DONE: insert form data as a new Show record in the db, instead
  error = False
  try:
    form = request.form
    venue_id = form['venue_id']
    artist_id = form['artist_id']
    start_time = form['start_time']

    show = UpcomingShow(start_time=start_time, venue_id=venue_id, artist_id=artist_id)
    venue = Venue.query.get(venue_id)
    artist = Artist.query.get(artist_id)
    db.session.add(show)
    db.session.commit()

  except():
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
   # TODO:DONE: on unsuccessful db insert, flash an error instead.
   # e.g., flash('An error occurred. Show could not be listed.')
   # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
   flash('An error occurred. Show' + ' could not be listed.') 
  else:
    flash('Show' + ' was successfully listed!')

  return render_template('pages/home.html')

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
