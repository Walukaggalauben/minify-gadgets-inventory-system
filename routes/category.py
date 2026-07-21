from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from services.category_service import CategoryService

category_bp = Blueprint(
    "category",
    __name__
)


def login_required():
    return "user_id" in session


@category_bp.route("/categories")
def index():

    if not login_required():
        return redirect("/")

    search = request.args.get("search", "").strip().lower()

    categories = CategoryService.get_all()

    if search:
        categories = [
            c for c in categories
            if search in c.name.lower()
        ]

    return render_template(
        "categories/index.html",
        categories=categories,
        search=search
    )


@category_bp.route("/categories/create", methods=["GET", "POST"])
def create():

    if not login_required():
        return redirect("/")

    if request.method == "POST":

        CategoryService.create(request.form)

        flash("Category created successfully.", "success")

        return redirect(url_for("category.index"))

    return render_template("categories/create.html")


@category_bp.route("/categories/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    if not login_required():
        return redirect("/")

    category = CategoryService.get(id)

    if request.method == "POST":

        CategoryService.update(
            category,
            request.form
        )

        flash("Category updated successfully.", "success")

        return redirect(url_for("category.index"))

    return render_template(
        "categories/edit.html",
        category=category
    )


@category_bp.route("/categories/toggle/<int:id>")
def toggle(id):

    if not login_required():
        return redirect("/")

    category = CategoryService.get(id)

    CategoryService.toggle_status(category)

    flash("Category status updated.", "success")

    return redirect(url_for("category.index"))