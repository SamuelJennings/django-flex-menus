# Context Aware Example

Context-aware menus adapt based on the current request context, user permissions, or specific objects passed as kwargs through the template tag. They're perfect for object detail pages, user dashboards, or any scenario where the menu needs to be tailored to the current context.

## How Context Works

The key to context-aware menus is passing kwargs through the `render_menu` template tag. These kwargs are then available to your menu's `check` functions, function-based url resolution and `get_context_data` methods.

```django-html
<!-- In your template -->
{% load flex_menu %}

<!-- Pass an instance object context to the menu -->
{% render_menu "detail_menu" instance=object %}

<!-- Pass multiple context variables -->
{% render_menu "user_menu" user=request.user can_edit=user_can_edit %}
```

## Object-Specific Menus

Let's start by creating a simple menu to place on our article detail page. This menu is designed for article authors and will have links to edit and delete the article.

```python
# menus.py
from flex_menu.menu import MenuGroup, MenuLink

class ArticleLink(MenuLink):
    """Menu link for article actions, context-aware based on the article instance"""
    template_name = "menus/article/link.html"

class ArticleMenu(MenuGroup):
    """Menu for article actions, context-aware based on the article instance"""
    template_name = "menus/article/menu.html"
    allowed_children = [ArticleLink]

article_menu = ArticleMenu("article_menu", 
    children=[
        ArticleLink(
            "edit", 
            view_name="article_edit",
        ),
        ArticleLink(
            "delete", 
            view_name="article_delete", 
        )
])
```

The problem here is that this menu will be visible to all users, even those who shouldn't see it. We can fix this by 
adding a `check` function to any links that require special permissions. Let's create a check function that verifies if 
the current user is the author of the article:

```python
def is_article_author(request, instance=None, **kwargs):
    """Check if the current user is the author of the article instance"""
    if not request.user.is_authenticated or not instance:
        return False
    return instance.author == request.user

# Update the menu links to use the check function
article_menu = ArticleMenu("article_menu",
    children=[
        ArticleLink(
            "edit", 
            view_name="article_edit",
            check=is_article_author  # Only show if user is the author
        ),
        ArticleLink(
            "delete", 
            view_name="article_delete", 
            check=is_article_author  # Only show if user is the author
        )
])
```

Now, the "edit" and "delete" links will only be visible if the current user is the author of the article instance passed
through the template tag. If all children are hidden by their checks, the ArticleMenu itself will also be hidden.

:::{note}
All arguments passed to the `render_menu` template tag are forwarded to check functions, URL callables, and `get_context_data` methods. This means you can pass any relevant context needed for your menu logic.

See [check functions](check-functions) and [dynamic URL resolution](#dynamic-url-resolution) for more examples.
:::

