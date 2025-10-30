# app/routes.py
import os
import random
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import db, Character, GeneralTag, SpeciesTag, AdditionalImage

main = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def delete_file(filename):
    """Safely deletes a file from the uploads folder."""
    try:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Error deleting file {filename}: {e}") # Log error

@main.route('/')
def index():
    characters = Character.query.order_by(Character.smash_count.desc()).all()
    return render_template('index.html', characters=characters)

@main.route('/character/<int:character_id>', methods=['GET', 'POST'])
def character_detail(character_id):
    character = Character.query.get_or_404(character_id)

    if request.method == 'POST':
        if not current_user.is_authenticated:
            abort(403)
        
        if 'additional_images' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('additional_images')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                new_image = AdditionalImage(filename=filename, character_id=character.id)
                db.session.add(new_image)
        
        db.session.commit()
        flash('Additional images have been uploaded!')
        return redirect(url_for('main.character_detail', character_id=character.id))

    return render_template('character_detail.html', character=character)

@main.route('/set-cover-image/<int:image_id>', methods=['POST'])
@login_required
def set_cover_image(image_id):
    image_to_promote = AdditionalImage.query.get_or_404(image_id)
    character = image_to_promote.character
    
    old_cover_filename = character.image_file
    new_cover_filename = image_to_promote.filename
    
    character.image_file = new_cover_filename
    image_to_promote.filename = old_cover_filename
    
    db.session.commit()
    flash(f'Cover image for {character.name} has been updated!')
    return redirect(url_for('main.character_detail', character_id=character.id))


@main.route('/delete-character/<int:character_id>', methods=['POST'])
@login_required
def delete_character(character_id):
    character = Character.query.get_or_404(character_id)
    
    delete_file(character.image_file)
    for image in character.additional_images:
        delete_file(image.filename)

    db.session.delete(character)
    db.session.commit()
    flash(f'{character.name} has been deleted.')
    return redirect(url_for('main.index'))

@main.route('/delete-image/<int:image_id>', methods=['POST'])
@login_required
def delete_image(image_id):
    image = AdditionalImage.query.get_or_404(image_id)
    character_id = image.character_id
    delete_file(image.filename)
    db.session.delete(image)
    db.session.commit()
    flash('Image has been deleted.')
    return redirect(url_for('main.character_detail', character_id=character_id))


@main.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            new_char = Character(
                name=request.form.get('name'),
                age=request.form.get('age'),
                from_where=request.form.get('from_where'),
                gender=request.form.get('gender'),
                image_file=filename
            )
            
            general_tags_ids = request.form.getlist('general_tags')
            species_tags_ids = request.form.getlist('species_tags')
            
            for tag_id in general_tags_ids:
                tag = GeneralTag.query.get(tag_id)
                if tag: new_char.general_tags.append(tag)
            
            for tag_id in species_tags_ids:
                tag = SpeciesTag.query.get(tag_id)
                if tag: new_char.species_tags.append(tag)
            
            db.session.add(new_char)
            db.session.commit()
            flash('New character added successfully!')
            return redirect(url_for('main.admin_panel'))

    general_tags = GeneralTag.query.all()
    species_tags = SpeciesTag.query.all()
    return render_template('admin_panel.html', general_tags=general_tags, species_tags=species_tags)

@main.route('/game-setup')
def game_setup():
    general_tags = GeneralTag.query.all()
    return render_template('game_setup.html', general_tags=general_tags)

@main.route('/start-game', methods=['POST'])
def start_game():
    selected_tags_ids = request.form.getlist('general_tags')
    num_characters = request.form.get('num_characters')
    gender = request.form.get('gender')

    query = Character.query
    
    if gender == 'Boy':
        query = query.filter(Character.gender == 'Boy')
    elif gender == 'Girl':
        query = query.filter(Character.gender == 'Girl')
    elif gender == 'MaleAndFemale':
         query = query.filter(Character.gender.in_(['Boy', 'Girl']))

    if 'all' not in selected_tags_ids:
        query = query.filter(Character.general_tags.any(GeneralTag.id.in_(selected_tags_ids)))
    
    all_filtered_chars = query.all()
    random.shuffle(all_filtered_chars)
    
    if num_characters == 'all':
        final_list = all_filtered_chars
    else:
        num = int(num_characters)
        if len(all_filtered_chars) < num:
            flash(f"Not enough characters to start a game of {num}. Only found {len(all_filtered_chars)}. Starting with all available.")
            final_list = all_filtered_chars
        else:
            final_list = all_filtered_chars[:num]
            
    n = len(final_list)
    if n > 1 and (n & (n-1)) != 0:
        power = 1
        while power * 2 <= n:
            power *= 2
        final_list = final_list[:power]
        flash(f"Bracket requires a power of 2. Truncating to the nearest power: {power} characters.")

    if len(final_list) < 2:
        flash('Not enough characters to start a game with the selected filters. Please try again.')
        return redirect(url_for('main.game_setup'))
        
    # MODIFIED: Now includes additional image URLs for the game
    characters_for_game = [{
        'id': char.id,
        'name': char.name,
        'age': char.age,
        'from_where': char.from_where,
        'image_url': url_for('static', filename='uploads/' + char.image_file),
        'additional_image_urls': [url_for('static', filename='uploads/' + img.filename) for img in char.additional_images]
    } for char in final_list]

    return render_template('game_play.html', characters_json=json.dumps(characters_for_game))

@main.route('/api/record-vote', methods=['POST'])
def record_vote():
    data = request.get_json()
    winner_id = data.get('winner_id')
    loser_id = data.get('loser_id')

    winner = Character.query.get(winner_id)
    loser = Character.query.get(loser_id)

    if winner and loser:
        winner.smash_count += 1
        loser.pass_count += 1
        db.session.commit()
        return jsonify({'success': True, 'message': 'Vote recorded.'})
    
    return jsonify({'success': False, 'message': 'Character not found.'}), 404
