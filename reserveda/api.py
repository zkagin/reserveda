# api.py
# Contains all functions that interface with the database, and may later convert into
# a fully capable and independent API (which would require adding additional
# authentication logic)

from reserveda import db, email as email_api
from reserveda.models import Group, Item, User, Event
from hashids import Hashids


def register(email, password, code=None):
    if code:
        group = Group.query.filter_by(code=code).first()
        if not group:
            return False
    else:
        last_org = Group.query.order_by(Group.id.desc()).first()
        last_id = last_org.id if last_org else -1
        code = Hashids(min_length=5).encode(last_id + 1)
        group = Group(name="Unknown", code=code)
        db.session.add(group)
        db.session.commit()
    user = User(email=email, group_id=group.id)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def login(email, password):
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return user
    else:
        return None


def get_item(item_id):
    return Item.query.filter_by(id=item_id).first()


def list_items(group_id):
    return (
        Item.query.filter_by(group_id=group_id, deleted=False).order_by(Item.id).all()
    )


def add_item(user_id, name):
    user = User.query.filter_by(id=user_id).first()
    item = Item(name=name, status=False, group_id=user.group_id)
    db.session.add(item)
    db.session.commit()
    event = Event(
        action="created", item_id=item.id, user_id=user_id, group_id=user.group_id
    )
    db.session.add(event)
    db.session.commit()
    return item


def check_item_access(user_id, item_id):
    item = Item.query.filter_by(id=item_id).first()
    user = User.query.filter_by(id=user_id).first()
    return item and user and item.group_id == user.group_id


def toggle_item(user_id, item_id, comment, force):
    if not check_item_access(user_id=user_id, item_id=item_id):
        return False
    item = Item.query.filter_by(id=item_id).first()
    if item.status and item.owner_id != user_id and not force:
        return False

    if item.status:
        item.status = False
        item.owner_id = None
        action = "returned"
    else:
        item.status = True
        item.owner_id = user_id
        action = "reserved"
    event = Event(
        action=action, item_id=item_id, user_id=user_id, group_id=item.group_id
    )
    db.session.add(item)
    db.session.add(event)
    if comment:
        event.comment = comment
    db.session.commit()
    return True


def delete_item(user_id, item_id):
    if not check_item_access(user_id=user_id, item_id=item_id):
        return False
    item = Item.query.filter_by(id=item_id).first()
    item.status = False
    item.owner_id = None
    item.deleted = True
    event = Event(
        action="deleted", item_id=item.id, user_id=user_id, group_id=item.group_id
    )
    db.session.add(event)
    db.session.add(item)
    db.session.commit()
    return True


def list_events(user_id, item_id):
    if not check_item_access(user_id=user_id, item_id=item_id):
        return False
    return Event.query.filter_by(item_id=item_id).order_by(Event.id).all()


def send_password_reset_email(email):
    user = User.query.filter_by(email=email).first()
    if user:
        email_api.send_password_reset_email(user)


def verify_reset_password_token(token):
    user = User.verify_reset_password_token(token)
    if user:
        return user.email
    return None


def set_password(email, password):
    user = User.query.filter_by(email=email).first()
    if user:
        user.set_password(password)
        db.session.commit()
