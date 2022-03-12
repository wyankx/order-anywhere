from flask import Blueprint, redirect, abort, render_template
from flask_login import login_required, current_user

blueprint = Blueprint(
    'settings',
    __name__,
    template_folder='templates'
)


@blueprint.route('/settings')
@login_required
def settings_redirect():
    if current_user.__class__.__name__ == 'Restaurant':
        return redirect('/settings/organisations')
    if current_user.__class__.__name__ == 'User':
        return redirect('/')


@blueprint.route('/settings/<string:current_setting>')
@login_required
def settings(current_setting):
    if current_user.__class__.__name__ == 'Restaurant':
        # Settings dict which have next structure [setting -> html markup]
        setting_names = {'organisations': 'Организации', 'menu': 'Меню'}
        settings = {
            'organisations': [
                f'''<h1>Изменение организаций</h1>
                <a class="btn btn-outline-primary" href="/organisations_add">Добавить</a><br><br>
                {'<br>'.join([f'<div class="card" style="padding: 10px;">'
                              f'<div class="container-fluid d-flex" style="justify-content: space-between; align-items: center;">'
                              f'<div>'
                              f'<h3>{place.title}</h3>'
                              f'</div>'
                              f'<div class="d-flex" style="align-items: center;">'
                              f'<div style="margin: 0;">'
                              f'<p style="margin: 0;">'
                              f'<a class="btn btn-outline-primary" href="/organisation_edit/{place.id}">Изменить</a>'
                              f'<a class="btn btn-outline-danger" href="/organisation_delete/{place.id}">Удалить</a>'
                              f'</p>'
                              f'</div>'
                              f'</div>'
                              f'</div>'
                              f'</div>'
                              for place in current_user.places])}'''
            ],
            'menu': [
                f'''<h1>Изменение категорий</h1>
                <a class="btn btn-outline-primary" href="/categories_add">Добавить</a><br><br>
                {'<br>'.join([f'<div class="card" style="padding: 10px;">'
                              f'<div class="container-fluid d-flex" style="justify-content: space-between; align-items: center;">'
                              f'<div>'
                              f'<h3>{category.title}</h3>'
                              f'</div>'
                              f'<div class="d-flex" style="align-items: center;">'
                              f'<div style="margin: 0;">'
                              f'<p style="margin: 0;">'
                              f'<a class="btn btn-outline-primary" href="/category_edit/{category.id}">Изменить</a>'
                              f'<a class="btn btn-outline-danger" href="/category_delete/{category.id}">Удалить</a>'
                              f'</p>'
                              f'</div>'
                              f'</div>'
                              f'</div>'
                              f'</div>'
                              for category in current_user.menu.categories])}''',
                f'''<h1>Изменение меню</h1>
                <a class="btn btn-outline-primary" href="/menu_items_add">Добавить</a><br><br>
                {'<br>'.join([f'<h2>{category.title}</h2><br>' + 
                              '<br>'.join([f'<div class="card" style="padding: 10px;">'
                              f'<div class="container-fluid d-flex" style="justify-content: space-between; align-items: center;">'
                              f'<div>'
                              f'<h3>{menu_item.title}: {menu_item.price}руб.</h3>'
                              f'</div>'
                              f'<div class="d-flex" style="align-items: center;">'
                              f'<div style="margin: 0;">'
                              f'<p style="margin: 0;">'
                              f'<a class="btn btn-outline-primary" href="/menu_item_edit/{menu_item.id}">Изменить</a>'
                              f'<a class="btn btn-outline-danger" href="/menu_item_delete/{menu_item.id}">Удалить</a>'
                              f'</p>'
                              f'</div>'
                              f'</div>'
                              f'</div>'
                              f'<img src="/menu_item_image/{menu_item.id}" style="width: 30vmin">'
                              f'</div>'
                              for menu_item in category.menu_items]) for category in current_user.menu.categories])}'''
            ]
        }
    elif current_user.__class__.__name__ == 'User':
        # Settings dict which have next structure [setting -> html markup]
        setting_names = {}
        settings = {}
    if current_setting not in setting_names.keys():
        abort(404)
    return render_template('settings.html', title='Организации',  current_setting=current_setting, settings=settings, setting_names=setting_names)
