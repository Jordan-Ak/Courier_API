from .models import Tags


def tag_create(name) -> object:
    tag = Tags.objects.create(name = name)
    tag.save()
    return tag