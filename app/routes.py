from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory
from .forms import RegistrationForm, LoginForm, AddItemForm, EditItemForm
from .models import db, User, Item
from flask_login import login_user, logout_user, login_required, current_user
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import jsonify
from .models import Item

bp = Blueprint('main', __name__)
UPLOAD_FOLDER = 'uploads'  # Relative to 'app' directory.  Create this!
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Helper function to check file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
@login_required
def index():
    items = Item.query.filter_by(user_id=current_user.id).order_by(Item.created_at.desc()).all()
    return render_template('index.html', items=items)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # Don't allow re-registration

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login')) # Change here!
    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')  # Handle redirection after login
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Login failed. Check email and password.', 'danger')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login')) # Change here!

@bp.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    form = AddItemForm()
    if form.validate_on_submit():
        # Handle file upload
        filename = None
        if form.image.data:
            file = form.image.data
             # Check if the file is allowed
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Ensure unique filename
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{timestamp}{ext}"

                # Create the uploads directory if it doesn't exist
                os.makedirs(os.path.join(bp.root_path, UPLOAD_FOLDER), exist_ok=True)
                filepath = os.path.join(bp.root_path, UPLOAD_FOLDER, filename)
                file.save(filepath)

            else:
                flash('Invalid file type. Allowed types: png, jpg, jpeg, gif', 'danger')
                return redirect(url_for('main.add_item'))


        item = Item(
            name=form.name.data,
            room=form.room.data,
            cost=form.cost.data,
            bought_by=form.bought_by.data,
            purchase_date=form.purchase_date.data,
            is_new=form.is_new.data,
            category=form.category.data,
            image_filename=filename,
            user_id=current_user.id
        )
        db.session.add(item)
        db.session.commit()
        flash('Item added successfully!', 'success')
        return redirect(url_for('main.index'))
    return render_template('add_item.html', form=form)

@bp.route('/item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def item(item_id):
    item = Item.query.get_or_404(item_id)
    # Check ownership! Important for security.
    if item.user_id != current_user.id:
        flash("You don't have permission to access this item.", "danger")
        return redirect(url_for('main.index'))

    form = EditItemForm(obj=item)  # Pre-populate the form

    if form.validate_on_submit():
        item.name = form.name.data
        item.room = form.room.data
        item.cost = form.cost.data
        item.bought_by = form.bought_by.data
        item.purchase_date = form.purchase_date.data
        item.is_new = form.is_new.data
        item.category = form.category.data

        # Handle image update
        if form.image.data:
            file = form.image.data
            if file and allowed_file(file.filename):
                # Delete old image if it exists
                if item.image_filename:
                    old_filepath = os.path.join(bp.root_path, UPLOAD_FOLDER, item.image_filename)
                    if os.path.exists(old_filepath):
                        os.remove(old_filepath)

                # Save new image
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{timestamp}{ext}"
                filepath = os.path.join(bp.root_path, UPLOAD_FOLDER, filename)
                file.save(filepath)
                item.image_filename = filename

        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('main.item', item_id=item.id))

    return render_template('item.html', form=form, item=item)


@bp.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    # Check if the current user owns the image being requested
    item = Item.query.filter_by(image_filename=filename).first()
    if not item or item.user_id != current_user.id:
        flash("You don't have permission to access this file.", "danger")
        return redirect(url_for('main.index'))
    try:
        return send_from_directory(os.path.join(bp.root_path, UPLOAD_FOLDER), filename)
    except FileNotFoundError:
        flash("File not found.", "danger") #Or you could return a 404 directly
        return redirect(url_for('main.index'))

@bp.route('/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash("You don't have permission to delete this item.", "danger")
        return redirect(url_for('main.index'))

    # Delete associated image file
    if item.image_filename:
        filepath = os.path.join(bp.root_path, UPLOAD_FOLDER, item.image_filename)
        if os.path.exists(filepath):
            os.remove(filepath)

    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('main.index'))

# API Route
@bp.route('/api/items_summary', methods=['GET'])
def items_summary():
    items = Item.query.all()
    result = []
    for item in items:
        result.append({
            'name': item.name,
            'room': item.room,
            'category': item.category,
            'purchase_date': item.purchase_date.isoformat() if item.purchase_date else None
        })
    return jsonify(result)

