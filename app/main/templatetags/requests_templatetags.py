from django import template
from django.db import models

register = template.Library()

@register.filter
def getattr(model: models.Model, attr: str) -> str:
    """Gets the value of an object's attribute
    Args:
        model (models.Model): The model object
        attr (str): The attribute name


    Returns:
        str: The value of the  model's attribute
    """
    return model.__dict__[attr]


@register.filter
def map_class(value: str) -> str:
    """Maps a value to a CSS class


    Args:
        value (str): The value to map


    Returns:
        str: The CSS class
    """
    CLASS_MAP = {
        "running": "text-bg-primary",
        "finished": "text-bg-success",
        "retrying": "text-bg-warning",
        "failure": "text-bg-danger",
        "cancelled": "text-bg-danger",
    }

    return CLASS_MAP.get(value, "text-bg-secondary")


@register.filter
def get_value(dictionary, key) -> str:
    """Gets the value of a key in a dictionary
    Args:
        dictionary (dict): The dictionary
        key (str): The key


    Returns:
        str: The value of the key
    """
    return dictionary.get(key)
