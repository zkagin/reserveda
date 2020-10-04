from reserveda import db
from reserveda.models import Group, Item, User
from hashids import Hashids


def setup_db():
    # db.drop_all()
    db.create_all()


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


def list_items(group_id):
    return Group.query.filter_by(id=group_id).first().items


def add_item(email, name):
    user = User.query.filter_by(email=email).first()
    item = Item(name=name, status=False, group_id=user.group_id)
    db.session.add(item)
    db.session.commit()
    return item


def toggle_item(id):
    item = Item.query.filter_by(id=id).first()
    item.status = not item.status
    db.session.add(item)
    db.session.commit()
    return item.status
